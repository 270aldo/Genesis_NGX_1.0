"""
Monitoring Utilities for ADK
============================

Provides decorators and utilities for performance monitoring,
metrics collection, and observability.
"""

from typing import Any, Callable, Dict, Optional, List
from functools import wraps
import time
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
from prometheus_client import Counter, Histogram, Gauge, Summary

from core.logging_config import get_logger

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)


# Prometheus metrics
agent_requests_total = Counter(
    'adk_agent_requests_total',
    'Total number of agent requests',
    ['agent_id', 'method', 'status']
)

agent_request_duration = Histogram(
    'adk_agent_request_duration_seconds',
    'Agent request duration in seconds',
    ['agent_id', 'method']
)

agent_active_requests = Gauge(
    'adk_agent_active_requests',
    'Number of active agent requests',
    ['agent_id']
)

agent_errors_total = Counter(
    'adk_agent_errors_total',
    'Total number of agent errors',
    ['agent_id', 'error_type']
)

agent_cache_hits = Counter(
    'adk_agent_cache_hits_total',
    'Total number of cache hits',
    ['agent_id']
)

agent_cache_misses = Counter(
    'adk_agent_cache_misses_total',
    'Total number of cache misses',
    ['agent_id']
)


class MetricsCollector:
    """Collects and aggregates metrics for agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.start_time = time.time()
        self._request_count = 0
        self._error_count = 0
        self._total_duration = 0.0
        self._cache_hits = 0
        self._cache_misses = 0
    
    def record_request(self, duration: float, success: bool = True):
        """Record a request with its duration."""
        self._request_count += 1
        self._total_duration += duration
        
        status = "success" if success else "error"
        agent_requests_total.labels(
            agent_id=self.agent_id,
            method="execute",
            status=status
        ).inc()
        
        agent_request_duration.labels(
            agent_id=self.agent_id,
            method="execute"
        ).observe(duration)
    
    def record_error(self, error_type: str):
        """Record an error occurrence."""
        self._error_count += 1
        agent_errors_total.labels(
            agent_id=self.agent_id,
            error_type=error_type
        ).inc()
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self._cache_hits += 1
        agent_cache_hits.labels(agent_id=self.agent_id).inc()
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self._cache_misses += 1
        agent_cache_misses.labels(agent_id=self.agent_id).inc()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        uptime = time.time() - self.start_time
        avg_duration = (
            self._total_duration / self._request_count 
            if self._request_count > 0 
            else 0
        )
        error_rate = (
            self._error_count / self._request_count
            if self._request_count > 0
            else 0
        )
        cache_hit_rate = (
            self._cache_hits / (self._cache_hits + self._cache_misses)
            if (self._cache_hits + self._cache_misses) > 0
            else 0
        )
        
        return {
            "agent_id": self.agent_id,
            "uptime_seconds": uptime,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": error_rate,
            "average_duration": avg_duration,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": cache_hit_rate
        }


def track_performance(
    operation_name: Optional[str] = None,
    include_args: bool = False,
    log_result: bool = False
):
    """
    Decorator to track function performance with OpenTelemetry.
    
    Args:
        operation_name: Custom operation name (defaults to function name)
        include_args: Whether to include function arguments in span attributes
        log_result: Whether to log the function result
    
    Example:
        @track_performance(operation_name="process_request")
        async def process(request):
            # Processing logic
            return result
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(op_name) as span:
                # Add function arguments as span attributes if requested
                if include_args:
                    for i, arg in enumerate(args):
                        span.set_attribute(f"arg_{i}", str(arg)[:100])
                    for key, value in kwargs.items():
                        span.set_attribute(f"kwarg_{key}", str(value)[:100])
                
                start_time = time.time()
                
                try:
                    # Execute function
                    result = await func(*args, **kwargs)
                    
                    # Log result if requested
                    if log_result:
                        span.set_attribute("result", str(result)[:100])
                    
                    span.set_status(Status(StatusCode.OK))
                    
                    # Log performance
                    duration = time.time() - start_time
                    logger.info(
                        f"{op_name} completed",
                        extra={
                            "operation": op_name,
                            "duration": duration,
                            "success": True
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    # Log error
                    duration = time.time() - start_time
                    logger.error(
                        f"{op_name} failed",
                        extra={
                            "operation": op_name,
                            "duration": duration,
                            "success": False,
                            "error": str(e)
                        },
                        exc_info=True
                    )
                    
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions
            with tracer.start_as_current_span(op_name) as span:
                if include_args:
                    for i, arg in enumerate(args):
                        span.set_attribute(f"arg_{i}", str(arg)[:100])
                    for key, value in kwargs.items():
                        span.set_attribute(f"kwarg_{key}", str(value)[:100])
                
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    
                    if log_result:
                        span.set_attribute("result", str(result)[:100])
                    
                    span.set_status(Status(StatusCode.OK))
                    
                    duration = time.time() - start_time
                    logger.info(
                        f"{op_name} completed",
                        extra={
                            "operation": op_name,
                            "duration": duration,
                            "success": True
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    duration = time.time() - start_time
                    logger.error(
                        f"{op_name} failed",
                        extra={
                            "operation": op_name,
                            "duration": duration,
                            "success": False,
                            "error": str(e)
                        },
                        exc_info=True
                    )
                    
                    raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@asynccontextmanager
async def measure_execution_time(
    operation_name: str,
    log_threshold: Optional[float] = None
):
    """
    Context manager to measure execution time.
    
    Args:
        operation_name: Name of the operation being measured
        log_threshold: Only log if duration exceeds this threshold (seconds)
    
    Example:
        async with measure_execution_time("database_query", log_threshold=1.0):
            result = await db.query(sql)
    """
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        
        if log_threshold is None or duration >= log_threshold:
            logger.info(
                f"{operation_name} execution time",
                extra={
                    "operation": operation_name,
                    "duration": duration
                }
            )


def log_metrics(
    agent_id: str,
    metrics: Dict[str, Any],
    level: str = "INFO"
):
    """
    Log metrics in a structured format.
    
    Args:
        agent_id: ID of the agent
        metrics: Dictionary of metrics to log
        level: Log level (INFO, WARNING, ERROR)
    """
    log_func = getattr(logger, level.lower(), logger.info)
    
    log_func(
        "Agent metrics",
        extra={
            "agent_id": agent_id,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


class PerformanceMonitor:
    """Monitor performance across multiple operations."""
    
    def __init__(self, name: str):
        self.name = name
        self.operations: Dict[str, List[float]] = {}
    
    def record(self, operation: str, duration: float):
        """Record operation duration."""
        if operation not in self.operations:
            self.operations[operation] = []
        self.operations[operation].append(duration)
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        if operation:
            durations = self.operations.get(operation, [])
            if not durations:
                return {"error": f"No data for operation: {operation}"}
            
            return self._calculate_stats(operation, durations)
        
        # Return stats for all operations
        return {
            op: self._calculate_stats(op, durations)
            for op, durations in self.operations.items()
        }
    
    def _calculate_stats(
        self,
        operation: str,
        durations: List[float]
    ) -> Dict[str, Any]:
        """Calculate statistics for a list of durations."""
        if not durations:
            return {}
        
        sorted_durations = sorted(durations)
        count = len(durations)
        
        return {
            "operation": operation,
            "count": count,
            "min": min(durations),
            "max": max(durations),
            "mean": sum(durations) / count,
            "median": sorted_durations[count // 2],
            "p95": sorted_durations[int(count * 0.95)] if count > 20 else None,
            "p99": sorted_durations[int(count * 0.99)] if count > 100 else None
        }
    
    def reset(self, operation: Optional[str] = None):
        """Reset collected metrics."""
        if operation:
            self.operations.pop(operation, None)
        else:
            self.operations.clear()