"""
Rate limiting configuration for NGX Agents API.

This module provides rate limiting functionality to protect the API
from abuse and ensure fair usage across all users.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from core.logging_config import get_logger

logger = get_logger(__name__)

# Create the limiter instance
# Using IP address as the key by default
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"],  # Global default limit
    headers_enabled=True,  # Include rate limit info in response headers
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded errors.
    
    Args:
        request: The FastAPI request object
        exc: The RateLimitExceeded exception
        
    Returns:
        JSONResponse with 429 status code
    """
    response_data = {
        "error": "Rate limit exceeded",
        "message": f"Too many requests. Please retry after {exc.retry_after} seconds.",
        "retry_after": exc.retry_after
    }
    
    # Log rate limit violation for monitoring
    logger.warning(
        f"Rate limit exceeded for IP: {get_remote_address(request)}",
        extra={
            "ip_address": get_remote_address(request),
            "path": request.url.path,
            "retry_after": exc.retry_after
        }
    )
    
    return JSONResponse(
        status_code=429,
        content=response_data,
        headers={
            "Retry-After": str(exc.retry_after),
            "X-RateLimit-Limit": str(exc.limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(exc.reset)
        }
    )


# Specific rate limits for different endpoints
auth_limiter = limiter.limit("5/minute")  # 5 login attempts per minute
chat_limiter = limiter.limit("30/minute")  # 30 chat requests per minute
heavy_operation_limiter = limiter.limit("10/hour")  # 10 heavy operations per hour