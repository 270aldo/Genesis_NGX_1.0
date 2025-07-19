"""
Health check router for the API.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from infrastructure.health import HealthCheck
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    tags=["health"],
    responses={503: {"description": "Service unavailable"}},
)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    health = HealthCheck()
    
    # Check critical dependencies
    db_status = await health.check_database()
    vertex_status = await health.check_vertex_ai()
    
    is_healthy = db_status[0] and vertex_status[0]
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "checks": {
            "database": {"status": db_status[0], "message": db_status[1]},
            "vertex_ai": {"status": vertex_status[0], "message": vertex_status[1]},
        }
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness probe for Kubernetes."""
    # TODO: Check if all services are ready
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness probe for Kubernetes."""
    return {"status": "alive"}