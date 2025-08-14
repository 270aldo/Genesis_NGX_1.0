"""
Security headers middleware for NGX Agents API.

This module provides security headers to protect against common web vulnerabilities
such as XSS, clickjacking, MIME sniffing, and more.
"""

import json

from fastapi import FastAPI, Request

from core.logging_config import get_logger

logger = get_logger(__name__)


def setup_security_headers_middleware(app: FastAPI) -> None:
    """
    Configure security headers middleware.

    Args:
        app: FastAPI application instance
    """

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """
        Add security headers to all responses.

        Headers added:
        - X-Content-Type-Options: Prevents MIME type sniffing
        - X-Frame-Options: Prevents clickjacking attacks
        - X-XSS-Protection: Enables XSS filter in older browsers
        - Strict-Transport-Security: Forces HTTPS connections
        - Referrer-Policy: Controls referrer information
        - Permissions-Policy: Controls browser features
        - Content-Security-Policy: Controls allowed resources
        """
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS protection (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Force HTTPS (only in production)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Disable browser features that aren't needed
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )

        # Content Security Policy - Secure configuration without unsafe directives
        # Using nonce-based approach for inline scripts/styles when needed
        import secrets

        nonce = secrets.token_urlsafe(16)

        # Store nonce in response for potential use by templates
        if hasattr(response, "nonce"):
            response.nonce = nonce

        csp_directives = [
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net",
            f"style-src 'self' 'nonce-{nonce}' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https://api.ngxagents.com wss://api.ngxagents.com https://*.supabase.co wss://*.supabase.co",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "object-src 'none'",
            "media-src 'self'",
            "worker-src 'self'",
            "manifest-src 'self'",
            "upgrade-insecure-requests",
        ]

        # Add CSP violation reporting endpoint
        csp_directives.append("report-uri /api/v1/security/csp-report")
        csp_directives.append("report-to csp-endpoint")

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Add Report-To header for CSP violation reporting
        response.headers["Report-To"] = json.dumps(
            {
                "group": "csp-endpoint",
                "max_age": 86400,
                "endpoints": [{"url": "/api/v1/security/csp-report"}],
            }
        )

        # Additional security headers for compliance

        # Cross-Origin Embedder Policy
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

        # Cross-Origin Opener Policy
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin Resource Policy
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Feature Policy / Permissions Policy (enhanced)
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "autoplay=(), "
            "camera=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "fullscreen=(self), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "sync-xhr=(), "
            "usb=(), "
            "xr-spatial-tracking=()"
        )

        # Clear-Site-Data on logout endpoints
        if request.url.path in ["/api/v1/auth/logout", "/api/v1/auth/signout"]:
            response.headers["Clear-Site-Data"] = '"cache", "cookies", "storage"'

        # COEP policy for cross-origin isolation
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"

        # Remove unnecessary headers that might reveal server info
        headers_to_remove = ["Server", "X-Powered-By"]
        for header in headers_to_remove:
            if header in response.headers:
                del response.headers[header]

        return response

    logger.info("Security headers middleware configured")
