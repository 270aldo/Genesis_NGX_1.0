"""
Budget Management Tasks for NGX Agents
Handles queued requests when budget limits are exceeded
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import asyncio
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from core.budget import budget_manager, BudgetPeriod
from core.settings_lazy import settings

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="tasks.budget.queue_over_budget_task",
    queue="low_priority",
    max_retries=24,  # Retry for up to 24 hours
    default_retry_delay=3600,  # Retry every hour
)
def queue_over_budget_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a task that was queued due to budget constraints.

    This task will periodically check if budget is available and execute
    when possible, or expire after 24 hours.

    Args:
        task_data: Dictionary containing:
            - agent_id: ID of the agent
            - prompt_tokens: Number of prompt tokens
            - completion_tokens: Number of completion tokens
            - model: Model to use
            - timestamp: When the task was queued
            - budget_info: Current budget status

    Returns:
        Dict with execution status
    """
    try:
        agent_id = task_data["agent_id"]
        timestamp = datetime.fromisoformat(task_data["timestamp"])

        # Check if task is too old (>24 hours)
        if datetime.now() - timestamp > timedelta(hours=24):
            logger.warning(f"Queued task for agent {agent_id} expired after 24 hours")
            return {
                "status": "expired",
                "agent_id": agent_id,
                "message": "Task expired after 24 hours in queue",
            }

        # Check current budget status
        budget = budget_manager.get_budget(agent_id)
        usage = budget_manager.get_usage(agent_id)

        if not budget:
            logger.error(f"No budget found for agent {agent_id}")
            return {
                "status": "error",
                "agent_id": agent_id,
                "message": "No budget configuration found",
            }

        # Check if we have budget available now
        if usage and usage.total_tokens >= budget.max_tokens:
            # Still over budget, retry later
            logger.info(
                f"Agent {agent_id} still over budget "
                f"({usage.total_tokens}/{budget.max_tokens}), retrying later"
            )

            # Calculate smart retry delay based on budget period
            retry_delay = _calculate_retry_delay(budget.period, budget.reset_day)

            raise self.retry(countdown=retry_delay)

        # Budget is available! Process the task
        logger.info(f"Budget available for agent {agent_id}, processing queued task")

        # Here you would normally execute the actual agent task
        # For now, we'll just record that it would be processed
        result = {
            "status": "processed",
            "agent_id": agent_id,
            "queued_duration_minutes": int(
                (datetime.now() - timestamp).total_seconds() / 60
            ),
            "budget_status": {
                "used": usage.total_tokens if usage else 0,
                "limit": budget.max_tokens,
                "percentage": (
                    (usage.total_tokens / budget.max_tokens * 100) if usage else 0
                ),
            },
        }

        # TODO: Actually execute the agent task here
        # This would involve calling the appropriate agent with the original request

        return result

    except MaxRetriesExceededError:
        logger.error(f"Max retries exceeded for agent {task_data.get('agent_id')}")
        return {
            "status": "failed",
            "agent_id": task_data.get("agent_id"),
            "message": "Max retries exceeded waiting for budget",
        }
    except Exception as e:
        logger.error(f"Error processing queued budget task: {e}")
        return {
            "status": "error",
            "agent_id": task_data.get("agent_id"),
            "message": str(e),
        }


@shared_task(name="tasks.budget.check_budget_alerts", queue="default")
def check_budget_alerts() -> Dict[str, Any]:
    """
    Periodic task to check budget usage and send alerts.

    Sends notifications when agents are approaching their budget limits.

    Returns:
        Summary of alerts sent
    """
    try:
        alerts_sent = []
        all_usage = budget_manager.get_all_usage()

        for agent_id, periods in all_usage.items():
            budget = budget_manager.get_budget(agent_id)
            if not budget:
                continue

            # Get current period usage
            period_key = budget_manager._get_period_key(agent_id)
            usage = periods.get(period_key)

            if not usage:
                continue

            # Calculate usage percentage
            percentage = (usage.total_tokens / budget.max_tokens) * 100

            # Send alerts at different thresholds
            if percentage >= 90 and percentage < 100:
                logger.warning(
                    f"Agent {agent_id} at {percentage:.1f}% of budget "
                    f"({usage.total_tokens}/{budget.max_tokens} tokens)"
                )
                alerts_sent.append(
                    {"agent_id": agent_id, "threshold": "90%", "usage": percentage}
                )

                # TODO: Send actual notification (email, Slack, etc.)

            elif percentage >= 75 and percentage < 90:
                logger.info(f"Agent {agent_id} at {percentage:.1f}% of budget")
                alerts_sent.append(
                    {"agent_id": agent_id, "threshold": "75%", "usage": percentage}
                )

        return {
            "status": "success",
            "alerts_sent": len(alerts_sent),
            "details": alerts_sent,
        }

    except Exception as e:
        logger.error(f"Error checking budget alerts: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(name="tasks.budget.reset_period_budgets", queue="default")
def reset_period_budgets() -> Dict[str, Any]:
    """
    Task to handle budget resets at period boundaries.

    This should be scheduled to run daily to catch any budgets
    that need resetting.

    Returns:
        Summary of budgets reset
    """
    try:
        reset_count = 0

        for agent_id in budget_manager.budgets.keys():
            if budget_manager._should_reset(agent_id):
                budget_manager._reset_usage(agent_id)
                reset_count += 1
                logger.info(f"Reset budget for agent {agent_id}")

        return {"status": "success", "budgets_reset": reset_count}

    except Exception as e:
        logger.error(f"Error resetting budgets: {e}")
        return {"status": "error", "message": str(e)}


def _calculate_retry_delay(period: BudgetPeriod, reset_day: Optional[int]) -> int:
    """
    Calculate smart retry delay based on budget period.

    Args:
        period: Budget period type
        reset_day: Day of reset (if applicable)

    Returns:
        Retry delay in seconds
    """
    now = datetime.now()

    if period == BudgetPeriod.DAILY:
        # Retry at next midnight
        tomorrow = now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        delay = (tomorrow - now).total_seconds()

    elif period == BudgetPeriod.WEEKLY:
        # Retry on reset day
        days_until_reset = (reset_day - now.weekday() - 1) % 7
        if days_until_reset == 0:
            days_until_reset = 7
        next_reset = now.replace(hour=0, minute=0, second=0) + timedelta(
            days=days_until_reset
        )
        delay = (next_reset - now).total_seconds()

    elif period == BudgetPeriod.MONTHLY:
        # Retry on reset day of month
        if now.day < reset_day:
            next_reset = now.replace(day=reset_day, hour=0, minute=0, second=0)
        else:
            # Next month
            if now.month == 12:
                next_reset = now.replace(
                    year=now.year + 1,
                    month=1,
                    day=reset_day,
                    hour=0,
                    minute=0,
                    second=0,
                )
            else:
                next_reset = now.replace(
                    month=now.month + 1, day=reset_day, hour=0, minute=0, second=0
                )
        delay = (next_reset - now).total_seconds()

    else:
        # Default retry in 1 hour for infinite/yearly budgets
        delay = 3600

    # Cap delay at 24 hours and ensure minimum of 1 hour
    return int(max(3600, min(delay, 86400)))


# Register periodic tasks in beat schedule
from core.celery_app import app

app.conf.beat_schedule.update(
    {
        "budget-alerts": {
            "task": "tasks.budget.check_budget_alerts",
            "schedule": 3600.0,  # Every hour
            "options": {
                "queue": "default",
                "priority": 5,
            },
        },
        "budget-resets": {
            "task": "tasks.budget.reset_period_budgets",
            "schedule": 86400.0,  # Every 24 hours
            "options": {
                "queue": "default",
                "priority": 5,
            },
        },
    }
)
