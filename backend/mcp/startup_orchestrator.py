#!/usr/bin/env python3
"""
MCP Startup Orchestrator

Ensures high availability of the MCP Gateway and GENESIS ecosystem.
Features:
- Service health monitoring
- Automatic restart on failures
- Graceful degradation
- Load balancing preparation
- Dependency management
"""

import asyncio
import os
import sys
import signal
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import subprocess
import psutil
import aiohttp
from pathlib import Path

from core.logging_config import get_logger
from mcp.config import settings, NGX_TOOLS

logger = get_logger(__name__)


class ServiceMonitor:
    """Monitor and manage a single service"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.status = "stopped"
        self.health_check_failures = 0
        self.last_health_check = None
        self.restart_count = 0
        self.max_restarts = 5
        self.restart_window = timedelta(minutes=10)
        self.restart_timestamps: List[datetime] = []
        
    async def start(self) -> bool:
        """Start the service"""
        if self.process and self.process.poll() is None:
            logger.info(f"{self.name} is already running")
            return True
            
        try:
            cmd = self.config.get("start_command", [])
            if not cmd:
                logger.error(f"No start command configured for {self.name}")
                return False
                
            env = os.environ.copy()
            env.update(self.config.get("environment", {}))
            
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.config.get("working_directory", ".")
            )
            
            # Wait a bit to ensure process started
            await asyncio.sleep(2)
            
            if self.process.poll() is None:
                self.status = "running"
                logger.info(f"Started {self.name} (PID: {self.process.pid})")
                return True
            else:
                self.status = "failed"
                logger.error(f"Failed to start {self.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {self.name}: {e}")
            self.status = "error"
            return False
    
    async def stop(self) -> bool:
        """Stop the service gracefully"""
        if not self.process:
            return True
            
        try:
            # Try graceful shutdown first
            self.process.terminate()
            await asyncio.sleep(5)
            
            if self.process.poll() is None:
                # Force kill if still running
                self.process.kill()
                await asyncio.sleep(2)
                
            self.status = "stopped"
            self.process = None
            logger.info(f"Stopped {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping {self.name}: {e}")
            return False
    
    async def check_health(self) -> bool:
        """Check if service is healthy"""
        if self.status != "running":
            return False
            
        health_url = self.config.get("health_check_url")
        if not health_url:
            # Just check if process is alive
            return self.process and self.process.poll() is None
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    health_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    self.last_health_check = datetime.utcnow()
                    
                    if response.status == 200:
                        self.health_check_failures = 0
                        return True
                    else:
                        self.health_check_failures += 1
                        logger.warning(f"{self.name} health check returned {response.status}")
                        return False
                        
        except Exception as e:
            self.health_check_failures += 1
            logger.error(f"{self.name} health check failed: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart the service"""
        # Check restart limits
        now = datetime.utcnow()
        self.restart_timestamps = [
            ts for ts in self.restart_timestamps 
            if now - ts < self.restart_window
        ]
        
        if len(self.restart_timestamps) >= self.max_restarts:
            logger.error(f"{self.name} exceeded restart limit ({self.max_restarts} in {self.restart_window})")
            self.status = "restart_limit_exceeded"
            return False
            
        logger.info(f"Restarting {self.name}...")
        await self.stop()
        await asyncio.sleep(2)
        
        if await self.start():
            self.restart_count += 1
            self.restart_timestamps.append(now)
            return True
        else:
            return False


class StartupOrchestrator:
    """Orchestrate startup and monitoring of all services"""
    
    def __init__(self):
        self.services: Dict[str, ServiceMonitor] = {}
        self.running = False
        self.session: Optional[aiohttp.ClientSession] = None
        self._setup_signal_handlers()
        
    def _setup_signal_handlers(self):
        """Set up graceful shutdown handlers"""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        
    async def initialize(self):
        """Initialize the orchestrator"""
        self.session = aiohttp.ClientSession()
        
        # Define service configurations
        service_configs = {
            "mcp_gateway": {
                "start_command": [
                    sys.executable, "-m", "mcp.main"
                ],
                "working_directory": str(Path(__file__).parent.parent),
                "health_check_url": f"http://{settings.mcp_host}:{settings.mcp_port}/health",
                "environment": {
                    "MCP_HOST": settings.mcp_host,
                    "MCP_PORT": str(settings.mcp_port),
                    "MCP_API_KEY": settings.mcp_api_key
                },
                "priority": 1,
                "dependencies": []
            },
            "genesis_backend": {
                "start_command": [
                    sys.executable, "-m", "uvicorn", "main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000",
                    "--reload"
                ],
                "working_directory": str(Path(__file__).parent.parent),
                "health_check_url": "http://localhost:8000/health",
                "environment": {},
                "priority": 2,
                "dependencies": ["mcp_gateway"]
            }
        }
        
        # Create service monitors
        for name, config in service_configs.items():
            self.services[name] = ServiceMonitor(name, config)
            
        logger.info("Startup Orchestrator initialized")
        
    async def start_all_services(self):
        """Start all services in dependency order"""
        # Sort services by priority
        sorted_services = sorted(
            self.services.items(),
            key=lambda x: x[1].config.get("priority", 99)
        )
        
        for name, monitor in sorted_services:
            # Check dependencies
            deps = monitor.config.get("dependencies", [])
            for dep in deps:
                if dep in self.services and self.services[dep].status != "running":
                    logger.warning(f"Dependency {dep} not running for {name}")
                    
            # Start service
            if await monitor.start():
                logger.info(f"Successfully started {name}")
                # Wait for service to be ready
                await asyncio.sleep(3)
            else:
                logger.error(f"Failed to start {name}")
                
    async def monitor_loop(self):
        """Main monitoring loop"""
        self.running = True
        check_interval = 30  # seconds
        
        while self.running:
            try:
                # Check health of all services
                for name, monitor in self.services.items():
                    if monitor.status == "running":
                        healthy = await monitor.check_health()
                        
                        if not healthy:
                            logger.warning(f"{name} is unhealthy (failures: {monitor.health_check_failures})")
                            
                            # Restart if too many failures
                            if monitor.health_check_failures >= 3:
                                logger.info(f"Attempting to restart {name} due to health check failures")
                                await monitor.restart()
                                
                # Generate status report
                if datetime.utcnow().minute % 5 == 0:  # Every 5 minutes
                    await self.generate_status_report()
                    
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(check_interval)
                
    async def generate_status_report(self):
        """Generate and log status report"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        for name, monitor in self.services.items():
            report["services"][name] = {
                "status": monitor.status,
                "health_check_failures": monitor.health_check_failures,
                "restart_count": monitor.restart_count,
                "last_health_check": monitor.last_health_check.isoformat() if monitor.last_health_check else None,
                "pid": monitor.process.pid if monitor.process else None
            }
            
        # Save report
        report_path = Path("logs/orchestrator_status.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        # Log summary
        running = sum(1 for m in self.services.values() if m.status == "running")
        total = len(self.services)
        logger.info(f"Status Report: {running}/{total} services running")
        
    async def shutdown(self):
        """Graceful shutdown of all services"""
        logger.info("Starting graceful shutdown...")
        
        # Stop services in reverse priority order
        sorted_services = sorted(
            self.services.items(),
            key=lambda x: x[1].config.get("priority", 99),
            reverse=True
        )
        
        for name, monitor in sorted_services:
            await monitor.stop()
            
        if self.session:
            await self.session.close()
            
        logger.info("Shutdown complete")
        
    async def run(self):
        """Main orchestrator run method"""
        try:
            await self.initialize()
            await self.start_all_services()
            
            # Run monitoring loop
            await self.monitor_loop()
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
        finally:
            await self.shutdown()


class HighAvailabilityManager:
    """Manage high availability features"""
    
    def __init__(self):
        self.primary_url = f"http://{settings.mcp_host}:{settings.mcp_port}"
        self.backup_urls = []  # Future: Add backup MCP gateways
        self.circuit_breaker_failures = {}
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = timedelta(minutes=5)
        
    async def get_healthy_endpoint(self) -> Optional[str]:
        """Get a healthy MCP endpoint"""
        # Try primary first
        if await self._check_endpoint(self.primary_url):
            return self.primary_url
            
        # Try backups
        for backup_url in self.backup_urls:
            if await self._check_endpoint(backup_url):
                logger.info(f"Failing over to backup MCP: {backup_url}")
                return backup_url
                
        logger.error("No healthy MCP endpoints available")
        return None
        
    async def _check_endpoint(self, url: str) -> bool:
        """Check if an endpoint is healthy"""
        # Check circuit breaker
        if url in self.circuit_breaker_failures:
            failure_time, count = self.circuit_breaker_failures[url]
            if datetime.utcnow() - failure_time < self.circuit_breaker_timeout:
                return False  # Circuit is open
                
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{url}/health",
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    if response.status == 200:
                        # Reset circuit breaker
                        if url in self.circuit_breaker_failures:
                            del self.circuit_breaker_failures[url]
                        return True
                    else:
                        self._record_failure(url)
                        return False
                        
        except Exception:
            self._record_failure(url)
            return False
            
    def _record_failure(self, url: str):
        """Record endpoint failure for circuit breaker"""
        if url in self.circuit_breaker_failures:
            failure_time, count = self.circuit_breaker_failures[url]
            self.circuit_breaker_failures[url] = (failure_time, count + 1)
        else:
            self.circuit_breaker_failures[url] = (datetime.utcnow(), 1)


async def main():
    """Main entry point"""
    orchestrator = StartupOrchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())