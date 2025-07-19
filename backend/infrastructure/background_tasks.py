"""
Background task management for NGX Agents.

This module provides a centralized way to manage background tasks
such as periodic cleanup, metrics collection, and maintenance jobs.
"""

import asyncio
from typing import Optional, List, Callable, Dict, Any
from datetime import datetime
from core.logging_config import get_logger

logger = get_logger(__name__)


class BackgroundTask:
    """Represents a background task."""
    
    def __init__(
        self,
        name: str,
        func: Callable,
        interval: int,
        enabled: bool = True
    ):
        """
        Initialize a background task.
        
        Args:
            name: Task name
            func: Async function to execute
            interval: Interval in seconds between executions
            enabled: Whether the task is enabled
        """
        self.name = name
        self.func = func
        self.interval = interval
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0
        self.task: Optional[asyncio.Task] = None


class BackgroundTaskManager:
    """Manager for background tasks."""
    
    _instance: Optional["BackgroundTaskManager"] = None
    
    def __init__(self):
        """Initialize the background task manager."""
        self.tasks: Dict[str, BackgroundTask] = {}
        self.is_running = False
        
    @classmethod
    def get_instance(cls) -> "BackgroundTaskManager":
        """Get singleton instance of BackgroundTaskManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_task(
        self,
        name: str,
        func: Callable,
        interval: int,
        enabled: bool = True
    ) -> None:
        """
        Register a new background task.
        
        Args:
            name: Task name
            func: Async function to execute
            interval: Interval in seconds between executions
            enabled: Whether the task is enabled
        """
        if name in self.tasks:
            logger.warning(f"Task '{name}' already registered, overwriting")
            
        task = BackgroundTask(name, func, interval, enabled)
        self.tasks[name] = task
        logger.info(f"Registered background task: {name} (interval: {interval}s)")
    
    async def start(self) -> None:
        """Start all registered background tasks."""
        if self.is_running:
            logger.warning("Background task manager is already running")
            return
            
        self.is_running = True
        logger.info("Starting background task manager")
        
        # Register default tasks
        self._register_default_tasks()
        
        # Start all enabled tasks
        for task in self.tasks.values():
            if task.enabled:
                task.task = asyncio.create_task(self._run_task(task))
                
        logger.info(f"Started {len([t for t in self.tasks.values() if t.enabled])} background tasks")
    
    async def stop(self) -> None:
        """Stop all background tasks."""
        self.is_running = False
        
        # Cancel all running tasks
        for task in self.tasks.values():
            if task.task and not task.task.done():
                task.task.cancel()
                
        # Wait for all tasks to complete
        tasks_to_wait = [t.task for t in self.tasks.values() if t.task]
        if tasks_to_wait:
            await asyncio.gather(*tasks_to_wait, return_exceptions=True)
            
        logger.info("Background task manager stopped")
    
    async def _run_task(self, task: BackgroundTask) -> None:
        """Run a background task in a loop."""
        logger.info(f"Starting background task: {task.name}")
        
        while self.is_running and task.enabled:
            try:
                # Execute the task
                await task.func()
                task.last_run = datetime.now()
                task.run_count += 1
                
                # Wait for the interval
                await asyncio.sleep(task.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                task.error_count += 1
                logger.error(f"Error in background task '{task.name}': {e}")
                
                # Wait before retry (exponential backoff)
                wait_time = min(task.interval * (2 ** min(task.error_count, 5)), 3600)
                await asyncio.sleep(wait_time)
    
    def _register_default_tasks(self) -> None:
        """Register default background tasks."""
        # Cleanup task
        self.register_task(
            name="cleanup_old_data",
            func=self._cleanup_old_data,
            interval=3600,  # 1 hour
            enabled=True
        )
        
        # Metrics collection task
        self.register_task(
            name="collect_metrics",
            func=self._collect_metrics,
            interval=300,  # 5 minutes
            enabled=True
        )
        
        # Health check task
        self.register_task(
            name="health_check",
            func=self._health_check,
            interval=60,  # 1 minute
            enabled=True
        )
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old data from the system."""
        logger.info("Running cleanup task")
        # TODO: Implement actual cleanup logic
        # - Remove old logs
        # - Clean expired cache entries
        # - Archive old conversations
    
    async def _collect_metrics(self) -> None:
        """Collect system metrics."""
        logger.info("Collecting system metrics")
        # TODO: Implement metrics collection
        # - Memory usage
        # - Request counts
        # - Error rates
        # - Agent performance
    
    async def _health_check(self) -> None:
        """Perform health checks on system components."""
        logger.debug("Running health check")
        # TODO: Implement health checks
        # - Database connectivity
        # - External service availability
        # - System resource checks
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all background tasks."""
        status = {}
        for name, task in self.tasks.items():
            status[name] = {
                "enabled": task.enabled,
                "interval": task.interval,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "run_count": task.run_count,
                "error_count": task.error_count,
                "is_running": task.task and not task.task.done() if task.task else False
            }
        return status
    
    def enable_task(self, name: str) -> None:
        """Enable a background task."""
        if name in self.tasks:
            self.tasks[name].enabled = True
            logger.info(f"Enabled task: {name}")
        else:
            logger.warning(f"Task not found: {name}")
    
    def disable_task(self, name: str) -> None:
        """Disable a background task."""
        if name in self.tasks:
            self.tasks[name].enabled = False
            if self.tasks[name].task and not self.tasks[name].task.done():
                self.tasks[name].task.cancel()
            logger.info(f"Disabled task: {name}")
        else:
            logger.warning(f"Task not found: {name}")