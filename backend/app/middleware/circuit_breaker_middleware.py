"""
Circuit Breaker Middleware for FastAPI
======================================

Integrates circuit breakers into the FastAPI application to protect
against cascading failures and provide graceful degradation.
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.circuit_breaker_enhanced import (
    circuit_breaker_manager,
    initialize_default_breakers,
)

logger = logging.getLogger(__name__)


class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply circuit breaker protection to API endpoints.

    This middleware:
    1. Initializes default circuit breakers on startup
    2. Monitors request failures and applies circuit breaker logic
    3. Provides fallback responses when circuits are open
    4. Exposes circuit breaker status via special endpoints
    """

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        # Initialize default circuit breakers
        initialize_default_breakers()
        logger.info("Circuit breaker middleware initialized")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process requests with circuit breaker protection."""

        # Special endpoint to check circuit breaker status
        if request.url.path == "/api/v1/circuit-breakers/status":
            status = await circuit_breaker_manager.get_all_status()
            return JSONResponse(content={"status": "ok", "circuit_breakers": status})

        # Special endpoint to reset circuit breakers (admin only)
        if (
            request.url.path == "/api/v1/circuit-breakers/reset"
            and request.method == "POST"
        ):
            # TODO: Add admin authentication check here
            await circuit_breaker_manager.reset_all()
            return JSONResponse(
                content={"status": "ok", "message": "All circuit breakers reset"}
            )

        # Determine which circuit breaker to use based on the endpoint
        breaker_name = self._get_breaker_name(request.url.path)

        if breaker_name:
            breaker = circuit_breaker_manager.get(breaker_name)

            # Check if circuit is open
            if breaker.state.value == "open":
                # Check if we should attempt reset
                should_reset = await breaker._should_attempt_reset()
                if not should_reset:
                    # Return fallback response
                    logger.warning(
                        f"Circuit breaker '{breaker_name}' is OPEN, returning fallback"
                    )
                    return JSONResponse(
                        status_code=503,
                        content={
                            "error": "Service temporarily unavailable",
                            "circuit_breaker": breaker_name,
                            "retry_after": int(
                                breaker.config.timeout
                                - (time.time() - breaker._last_state_change)
                            ),
                        },
                        headers={
                            "Retry-After": str(
                                int(
                                    breaker.config.timeout
                                    - (time.time() - breaker._last_state_change)
                                )
                            )
                        },
                    )

        # Process the request normally
        try:
            start_time = time.time()
            response = await call_next(request)
            response_time = (time.time() - start_time) * 1000  # ms

            # Record success if using circuit breaker
            if breaker_name and response.status_code < 500:
                breaker = circuit_breaker_manager.get(breaker_name)
                await breaker._record_success()

            # Add circuit breaker headers
            if breaker_name:
                breaker = circuit_breaker_manager.get(breaker_name)
                response.headers["X-Circuit-Breaker"] = breaker_name
                response.headers["X-Circuit-State"] = breaker.state.value

            return response

        except Exception as e:
            # Record failure if using circuit breaker
            if breaker_name:
                breaker = circuit_breaker_manager.get(breaker_name)
                await breaker._record_failure()

                # If circuit is now open, return fallback
                if breaker.state.value == "open":
                    logger.error(
                        f"Request failed and circuit breaker '{breaker_name}' opened: {e}"
                    )
                    return JSONResponse(
                        status_code=503,
                        content={
                            "error": "Service temporarily unavailable",
                            "circuit_breaker": breaker_name,
                            "retry_after": breaker.config.timeout,
                        },
                        headers={"Retry-After": str(int(breaker.config.timeout))},
                    )

            # Re-raise the exception for normal error handling
            raise

    def _get_breaker_name(self, path: str) -> str:
        """
        Determine which circuit breaker to use based on the request path.

        Args:
            path: Request path

        Returns:
            Circuit breaker name or None
        """
        # Agent endpoints
        if "/agents/" in path or "/api/v1/agents/" in path:
            # Extract agent name from path
            parts = path.split("/")
            for i, part in enumerate(parts):
                if part == "agents" and i + 1 < len(parts):
                    agent_name = parts[i + 1].upper()
                    if agent_name in [
                        "NEXUS",
                        "BLAZE",
                        "SAGE",
                        "SPARK",
                        "WAVE",
                        "LUNA",
                        "STELLA",
                        "NOVA",
                        "CODE",
                    ]:
                        return f"agent_{agent_name}"
            return "agent_NEXUS"  # Default to orchestrator

        # Vertex AI endpoints
        if any(x in path for x in ["/chat", "/generate", "/embed", "/vision"]):
            return "vertex_ai"

        # Database endpoints
        if any(x in path for x in ["/users", "/profiles", "/conversations"]):
            return "supabase"

        # Redis/cache endpoints
        if "/cache" in path or "/session" in path:
            return "redis"

        # No circuit breaker for this endpoint
        return None


async def add_circuit_breaker_routes(app):
    """
    Add circuit breaker management routes to the application.

    These routes provide visibility and control over circuit breakers:
    - GET /api/v1/circuit-breakers/status - Get status of all breakers
    - POST /api/v1/circuit-breakers/reset - Reset all breakers (admin only)
    - GET /api/v1/circuit-breakers/{name}/status - Get status of specific breaker
    - POST /api/v1/circuit-breakers/{name}/reset - Reset specific breaker
    """
    from fastapi import APIRouter, Depends, HTTPException

    from app.core.dependencies import get_current_user_admin

    router = APIRouter(
        prefix="/api/v1/circuit-breakers",
        tags=["Circuit Breakers"],
        responses={404: {"description": "Not found"}},
    )

    @router.get("/status")
    async def get_all_circuit_breakers_status():
        """Get status of all circuit breakers."""
        return await circuit_breaker_manager.get_all_status()

    @router.get("/{name}/status")
    async def get_circuit_breaker_status(name: str):
        """Get status of a specific circuit breaker."""
        if name not in circuit_breaker_manager._breakers:
            raise HTTPException(
                status_code=404, detail=f"Circuit breaker '{name}' not found"
            )

        breaker = circuit_breaker_manager.get(name)
        return await breaker.get_status()

    @router.post("/reset", dependencies=[Depends(get_current_user_admin)])
    async def reset_all_circuit_breakers():
        """Reset all circuit breakers (admin only)."""
        await circuit_breaker_manager.reset_all()
        return {"status": "ok", "message": "All circuit breakers reset"}

    @router.post("/{name}/reset", dependencies=[Depends(get_current_user_admin)])
    async def reset_circuit_breaker(name: str):
        """Reset a specific circuit breaker (admin only)."""
        if name not in circuit_breaker_manager._breakers:
            raise HTTPException(
                status_code=404, detail=f"Circuit breaker '{name}' not found"
            )

        breaker = circuit_breaker_manager.get(name)
        await breaker.reset()
        return {"status": "ok", "message": f"Circuit breaker '{name}' reset"}

    app.include_router(router)
    logger.info("Circuit breaker routes added")
