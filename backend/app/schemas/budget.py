"""
Budget Management Schemas
Pydantic models for budget monitoring API
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class BudgetPeriodEnum(str, Enum):
    """Budget period options."""

    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"
    infinite = "infinite"


class BudgetActionEnum(str, Enum):
    """Budget action options."""

    block = "block"
    degrade = "degrade"
    warn = "warn"
    queue = "queue"


class BudgetUpdateRequest(BaseModel):
    """Request model for updating agent budget."""

    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens allowed")
    period: Optional[BudgetPeriodEnum] = Field(None, description="Budget period")
    action_on_limit: Optional[BudgetActionEnum] = Field(
        None, description="Action when limit is reached"
    )
    fallback_model: Optional[str] = Field(
        None, description="Fallback model for degradation"
    )
    reset_day: Optional[int] = Field(
        None, ge=1, le=31, description="Day of period to reset budget"
    )


class BudgetUsageResponse(BaseModel):
    """Budget usage information."""

    prompt_tokens: int = Field(description="Tokens used in prompts")
    completion_tokens: int = Field(description="Tokens used in completions")
    total_tokens: int = Field(description="Total tokens used")
    estimated_cost_usd: float = Field(description="Estimated cost in USD")


class BudgetConfigResponse(BaseModel):
    """Budget configuration information."""

    agent_id: str = Field(description="Agent identifier")
    max_tokens: int = Field(description="Maximum tokens allowed")
    period: BudgetPeriodEnum = Field(description="Budget period")
    action_on_limit: BudgetActionEnum = Field(
        description="Action when limit is reached"
    )
    fallback_model: Optional[str] = Field(None, description="Fallback model")
    reset_day: int = Field(description="Day of period to reset budget")


class BudgetStatusResponse(BaseModel):
    """Comprehensive budget status response."""

    agent_id: str = Field(description="Agent identifier")
    budget: BudgetConfigResponse = Field(description="Budget configuration")
    usage: Optional[BudgetUsageResponse] = Field(None, description="Current usage")
    percentage: float = Field(description="Usage percentage of budget")
    remaining: int = Field(description="Remaining tokens in budget")
    period: str = Field(description="Current period key")
    next_reset: Optional[datetime] = Field(None, description="Next reset date")

    # Enhanced metrics
    estimated_monthly_cost_usd: Optional[float] = Field(
        None, description="Estimated monthly cost"
    )
    days_until_reset: Optional[int] = Field(None, description="Days until budget reset")
    usage_trend: Optional[str] = Field(None, description="Usage trend direction")
    health_status: Optional[str] = Field(None, description="Health status indicator")
    projected_overage: Optional[Dict[str, Any]] = Field(
        None, description="Projected overage information"
    )
    optimization_suggestions: Optional[List[str]] = Field(
        None, description="Optimization suggestions"
    )
    historical_usage: Optional[List[Dict[str, Any]]] = Field(
        None, description="Historical usage data"
    )


class BudgetAlertResponse(BaseModel):
    """Budget alert information."""

    agent_id: str = Field(description="Agent identifier")
    alert_type: str = Field(description="Alert type (warning, critical)")
    percentage: float = Field(description="Current usage percentage")
    message: str = Field(description="Alert message")
    recommended_action: str = Field(description="Recommended action")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Alert timestamp"
    )


class BudgetSummaryResponse(BaseModel):
    """Overall budget summary."""

    total_agents: int = Field(description="Total number of agents")
    total_monthly_tokens: int = Field(description="Total monthly token budget")
    total_used_tokens: int = Field(description="Total tokens used in current period")
    estimated_monthly_cost_usd: float = Field(description="Estimated monthly cost")
    agents_over_75_percent: int = Field(description="Agents over 75% usage")
    agents_over_90_percent: int = Field(description="Agents over 90% usage")
    cost_by_agent: Dict[str, float] = Field(description="Cost breakdown by agent")
    efficiency_metrics: Dict[str, Any] = Field(
        description="Efficiency and utilization metrics"
    )


class BudgetMetricsResponse(BaseModel):
    """Detailed budget metrics for analytics."""

    period_start: datetime = Field(description="Period start date")
    period_end: datetime = Field(description="Period end date")
    total_requests: int = Field(description="Total requests processed")
    total_tokens: int = Field(description="Total tokens consumed")
    cost_breakdown: Dict[str, float] = Field(description="Cost breakdown by service")
    efficiency_score: float = Field(description="Overall efficiency score")
    recommendations: List[str] = Field(description="Cost optimization recommendations")


class BudgetOptimizationResponse(BaseModel):
    """Budget optimization recommendations."""

    agent_id: str = Field(description="Agent identifier")
    current_efficiency: float = Field(description="Current efficiency percentage")
    potential_savings: float = Field(description="Potential monthly savings in USD")
    recommendations: List[Dict[str, Any]] = Field(
        description="Specific optimization recommendations"
    )
    implementation_priority: str = Field(
        description="Priority level for implementation"
    )


class BudgetForecastResponse(BaseModel):
    """Budget usage forecast."""

    agent_id: str = Field(description="Agent identifier")
    forecast_period_days: int = Field(description="Forecast period in days")
    predicted_usage: int = Field(description="Predicted token usage")
    predicted_cost: float = Field(description="Predicted cost in USD")
    confidence_level: float = Field(description="Forecast confidence level")
    trend_analysis: Dict[str, Any] = Field(description="Trend analysis data")
    risk_factors: List[str] = Field(description="Risk factors affecting forecast")


class BudgetAuditLogResponse(BaseModel):
    """Budget audit log entry."""

    timestamp: datetime = Field(description="Log entry timestamp")
    agent_id: str = Field(description="Agent identifier")
    action: str = Field(description="Action performed")
    user_id: Optional[str] = Field(None, description="User who performed action")
    previous_values: Dict[str, Any] = Field(description="Previous configuration values")
    new_values: Dict[str, Any] = Field(description="New configuration values")
    reason: Optional[str] = Field(None, description="Reason for change")
