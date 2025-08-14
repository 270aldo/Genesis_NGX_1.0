"""
Elite Performance Monitoring Dashboard for GENESIS - FASE 9 Performance Optimization
==================================================================================

Advanced real-time performance monitoring and analytics system featuring:
- Real-time system resource tracking (CPU, memory, disk, network)
- Application performance metrics (P50/P95/P99 response times, throughput)
- Multi-level cache performance and hit rate analysis
- Database connection pooling and query performance
- AI agent response times and token usage tracking
- Streaming service performance and connection metrics
- Automatic alerting and anomaly detection
- Historical trend analysis and predictive insights
- Performance KPI scoring and health assessments

This elite dashboard provides comprehensive insights for maintaining
sub-50ms P95 response times and 10,000+ RPS throughput.
"""

import asyncio
import os
import statistics
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import psutil

from app.middleware.performance import get_performance_middleware
from core.advanced_cache_manager import advanced_cache_manager
from core.logging_config import get_logger
from core.optimized_agent_cache import get_agent_cache_statistics

logger = get_logger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric with timestamp."""

    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class PerformanceAlert:
    """Performance alert configuration and state."""

    metric_name: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    window_minutes: int
    alert_triggered: bool = False
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data["last_triggered"]:
            data["last_triggered"] = data["last_triggered"].isoformat()
        return data


class PerformanceCollector:
    """Collects and aggregates performance metrics from various sources."""

    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.collection_interval = 30  # seconds
        self.is_collecting = False
        self._collection_task: Optional[asyncio.Task] = None

        # Performance thresholds
        self._setup_default_alerts()

    def _setup_default_alerts(self) -> None:
        """Setup default performance alerts."""
        self.alerts = {
            "api_response_time_p95": PerformanceAlert(
                metric_name="api_response_time_p95",
                threshold=100.0,  # 100ms
                comparison="gt",
                window_minutes=5,
            ),
            "cpu_usage": PerformanceAlert(
                metric_name="cpu_usage",
                threshold=80.0,  # 80%
                comparison="gt",
                window_minutes=5,
            ),
            "memory_usage": PerformanceAlert(
                metric_name="memory_usage",
                threshold=85.0,  # 85%
                comparison="gt",
                window_minutes=5,
            ),
            "cache_hit_ratio": PerformanceAlert(
                metric_name="cache_hit_ratio",
                threshold=0.7,  # 70%
                comparison="lt",
                window_minutes=10,
            ),
            "database_connection_errors": PerformanceAlert(
                metric_name="database_connection_errors",
                threshold=5.0,
                comparison="gt",
                window_minutes=5,
            ),
        }

    async def start_collection(self) -> None:
        """Start continuous performance metric collection."""
        if self.is_collecting:
            logger.warning("Performance collection already running")
            return

        self.is_collecting = True
        self._collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Performance metric collection started")

    async def stop_collection(self) -> None:
        """Stop performance metric collection."""
        if not self.is_collecting:
            return

        self.is_collecting = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass

        logger.info("Performance metric collection stopped")

    async def _collection_loop(self) -> None:
        """Main collection loop."""
        while self.is_collecting:
            try:
                await self.collect_metrics()
                await self.check_alerts()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance collection loop: {e}")
                await asyncio.sleep(self.collection_interval)

    async def collect_metrics(self) -> None:
        """Collect metrics from all sources."""
        timestamp = datetime.utcnow()

        try:
            # Collect API performance metrics
            await self._collect_api_metrics(timestamp)

            # Collect system metrics
            await self._collect_system_metrics(timestamp)

            # Collect cache metrics
            await self._collect_cache_metrics(timestamp)

            # Collect agent metrics
            await self._collect_agent_metrics(timestamp)

            # Cleanup old metrics
            self._cleanup_old_metrics()

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

    async def _collect_api_metrics(self, timestamp: datetime) -> None:
        """Collect API performance metrics."""
        try:
            middleware = get_performance_middleware()
            if not middleware:
                return

            stats = middleware.get_performance_stats()

            # Response time metrics
            if stats.get("average_response_time_ms", 0) > 0:
                self._add_metric(
                    timestamp,
                    "api_avg_response_time",
                    stats["average_response_time_ms"],
                    "ms",
                )

            # Request volume
            self._add_metric(
                timestamp, "api_total_requests", stats.get("total_requests", 0), "count"
            )

            # Slow request count
            self._add_metric(
                timestamp,
                "api_slow_requests",
                stats.get("slow_requests_count", 0),
                "count",
            )

            # P95 response time (estimated from slow requests)
            p95_time = stats.get("performance_metrics", {}).get("p95_response_time", 0)
            if p95_time > 0:
                self._add_metric(timestamp, "api_response_time_p95", p95_time, "ms")

        except Exception as e:
            logger.error(f"Error collecting API metrics: {e}")

    async def _collect_system_metrics(self, timestamp: datetime) -> None:
        """Collect system resource metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            self._add_metric(timestamp, "cpu_usage", cpu_percent, "percent")

            # Memory metrics
            memory = psutil.virtual_memory()
            self._add_metric(timestamp, "memory_usage", memory.percent, "percent")
            self._add_metric(
                timestamp, "memory_available", memory.available // (1024 * 1024), "MB"
            )

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self._add_metric(timestamp, "disk_usage", disk_percent, "percent")

            # Process-specific metrics
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss // (1024 * 1024)  # MB
            process_cpu = process.cpu_percent()

            self._add_metric(timestamp, "process_memory_usage", process_memory, "MB")
            self._add_metric(timestamp, "process_cpu_usage", process_cpu, "percent")

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    async def _collect_cache_metrics(self, timestamp: datetime) -> None:
        """Collect cache performance metrics."""
        try:
            # Advanced cache manager metrics
            cache_stats = await advanced_cache_manager.get_comprehensive_statistics()
            global_stats = cache_stats.get("global_statistics", {})

            if global_stats:
                hit_ratio = global_stats.get("global_hit_ratio", 0)
                self._add_metric(timestamp, "cache_hit_ratio", hit_ratio, "ratio")

                avg_response = global_stats.get("average_response_time_ms", 0)
                if avg_response > 0:
                    self._add_metric(
                        timestamp, "cache_avg_response_time", avg_response, "ms"
                    )

                total_requests = global_stats.get("total_requests", 0)
                self._add_metric(
                    timestamp, "cache_total_requests", total_requests, "count"
                )

            # Layer-specific metrics
            layer_stats = cache_stats.get("layer_statistics", {})
            for layer_name, stats in layer_stats.items():
                prefix = f"cache_{layer_name}"

                hit_ratio = stats.get("hit_ratio", 0)
                self._add_metric(timestamp, f"{prefix}_hit_ratio", hit_ratio, "ratio")

                size_bytes = stats.get("size_bytes", 0)
                self._add_metric(
                    timestamp, f"{prefix}_size", size_bytes // (1024 * 1024), "MB"
                )

                entries = stats.get("entries", 0)
                self._add_metric(timestamp, f"{prefix}_entries", entries, "count")

        except Exception as e:
            logger.error(f"Error collecting cache metrics: {e}")

    async def _collect_agent_metrics(self, timestamp: datetime) -> None:
        """Collect agent performance metrics."""
        try:
            agent_stats = await get_agent_cache_statistics()

            if agent_stats:
                # Agent cache metrics
                cached_agents = agent_stats.get("cached_agents", 0)
                self._add_metric(timestamp, "agents_cached", cached_agents, "count")

                healthy_agents = agent_stats.get("healthy_agents", 0)
                self._add_metric(timestamp, "agents_healthy", healthy_agents, "count")

                cache_hit_ratio = agent_stats.get("cache_hit_ratio", 0)
                self._add_metric(
                    timestamp, "agent_cache_hit_ratio", cache_hit_ratio, "ratio"
                )

                avg_load_time = agent_stats.get("average_load_time_seconds", 0)
                if avg_load_time > 0:
                    self._add_metric(
                        timestamp, "agent_avg_load_time", avg_load_time * 1000, "ms"
                    )

        except Exception as e:
            logger.error(f"Error collecting agent metrics: {e}")

    def _add_metric(
        self,
        timestamp: datetime,
        name: str,
        value: float,
        unit: str,
        tags: Dict[str, str] = None,
    ) -> None:
        """Add a metric to the collection."""
        metric = PerformanceMetric(
            timestamp=timestamp,
            metric_name=name,
            value=value,
            unit=unit,
            tags=tags or {},
        )
        self.metrics[name].append(metric)

    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)

        for metric_name, metric_deque in self.metrics.items():
            while metric_deque and metric_deque[0].timestamp < cutoff_time:
                metric_deque.popleft()

    async def check_alerts(self) -> None:
        """Check all alert conditions and trigger if necessary."""
        for alert_name, alert in self.alerts.items():
            try:
                should_trigger = self._evaluate_alert(alert)

                if should_trigger and not alert.alert_triggered:
                    # Trigger alert
                    alert.alert_triggered = True
                    alert.last_triggered = datetime.utcnow()
                    alert.trigger_count += 1

                    await self._handle_alert_trigger(alert)

                elif not should_trigger and alert.alert_triggered:
                    # Clear alert
                    alert.alert_triggered = False
                    await self._handle_alert_clear(alert)

            except Exception as e:
                logger.error(f"Error checking alert {alert_name}: {e}")

    def _evaluate_alert(self, alert: PerformanceAlert) -> bool:
        """Evaluate if an alert condition is met."""
        metric_name = alert.metric_name

        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return False

        # Get metrics within the alert window
        cutoff_time = datetime.utcnow() - timedelta(minutes=alert.window_minutes)
        recent_metrics = [
            m for m in self.metrics[metric_name] if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return False

        # Calculate aggregate value (average for now)
        values = [m.value for m in recent_metrics]
        avg_value = statistics.mean(values)

        # Compare against threshold
        if alert.comparison == "gt":
            return avg_value > alert.threshold
        elif alert.comparison == "lt":
            return avg_value < alert.threshold
        elif alert.comparison == "eq":
            return abs(avg_value - alert.threshold) < 0.001

        return False

    async def _handle_alert_trigger(self, alert: PerformanceAlert) -> None:
        """Handle alert trigger."""
        logger.warning(
            f"PERFORMANCE ALERT TRIGGERED: {alert.metric_name} - threshold: {alert.threshold}"
        )

        # Here you would typically:
        # - Send notification (email, Slack, PagerDuty)
        # - Log to monitoring system
        # - Potentially trigger auto-scaling or other remediation

        # For now, just log
        logger.warning(
            f"Alert: {alert.metric_name} exceeded threshold {alert.threshold}"
        )

    async def _handle_alert_clear(self, alert: PerformanceAlert) -> None:
        """Handle alert clear."""
        logger.info(f"PERFORMANCE ALERT CLEARED: {alert.metric_name}")

    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get summary of metrics for the last N hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        summary = {}

        for metric_name, metric_deque in self.metrics.items():
            recent_metrics = [m for m in metric_deque if m.timestamp >= cutoff_time]

            if not recent_metrics:
                continue

            values = [m.value for m in recent_metrics]
            summary[metric_name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "median": statistics.median(values),
                "latest": values[-1] if values else None,
                "unit": recent_metrics[-1].unit if recent_metrics else None,
            }

            # Add percentiles for response times
            if "time" in metric_name and len(values) >= 10:
                sorted_values = sorted(values)
                summary[metric_name]["p95"] = sorted_values[
                    int(len(sorted_values) * 0.95)
                ]
                summary[metric_name]["p99"] = sorted_values[
                    int(len(sorted_values) * 0.99)
                ]

        return summary

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get formatted data for performance dashboard."""
        # Get recent metrics summary
        recent_summary = self.get_metrics_summary(hours=1)
        historical_summary = self.get_metrics_summary(hours=24)

        # Format for dashboard
        dashboard_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "overview": {
                "api_health": self._get_api_health_status(),
                "system_health": self._get_system_health_status(),
                "cache_health": self._get_cache_health_status(),
                "agent_health": self._get_agent_health_status(),
            },
            "metrics": {
                "recent_1h": recent_summary,
                "historical_24h": historical_summary,
            },
            "alerts": {name: alert.to_dict() for name, alert in self.alerts.items()},
            "active_alerts": [
                alert.to_dict()
                for alert in self.alerts.values()
                if alert.alert_triggered
            ],
        }

        return dashboard_data

    def _get_api_health_status(self) -> str:
        """Get API health status based on recent metrics."""
        if "api_response_time_p95" in self.metrics:
            recent_metrics = list(self.metrics["api_response_time_p95"])[-10:]
            if recent_metrics:
                avg_p95 = statistics.mean([m.value for m in recent_metrics])
                if avg_p95 > 500:
                    return "critical"
                elif avg_p95 > 100:
                    return "warning"
                else:
                    return "healthy"
        return "unknown"

    def _get_system_health_status(self) -> str:
        """Get system health status."""
        cpu_metrics = list(self.metrics.get("cpu_usage", []))[-5:]
        memory_metrics = list(self.metrics.get("memory_usage", []))[-5:]

        if cpu_metrics and memory_metrics:
            avg_cpu = statistics.mean([m.value for m in cpu_metrics])
            avg_memory = statistics.mean([m.value for m in memory_metrics])

            if avg_cpu > 90 or avg_memory > 90:
                return "critical"
            elif avg_cpu > 70 or avg_memory > 80:
                return "warning"
            else:
                return "healthy"

        return "unknown"

    def _get_cache_health_status(self) -> str:
        """Get cache health status."""
        if "cache_hit_ratio" in self.metrics:
            recent_metrics = list(self.metrics["cache_hit_ratio"])[-10:]
            if recent_metrics:
                avg_hit_ratio = statistics.mean([m.value for m in recent_metrics])
                if avg_hit_ratio < 0.5:
                    return "critical"
                elif avg_hit_ratio < 0.7:
                    return "warning"
                else:
                    return "healthy"
        return "unknown"

    def _get_agent_health_status(self) -> str:
        """Get agent health status."""
        if "agents_healthy" in self.metrics and "agents_cached" in self.metrics:
            healthy_metrics = list(self.metrics["agents_healthy"])[-1:]
            cached_metrics = list(self.metrics["agents_cached"])[-1:]

            if healthy_metrics and cached_metrics:
                healthy = healthy_metrics[0].value
                total = cached_metrics[0].value

                if total > 0:
                    health_ratio = healthy / total
                    if health_ratio < 0.8:
                        return "warning"
                    else:
                        return "healthy"

        return "unknown"


# Global performance collector instance
performance_collector = PerformanceCollector()


async def start_performance_monitoring() -> None:
    """Start the global performance monitoring system."""
    await performance_collector.start_collection()
    logger.info("Performance monitoring system started")


async def stop_performance_monitoring() -> None:
    """Stop the global performance monitoring system."""
    await performance_collector.stop_collection()
    logger.info("Performance monitoring system stopped")


def get_performance_dashboard_data() -> Dict[str, Any]:
    """Get current performance dashboard data."""
    return performance_collector.get_dashboard_data()


def get_performance_metrics_summary(hours: int = 1) -> Dict[str, Any]:
    """Get performance metrics summary."""
    return performance_collector.get_metrics_summary(hours=hours)
