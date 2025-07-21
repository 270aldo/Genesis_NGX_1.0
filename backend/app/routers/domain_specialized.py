"""
Domain Specialized Models API Router - NGX Agents Advanced AI
REST API endpoints for domain-specialized AI model recommendations.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field, validator

from core.auth import get_current_user
from core.domain_specialized_models import (
    DomainSpecializedModels,
    DomainProfile,
    UserDomain,
    ModelSpecialization,
    SpecializedRecommendation,
)
from core.telemetry import trace_async
from clients.vertex_ai.vertex_ai_client import VertexAIClient

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/api/v1/domain-specialized",
    tags=["domain-specialized"],
    responses={404: {"description": "Not found"}},
)

# Initialize domain specialized models
domain_models = DomainSpecializedModels()


# Pydantic models for request/response validation
class CreateProfileRequest(BaseModel):
    """Request model for creating a domain profile."""

    program_type: str = Field(..., description="User's program (PRIME or LONGEVITY)")
    age: int = Field(..., ge=13, le=120, description="User's age")
    gender: str = Field(..., description="User's gender (male, female, other)")
    fitness_level: str = Field(
        ..., description="Fitness level (beginner, intermediate, advanced, elite)"
    )

    # Health information
    medical_conditions: List[str] = Field(
        default_factory=list, description="Medical conditions"
    )
    physical_limitations: List[str] = Field(
        default_factory=list, description="Physical limitations"
    )
    dietary_restrictions: List[str] = Field(
        default_factory=list, description="Dietary restrictions"
    )

    # Goals and preferences
    primary_goals: List[str] = Field(..., description="Primary fitness goals")
    secondary_goals: List[str] = Field(
        default_factory=list, description="Secondary goals"
    )
    training_style: str = Field(
        default="balanced", description="Preferred training style"
    )
    available_hours: int = Field(
        ..., ge=0, le=50, description="Available hours per week"
    )

    # Experience
    training_years: float = Field(
        default=0.0, ge=0.0, description="Years of training experience"
    )
    injury_history: List[Dict[str, Any]] = Field(
        default_factory=list, description="Injury history"
    )

    # Additional data
    questionnaire_responses: Dict[str, Any] = Field(
        default_factory=dict, description="Questionnaire responses"
    )
    app_behavior: Dict[str, Any] = Field(
        default_factory=dict, description="App behavior data"
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict, description="User preferences"
    )
    historical_data: Dict[str, Any] = Field(
        default_factory=dict, description="Historical performance data"
    )

    @validator("program_type")
    def validate_program_type(cls, v):
        valid_programs = ["PRIME", "LONGEVITY"]
        if v not in valid_programs:
            raise ValueError(f"program_type must be one of {valid_programs}")
        return v

    @validator("gender")
    def validate_gender(cls, v):
        valid_genders = ["male", "female", "other"]
        if v not in valid_genders:
            raise ValueError(f"gender must be one of {valid_genders}")
        return v

    @validator("fitness_level")
    def validate_fitness_level(cls, v):
        valid_levels = ["beginner", "intermediate", "advanced", "elite"]
        if v not in valid_levels:
            raise ValueError(f"fitness_level must be one of {valid_levels}")
        return v


class DomainProfileResponse(BaseModel):
    """Response model for domain profile."""

    user_id: str
    primary_domain: str
    secondary_domains: List[str]

    # Demographics
    age: int
    gender: str
    fitness_level: str

    # Health
    medical_conditions: List[str]
    physical_limitations: List[str]
    dietary_restrictions: List[str]

    # Goals
    primary_goals: List[str]
    secondary_goals: List[str]
    preferred_training_style: str
    available_time_per_week: int

    # History
    training_history_years: float
    injury_history: List[Dict[str, Any]]
    success_patterns: Dict[str, Any]
    failure_patterns: Dict[str, Any]

    # Psychographics
    motivation_type: str
    personality_traits: Dict[str, float]
    stress_response: str
    social_preference: str

    # Metadata
    created_at: datetime
    profile_version: str = "1.0"


class GenerateRecommendationsRequest(BaseModel):
    """Request model for generating specialized recommendations."""

    specialization: str = Field(..., description="Type of specialization required")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )
    limit: int = Field(
        default=5, ge=1, le=10, description="Maximum recommendations to generate"
    )

    @validator("specialization")
    def validate_specialization(cls, v):
        valid_specializations = [s.value for s in ModelSpecialization]
        if v not in valid_specializations:
            raise ValueError(f"specialization must be one of {valid_specializations}")
        return v


class SpecializedRecommendationResponse(BaseModel):
    """Response model for specialized recommendation."""

    recommendation_id: str
    user_id: str
    domain: str
    specialization: str

    # Content
    title: str
    description: str
    rationale: str

    # Details
    protocol_adjustments: Dict[str, Any]
    personalization_factors: List[str]
    expected_outcomes: Dict[str, Any]

    # Metrics
    confidence_score: float
    relevance_score: float
    priority_level: int

    # Timing
    recommended_duration_weeks: int
    review_frequency_days: int

    # Metadata
    created_at: datetime
    expires_at: Optional[datetime]
    based_on_evidence: List[Dict[str, str]]


class AdaptProtocolRequest(BaseModel):
    """Request model for adapting protocols."""

    base_protocol: Dict[str, Any] = Field(..., description="Base protocol to adapt")
    adaptation_level: str = Field(
        default="full", description="Level of adaptation (minimal, moderate, full)"
    )


class AdaptProtocolResponse(BaseModel):
    """Response model for adapted protocol."""

    user_id: str
    domain: str
    original_protocol: Dict[str, Any]
    adapted_protocol: Dict[str, Any]
    adaptations_applied: List[str]
    confidence_score: float
    timestamp: datetime


# Helper functions
def _profile_to_response(profile: DomainProfile) -> DomainProfileResponse:
    """Convert DomainProfile to response model."""
    return DomainProfileResponse(
        user_id=profile.user_id,
        primary_domain=profile.primary_domain.value,
        secondary_domains=[d.value for d in profile.secondary_domains],
        age=profile.age,
        gender=profile.gender,
        fitness_level=profile.fitness_level,
        medical_conditions=profile.medical_conditions,
        physical_limitations=profile.physical_limitations,
        dietary_restrictions=profile.dietary_restrictions,
        primary_goals=profile.primary_goals,
        secondary_goals=profile.secondary_goals,
        preferred_training_style=profile.preferred_training_style,
        available_time_per_week=profile.available_time_per_week,
        training_history_years=profile.training_history_years,
        injury_history=profile.injury_history,
        success_patterns=profile.success_patterns,
        failure_patterns=profile.failure_patterns,
        motivation_type=profile.motivation_type,
        personality_traits=profile.personality_traits,
        stress_response=profile.stress_response,
        social_preference=profile.social_preference,
        created_at=datetime.now(),
    )


def _recommendation_to_response(
    rec: SpecializedRecommendation,
) -> SpecializedRecommendationResponse:
    """Convert SpecializedRecommendation to response model."""
    return SpecializedRecommendationResponse(
        recommendation_id=rec.recommendation_id,
        user_id=rec.user_id,
        domain=rec.domain.value,
        specialization=rec.specialization.value,
        title=rec.title,
        description=rec.description,
        rationale=rec.rationale,
        protocol_adjustments=rec.protocol_adjustments,
        personalization_factors=rec.personalization_factors,
        expected_outcomes=rec.expected_outcomes,
        confidence_score=rec.confidence_score,
        relevance_score=rec.relevance_score,
        priority_level=rec.priority_level,
        recommended_duration_weeks=rec.recommended_duration_weeks,
        review_frequency_days=rec.review_frequency_days,
        created_at=rec.created_at,
        expires_at=rec.expires_at,
        based_on_evidence=rec.based_on_evidence,
    )


# API Endpoints
@router.post("/profile", response_model=DomainProfileResponse)
@trace_async("create_domain_profile_api")
async def create_domain_profile(
    request: CreateProfileRequest, user_id: str = Depends(get_current_user)
) -> DomainProfileResponse:
    """
    Create or update a domain-specialized profile for the user.

    This endpoint analyzes user data to determine their primary domain
    and creates a comprehensive profile for specialized recommendations.
    """
    try:
        # Prepare user data from request
        user_data = {
            "program_type": request.program_type,
            "age": request.age,
            "gender": request.gender,
            "fitness_level": request.fitness_level,
            "medical_conditions": request.medical_conditions,
            "physical_limitations": request.physical_limitations,
            "dietary_restrictions": request.dietary_restrictions,
            "primary_goals": request.primary_goals,
            "secondary_goals": request.secondary_goals,
            "training_style": request.training_style,
            "available_hours": request.available_hours,
            "training_years": request.training_years,
            "injury_history": request.injury_history,
            "questionnaire_responses": request.questionnaire_responses,
            "app_behavior": request.app_behavior,
            "preferences": request.preferences,
            "historical_data": request.historical_data,
        }

        # Create domain profile
        profile = await domain_models.create_domain_profile(user_id, user_data)

        logger.info(
            f"Created domain profile for user {user_id}: {profile.primary_domain.value}"
        )

        return _profile_to_response(profile)

    except Exception as e:
        logger.error(f"Failed to create domain profile for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create domain profile: {str(e)}",
        )


@router.get("/profile", response_model=DomainProfileResponse)
@trace_async("get_domain_profile_api")
async def get_domain_profile(
    user_id: str = Depends(get_current_user),
) -> DomainProfileResponse:
    """
    Get the current domain profile for the user.

    Returns the cached domain profile if available, otherwise returns 404.
    """
    try:
        profile = await domain_models.get_cached_profile(user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain profile not found. Please create a profile first.",
            )

        logger.info(f"Retrieved domain profile for user {user_id}")

        return _profile_to_response(profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve domain profile for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve domain profile: {str(e)}",
        )


@router.post("/recommendations", response_model=PaginatedResponse[SpecializedRecommendationResponse])
@trace_async("generate_specialized_recommendations_api")
async def generate_specialized_recommendations(
    request: GenerateRecommendationsRequest,
    http_request: Request,
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=5, ge=1, le=20, description="Items per page"),
    user_id: str = Depends(get_current_user)
) -> PaginatedResponse[SpecializedRecommendationResponse]:
    """
    Generate domain-specialized recommendations for the user.

    This endpoint creates highly personalized recommendations based on
    the user's domain profile and requested specialization type.
    Results are paginated for better performance.
    """
    try:
        # Get user's domain profile
        profile = await domain_models.get_cached_profile(user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain profile not found. Please create a profile first.",
            )

        # Convert specialization string to enum
        specialization = ModelSpecialization(request.specialization)

        # Generate more recommendations than requested to allow for pagination
        max_recommendations = min(request.limit * 3, 30)  # Generate up to 30 recommendations
        
        # Generate recommendations
        recommendations = await domain_models.generate_specialized_recommendations(
            profile, specialization, request.context
        )

        # Limit to max_recommendations
        recommendations = recommendations[:max_recommendations]

        logger.info(
            f"Generated {len(recommendations)} specialized recommendations "
            f"for user {user_id} in {specialization.value}"
        )

        # Convert to response format
        recommendation_responses = [_recommendation_to_response(rec) for rec in recommendations]
        
        # Create pagination params
        pagination_params = PaginationParams(
            page=page,
            page_size=page_size,
            sort_by="priority_level",
            sort_order="desc"
        )
        
        # Apply pagination
        base_url = str(http_request.url).split('?')[0]
        paginated_response = paginate_list(
            items=recommendation_responses,
            params=pagination_params,
            base_url=base_url
        )
        
        return paginated_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate recommendations for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}",
        )


@router.post("/adapt-protocol", response_model=AdaptProtocolResponse)
@trace_async("adapt_protocol_api")
async def adapt_protocol(
    request: AdaptProtocolRequest, user_id: str = Depends(get_current_user)
) -> AdaptProtocolResponse:
    """
    Adapt a base protocol to the user's domain specifications.

    This endpoint takes a generic protocol and adapts it based on the
    user's domain profile, medical conditions, goals, and preferences.
    """
    try:
        # Get user's domain profile
        profile = await domain_models.get_cached_profile(user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain profile not found. Please create a profile first.",
            )

        # Adapt the protocol
        adapted_protocol = await domain_models.adapt_protocols_by_domain(
            profile, request.base_protocol
        )

        # Identify adaptations applied
        adaptations_applied = []
        if profile.primary_domain in [UserDomain.PRIME_BEGINNER]:
            adaptations_applied.append("beginner_adjustments")
        if profile.primary_domain in [
            UserDomain.LONGEVITY_SENIOR,
            UserDomain.LONGEVITY_ACTIVE,
        ]:
            adaptations_applied.append("longevity_modifications")
        if profile.medical_conditions:
            adaptations_applied.append("medical_restrictions")
        if profile.available_time_per_week < 3:
            adaptations_applied.append("time_optimization")

        logger.info(
            f"Adapted protocol for user {user_id} with domain {profile.primary_domain.value}"
        )

        return AdaptProtocolResponse(
            user_id=user_id,
            domain=profile.primary_domain.value,
            original_protocol=request.base_protocol,
            adapted_protocol=adapted_protocol,
            adaptations_applied=adaptations_applied,
            confidence_score=0.85,  # Would be calculated based on adaptation complexity
            timestamp=datetime.now(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to adapt protocol for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to adapt protocol: {str(e)}",
        )


@router.get("/domains", response_model=Dict[str, List[str]])
async def get_available_domains(
    user_id: str = Depends(get_current_user),
) -> Dict[str, List[str]]:
    """
    Get all available user domains and model specializations.

    This endpoint returns the complete list of domains and specializations
    that can be used for profile creation and recommendation generation.
    """
    try:
        return {
            "user_domains": [d.value for d in UserDomain],
            "model_specializations": [s.value for s in ModelSpecialization],
            "program_types": ["PRIME", "LONGEVITY"],
            "fitness_levels": ["beginner", "intermediate", "advanced", "elite"],
            "training_styles": [
                "balanced",
                "strength",
                "cardio",
                "hybrid",
                "functional",
            ],
        }

    except Exception as e:
        logger.error(f"Failed to retrieve domains: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve domains: {str(e)}",
        )


@router.get(
    "/recommendations/history", response_model=List[SpecializedRecommendationResponse]
)
@trace_async("get_recommendations_history_api")
async def get_recommendations_history(
    user_id: str = Depends(get_current_user),
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
) -> List[SpecializedRecommendationResponse]:
    """
    Get the history of specialized recommendations for the user.

    This endpoint returns previously generated recommendations with
    optional filtering by specialization or domain.
    """
    try:
        # This would typically query from database
        # For now, return empty list as placeholder
        logger.info(f"Retrieving recommendation history for user {user_id}")

        return []

    except Exception as e:
        logger.error(f"Failed to retrieve recommendation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}",
        )


@router.get("/health", response_model=Dict[str, Any])
async def domain_models_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the domain specialized models system.

    Verifies that the domain models engine is operational and can
    communicate with required dependencies.
    """
    try:
        # Test domain models initialization
        models_status = "healthy" if domain_models else "unhealthy"

        # Test Gemini client
        gemini_status = "healthy" if domain_models.vertex_ai_client else "not_configured"

        # Test Redis connection
        redis_status = "healthy"
        try:
            await domain_models.redis_client.ping()
        except Exception:
            redis_status = "unhealthy"

        overall_status = (
            "healthy"
            if all(
                [
                    models_status == "healthy",
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
                "domain_models": models_status,
                "vertex_ai_client": gemini_status,
                "redis_client": redis_status,
            },
            "available_domains": len([d for d in UserDomain]),
            "available_specializations": len([s for s in ModelSpecialization]),
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
