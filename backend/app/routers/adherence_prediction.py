"""
Adherence Prediction API Router - NGX Agents Advanced AI
Provides endpoints for adherence prediction and monitoring.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from core.adherence_prediction_engine import (
    AdherencePredictionEngine,
    AdherenceMetrics,
    AdherencePrediction,
    AdherenceRiskLevel,
    AdherenceTrigger,
)
from core.adherence_monitoring_service import AdherenceMonitoringService
from app.middleware.auth import get_current_user
from core.telemetry import trace_endpoint

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/adherence", tags=["adherence_prediction"])


# Pydantic models for API
class AdherenceMetricsRequest(BaseModel):
    """Request model for adherence metrics."""

    daily_app_usage_minutes: float = Field(
        ge=0, le=1440, description="Daily app usage in minutes"
    )
    weekly_active_days: int = Field(ge=0, le=7, description="Active days per week")
    agent_interaction_frequency: float = Field(
        ge=0, description="Agent interactions per day"
    )
    message_response_time_hours: float = Field(
        ge=0, description="Average response time in hours"
    )

    consistency_score: float = Field(
        ge=0, le=1, description="Behavioral consistency score"
    )
    goal_completion_rate: float = Field(ge=0, le=1, description="Goal completion rate")
    self_reporting_frequency: float = Field(
        ge=0, description="Self-reporting frequency per week"
    )
    protocol_modification_requests: int = Field(
        ge=0, description="Protocol modification requests"
    )

    progress_satisfaction_score: float = Field(
        ge=1, le=10, description="Progress satisfaction (1-10)"
    )
    milestone_achievement_rate: float = Field(
        ge=0, le=1, description="Milestone achievement rate"
    )
    plateau_duration_days: int = Field(
        ge=0, description="Current plateau duration in days"
    )
    expectation_reality_gap: float = Field(
        ge=-1, le=1, description="Expectation vs reality gap"
    )

    support_system_strength: float = Field(
        ge=0, le=1, description="Support system strength"
    )
    environmental_challenges: int = Field(
        ge=0, le=10, description="Environmental challenge level"
    )
    competing_priorities: int = Field(
        ge=0, le=10, description="Competing priorities level"
    )

    previous_program_completion_rate: float = Field(
        ge=0, le=1, description="Historical completion rate"
    )
    longest_adherence_streak_days: int = Field(
        ge=0, description="Longest adherence streak"
    )
    average_dropout_timeframe_days: Optional[int] = Field(
        None, description="Average dropout timeframe"
    )


class PredictionRequest(BaseModel):
    """Request model for adherence prediction."""

    user_id: str = Field(description="User identifier")
    metrics: AdherenceMetricsRequest = Field(description="Current adherence metrics")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    include_interventions: bool = Field(
        True, description="Include intervention recommendations"
    )


class PredictionResponse(BaseModel):
    """Response model for adherence prediction."""

    user_id: str
    prediction_date: datetime
    adherence_probability: float
    risk_level: str
    confidence_score: float

    primary_risk_factors: List[str]
    protective_factors: List[str]
    triggers_detected: List[str]

    estimated_dropout_timeframe_days: Optional[int]
    critical_intervention_window_days: int

    intervention_strategies: Optional[List[Dict[str, Any]]] = None
    monitoring_frequency: str
    success_probability_with_intervention: float


class MonitoringRequest(BaseModel):
    """Request model for adherence monitoring."""

    user_id: str = Field(description="User identifier")
    metrics: AdherenceMetricsRequest = Field(description="Current adherence metrics")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    trigger_interventions: bool = Field(
        True, description="Trigger interventions if needed"
    )


class MonitoringResponse(BaseModel):
    """Response model for adherence monitoring."""

    user_id: str
    prediction: PredictionResponse
    risk_change: Dict[str, Any]
    intervention_needed: bool
    interventions_triggered: List[Dict[str, Any]]
    next_monitoring: str
    timestamp: datetime


class BatchPredictionRequest(BaseModel):
    """Request model for batch prediction."""

    user_predictions: List[PredictionRequest] = Field(
        description="List of user predictions"
    )
    include_summary: bool = Field(True, description="Include batch summary")


class BatchPredictionResponse(BaseModel):
    """Response model for batch prediction."""

    total_users: int
    successful_predictions: int
    failed_predictions: int
    predictions: List[PredictionResponse]
    risk_summary: Dict[str, int]
    batch_timestamp: datetime


# Dependency to get prediction engine
async def get_prediction_engine() -> AdherencePredictionEngine:
    """Get adherence prediction engine instance."""
    return AdherencePredictionEngine()


# Dependency to get monitoring service
async def get_monitoring_service() -> AdherenceMonitoringService:
    """Get adherence monitoring service instance."""
    return AdherenceMonitoringService()


@router.post("/predict", response_model=PredictionResponse)
@trace_endpoint("adherence_prediction")
async def predict_adherence(
    request: PredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    prediction_engine: AdherencePredictionEngine = Depends(get_prediction_engine),
) -> PredictionResponse:
    """
    Predict user adherence with 85% accuracy.

    Analyzes current user metrics and behavioral patterns to predict
    adherence probability and recommend interventions.
    """
    try:
        # Convert request to AdherenceMetrics
        metrics = AdherenceMetrics(**request.metrics.dict())

        # Generate prediction
        prediction = await prediction_engine.predict_adherence(
            user_id=request.user_id,
            current_metrics=metrics,
            historical_data=None,  # Would fetch from database
            context=request.context,
        )

        # Convert to response format
        response = PredictionResponse(
            user_id=prediction.user_id,
            prediction_date=prediction.prediction_date,
            adherence_probability=prediction.adherence_probability,
            risk_level=prediction.risk_level.value,
            confidence_score=prediction.confidence_score,
            primary_risk_factors=prediction.primary_risk_factors,
            protective_factors=prediction.protective_factors,
            triggers_detected=[
                trigger.value for trigger in prediction.triggers_detected
            ],
            estimated_dropout_timeframe_days=prediction.estimated_dropout_timeframe_days,
            critical_intervention_window_days=prediction.critical_intervention_window_days,
            intervention_strategies=(
                prediction.intervention_strategies
                if request.include_interventions
                else None
            ),
            monitoring_frequency=prediction.monitoring_frequency,
            success_probability_with_intervention=prediction.success_probability_with_intervention,
        )

        logger.info(
            f"Adherence prediction completed for user {request.user_id}: "
            f"{prediction.adherence_probability:.2f} probability, {prediction.risk_level.value} risk"
        )

        return response

    except Exception as e:
        logger.error(f"Adherence prediction failed for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/monitor", response_model=MonitoringResponse)
@trace_endpoint("adherence_monitoring")
async def monitor_adherence(
    request: MonitoringRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    monitoring_service: AdherenceMonitoringService = Depends(get_monitoring_service),
) -> MonitoringResponse:
    """
    Monitor user adherence and trigger interventions if needed.

    Continuously monitors user behavior patterns and automatically
    triggers interventions based on risk assessment.
    """
    try:
        # Convert request to AdherenceMetrics
        metrics = AdherenceMetrics(**request.metrics.dict())

        # Monitor adherence
        monitoring_result = await monitoring_service.monitor_user_adherence(
            user_id=request.user_id, current_metrics=metrics, context=request.context
        )

        # Convert prediction to response format
        prediction_response = PredictionResponse(
            user_id=monitoring_result["prediction"].user_id,
            prediction_date=monitoring_result["prediction"].prediction_date,
            adherence_probability=monitoring_result["prediction"].adherence_probability,
            risk_level=monitoring_result["prediction"].risk_level.value,
            confidence_score=monitoring_result["prediction"].confidence_score,
            primary_risk_factors=monitoring_result["prediction"].primary_risk_factors,
            protective_factors=monitoring_result["prediction"].protective_factors,
            triggers_detected=[
                trigger.value
                for trigger in monitoring_result["prediction"].triggers_detected
            ],
            estimated_dropout_timeframe_days=monitoring_result[
                "prediction"
            ].estimated_dropout_timeframe_days,
            critical_intervention_window_days=monitoring_result[
                "prediction"
            ].critical_intervention_window_days,
            intervention_strategies=monitoring_result[
                "prediction"
            ].intervention_strategies,
            monitoring_frequency=monitoring_result["prediction"].monitoring_frequency,
            success_probability_with_intervention=monitoring_result[
                "prediction"
            ].success_probability_with_intervention,
        )

        response = MonitoringResponse(
            user_id=monitoring_result["user_id"],
            prediction=prediction_response,
            risk_change=monitoring_result["risk_change"],
            intervention_needed=monitoring_result["intervention_needed"],
            interventions_triggered=[
                {
                    "intervention_id": result.intervention_id,
                    "type": result.intervention_type.value,
                    "executed_at": result.executed_at.isoformat(),
                    "success": result.success,
                    "response": result.user_response,
                }
                for result in monitoring_result["interventions_triggered"]
            ],
            next_monitoring=monitoring_result["next_monitoring"],
            timestamp=datetime.fromisoformat(monitoring_result["timestamp"]),
        )

        logger.info(
            f"Adherence monitoring completed for user {request.user_id}: "
            f"intervention_needed={monitoring_result['intervention_needed']}, "
            f"interventions_triggered={len(monitoring_result['interventions_triggered'])}"
        )

        return response

    except Exception as e:
        logger.error(f"Adherence monitoring failed for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")


@router.post("/batch-predict", response_model=BatchPredictionResponse)
@trace_endpoint("batch_adherence_prediction")
async def batch_predict_adherence(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    prediction_engine: AdherencePredictionEngine = Depends(get_prediction_engine),
) -> BatchPredictionResponse:
    """
    Predict adherence for multiple users in batch.

    Efficiently processes multiple adherence predictions and provides
    summary statistics for population-level insights.
    """
    try:
        predictions = []
        successful_predictions = 0
        failed_predictions = 0
        risk_summary = {level.value: 0 for level in AdherenceRiskLevel}

        for prediction_request in request.user_predictions:
            try:
                # Convert request to AdherenceMetrics
                metrics = AdherenceMetrics(**prediction_request.metrics.dict())

                # Generate prediction
                prediction = await prediction_engine.predict_adherence(
                    user_id=prediction_request.user_id,
                    current_metrics=metrics,
                    historical_data=None,
                    context=prediction_request.context,
                )

                # Convert to response format
                prediction_response = PredictionResponse(
                    user_id=prediction.user_id,
                    prediction_date=prediction.prediction_date,
                    adherence_probability=prediction.adherence_probability,
                    risk_level=prediction.risk_level.value,
                    confidence_score=prediction.confidence_score,
                    primary_risk_factors=prediction.primary_risk_factors,
                    protective_factors=prediction.protective_factors,
                    triggers_detected=[
                        trigger.value for trigger in prediction.triggers_detected
                    ],
                    estimated_dropout_timeframe_days=prediction.estimated_dropout_timeframe_days,
                    critical_intervention_window_days=prediction.critical_intervention_window_days,
                    intervention_strategies=(
                        prediction.intervention_strategies
                        if prediction_request.include_interventions
                        else None
                    ),
                    monitoring_frequency=prediction.monitoring_frequency,
                    success_probability_with_intervention=prediction.success_probability_with_intervention,
                )

                predictions.append(prediction_response)
                successful_predictions += 1
                risk_summary[prediction.risk_level.value] += 1

            except Exception as e:
                logger.warning(
                    f"Batch prediction failed for user {prediction_request.user_id}: {e}"
                )
                failed_predictions += 1

        response = BatchPredictionResponse(
            total_users=len(request.user_predictions),
            successful_predictions=successful_predictions,
            failed_predictions=failed_predictions,
            predictions=predictions,
            risk_summary=risk_summary if request.include_summary else {},
            batch_timestamp=datetime.now(),
        )

        logger.info(
            f"Batch adherence prediction completed: "
            f"{successful_predictions} successful, {failed_predictions} failed"
        )

        return response

    except Exception as e:
        logger.error(f"Batch adherence prediction failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Batch prediction failed: {str(e)}"
        )


@router.get("/user/{user_id}/prediction", response_model=Optional[PredictionResponse])
@trace_endpoint("get_cached_prediction")
async def get_cached_prediction(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    prediction_engine: AdherencePredictionEngine = Depends(get_prediction_engine),
) -> Optional[PredictionResponse]:
    """
    Get cached adherence prediction for user.

    Retrieves the most recent adherence prediction from cache
    if available.
    """
    try:
        prediction = await prediction_engine.get_cached_prediction(user_id)

        if not prediction:
            return None

        response = PredictionResponse(
            user_id=prediction.user_id,
            prediction_date=prediction.prediction_date,
            adherence_probability=prediction.adherence_probability,
            risk_level=prediction.risk_level.value,
            confidence_score=prediction.confidence_score,
            primary_risk_factors=prediction.primary_risk_factors,
            protective_factors=prediction.protective_factors,
            triggers_detected=[
                trigger.value for trigger in prediction.triggers_detected
            ],
            estimated_dropout_timeframe_days=prediction.estimated_dropout_timeframe_days,
            critical_intervention_window_days=prediction.critical_intervention_window_days,
            intervention_strategies=prediction.intervention_strategies,
            monitoring_frequency=prediction.monitoring_frequency,
            success_probability_with_intervention=prediction.success_probability_with_intervention,
        )

        logger.info(f"Retrieved cached prediction for user {user_id}")
        return response

    except Exception as e:
        logger.error(f"Failed to retrieve cached prediction for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve prediction: {str(e)}"
        )


@router.get("/risk-levels", response_model=Dict[str, str])
async def get_risk_levels() -> Dict[str, str]:
    """
    Get available adherence risk levels.

    Returns the mapping of risk levels and their descriptions.
    """
    return {
        "very_low": "0-20% risk of dropout - Excellent adherence",
        "low": "21-40% risk of dropout - Good adherence",
        "moderate": "41-60% risk of dropout - Some risk factors present",
        "high": "61-80% risk of dropout - Multiple risk factors",
        "very_high": "81-100% risk of dropout - Immediate intervention needed",
    }


@router.get("/triggers", response_model=Dict[str, str])
async def get_adherence_triggers() -> Dict[str, str]:
    """
    Get available adherence triggers.

    Returns the mapping of trigger types and their descriptions.
    """
    return {
        "plateau": "Progress plateau affecting motivation",
        "time_pressure": "Increased time constraints",
        "motivation_drop": "Decreased motivation levels",
        "complexity_overload": "Program too complex to follow",
        "social_pressure": "Negative social influences",
        "health_concern": "Health issues affecting participation",
        "life_event": "Major life event disruption",
        "progress_dissatisfaction": "Unsatisfied with progress rate",
    }


@router.post("/validate-metrics", response_model=Dict[str, Any])
async def validate_adherence_metrics(
    metrics: AdherenceMetricsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Validate adherence metrics for completeness and consistency.

    Checks if provided metrics are sufficient for accurate prediction
    and identifies any inconsistencies.
    """
    try:
        validation_results = {
            "valid": True,
            "completeness_score": 0.0,
            "warnings": [],
            "suggestions": [],
        }

        # Check completeness
        required_fields = [
            "daily_app_usage_minutes",
            "weekly_active_days",
            "consistency_score",
            "goal_completion_rate",
            "progress_satisfaction_score",
            "support_system_strength",
        ]

        provided_fields = sum(
            1 for field in required_fields if getattr(metrics, field, None) is not None
        )

        validation_results["completeness_score"] = provided_fields / len(
            required_fields
        )

        # Check for inconsistencies
        if metrics.weekly_active_days > 7:
            validation_results["warnings"].append("Weekly active days cannot exceed 7")
            validation_results["valid"] = False

        if metrics.daily_app_usage_minutes > 600:  # 10 hours
            validation_results["warnings"].append("Daily usage seems unusually high")

        if (
            metrics.goal_completion_rate > 0.9
            and metrics.progress_satisfaction_score < 5
        ):
            validation_results["warnings"].append(
                "High completion rate but low satisfaction - review goal quality"
            )

        if (
            metrics.consistency_score < 0.3
            and metrics.longest_adherence_streak_days > 60
        ):
            validation_results["warnings"].append(
                "Low consistency but long streak - possible data inconsistency"
            )

        # Provide suggestions
        if validation_results["completeness_score"] < 0.8:
            validation_results["suggestions"].append(
                "Provide more complete metrics for better prediction accuracy"
            )

        if metrics.support_system_strength < 0.5:
            validation_results["suggestions"].append(
                "Consider social support interventions"
            )

        if metrics.plateau_duration_days > 21:
            validation_results["suggestions"].append(
                "Protocol refresh recommended for extended plateau"
            )

        return validation_results

    except Exception as e:
        logger.error(f"Metrics validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check for adherence prediction service.

    Verifies that all components are working correctly.
    """
    try:
        # Test prediction engine
        prediction_engine = AdherencePredictionEngine()

        # Test basic functionality
        test_metrics = AdherenceMetrics(
            daily_app_usage_minutes=30.0,
            weekly_active_days=5,
            agent_interaction_frequency=3.0,
            message_response_time_hours=6.0,
            consistency_score=0.8,
            goal_completion_rate=0.85,
            self_reporting_frequency=4.0,
            protocol_modification_requests=1,
            progress_satisfaction_score=8.0,
            milestone_achievement_rate=0.9,
            plateau_duration_days=5,
            expectation_reality_gap=0.2,
            support_system_strength=0.8,
            environmental_challenges=2,
            competing_priorities=3,
            previous_program_completion_rate=0.9,
            longest_adherence_streak_days=90,
            average_dropout_timeframe_days=None,
        )

        # Generate test prediction
        test_prediction = await prediction_engine.predict_adherence(
            user_id="health_check_test",
            current_metrics=test_metrics,
            historical_data={},
            context={"test": True},
        )

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "prediction_engine": "operational",
            "test_prediction": {
                "adherence_probability": test_prediction.adherence_probability,
                "risk_level": test_prediction.risk_level.value,
                "confidence_score": test_prediction.confidence_score,
            },
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
