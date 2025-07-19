"""
Budget Monitoring API
Real-time monitoring and management of agent budgets
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from core.budget import budget_manager, BudgetPeriod, BudgetAction
from core.auth import get_current_user
from app.schemas.budget import (
    BudgetStatusResponse,
    BudgetUpdateRequest,
    BudgetAlertResponse,
    BudgetUsageResponse,
    BudgetSummaryResponse,
)
from tasks.budget import check_budget_alerts, reset_period_budgets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/budget", tags=["Budget Monitoring"])


@router.get("/status", response_model=List[BudgetStatusResponse])
async def get_all_budget_status(
    current_user: Dict = Depends(get_current_user),
) -> List[BudgetStatusResponse]:
    """
    Get budget status for all agents.

    Returns current usage, limits, and projections for each agent.
    """
    try:
        statuses = []

        for agent_id in budget_manager.budgets.keys():
            status = budget_manager.get_budget_status(agent_id)

            # Calculate additional metrics
            budget = budget_manager.get_budget(agent_id)
            usage = budget_manager.get_usage(agent_id)

            if budget and usage:
                # Estimate cost
                estimated_cost = _estimate_monthly_cost(
                    usage.total_tokens, budget.max_tokens, agent_id
                )

                # Days until reset
                next_reset = budget_manager._get_next_reset_date(agent_id)
                days_until_reset = None
                if next_reset:
                    days_until_reset = (next_reset - datetime.now()).days

                # Trending direction
                trend = _calculate_usage_trend(agent_id)

                status.update(
                    {
                        "estimated_monthly_cost_usd": estimated_cost,
                        "days_until_reset": days_until_reset,
                        "usage_trend": trend,
                        "health_status": _get_health_status(status["percentage"]),
                    }
                )

            statuses.append(BudgetStatusResponse(**status))

        return statuses

    except Exception as e:
        logger.error(f"Error getting budget status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{agent_id}", response_model=BudgetStatusResponse)
async def get_agent_budget_status(
    agent_id: str, current_user: Dict = Depends(get_current_user)
) -> BudgetStatusResponse:
    """
    Get detailed budget status for a specific agent.
    """
    try:
        status = budget_manager.get_budget_status(agent_id)

        if status.get("status") == "no_budget":
            raise HTTPException(
                status_code=404, detail=f"No budget configured for agent {agent_id}"
            )

        # Add enhanced metrics
        budget = budget_manager.get_budget(agent_id)
        usage = budget_manager.get_usage(agent_id)

        if budget and usage:
            status.update(
                {
                    "estimated_monthly_cost_usd": _estimate_monthly_cost(
                        usage.total_tokens, budget.max_tokens, agent_id
                    ),
                    "projected_overage": _calculate_projected_overage(agent_id),
                    "optimization_suggestions": _get_optimization_suggestions(agent_id),
                    "historical_usage": _get_historical_usage(agent_id, days=30),
                }
            )

        return BudgetStatusResponse(**status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{agent_id}")
async def update_agent_budget(
    agent_id: str,
    update_request: BudgetUpdateRequest,
    current_user: Dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Update budget configuration for an agent.
    """
    try:
        budget = budget_manager.get_budget(agent_id)

        if not budget:
            raise HTTPException(
                status_code=404, detail=f"No budget found for agent {agent_id}"
            )

        # Update budget fields
        if update_request.max_tokens is not None:
            budget.max_tokens = update_request.max_tokens

        if update_request.period is not None:
            budget.period = BudgetPeriod(update_request.period)

        if update_request.action_on_limit is not None:
            budget.action_on_limit = BudgetAction(update_request.action_on_limit)

        if update_request.fallback_model is not None:
            budget.fallback_model = update_request.fallback_model

        # Save updated budget
        budget_manager.set_budget(budget)

        logger.info(
            f"Budget updated for agent {agent_id} by user {current_user.get('id')}"
        )

        return {
            "status": "success",
            "message": f"Budget updated for agent {agent_id}",
            "updated_budget": budget.dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating budget for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/{agent_id}")
async def reset_agent_budget(
    agent_id: str, current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Manually reset budget usage for an agent.
    """
    try:
        budget = budget_manager.get_budget(agent_id)

        if not budget:
            raise HTTPException(
                status_code=404, detail=f"No budget found for agent {agent_id}"
            )

        # Store current usage for audit
        current_usage = budget_manager.get_usage(agent_id)

        # Reset the budget
        budget_manager._reset_usage(agent_id)

        logger.warning(
            f"Budget manually reset for agent {agent_id} by user {current_user.get('id')}. "
            f"Previous usage: {current_usage.total_tokens if current_usage else 0} tokens"
        )

        return {
            "status": "success",
            "message": f"Budget reset for agent {agent_id}",
            "previous_usage": current_usage.dict() if current_usage else None,
            "reset_timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting budget for agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=List[BudgetAlertResponse])
async def get_budget_alerts(
    background_tasks: BackgroundTasks, current_user: Dict = Depends(get_current_user)
) -> List[BudgetAlertResponse]:
    """
    Get current budget alerts and trigger alert check.
    """
    try:
        # Trigger alert check in background
        background_tasks.add_task(check_budget_alerts.delay)

        alerts = []
        all_usage = budget_manager.get_all_usage()

        for agent_id, periods in all_usage.items():
            budget = budget_manager.get_budget(agent_id)
            if not budget:
                continue

            period_key = budget_manager._get_period_key(agent_id)
            usage = periods.get(period_key)

            if not usage:
                continue

            percentage = (usage.total_tokens / budget.max_tokens) * 100

            # Generate alerts based on thresholds
            if percentage >= 90:
                alerts.append(
                    BudgetAlertResponse(
                        agent_id=agent_id,
                        alert_type="critical",
                        percentage=percentage,
                        message=f"Agent {agent_id} at {percentage:.1f}% of budget",
                        recommended_action="Consider increasing budget or reducing usage",
                    )
                )
            elif percentage >= 75:
                alerts.append(
                    BudgetAlertResponse(
                        agent_id=agent_id,
                        alert_type="warning",
                        percentage=percentage,
                        message=f"Agent {agent_id} at {percentage:.1f}% of budget",
                        recommended_action="Monitor usage closely",
                    )
                )

        return alerts

    except Exception as e:
        logger.error(f"Error getting budget alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(
    current_user: Dict = Depends(get_current_user),
) -> BudgetSummaryResponse:
    """
    Get overall budget summary and cost analysis.
    """
    try:
        summary = {
            "total_agents": len(budget_manager.budgets),
            "total_monthly_tokens": 0,
            "total_used_tokens": 0,
            "estimated_monthly_cost_usd": 0,
            "agents_over_75_percent": 0,
            "agents_over_90_percent": 0,
            "cost_by_agent": {},
            "efficiency_metrics": {},
        }

        all_usage = budget_manager.get_all_usage()

        for agent_id, budget in budget_manager.budgets.items():
            summary["total_monthly_tokens"] += budget.max_tokens

            period_key = budget_manager._get_period_key(agent_id)
            periods = all_usage.get(agent_id, {})
            usage = periods.get(period_key)

            if usage:
                summary["total_used_tokens"] += usage.total_tokens
                percentage = (usage.total_tokens / budget.max_tokens) * 100

                if percentage >= 90:
                    summary["agents_over_90_percent"] += 1
                elif percentage >= 75:
                    summary["agents_over_75_percent"] += 1

                # Calculate cost for this agent
                agent_cost = _estimate_monthly_cost(
                    usage.total_tokens, budget.max_tokens, agent_id
                )
                summary["cost_by_agent"][agent_id] = agent_cost
                summary["estimated_monthly_cost_usd"] += agent_cost

        # Calculate efficiency metrics
        if summary["total_monthly_tokens"] > 0:
            summary["efficiency_metrics"] = {
                "overall_utilization_percentage": (
                    summary["total_used_tokens"] / summary["total_monthly_tokens"]
                )
                * 100,
                "cost_per_million_tokens": (
                    (
                        summary["estimated_monthly_cost_usd"]
                        / (summary["total_monthly_tokens"] / 1000000)
                    )
                    if summary["total_monthly_tokens"] > 0
                    else 0
                ),
                "top_cost_agents": sorted(
                    summary["cost_by_agent"].items(), key=lambda x: x[1], reverse=True
                )[:5],
            }

        return BudgetSummaryResponse(**summary)

    except Exception as e:
        logger.error(f"Error getting budget summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/maintenance/reset-all")
async def reset_all_budgets(
    background_tasks: BackgroundTasks, current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Trigger budget reset check for all agents (admin only).
    """
    try:
        # Verify admin permissions (implement as needed)
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin privileges required")

        # Trigger reset task in background
        task = reset_period_budgets.delay()

        logger.warning(f"Budget reset triggered by admin {current_user.get('id')}")

        return {
            "status": "success",
            "message": "Budget reset check triggered",
            "task_id": task.id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering budget reset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions


def _estimate_monthly_cost(used_tokens: int, max_tokens: int, agent_id: str) -> float:
    """Estimate monthly cost based on current usage."""
    # Basic cost estimation - can be enhanced with actual model pricing
    cost_per_million_tokens = 5.0  # Estimated average
    return (used_tokens / 1000000) * cost_per_million_tokens


def _calculate_usage_trend(agent_id: str) -> str:
    """Calculate usage trend for an agent."""
    # This would analyze historical data - simplified for now
    return "stable"


def _get_health_status(percentage: float) -> str:
    """Get health status based on usage percentage."""
    if percentage >= 90:
        return "critical"
    elif percentage >= 75:
        return "warning"
    elif percentage >= 50:
        return "moderate"
    else:
        return "healthy"


def _calculate_projected_overage(agent_id: str) -> Dict[str, Any]:
    """Calculate projected budget overage."""
    # Simplified projection - can be enhanced with trend analysis
    return {
        "projected_overage_tokens": 0,
        "projected_overage_percentage": 0,
        "days_to_overage": None,
    }


def _get_optimization_suggestions(agent_id: str) -> List[str]:
    """Get optimization suggestions for an agent."""
    suggestions = []

    budget = budget_manager.get_budget(agent_id)
    usage = budget_manager.get_usage(agent_id)

    if budget and usage:
        percentage = (usage.total_tokens / budget.max_tokens) * 100

        if percentage > 80:
            suggestions.append("Consider using fallback model for non-critical queries")
            suggestions.append("Implement request queueing during peak hours")

        if percentage > 60:
            suggestions.append("Review query complexity and optimize prompts")
            suggestions.append("Enable response caching for repeated queries")

    return suggestions


def _get_historical_usage(agent_id: str, days: int) -> List[Dict[str, Any]]:
    """Get historical usage data for an agent."""
    # This would query historical data - simplified for now
    return []
