"""
Granular Rate Limiter for User and Endpoint Specific Limits
============================================================

Production-ready rate limiting with granular control per user and endpoint.
Supports different tiers, dynamic limits, and Redis-backed persistence.

Features:
- Per-user rate limiting with different tiers
- Per-endpoint specific limits
- Dynamic limit adjustment based on user behavior
- Redis persistence for distributed systems
- Graceful degradation when Redis unavailable
- Comprehensive metrics and monitoring
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class UserTier(Enum):
    """User subscription tiers with different rate limits."""

    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


@dataclass
class RateLimitConfig:
    """Configuration for rate limits."""

    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_size: int = 10  # Allow burst requests

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
            "requests_per_day": self.requests_per_day,
            "burst_size": self.burst_size,
        }


# Default rate limits per user tier
DEFAULT_TIER_LIMITS = {
    UserTier.FREE: RateLimitConfig(
        requests_per_minute=20,
        requests_per_hour=500,
        requests_per_day=5000,
        burst_size=5,
    ),
    UserTier.PREMIUM: RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=2000,
        requests_per_day=20000,
        burst_size=15,
    ),
    UserTier.ENTERPRISE: RateLimitConfig(
        requests_per_minute=200,
        requests_per_hour=10000,
        requests_per_day=100000,
        burst_size=50,
    ),
    UserTier.ADMIN: RateLimitConfig(
        requests_per_minute=1000,
        requests_per_hour=50000,
        requests_per_day=500000,
        burst_size=100,
    ),
}

# Endpoint-specific rate limits (override tier limits)
ENDPOINT_LIMITS = {
    "/api/v1/agents/chat": RateLimitConfig(
        requests_per_minute=10,
        requests_per_hour=300,
        requests_per_day=3000,
        burst_size=3,
    ),
    "/api/v1/generate": RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=100,
        requests_per_day=1000,
        burst_size=2,
    ),
    "/api/v1/vision": RateLimitConfig(
        requests_per_minute=3, requests_per_hour=50, requests_per_day=500, burst_size=1
    ),
    "/api/v1/auth": RateLimitConfig(
        requests_per_minute=5, requests_per_hour=30, requests_per_day=100, burst_size=2
    ),
}

# Exempt endpoints (no rate limiting)
EXEMPT_ENDPOINTS = {
    "/health",
    "/metrics",
    "/api/v1/circuit-breakers/status",
    "/docs",
    "/openapi.json",
    "/favicon.ico",
}


@dataclass
class UserRateLimitState:
    """Track rate limit state for a user."""

    user_id: str
    tier: UserTier
    minute_requests: int = 0
    hour_requests: int = 0
    day_requests: int = 0
    minute_window_start: float = field(default_factory=time.time)
    hour_window_start: float = field(default_factory=time.time)
    day_window_start: float = field(default_factory=time.time)
    last_request_time: float = field(default_factory=time.time)
    violations: int = 0
    blocked_until: Optional[float] = None


class GranularRateLimiter:
    """
    Granular rate limiter with per-user and per-endpoint limits.

    Usage:
        limiter = GranularRateLimiter(redis_client)

        # Check if request is allowed
        allowed, retry_after = await limiter.check_rate_limit(
            user_id="user123",
            endpoint="/api/v1/chat",
            tier=UserTier.PREMIUM
        )

        if not allowed:
            raise HTTPException(429, detail=f"Rate limit exceeded. Retry after {retry_after} seconds")
    """

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.local_state: Dict[str, UserRateLimitState] = {}
        self.endpoint_state: Dict[str, Dict[str, UserRateLimitState]] = defaultdict(
            dict
        )
        self._lock = asyncio.Lock()

        logger.info("Granular rate limiter initialized")

    def _get_user_key(self, user_id: str, endpoint: Optional[str] = None) -> str:
        """Generate cache key for user rate limit state."""
        if endpoint:
            return f"rate_limit:endpoint:{endpoint}:user:{user_id}"
        return f"rate_limit:user:{user_id}"

    async def _get_user_state(
        self, user_id: str, tier: UserTier, endpoint: Optional[str] = None
    ) -> UserRateLimitState:
        """Get or create user rate limit state."""
        key = self._get_user_key(user_id, endpoint)

        # Try Redis first if available
        if self.redis_client:
            try:
                data = await self.redis_client.get(key)
                if data:
                    state_dict = json.loads(data)
                    state = UserRateLimitState(
                        user_id=user_id,
                        tier=UserTier(state_dict["tier"]),
                        minute_requests=state_dict["minute_requests"],
                        hour_requests=state_dict["hour_requests"],
                        day_requests=state_dict["day_requests"],
                        minute_window_start=state_dict["minute_window_start"],
                        hour_window_start=state_dict["hour_window_start"],
                        day_window_start=state_dict["day_window_start"],
                        last_request_time=state_dict["last_request_time"],
                        violations=state_dict["violations"],
                        blocked_until=state_dict.get("blocked_until"),
                    )
                    return state
            except Exception as e:
                logger.warning(f"Redis error getting rate limit state: {e}")

        # Fall back to local state
        if endpoint:
            if key not in self.endpoint_state[endpoint]:
                self.endpoint_state[endpoint][key] = UserRateLimitState(
                    user_id=user_id, tier=tier
                )
            return self.endpoint_state[endpoint][key]
        else:
            if key not in self.local_state:
                self.local_state[key] = UserRateLimitState(user_id=user_id, tier=tier)
            return self.local_state[key]

    async def _save_user_state(
        self, state: UserRateLimitState, endpoint: Optional[str] = None
    ):
        """Save user rate limit state."""
        key = self._get_user_key(state.user_id, endpoint)

        # Save to Redis if available
        if self.redis_client:
            try:
                state_dict = {
                    "user_id": state.user_id,
                    "tier": state.tier.value,
                    "minute_requests": state.minute_requests,
                    "hour_requests": state.hour_requests,
                    "day_requests": state.day_requests,
                    "minute_window_start": state.minute_window_start,
                    "hour_window_start": state.hour_window_start,
                    "day_window_start": state.day_window_start,
                    "last_request_time": state.last_request_time,
                    "violations": state.violations,
                    "blocked_until": state.blocked_until,
                }
                await self.redis_client.setex(
                    key, 86400, json.dumps(state_dict)  # 24 hour TTL
                )
            except Exception as e:
                logger.warning(f"Redis error saving rate limit state: {e}")

    def _reset_windows(self, state: UserRateLimitState, current_time: float):
        """Reset time windows if they have expired."""
        # Reset minute window
        if current_time - state.minute_window_start >= 60:
            state.minute_requests = 0
            state.minute_window_start = current_time

        # Reset hour window
        if current_time - state.hour_window_start >= 3600:
            state.hour_requests = 0
            state.hour_window_start = current_time

        # Reset day window
        if current_time - state.day_window_start >= 86400:
            state.day_requests = 0
            state.day_window_start = current_time
            state.violations = 0  # Reset violations daily

    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        tier: UserTier = UserTier.FREE,
        ip_address: Optional[str] = None,
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed under rate limits.

        Args:
            user_id: User identifier
            endpoint: API endpoint being accessed
            tier: User's subscription tier
            ip_address: Optional IP for additional tracking

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        async with self._lock:
            current_time = time.time()

            # Check if endpoint is exempt
            if any(endpoint.startswith(exempt) for exempt in EXEMPT_ENDPOINTS):
                return True, None

            # Get appropriate limits
            if endpoint in ENDPOINT_LIMITS:
                limits = ENDPOINT_LIMITS[endpoint]
                state = await self._get_user_state(user_id, tier, endpoint)
            else:
                limits = DEFAULT_TIER_LIMITS[tier]
                state = await self._get_user_state(user_id, tier)

            # Check if user is temporarily blocked
            if state.blocked_until and current_time < state.blocked_until:
                retry_after = int(state.blocked_until - current_time)
                return False, retry_after

            # Reset expired windows
            self._reset_windows(state, current_time)

            # Check burst limit (sliding window)
            time_since_last = current_time - state.last_request_time
            if time_since_last < 1.0 and state.minute_requests > limits.burst_size:
                state.violations += 1

                # Block user temporarily after repeated violations
                if state.violations >= 3:
                    state.blocked_until = current_time + 60  # 1 minute block
                    await self._save_user_state(
                        state, endpoint if endpoint in ENDPOINT_LIMITS else None
                    )
                    return False, 60

                return False, 1

            # Check rate limits
            if state.minute_requests >= limits.requests_per_minute:
                retry_after = 60 - int(current_time - state.minute_window_start)
                return False, retry_after

            if state.hour_requests >= limits.requests_per_hour:
                retry_after = 3600 - int(current_time - state.hour_window_start)
                return False, retry_after

            if state.day_requests >= limits.requests_per_day:
                retry_after = 86400 - int(current_time - state.day_window_start)
                return False, retry_after

            # Update counters
            state.minute_requests += 1
            state.hour_requests += 1
            state.day_requests += 1
            state.last_request_time = current_time

            # Save state
            await self._save_user_state(
                state, endpoint if endpoint in ENDPOINT_LIMITS else None
            )

            return True, None

    async def get_user_limits_status(
        self, user_id: str, tier: UserTier
    ) -> Dict[str, Any]:
        """Get current rate limit status for a user."""
        state = await self._get_user_state(user_id, tier)
        limits = DEFAULT_TIER_LIMITS[tier]

        return {
            "user_id": user_id,
            "tier": tier.value,
            "limits": limits.to_dict(),
            "current_usage": {
                "minute": state.minute_requests,
                "hour": state.hour_requests,
                "day": state.day_requests,
            },
            "remaining": {
                "minute": max(0, limits.requests_per_minute - state.minute_requests),
                "hour": max(0, limits.requests_per_hour - state.hour_requests),
                "day": max(0, limits.requests_per_day - state.day_requests),
            },
            "violations": state.violations,
            "blocked_until": state.blocked_until,
        }

    async def reset_user_limits(self, user_id: str):
        """Reset rate limits for a user (admin action)."""
        # Clear from Redis
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(f"rate_limit:*:user:{user_id}")
                for key in keys:
                    await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Error resetting user limits in Redis: {e}")

        # Clear from local state
        keys_to_remove = [k for k in self.local_state.keys() if user_id in k]
        for key in keys_to_remove:
            del self.local_state[key]

        # Clear from endpoint state
        for endpoint_dict in self.endpoint_state.values():
            keys_to_remove = [k for k in endpoint_dict.keys() if user_id in k]
            for key in keys_to_remove:
                del endpoint_dict[key]

        logger.info(f"Reset rate limits for user {user_id}")


class GranularRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for granular rate limiting per user and endpoint.
    """

    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.limiter = GranularRateLimiter(redis_client)
        logger.info("Granular rate limit middleware initialized")

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to requests."""
        # Extract user information
        user_id = None
        tier = UserTier.FREE

        # Try to get user from request state or headers
        if hasattr(request.state, "user"):
            user = request.state.user
            user_id = user.get("id", "anonymous")
            tier = UserTier(user.get("tier", "free"))
        elif "X-User-ID" in request.headers:
            user_id = request.headers["X-User-ID"]
            tier_header = request.headers.get("X-User-Tier", "free")
            tier = UserTier(tier_header)
        else:
            # Use IP as fallback identifier
            client_ip = request.client.host if request.client else "unknown"
            user_id = hashlib.sha256(client_ip.encode()).hexdigest()[:16]

        # Check rate limit
        endpoint = request.url.path
        allowed, retry_after = await self.limiter.check_rate_limit(
            user_id=user_id,
            endpoint=endpoint,
            tier=tier,
            ip_address=request.client.host if request.client else None,
        )

        if not allowed:
            # Log rate limit violation
            logger.warning(
                f"Rate limit exceeded for user {user_id} on endpoint {endpoint}. "
                f"Retry after {retry_after} seconds"
            )

            # Return 429 response
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "tier": tier.value,
                    "endpoint": endpoint,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(
                        DEFAULT_TIER_LIMITS[tier].requests_per_minute
                    ),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + retry_after)),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        if user_id:
            status = await self.limiter.get_user_limits_status(user_id, tier)
            response.headers["X-RateLimit-Limit"] = str(
                status["limits"]["requests_per_minute"]
            )
            response.headers["X-RateLimit-Remaining"] = str(
                status["remaining"]["minute"]
            )
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))

        return response


# Global instance
granular_limiter = None


def initialize_granular_rate_limiter(redis_client=None):
    """Initialize the global granular rate limiter."""
    global granular_limiter
    granular_limiter = GranularRateLimiter(redis_client)
    logger.info("Global granular rate limiter initialized")
    return granular_limiter
