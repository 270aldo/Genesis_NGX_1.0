"""
Advanced rate limiting configuration for GENESIS API.

This module provides sophisticated rate limiting with:
- Per-user rate limiting
- Per-endpoint customization
- Redis-backed distributed rate limiting
- Progressive delays for repeated violations
- Whitelist/blacklist support
"""

import time
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta
from functools import wraps

from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis
from pydantic import BaseModel

from core.settings_lazy import settings
from core.logging_config import get_logger
from core.auth import get_current_user_optional

logger = get_logger(__name__)


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting rules."""
    
    # Authentication endpoints
    auth_requests_per_minute: int = 5
    auth_requests_per_hour: int = 20
    
    # Chat endpoints
    chat_requests_per_minute: int = 30
    chat_requests_per_hour: int = 500
    
    # Heavy operations (AI processing)
    heavy_requests_per_minute: int = 5
    heavy_requests_per_hour: int = 50
    
    # API key limits (higher for authenticated users)
    api_key_multiplier: float = 2.0
    
    # Progressive delay settings
    violation_threshold: int = 3
    base_delay_seconds: int = 60
    max_delay_seconds: int = 3600  # 1 hour max


class AdvancedRateLimiter:
    """Advanced rate limiter with Redis backend and user-aware limiting."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.config = RateLimitConfig()
        self.violation_tracker: Dict[str, int] = {}
        
        # Create base limiter with custom key function
        self.limiter = Limiter(
            key_func=self._get_rate_limit_key,
            default_limits=["1000/hour"],
            headers_enabled=True,
            storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}" if redis_client else None
        )
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """
        Generate rate limit key based on user ID or IP address.
        
        Authenticated users get their own rate limit bucket.
        """
        # Try to get user from request state (set by auth middleware)
        user = getattr(request.state, "user", None)
        
        if user and hasattr(user, "id"):
            return f"user:{user.id}"
        
        # Fall back to IP address
        return f"ip:{get_remote_address(request)}"
    
    async def check_violations(self, key: str) -> int:
        """Check how many rate limit violations a key has."""
        if self.redis_client:
            violations = await self.redis_client.get(f"violations:{key}")
            return int(violations) if violations else 0
        else:
            return self.violation_tracker.get(key, 0)
    
    async def increment_violations(self, key: str):
        """Increment violation count for a key."""
        if self.redis_client:
            pipe = self.redis_client.pipeline()
            pipe.incr(f"violations:{key}")
            pipe.expire(f"violations:{key}", 86400)  # Reset after 24 hours
            await pipe.execute()
        else:
            self.violation_tracker[key] = self.violation_tracker.get(key, 0) + 1
    
    async def calculate_delay(self, key: str) -> int:
        """Calculate progressive delay based on violations."""
        violations = await self.check_violations(key)
        
        if violations < self.config.violation_threshold:
            return 0
        
        # Progressive delay: doubles with each violation
        delay = self.config.base_delay_seconds * (2 ** (violations - self.config.violation_threshold))
        return min(delay, self.config.max_delay_seconds)
    
    def get_limit_for_endpoint(self, endpoint: str, user_authenticated: bool = False) -> str:
        """Get rate limit string for specific endpoint."""
        multiplier = self.config.api_key_multiplier if user_authenticated else 1.0
        
        # Auth endpoints
        if endpoint.startswith("/auth") or endpoint.startswith("/login"):
            per_minute = int(self.config.auth_requests_per_minute * multiplier)
            per_hour = int(self.config.auth_requests_per_hour * multiplier)
            return f"{per_minute}/minute;{per_hour}/hour"
        
        # Chat endpoints
        elif endpoint.startswith("/chat") or endpoint.startswith("/message"):
            per_minute = int(self.config.chat_requests_per_minute * multiplier)
            per_hour = int(self.config.chat_requests_per_hour * multiplier)
            return f"{per_minute}/minute;{per_hour}/hour"
        
        # Heavy operations
        elif any(endpoint.startswith(p) for p in ["/generate", "/analyze", "/process"]):
            per_minute = int(self.config.heavy_requests_per_minute * multiplier)
            per_hour = int(self.config.heavy_requests_per_hour * multiplier)
            return f"{per_minute}/minute;{per_hour}/hour"
        
        # Default
        return "60/minute;1000/hour" if user_authenticated else "30/minute;500/hour"
    
    def limit(self, endpoint: str):
        """Decorator for applying rate limits to endpoints."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                # Check if user is authenticated
                user = await get_current_user_optional(request)
                user_authenticated = user is not None
                
                # Get appropriate limit
                limit_string = self.get_limit_for_endpoint(
                    endpoint or request.url.path,
                    user_authenticated
                )
                
                # Apply rate limit
                rate_limiter = self.limiter.limit(limit_string)
                
                # Execute with rate limiting
                try:
                    return await rate_limiter(func)(request, *args, **kwargs)
                except RateLimitExceeded as exc:
                    # Handle rate limit exceeded
                    key = self._get_rate_limit_key(request)
                    await self.increment_violations(key)
                    delay = await self.calculate_delay(key)
                    
                    # Log security event
                    logger.warning(
                        f"Rate limit exceeded - Key: {key}, Endpoint: {request.url.path}",
                        extra={
                            "security_event": "rate_limit_exceeded",
                            "key": key,
                            "endpoint": request.url.path,
                            "violations": await self.check_violations(key),
                            "delay": delay,
                            "user_id": user.id if user else None,
                            "ip_address": get_remote_address(request)
                        }
                    )
                    
                    # Return enhanced error response
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"Too many requests. Retry after {exc.retry_after + delay} seconds.",
                            "retry_after": exc.retry_after + delay,
                            "violations": await self.check_violations(key)
                        },
                        headers={
                            "Retry-After": str(exc.retry_after + delay),
                            "X-RateLimit-Limit": str(exc.limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Reset": str(exc.reset),
                            "X-RateLimit-Violations": str(await self.check_violations(key))
                        }
                    )
            
            return wrapper
        return decorator


# Global rate limiter instance
advanced_limiter = AdvancedRateLimiter()


# Convenience decorators for common endpoints
auth_rate_limit = advanced_limiter.limit("/auth")
chat_rate_limit = advanced_limiter.limit("/chat")
heavy_rate_limit = advanced_limiter.limit("/process")


# IP-based blocking for severe violations
class IPBlocker:
    """Manages IP blocking for severe rate limit violations."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.blocked_ips: set = set()
    
    async def is_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked."""
        if self.redis_client:
            blocked = await self.redis_client.get(f"blocked_ip:{ip}")
            return blocked is not None
        return ip in self.blocked_ips
    
    async def block_ip(self, ip: str, duration: int = 86400):
        """Block an IP for a specified duration (default 24 hours)."""
        logger.warning(
            f"Blocking IP {ip} for {duration} seconds",
            extra={
                "security_event": "ip_blocked",
                "ip_address": ip,
                "duration": duration
            }
        )
        
        if self.redis_client:
            await self.redis_client.setex(f"blocked_ip:{ip}", duration, "1")
        else:
            self.blocked_ips.add(ip)
    
    async def unblock_ip(self, ip: str):
        """Manually unblock an IP."""
        logger.info(f"Unblocking IP {ip}")
        
        if self.redis_client:
            await self.redis_client.delete(f"blocked_ip:{ip}")
        else:
            self.blocked_ips.discard(ip)


# Global IP blocker instance
ip_blocker = IPBlocker()


# Middleware for checking blocked IPs
async def check_ip_block(request: Request, call_next):
    """Middleware to check if requesting IP is blocked."""
    ip = get_remote_address(request)
    
    if await ip_blocker.is_blocked(ip):
        logger.warning(
            f"Blocked IP attempted access: {ip}",
            extra={
                "security_event": "blocked_ip_access",
                "ip_address": ip,
                "path": request.url.path
            }
        )
        
        return JSONResponse(
            status_code=403,
            content={
                "error": "Access denied",
                "message": "Your IP has been temporarily blocked due to excessive violations."
            }
        )
    
    return await call_next(request)