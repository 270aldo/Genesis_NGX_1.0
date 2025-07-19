#!/usr/bin/env python3
"""
Start Budget Monitoring System
Initializes real-time budget monitoring for NGX Agents
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from monitoring.budget_dashboard import dashboard, start_budget_monitoring
from core.settings import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class BudgetMonitoringService:
    """Budget monitoring service with graceful shutdown."""

    def __init__(self):
        self.monitoring_task = None
        self.running = False

    async def start(self):
        """Start the monitoring service."""
        try:
            logger.info("🚀 Starting NGX Agents Budget Monitoring System")

            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()

            # Start monitoring
            self.running = True
            self.monitoring_task = asyncio.create_task(start_budget_monitoring())

            logger.info("✅ Budget monitoring system started successfully")
            logger.info("📊 Monitoring all agent budgets in real-time")
            logger.info("🔔 Alerts will be triggered at 75% and 90% usage")

            # Keep the service running
            await self.monitoring_task

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            await self.stop()
        except Exception as e:
            logger.error(f"Error starting monitoring service: {e}")
            await self.stop()

    async def stop(self):
        """Stop the monitoring service gracefully."""
        if self.running:
            logger.info("🛑 Stopping budget monitoring system...")

            self.running = False
            dashboard.stop_monitoring()

            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass

            logger.info("✅ Budget monitoring system stopped gracefully")

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point."""
    service = BudgetMonitoringService()
    await service.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
