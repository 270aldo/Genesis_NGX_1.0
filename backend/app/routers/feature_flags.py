"""
Feature Flags API Router
=======================

API endpoints for managing feature flags.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from core.auth import get_current_user, require_admin
from core.feature_flags import FeatureFlag, FlagStatus, FlagType, get_feature_flags
from core.logging_config import get_logger
from core.ngx_feature_flags import get_ngx_client_flags

logger = get_logger(__name__)

router = APIRouter(
    prefix="/feature-flags",
    tags=["feature-flags"],
    responses={401: {"description": "Unauthorized"}, 403: {"description": "Forbidden"}},
)


# Request/Response models
class FlagEvaluationRequest(BaseModel):
    """Request to evaluate a feature flag."""

    user_id: Optional[str] = None
    user_segment: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FlagEvaluationResponse(BaseModel):
    """Response from flag evaluation."""

    flag_name: str
    enabled: bool
    variant: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreateFlagRequest(BaseModel):
    """Request to create a feature flag."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    type: FlagType = Field(default=FlagType.BOOLEAN)
    default_value: Any = Field(default=False)

    # Targeting
    target_percentage: Optional[int] = Field(None, ge=0, le=100)
    target_users: List[str] = Field(default_factory=list)
    target_segments: List[str] = Field(default_factory=list)

    # Schedule
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Variants
    variants: Dict[str, Any] = Field(default_factory=dict)


class UpdateFlagRequest(BaseModel):
    """Request to update a feature flag."""

    description: Optional[str] = Field(None, max_length=500)
    status: Optional[FlagStatus] = None
    default_value: Optional[Any] = None

    # Targeting
    target_percentage: Optional[int] = Field(None, ge=0, le=100)
    target_users: Optional[List[str]] = None
    target_segments: Optional[List[str]] = None

    # Schedule
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Variants
    variants: Optional[Dict[str, Any]] = None


class BulkEvaluationRequest(BaseModel):
    """Request to evaluate multiple flags."""

    flag_names: List[str]
    context: FlagEvaluationRequest


@router.get("/", response_model=List[FeatureFlag])
async def list_feature_flags(
    status: Optional[FlagStatus] = Query(None),
    type: Optional[FlagType] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[FeatureFlag]:
    """
    List all feature flags.

    Requires authentication. Admins see all flags, users see only active flags.
    """
    try:
        manager = await get_feature_flags()
        all_flags = await manager.get_all_flags()

        # Filter based on user role
        is_admin = current_user.get("role") == "admin"
        if not is_admin:
            # Non-admins only see active flags
            all_flags = [f for f in all_flags if f.status == FlagStatus.ACTIVE]

        # Apply filters
        if status:
            all_flags = [f for f in all_flags if f.status == status]

        if type:
            all_flags = [f for f in all_flags if f.type == type]

        if search:
            search_lower = search.lower()
            all_flags = [
                f
                for f in all_flags
                if search_lower in f.name.lower()
                or search_lower in f.description.lower()
            ]

        # Apply pagination
        total = len(all_flags)
        flags = all_flags[offset : offset + limit]

        logger.info(
            f"Listed {len(flags)} feature flags for user {current_user['id']}",
            extra={
                "user_id": current_user["id"],
                "total": total,
                "filters": {"status": status, "type": type, "search": search},
            },
        )

        return flags

    except Exception as e:
        logger.error(f"Error listing feature flags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list feature flags",
        )


@router.get("/{flag_name}", response_model=FeatureFlag)
async def get_feature_flag(
    flag_name: str, current_user: Dict[str, Any] = Depends(get_current_user)
) -> FeatureFlag:
    """Get a specific feature flag."""
    try:
        manager = await get_feature_flags()
        flag = await manager.get_flag(flag_name)

        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{flag_name}' not found",
            )

        # Check access
        is_admin = current_user.get("role") == "admin"
        if not is_admin and flag.status != FlagStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{flag_name}' not found",
            )

        return flag

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feature flag",
        )


@router.post("/{flag_name}/evaluate", response_model=FlagEvaluationResponse)
async def evaluate_feature_flag(
    flag_name: str,
    request: FlagEvaluationRequest = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> FlagEvaluationResponse:
    """Evaluate a feature flag for given context."""
    try:
        manager = await get_feature_flags()

        # Build evaluation context
        context = {
            "user_id": request.user_id or current_user["id"],
            "user_segment": request.user_segment,
            **request.metadata,
        }

        # Check if enabled
        enabled = await manager.is_enabled(flag_name, context)

        # Get variant if applicable
        variant = None
        flag = await manager.get_flag(flag_name)
        if flag and flag.type == FlagType.VARIANT:
            variant = await manager.get_variant(flag_name, context)

        response = FlagEvaluationResponse(
            flag_name=flag_name,
            enabled=enabled,
            variant=variant,
            metadata={
                "evaluated_at": datetime.utcnow().isoformat(),
                "context": context,
            },
        )

        logger.info(
            f"Evaluated feature flag '{flag_name}' for user {context['user_id']}",
            extra={
                "flag_name": flag_name,
                "user_id": context["user_id"],
                "result": enabled,
                "variant": variant,
            },
        )

        return response

    except Exception as e:
        logger.error(f"Error evaluating feature flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate feature flag",
        )


@router.post("/evaluate/bulk", response_model=Dict[str, FlagEvaluationResponse])
async def evaluate_multiple_flags(
    request: BulkEvaluationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, FlagEvaluationResponse]:
    """Evaluate multiple feature flags at once."""
    try:
        manager = await get_feature_flags()
        results = {}

        # Build evaluation context
        context = {
            "user_id": request.context.user_id or current_user["id"],
            "user_segment": request.context.user_segment,
            **request.context.metadata,
        }

        # Evaluate each flag
        for flag_name in request.flag_names:
            try:
                enabled = await manager.is_enabled(flag_name, context)

                # Get variant if applicable
                variant = None
                flag = await manager.get_flag(flag_name)
                if flag and flag.type == FlagType.VARIANT:
                    variant = await manager.get_variant(flag_name, context)

                results[flag_name] = FlagEvaluationResponse(
                    flag_name=flag_name,
                    enabled=enabled,
                    variant=variant,
                    metadata={"evaluated_at": datetime.utcnow().isoformat()},
                )
            except Exception as e:
                logger.warning(f"Failed to evaluate flag {flag_name}: {e}")
                results[flag_name] = FlagEvaluationResponse(
                    flag_name=flag_name, enabled=False, metadata={"error": str(e)}
                )

        return results

    except Exception as e:
        logger.error(f"Error in bulk evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate feature flags",
        )


@router.post("/", response_model=FeatureFlag, dependencies=[Depends(require_admin)])
async def create_feature_flag(
    request: CreateFlagRequest, current_user: Dict[str, Any] = Depends(get_current_user)
) -> FeatureFlag:
    """
    Create a new feature flag.

    Requires admin privileges.
    """
    try:
        manager = await get_feature_flags()

        # Check if flag already exists
        existing = await manager.get_flag(request.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Feature flag '{request.name}' already exists",
            )

        # Create flag
        flag = FeatureFlag(
            name=request.name,
            description=request.description,
            type=request.type,
            default_value=request.default_value,
            target_percentage=request.target_percentage,
            target_users=request.target_users,
            target_segments=request.target_segments,
            start_date=request.start_date,
            end_date=request.end_date,
            variants=request.variants,
            metadata={
                "created_by": current_user["id"],
                "created_at": datetime.utcnow().isoformat(),
            },
        )

        # Save flag
        success = await manager.create_flag(flag)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create feature flag",
            )

        logger.info(
            f"Created feature flag '{flag.name}' by user {current_user['id']}",
            extra={
                "flag_name": flag.name,
                "created_by": current_user["id"],
                "flag_type": flag.type,
            },
        )

        return flag

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating feature flag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create feature flag",
        )


@router.patch(
    "/{flag_name}", response_model=FeatureFlag, dependencies=[Depends(require_admin)]
)
async def update_feature_flag(
    flag_name: str,
    request: UpdateFlagRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> FeatureFlag:
    """
    Update a feature flag.

    Requires admin privileges.
    """
    try:
        manager = await get_feature_flags()

        # Get existing flag
        flag = await manager.get_flag(flag_name)
        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{flag_name}' not found",
            )

        # Update fields
        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(flag, field, value)

        # Update metadata
        flag.updated_at = datetime.utcnow()
        flag.metadata["updated_by"] = current_user["id"]
        flag.metadata["updated_at"] = flag.updated_at.isoformat()

        # Save flag
        success = await manager.update_flag(flag)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update feature flag",
            )

        logger.info(
            f"Updated feature flag '{flag_name}' by user {current_user['id']}",
            extra={
                "flag_name": flag_name,
                "updated_by": current_user["id"],
                "updates": list(update_data.keys()),
            },
        )

        return flag

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feature flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feature flag",
        )


@router.delete("/{flag_name}", dependencies=[Depends(require_admin)])
async def delete_feature_flag(
    flag_name: str, current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete (archive) a feature flag.

    Requires admin privileges.
    """
    try:
        manager = await get_feature_flags()

        # Check if flag exists
        flag = await manager.get_flag(flag_name)
        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{flag_name}' not found",
            )

        # Delete flag (soft delete)
        success = await manager.delete_flag(flag_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete feature flag",
            )

        logger.info(
            f"Deleted feature flag '{flag_name}' by user {current_user['id']}",
            extra={"flag_name": flag_name, "deleted_by": current_user["id"]},
        )

        return {"message": f"Feature flag '{flag_name}' has been archived"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feature flag {flag_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete feature flag",
        )


@router.post("/cache/refresh", dependencies=[Depends(require_admin)])
async def refresh_flag_cache(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Refresh all cached feature flags.

    Requires admin privileges.
    """
    try:
        manager = await get_feature_flags()
        await manager.refresh_cache()

        logger.info(
            f"Feature flag cache refreshed by user {current_user['id']}",
            extra={"refreshed_by": current_user["id"]},
        )

        return {"message": "Feature flag cache has been refreshed"}

    except Exception as e:
        logger.error(f"Error refreshing flag cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh cache",
        )


@router.get("/ngx-client", response_model=Dict[str, Any])
async def get_ngx_client_flags(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get NGX-specific feature flags for the client.

    This endpoint returns feature flags specific to the NGX strategic pivot,
    where users interact only with NEXUS instead of directly with agents.

    Returns:
        Dictionary containing:
        - nexusOnlyMode: Whether users interact only with NEXUS
        - directAgentAccess: Whether direct agent access is allowed
        - showAgentCollaboration: Show when agents are collaborating
        - showAgentAttribution: Show which agent provided information
        - showAgentActivity: Show real-time agent activity
        - enableCoachingPowerup: Enable $499/mo coaching tier
        - enableBetaFeatures: Enable beta features
    """
    try:
        user_id = current_user.get("id")
        flags = await get_ngx_client_flags(user_id)

        logger.info(
            f"NGX client flags requested by user {user_id}",
            extra={
                "user_id": user_id,
                "flags": flags,
                "strategy": (
                    "nexus_only" if flags.get("nexusOnlyMode") else "multi_agent"
                ),
            },
        )

        return {
            "status": "success",
            "flags": flags,
            "metadata": {
                "user_id": user_id,
                "strategy": (
                    "nexus_only" if flags.get("nexusOnlyMode") else "multi_agent"
                ),
                "api_cost_reduction": "93%" if flags.get("nexusOnlyMode") else "0%",
            },
        }

    except Exception as e:
        logger.error(
            f"Error getting NGX client flags for user {current_user.get('id')}: {e}"
        )
        # Return safe defaults on error
        return {
            "status": "error",
            "flags": {
                "nexusOnlyMode": True,  # Default to new strategy
                "directAgentAccess": False,
                "showAgentCollaboration": True,
                "showAgentAttribution": True,
                "showAgentActivity": True,
                "enableCoachingPowerup": False,
                "enableBetaFeatures": False,
            },
            "metadata": {
                "user_id": current_user.get("id"),
                "error": str(e),
                "using_defaults": True,
            },
        }
