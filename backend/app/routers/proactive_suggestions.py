"""
Proactive Suggestions API Router - NGX Agents Advanced AI
REST API endpoints for the intelligent proactive suggestions system.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field, validator

from core.auth import get_current_user
from core.proactive_suggestions_engine import (
    ProactiveSuggestionsEngine,
    UserContext,
    ProactiveSuggestion,
    SuggestionType,
    SuggestionPriority,
    SuggestionTiming,
)
from core.telemetry import trace_async
from clients.vertex_ai.vertex_ai_client import VertexAIClient

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/proactive-suggestions",
    tags=["proactive-suggestions"],
    responses={404: {"description": "Not found"}},
)

# Initialize suggestions engine
suggestions_engine = ProactiveSuggestionsEngine()


# Pydantic models for request/response validation
class UserContextRequest(BaseModel):
    """Request model for user context."""

    program_type: str = Field(..., description="User's program type (PRIME, LONGEVITY)")
    current_energy_level: float = Field(
        ..., ge=0.0, le=1.0, description="Current energy level (0-1)"
    )
    stress_level: float = Field(
        ..., ge=0.0, le=1.0, description="Current stress level (0-1)"
    )
    motivation_level: float = Field(
        ..., ge=0.0, le=1.0, description="Current motivation level (0-1)"
    )
    adherence_trend: str = Field(
        ..., description="Adherence trend (improving, stable, declining)"
    )

    # Temporal context
    time_of_day: str = Field(
        ..., description="Current time of day (morning, afternoon, evening, night)"
    )
    day_of_week: str = Field(..., description="Current day of week")
    season: str = Field(
        ..., description="Current season (winter, spring, summer, fall)"
    )

    # Situational context
    location_type: str = Field(default="home", description="Current location type")
    social_context: str = Field(default="alone", description="Current social context")
    upcoming_events: List[Dict[str, Any]] = Field(
        default_factory=list, description="Upcoming events"
    )

    # Goals and achievements
    active_goals: List[Dict[str, Any]] = Field(
        default_factory=list, description="Active goals"
    )
    recent_achievements: List[Dict[str, Any]] = Field(
        default_factory=list, description="Recent achievements"
    )
    current_challenges: List[str] = Field(
        default_factory=list, description="Current challenges"
    )

    # Preferences
    communication_preferences: Dict[str, Any] = Field(
        default_factory=dict, description="Communication preferences"
    )
    successful_interventions: List[str] = Field(
        default_factory=list, description="Previously successful interventions"
    )
    failed_interventions: List[str] = Field(
        default_factory=list, description="Previously failed interventions"
    )

    @validator("adherence_trend")
    def validate_adherence_trend(cls, v):
        valid_trends = ["improving", "stable", "declining"]
        if v not in valid_trends:
            raise ValueError(f"adherence_trend must be one of {valid_trends}")
        return v

    @validator("time_of_day")
    def validate_time_of_day(cls, v):
        valid_times = ["morning", "afternoon", "evening", "night"]
        if v not in valid_times:
            raise ValueError(f"time_of_day must be one of {valid_times}")
        return v


class SuggestionResponse(BaseModel):
    """Response model for a proactive suggestion."""

    suggestion_id: str
    user_id: str
    agent_id: str
    suggestion_type: str
    priority: str
    timing: str

    title: str
    message: str
    action_items: List[str]
    reasoning: str

    context: Dict[str, Any]
    confidence_score: float
    expected_impact: Dict[str, float]

    created_at: datetime
    optimal_delivery_time: datetime
    expires_at: Optional[datetime] = None

    delivered: bool = False
    user_response: Optional[str] = None
    effectiveness_score: Optional[float] = None


class GenerateSuggestionsRequest(BaseModel):
    """Request model for generating proactive suggestions."""

    user_context: UserContextRequest
    limit: int = Field(
        default=5, ge=1, le=10, description="Maximum number of suggestions to generate"
    )


class GenerateSuggestionsResponse(BaseModel):
    """Response model for generated suggestions."""

    user_id: str
    suggestions: List[SuggestionResponse]
    generation_metadata: Dict[str, Any]
    timestamp: datetime


class MarkDeliveredRequest(BaseModel):
    """Request model for marking suggestion as delivered."""

    delivery_method: str = Field(
        default="app_notification", description="Method used to deliver suggestion"
    )


class RecordFeedbackRequest(BaseModel):
    """Request model for recording user feedback."""

    user_response: str = Field(..., description="User's response to the suggestion")
    effectiveness_score: float = Field(
        ..., ge=0.0, le=1.0, description="Effectiveness score (0-1)"
    )


class SuggestionHistoryResponse(BaseModel):
    """Response model for suggestion history."""

    suggestions: List[SuggestionResponse]
    total_count: int
    page: int
    per_page: int
    has_next: bool


class SuggestionsAnalyticsResponse(BaseModel):
    """Response model for suggestions analytics."""

    total_suggestions: int
    delivered_suggestions: int
    user_responses: int
    average_effectiveness: float
    top_suggestion_types: List[Dict[str, Any]]
    delivery_success_rate: float
    user_engagement_score: float


# Helper functions
def _convert_suggestion_to_response(
    suggestion: ProactiveSuggestion,
) -> SuggestionResponse:
    """Convert ProactiveSuggestion to SuggestionResponse."""
    return SuggestionResponse(
        suggestion_id=suggestion.suggestion_id,
        user_id=suggestion.user_id,
        agent_id=suggestion.agent_id,
        suggestion_type=suggestion.suggestion_type.value,
        priority=suggestion.priority.value,
        timing=suggestion.timing.value,
        title=suggestion.title,
        message=suggestion.message,
        action_items=suggestion.action_items,
        reasoning=suggestion.reasoning,
        context=suggestion.context,
        confidence_score=suggestion.confidence_score,
        expected_impact=suggestion.expected_impact,
        created_at=suggestion.created_at,
        optimal_delivery_time=suggestion.optimal_delivery_time,
        expires_at=suggestion.expires_at,
        delivered=suggestion.delivered,
        user_response=suggestion.user_response,
        effectiveness_score=suggestion.effectiveness_score,
    )


def _convert_context_request_to_user_context(
    user_id: str, context_request: UserContextRequest
) -> UserContext:
    """Convert UserContextRequest to UserContext."""
    return UserContext(
        user_id=user_id,
        program_type=context_request.program_type,
        current_energy_level=context_request.current_energy_level,
        stress_level=context_request.stress_level,
        motivation_level=context_request.motivation_level,
        adherence_trend=context_request.adherence_trend,
        time_of_day=context_request.time_of_day,
        day_of_week=context_request.day_of_week,
        season=context_request.season,
        location_type=context_request.location_type,
        social_context=context_request.social_context,
        upcoming_events=context_request.upcoming_events,
        active_goals=context_request.active_goals,
        recent_achievements=context_request.recent_achievements,
        current_challenges=context_request.current_challenges,
        communication_preferences=context_request.communication_preferences,
        successful_interventions=context_request.successful_interventions,
        failed_interventions=context_request.failed_interventions,
    )


# API Endpoints
@router.post("/generate", response_model=GenerateSuggestionsResponse)
@trace_async("generate_proactive_suggestions_api")
async def generate_proactive_suggestions(
    request: GenerateSuggestionsRequest, user_id: str = Depends(get_current_user)
) -> GenerateSuggestionsResponse:
    """
    Generate proactive suggestions for a user based on their current context.

    This endpoint analyzes the user's current state, behavior patterns, and context
    to generate personalized, actionable suggestions that can improve adherence
    and overall program success.
    """
    try:
        # Convert request to UserContext
        user_context = _convert_context_request_to_user_context(
            user_id, request.user_context
        )

        # Generate suggestions
        suggestions = await suggestions_engine.generate_proactive_suggestions(
            user_context, request.limit
        )

        # Convert to response format
        suggestion_responses = [
            _convert_suggestion_to_response(suggestion) for suggestion in suggestions
        ]

        # Generate metadata
        metadata = {
            "suggestions_generated": len(suggestions),
            "energy_level": user_context.current_energy_level,
            "stress_level": user_context.stress_level,
            "motivation_level": user_context.motivation_level,
            "adherence_trend": user_context.adherence_trend,
            "context_factors": {
                "time_of_day": user_context.time_of_day,
                "location": user_context.location_type,
                "social_context": user_context.social_context,
            },
            "average_confidence": (
                sum(s.confidence_score for s in suggestions) / len(suggestions)
                if suggestions
                else 0.0
            ),
        }

        logger.info(
            f"Generated {len(suggestions)} proactive suggestions for user {user_id}"
        )

        return GenerateSuggestionsResponse(
            user_id=user_id,
            suggestions=suggestion_responses,
            generation_metadata=metadata,
            timestamp=datetime.now(),
        )

    except Exception as e:
        logger.error(
            f"Failed to generate proactive suggestions for user {user_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(e)}",
        )


@router.post("/{suggestion_id}/delivered", response_model=Dict[str, Any])
@trace_async("mark_suggestion_delivered_api")
async def mark_suggestion_delivered(
    suggestion_id: str,
    request: MarkDeliveredRequest,
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Mark a suggestion as delivered to the user.

    This endpoint should be called when a suggestion has been successfully
    delivered to the user through any communication channel.
    """
    try:
        success = await suggestions_engine.mark_suggestion_delivered(
            suggestion_id, request.delivery_method
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or already marked as delivered",
            )

        logger.info(
            f"Suggestion {suggestion_id} marked as delivered via {request.delivery_method}"
        )

        return {
            "success": True,
            "suggestion_id": suggestion_id,
            "delivery_method": request.delivery_method,
            "delivered_at": datetime.now().isoformat(),
            "message": "Suggestion marked as delivered successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark suggestion {suggestion_id} as delivered: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark suggestion as delivered: {str(e)}",
        )


@router.post("/{suggestion_id}/feedback", response_model=Dict[str, Any])
@trace_async("record_suggestion_feedback_api")
async def record_suggestion_feedback(
    suggestion_id: str,
    request: RecordFeedbackRequest,
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Record user feedback on a delivered suggestion.

    This endpoint allows users to provide feedback on how helpful or effective
    a suggestion was, which helps improve future recommendation quality.
    """
    try:
        success = await suggestions_engine.record_suggestion_feedback(
            suggestion_id, request.user_response, request.effectiveness_score
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found or feedback already recorded",
            )

        logger.info(
            f"Feedback recorded for suggestion {suggestion_id}: {request.effectiveness_score}"
        )

        return {
            "success": True,
            "suggestion_id": suggestion_id,
            "user_response": request.user_response,
            "effectiveness_score": request.effectiveness_score,
            "feedback_recorded_at": datetime.now().isoformat(),
            "message": "Feedback recorded successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to record feedback for suggestion {suggestion_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {str(e)}",
        )


@router.get("/history", response_model=SuggestionHistoryResponse)
@trace_async("get_suggestion_history_api")
async def get_suggestion_history(
    user_id: str = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    suggestion_type: Optional[str] = Query(
        None, description="Filter by suggestion type"
    ),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    delivered_only: bool = Query(False, description="Show only delivered suggestions"),
) -> SuggestionHistoryResponse:
    """
    Get the history of suggestions for the current user.

    This endpoint returns a paginated list of all suggestions generated for
    the user, with optional filtering by type, priority, and delivery status.
    """
    try:
        # This would typically query a database
        # For now, return empty response as placeholder
        logger.info(f"Retrieving suggestion history for user {user_id} (page {page})")

        return SuggestionHistoryResponse(
            suggestions=[], total_count=0, page=page, per_page=per_page, has_next=False
        )

    except Exception as e:
        logger.error(f"Failed to retrieve suggestion history for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve suggestion history: {str(e)}",
        )


@router.get("/analytics", response_model=SuggestionsAnalyticsResponse)
@trace_async("get_suggestions_analytics_api")
async def get_suggestions_analytics(
    user_id: str = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
) -> SuggestionsAnalyticsResponse:
    """
    Get analytics and insights about suggestion effectiveness for the current user.

    This endpoint provides aggregated metrics about suggestion delivery,
    user engagement, and effectiveness over a specified time period.
    """
    try:
        # This would typically query analytics data from database/cache
        # For now, return placeholder analytics
        logger.info(
            f"Retrieving suggestions analytics for user {user_id} ({days} days)"
        )

        # Placeholder analytics data
        return SuggestionsAnalyticsResponse(
            total_suggestions=0,
            delivered_suggestions=0,
            user_responses=0,
            average_effectiveness=0.0,
            top_suggestion_types=[],
            delivery_success_rate=0.0,
            user_engagement_score=0.0,
        )

    except Exception as e:
        logger.error(
            f"Failed to retrieve suggestions analytics for user {user_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analytics: {str(e)}",
        )


@router.get("/types", response_model=Dict[str, List[str]])
async def get_suggestion_types(
    user_id: str = Depends(get_current_user),
) -> Dict[str, List[str]]:
    """
    Get available suggestion types and priorities.

    This endpoint returns the available suggestion types, priorities, and
    timing options that can be used for filtering and understanding suggestions.
    """
    try:
        return {
            "suggestion_types": [t.value for t in SuggestionType],
            "priorities": [p.value for p in SuggestionPriority],
            "timing_options": [t.value for t in SuggestionTiming],
        }

    except Exception as e:
        logger.error(f"Failed to retrieve suggestion types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve suggestion types: {str(e)}",
        )


@router.get("/health", response_model=Dict[str, Any])
async def suggestions_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the proactive suggestions system.

    This endpoint verifies that the suggestions engine is operational
    and can communicate with required dependencies.
    """
    try:
        # Test suggestions engine initialization
        engine_status = "healthy" if suggestions_engine else "unhealthy"

        # Test Gemini client if available
        gemini_status = (
            "healthy" if suggestions_engine.vertex_ai_client else "not_configured"
        )

        # Test Redis connection
        redis_status = "healthy"
        try:
            await suggestions_engine.redis_client.ping()
        except Exception:
            redis_status = "unhealthy"

        overall_status = (
            "healthy"
            if all(
                [
                    engine_status == "healthy",
                    gemini_status in ["healthy", "not_configured"],
                    redis_status == "healthy",
                ]
            )
            else "unhealthy"
        )

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "suggestions_engine": engine_status,
                "vertex_ai_client": gemini_status,
                "redis_client": redis_status,
            },
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "version": "1.0.0",
        }
