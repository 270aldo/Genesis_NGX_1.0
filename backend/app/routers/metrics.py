"""
Metrics router for Prometheus monitoring.
"""

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    tags=["metrics"],
    include_in_schema=False,  # Hide from API docs
)


@router.get("/metrics")
async def metrics() -> Response:
    """Expose metrics for Prometheus scraping."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)