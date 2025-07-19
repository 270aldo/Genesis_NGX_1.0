"""
Monitoring service for NGX Agents.

This module provides monitoring capabilities for the system,
including performance metrics, alerts, and system health tracking.
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
from core.logging_config import get_logger

logger = get_logger(__name__)


class MetricData:
    """Container for metric data points."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize metric data container."""
        self.values = deque(maxlen=max_size)
        self.timestamps = deque(maxlen=max_size)
    
    def add(self, value: float) -> None:
        """Add a new data point."""
        self.values.append(value)
        self.timestamps.append(time.time())
    
    def get_stats(self, window_seconds: int = 300) -> Dict[str, float]:
        """Get statistics for a time window."""
        if not self.values:
            return {"count": 0, "mean": 0, "min": 0, "max": 0}
        
        # Filter values within the time window
        cutoff_time = time.time() - window_seconds
        recent_values = [
            v for v, t in zip(self.values, self.timestamps)
            if t > cutoff_time
        ]
        
        if not recent_values:
            return {"count": 0, "mean": 0, "min": 0, "max": 0}
        
        return {
            "count": len(recent_values),
            "mean": sum(recent_values) / len(recent_values),
            "min": min(recent_values),
            "max": max(recent_values),
        }


class MonitoringService:
    """Service for monitoring system metrics and health."""
    
    _instance: Optional["MonitoringService"] = None
    
    def __init__(self):
        """Initialize the monitoring service."""
        self.is_running = False
        self.metrics: Dict[str, MetricData] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.monitoring_interval = 10  # seconds
        self.monitoring_task: Optional[asyncio.Task] = None
        
    @classmethod
    def get_instance(cls) -> "MonitoringService":
        """Get singleton instance of MonitoringService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def start(self) -> None:
        """Start the monitoring service."""
        if self.is_running:
            logger.warning("Monitoring service is already running")
            return
            
        self.is_running = True
        logger.info("Monitoring service started")
        
        # Start monitoring loop
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop(self) -> None:
        """Stop the monitoring service."""
        self.is_running = False
        
        # Cancel monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Monitoring service stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.is_running:
            try:
                await self._collect_system_metrics()
                await self._check_alerts()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)  # Wait before retry
    
    async def _collect_system_metrics(self) -> None:
        """Collect system metrics."""
        try:
            # TODO: Implement actual metric collection
            # Examples:
            # - CPU usage
            # - Memory usage
            # - Request latency
            # - Error rates
            # - Active connections
            pass
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _check_alerts(self) -> None:
        """Check for alert conditions."""
        try:
            # TODO: Implement alert checking
            # Examples:
            # - High error rate
            # - Low memory
            # - Service degradation
            # - Unusual traffic patterns
            pass
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    def record_metric(self, name: str, value: float) -> None:
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = MetricData()
        self.metrics[name].add(value)
    
    def get_metric_stats(self, name: str, window_seconds: int = 300) -> Dict[str, float]:
        """Get statistics for a metric."""
        if name not in self.metrics:
            return {"count": 0, "mean": 0, "min": 0, "max": 0}
        return self.metrics[name].get_stats(window_seconds)
    
    def add_alert(self, alert_type: str, message: str, severity: str = "warning") -> None:
        """Add an alert."""
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
        }
        self.alerts.append(alert)
        
        # Keep only recent alerts (last 1000)
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
            
        # Log the alert
        log_func = logger.warning if severity == "warning" else logger.error
        log_func(f"Alert [{alert_type}]: {message}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
        ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "monitoring_active": self.is_running,
            "metrics_collected": len(self.metrics),
            "recent_alerts": len(self.get_recent_alerts(1)),  # Last hour
            "status": "healthy" if len(self.get_recent_alerts(1)) == 0 else "degraded",
        }
    
    async def run_health_check(self) -> Dict[str, bool]:
        """Run a comprehensive health check."""
        health_status = {}
        
        # TODO: Implement actual health checks
        # Examples:
        health_status["database"] = True
        health_status["cache"] = True
        health_status["external_apis"] = True
        health_status["system_resources"] = True
        
        return health_status