"""
Real-time Budget Monitoring Dashboard
Advanced monitoring and alerting system for NGX Agents budgets
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import time

from core.budget import budget_manager
from core.redis_pool import get_redis_connection
from tasks.budget import check_budget_alerts

logger = logging.getLogger(__name__)


@dataclass
class BudgetMetric:
    """Budget metric data structure."""

    agent_id: str
    timestamp: datetime
    tokens_used: int
    tokens_limit: int
    percentage: float
    cost_usd: float
    requests_count: int
    avg_tokens_per_request: float
    health_status: str


@dataclass
class SystemMetrics:
    """System-wide budget metrics."""

    timestamp: datetime
    total_agents: int
    total_tokens_used: int
    total_tokens_limit: int
    total_cost_usd: float
    agents_healthy: int
    agents_warning: int
    agents_critical: int
    efficiency_score: float


class BudgetDashboard:
    """Real-time budget monitoring dashboard."""

    def __init__(self):
        self.redis = None
        self.monitoring_active = False
        self.metrics_history: List[SystemMetrics] = []
        self.agent_metrics: Dict[str, List[BudgetMetric]] = {}
        self.alert_handlers: List[callable] = []

    async def start_monitoring(self, interval_seconds: int = 60):
        """
        Start real-time budget monitoring.

        Args:
            interval_seconds: Monitoring interval in seconds
        """
        try:
            self.redis = await get_redis_connection()
            self.monitoring_active = True

            logger.info(f"Starting budget monitoring with {interval_seconds}s interval")

            while self.monitoring_active:
                try:
                    # Collect metrics
                    await self._collect_metrics()

                    # Check for alerts
                    await self._check_alerts()

                    # Store metrics in Redis
                    await self._store_metrics()

                    # Cleanup old metrics
                    await self._cleanup_old_metrics()

                    await asyncio.sleep(interval_seconds)

                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(5)  # Short delay before retry

        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
        finally:
            self.monitoring_active = False

    def stop_monitoring(self):
        """Stop the monitoring process."""
        self.monitoring_active = False
        logger.info("Budget monitoring stopped")

    async def _collect_metrics(self):
        """Collect current budget metrics for all agents."""
        try:
            current_time = datetime.now()
            system_metrics = SystemMetrics(
                timestamp=current_time,
                total_agents=len(budget_manager.budgets),
                total_tokens_used=0,
                total_tokens_limit=0,
                total_cost_usd=0,
                agents_healthy=0,
                agents_warning=0,
                agents_critical=0,
                efficiency_score=0,
            )

            agent_metrics = {}

            for agent_id in budget_manager.budgets.keys():
                try:
                    status = budget_manager.get_budget_status(agent_id)
                    budget = budget_manager.get_budget(agent_id)
                    usage = budget_manager.get_usage(agent_id)

                    if not budget or not usage:
                        continue

                    # Calculate metrics
                    percentage = status.get("percentage", 0)
                    health_status = self._get_health_status(percentage)
                    cost_usd = self._estimate_cost(usage.total_tokens, agent_id)

                    # Get request count from Redis (if available)
                    requests_count = await self._get_request_count(agent_id)
                    avg_tokens = usage.total_tokens / max(requests_count, 1)

                    # Create agent metric
                    metric = BudgetMetric(
                        agent_id=agent_id,
                        timestamp=current_time,
                        tokens_used=usage.total_tokens,
                        tokens_limit=budget.max_tokens,
                        percentage=percentage,
                        cost_usd=cost_usd,
                        requests_count=requests_count,
                        avg_tokens_per_request=avg_tokens,
                        health_status=health_status,
                    )

                    # Store agent metric
                    if agent_id not in self.agent_metrics:
                        self.agent_metrics[agent_id] = []
                    self.agent_metrics[agent_id].append(metric)

                    # Update system metrics
                    system_metrics.total_tokens_used += usage.total_tokens
                    system_metrics.total_tokens_limit += budget.max_tokens
                    system_metrics.total_cost_usd += cost_usd

                    if health_status == "healthy":
                        system_metrics.agents_healthy += 1
                    elif health_status == "warning":
                        system_metrics.agents_warning += 1
                    else:
                        system_metrics.agents_critical += 1

                except Exception as e:
                    logger.error(f"Error collecting metrics for agent {agent_id}: {e}")

            # Calculate efficiency score
            if system_metrics.total_tokens_limit > 0:
                utilization = (
                    system_metrics.total_tokens_used / system_metrics.total_tokens_limit
                )
                health_score = system_metrics.agents_healthy / max(
                    system_metrics.total_agents, 1
                )
                system_metrics.efficiency_score = (
                    utilization * 0.7 + health_score * 0.3
                ) * 100

            # Store system metrics
            self.metrics_history.append(system_metrics)

            # Keep only last 24 hours of metrics
            cutoff_time = current_time - timedelta(hours=24)
            self.metrics_history = [
                m for m in self.metrics_history if m.timestamp > cutoff_time
            ]

            logger.debug(
                f"Collected metrics: {system_metrics.total_agents} agents, "
                f"{system_metrics.total_tokens_used:,} tokens used"
            )

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

    async def _check_alerts(self):
        """Check for budget alerts and trigger handlers."""
        try:
            alerts = []

            for agent_id in budget_manager.budgets.keys():
                status = budget_manager.get_budget_status(agent_id)
                percentage = status.get("percentage", 0)

                if percentage >= 90:
                    alerts.append(
                        {
                            "agent_id": agent_id,
                            "level": "critical",
                            "percentage": percentage,
                            "message": f"Agent {agent_id} at {percentage:.1f}% of budget",
                        }
                    )
                elif percentage >= 75:
                    alerts.append(
                        {
                            "agent_id": agent_id,
                            "level": "warning",
                            "percentage": percentage,
                            "message": f"Agent {agent_id} at {percentage:.1f}% of budget",
                        }
                    )

            # Trigger alert handlers
            if alerts:
                for handler in self.alert_handlers:
                    try:
                        await handler(alerts)
                    except Exception as e:
                        logger.error(f"Error in alert handler: {e}")

        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    async def _store_metrics(self):
        """Store metrics in Redis for real-time access."""
        try:
            if not self.redis:
                return

            # Store current system metrics
            if self.metrics_history:
                latest_metrics = self.metrics_history[-1]
                await self.redis.setex(
                    "budget:system_metrics",
                    3600,  # 1 hour TTL
                    json.dumps(asdict(latest_metrics), default=str),
                )

            # Store agent metrics
            for agent_id, metrics in self.agent_metrics.items():
                if metrics:
                    latest_metric = metrics[-1]
                    await self.redis.setex(
                        f"budget:agent:{agent_id}",
                        3600,  # 1 hour TTL
                        json.dumps(asdict(latest_metric), default=str),
                    )

            # Store alerts summary
            alert_count = sum(
                1
                for metrics in self.agent_metrics.values()
                for metric in metrics[-1:]
                if metric.health_status != "healthy"
            )

            await self.redis.setex(
                "budget:alert_count", 300, str(alert_count)  # 5 minutes TTL
            )

        except Exception as e:
            logger.error(f"Error storing metrics in Redis: {e}")

    async def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory leaks."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)

            # Clean agent metrics
            for agent_id in list(self.agent_metrics.keys()):
                self.agent_metrics[agent_id] = [
                    m for m in self.agent_metrics[agent_id] if m.timestamp > cutoff_time
                ]

                # Remove empty lists
                if not self.agent_metrics[agent_id]:
                    del self.agent_metrics[agent_id]

        except Exception as e:
            logger.error(f"Error cleaning up metrics: {e}")

    async def _get_request_count(self, agent_id: str) -> int:
        """Get request count for an agent from Redis."""
        try:
            if self.redis:
                count = await self.redis.get(f"agent:requests:{agent_id}")
                return int(count) if count else 0
            return 0
        except Exception:
            return 0

    def _get_health_status(self, percentage: float) -> str:
        """Get health status based on usage percentage."""
        if percentage >= 90:
            return "critical"
        elif percentage >= 75:
            return "warning"
        else:
            return "healthy"

    def _estimate_cost(self, tokens: int, agent_id: str) -> float:
        """Estimate cost for token usage."""
        # Basic cost estimation - $5 per million tokens average
        return (tokens / 1000000) * 5.0

    def add_alert_handler(self, handler: callable):
        """Add an alert handler function."""
        self.alert_handlers.append(handler)

    async def get_system_metrics(self) -> Optional[SystemMetrics]:
        """Get latest system metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    async def get_agent_metrics(self, agent_id: str) -> List[BudgetMetric]:
        """Get metrics for a specific agent."""
        return self.agent_metrics.get(agent_id, [])

    async def get_metrics_from_redis(self) -> Dict[str, Any]:
        """Get current metrics from Redis."""
        try:
            if not self.redis:
                return {}

            # Get system metrics
            system_data = await self.redis.get("budget:system_metrics")
            system_metrics = json.loads(system_data) if system_data else {}

            # Get agent metrics
            agent_metrics = {}
            for agent_id in budget_manager.budgets.keys():
                agent_data = await self.redis.get(f"budget:agent:{agent_id}")
                if agent_data:
                    agent_metrics[agent_id] = json.loads(agent_data)

            # Get alert count
            alert_count = await self.redis.get("budget:alert_count")

            return {
                "system_metrics": system_metrics,
                "agent_metrics": agent_metrics,
                "alert_count": int(alert_count) if alert_count else 0,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting metrics from Redis: {e}")
            return {}


# Global dashboard instance
dashboard = BudgetDashboard()


# Alert handlers


async def log_alert_handler(alerts: List[Dict[str, Any]]):
    """Log alerts to system logger."""
    for alert in alerts:
        level = alert["level"]
        message = alert["message"]

        if level == "critical":
            logger.critical(f"BUDGET ALERT: {message}")
        else:
            logger.warning(f"BUDGET ALERT: {message}")


async def slack_alert_handler(alerts: List[Dict[str, Any]]):
    """Send alerts to Slack (placeholder implementation)."""
    try:
        # This would integrate with Slack API
        # For now, just log the alerts
        for alert in alerts:
            logger.info(f"Slack alert: {alert['message']}")
    except Exception as e:
        logger.error(f"Error sending Slack alert: {e}")


# Register default alert handlers
dashboard.add_alert_handler(log_alert_handler)
dashboard.add_alert_handler(slack_alert_handler)


# Monitoring startup function
async def start_budget_monitoring():
    """Start the budget monitoring dashboard."""
    await dashboard.start_monitoring(interval_seconds=60)
