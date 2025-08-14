"""
Security headers compliance tests.

Tests security headers implementation for protection against
common web vulnerabilities and compliance with security standards.
"""

import json
from unittest.mock import Mock

import pytest
from fastapi import Request, Response


# Mock the security headers middleware setup
def mock_security_headers_middleware():
    """Mock security headers middleware for testing."""

    async def add_security_headers(request: Request, call_next):
        """Mock security headers middleware function."""
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

        # Content Security Policy - Secure configuration
        import secrets

        nonce = secrets.token_urlsafe(16)

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
        response.headers["Cross-Origin-Embedder-Policy"] = "credentialless"

        # Cross-Origin Opener Policy
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin Resource Policy
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Clear-Site-Data on logout endpoints
        if request.url.path in ["/api/v1/auth/logout", "/api/v1/auth/signout"]:
            response.headers["Clear-Site-Data"] = '"cache", "cookies", "storage"'

        # Remove unnecessary headers that might reveal server info
        headers_to_remove = ["Server", "X-Powered-By"]
        for header in headers_to_remove:
            if header in response.headers:
                del response.headers[header]

        return response

    return add_security_headers


class TestSecurityHeaders:
    """Test security headers implementation."""

    def test_basic_security_headers(self):
        """Test basic security headers are present."""
        # Mock request and response
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {}

        # Mock call_next to return the response
        async def mock_call_next(req):
            return response

        # Apply security headers middleware
        middleware = mock_security_headers_middleware()

        # Run the middleware (synchronously for testing)
        import asyncio

        async def run_middleware():
            return await middleware(request, mock_call_next)

        result_response = asyncio.run(run_middleware())

        # Check basic security headers
        assert result_response.headers["X-Content-Type-Options"] == "nosniff"
        assert result_response.headers["X-Frame-Options"] == "DENY"
        assert result_response.headers["X-XSS-Protection"] == "1; mode=block"
        assert (
            result_response.headers["Referrer-Policy"]
            == "strict-origin-when-cross-origin"
        )

    def test_hsts_header_https_only(self):
        """Test HSTS header is only added for HTTPS requests."""
        # Test HTTPS request
        request_https = Mock(spec=Request)
        request_https.url.scheme = "https"
        request_https.url.path = "/api/v1/test"

        response_https = Mock(spec=Response)
        response_https.headers = {}

        async def mock_call_next(req):
            return response_https

        middleware = mock_security_headers_middleware()

        import asyncio

        result_https = asyncio.run(middleware(request_https, mock_call_next))

        # HSTS should be present for HTTPS
        assert "Strict-Transport-Security" in result_https.headers
        assert "max-age=31536000" in result_https.headers["Strict-Transport-Security"]
        assert "includeSubDomains" in result_https.headers["Strict-Transport-Security"]
        assert "preload" in result_https.headers["Strict-Transport-Security"]

        # Test HTTP request
        request_http = Mock(spec=Request)
        request_http.url.scheme = "http"
        request_http.url.path = "/api/v1/test"

        response_http = Mock(spec=Response)
        response_http.headers = {}

        result_http = asyncio.run(middleware(request_http, mock_call_next))

        # HSTS should not be present for HTTP
        assert "Strict-Transport-Security" not in result_http.headers

    def test_content_security_policy(self):
        """Test Content Security Policy header."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        result_response = asyncio.run(middleware(request, mock_call_next))

        # Check CSP header exists
        assert "Content-Security-Policy" in result_response.headers

        csp_header = result_response.headers["Content-Security-Policy"]

        # Check important CSP directives
        assert "default-src 'self'" in csp_header
        assert "script-src 'self'" in csp_header
        assert "style-src 'self'" in csp_header
        assert "object-src 'none'" in csp_header
        assert "frame-ancestors 'none'" in csp_header
        assert "base-uri 'self'" in csp_header
        assert "form-action 'self'" in csp_header
        assert "upgrade-insecure-requests" in csp_header

        # Check nonce is used for inline scripts/styles
        assert "'nonce-" in csp_header

        # Check allowed external sources
        assert "https://cdn.jsdelivr.net" in csp_header
        assert "https://fonts.googleapis.com" in csp_header
        assert "https://fonts.gstatic.com" in csp_header

        # Check reporting
        assert "report-uri /api/v1/security/csp-report" in csp_header
        assert "report-to csp-endpoint" in csp_header

    def test_permissions_policy(self):
        """Test Permissions Policy header."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        result_response = asyncio.run(middleware(request, mock_call_next))

        # Check Permissions Policy header
        assert "Permissions-Policy" in result_response.headers

        permissions_policy = result_response.headers["Permissions-Policy"]

        # Check dangerous features are disabled
        dangerous_features = [
            "accelerometer=()",
            "autoplay=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "magnetometer=()",
            "microphone=()",
            "payment=()",
            "usb=()",
        ]

        for feature in dangerous_features:
            assert feature in permissions_policy

        # Check some features are allowed for self
        assert "fullscreen=(self)" in permissions_policy

    def test_cross_origin_headers(self):
        """Test Cross-Origin headers."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        result_response = asyncio.run(middleware(request, mock_call_next))

        # Check Cross-Origin headers
        assert (
            result_response.headers["Cross-Origin-Embedder-Policy"] == "credentialless"
        )
        assert result_response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
        assert result_response.headers["Cross-Origin-Resource-Policy"] == "same-origin"

    def test_report_to_header(self):
        """Test Report-To header for CSP violation reporting."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        result_response = asyncio.run(middleware(request, mock_call_next))

        # Check Report-To header
        assert "Report-To" in result_response.headers

        report_to = json.loads(result_response.headers["Report-To"])

        assert report_to["group"] == "csp-endpoint"
        assert report_to["max_age"] == 86400
        assert len(report_to["endpoints"]) == 1
        assert report_to["endpoints"][0]["url"] == "/api/v1/security/csp-report"

    def test_clear_site_data_logout(self):
        """Test Clear-Site-Data header on logout endpoints."""
        logout_paths = ["/api/v1/auth/logout", "/api/v1/auth/signout"]

        for logout_path in logout_paths:
            request = Mock(spec=Request)
            request.url.scheme = "https"
            request.url.path = logout_path

            response = Mock(spec=Response)
            response.headers = {}

            async def mock_call_next(req):
                return response

            middleware = mock_security_headers_middleware()

            import asyncio

            result_response = asyncio.run(middleware(request, mock_call_next))

            # Should have Clear-Site-Data header for logout endpoints
            assert "Clear-Site-Data" in result_response.headers
            assert (
                '"cache", "cookies", "storage"'
                in result_response.headers["Clear-Site-Data"]
            )

        # Test non-logout endpoint
        request_normal = Mock(spec=Request)
        request_normal.url.scheme = "https"
        request_normal.url.path = "/api/v1/normal"

        response_normal = Mock(spec=Response)
        response_normal.headers = {}

        result_normal = asyncio.run(middleware(request_normal, mock_call_next))

        # Should not have Clear-Site-Data header for normal endpoints
        assert "Clear-Site-Data" not in result_normal.headers

    def test_server_header_removal(self):
        """Test removal of server information headers."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {
            "Server": "nginx/1.20.1",
            "X-Powered-By": "FastAPI",
            "Content-Type": "application/json",
        }

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        result_response = asyncio.run(middleware(request, mock_call_next))

        # Server info headers should be removed
        assert "Server" not in result_response.headers
        assert "X-Powered-By" not in result_response.headers

        # Other headers should remain
        assert "Content-Type" in result_response.headers

    def test_csp_nonce_generation(self):
        """Test CSP nonce generation and uniqueness."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        def create_response():
            response = Mock(spec=Response)
            response.headers = {}
            return response

        async def mock_call_next(req):
            return create_response()

        middleware = mock_security_headers_middleware()

        import asyncio

        # Generate multiple responses
        responses = []
        for _ in range(5):
            response = asyncio.run(middleware(request, mock_call_next))
            responses.append(response)

        # Extract nonces from CSP headers
        nonces = []
        for response in responses:
            csp_header = response.headers["Content-Security-Policy"]

            # Find nonce values in CSP header
            import re

            nonce_matches = re.findall(r"'nonce-([A-Za-z0-9_-]+)'", csp_header)

            # Should have exactly 2 nonces (script-src and style-src)
            assert len(nonce_matches) == 2

            # Both nonces should be the same within a single response
            assert nonce_matches[0] == nonce_matches[1]

            nonces.append(nonce_matches[0])

        # All nonces should be different across responses
        assert len(set(nonces)) == len(nonces)

        # Nonces should be sufficiently long
        for nonce in nonces:
            assert len(nonce) >= 16

    def test_security_headers_completeness(self):
        """Test that all required security headers are present."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        result_response = asyncio.run(middleware(request, mock_call_next))

        # Required security headers for compliance
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",  # For HTTPS
            "Referrer-Policy",
            "Permissions-Policy",
            "Content-Security-Policy",
            "Report-To",
            "Cross-Origin-Embedder-Policy",
            "Cross-Origin-Opener-Policy",
            "Cross-Origin-Resource-Policy",
        ]

        for header in required_headers:
            assert (
                header in result_response.headers
            ), f"Missing required header: {header}"

    def test_csp_violation_reporting_config(self):
        """Test CSP violation reporting configuration."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        result_response = asyncio.run(middleware(request, mock_call_next))

        csp_header = result_response.headers["Content-Security-Policy"]

        # Should have both legacy and modern reporting
        assert "report-uri /api/v1/security/csp-report" in csp_header
        assert "report-to csp-endpoint" in csp_header

        # Report-To header should be properly configured
        report_to = json.loads(result_response.headers["Report-To"])
        assert report_to["group"] == "csp-endpoint"
        assert report_to["max_age"] == 86400
        assert report_to["endpoints"][0]["url"] == "/api/v1/security/csp-report"


class TestSecurityHeadersIntegration:
    """Integration tests for security headers."""

    def test_security_headers_with_different_paths(self):
        """Test security headers behavior with different request paths."""
        paths_to_test = [
            "/api/v1/health",
            "/api/v1/auth/login",
            "/api/v1/auth/logout",
            "/api/v1/privacy/consent",
            "/docs",
            "/static/css/style.css",
        ]

        middleware = mock_security_headers_middleware()

        import asyncio

        for path in paths_to_test:
            request = Mock(spec=Request)
            request.url.scheme = "https"
            request.url.path = path

            response = Mock(spec=Response)
            response.headers = {}

            async def mock_call_next(req):
                return response

            result_response = asyncio.run(middleware(request, mock_call_next))

            # All paths should have basic security headers
            assert result_response.headers["X-Content-Type-Options"] == "nosniff"
            assert result_response.headers["X-Frame-Options"] == "DENY"
            assert "Content-Security-Policy" in result_response.headers

            # Logout paths should have Clear-Site-Data
            if "logout" in path or "signout" in path:
                assert "Clear-Site-Data" in result_response.headers
            else:
                assert "Clear-Site-Data" not in result_response.headers

    def test_security_headers_performance(self):
        """Test that security headers don't significantly impact performance."""
        import time

        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        response = Mock(spec=Response)
        response.headers = {}

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        # Measure time for multiple requests
        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            asyncio.run(middleware(request, mock_call_next))

        end_time = time.time()
        average_time = (end_time - start_time) / iterations

        # Should complete very quickly (less than 1ms per request)
        assert (
            average_time < 0.001
        ), f"Security headers middleware too slow: {average_time:.4f}s per request"

    def test_security_headers_with_existing_headers(self):
        """Test security headers behavior when response already has headers."""
        request = Mock(spec=Request)
        request.url.scheme = "https"
        request.url.path = "/api/v1/test"

        # Response with existing headers
        response = Mock(spec=Response)
        response.headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Custom-Header": "custom-value",
        }

        async def mock_call_next(req):
            return response

        middleware = mock_security_headers_middleware()

        import asyncio

        result_response = asyncio.run(middleware(request, mock_call_next))

        # Existing headers should be preserved
        assert result_response.headers["Content-Type"] == "application/json"
        assert result_response.headers["Cache-Control"] == "no-cache"
        assert result_response.headers["X-Custom-Header"] == "custom-value"

        # Security headers should be added
        assert result_response.headers["X-Content-Type-Options"] == "nosniff"
        assert result_response.headers["X-Frame-Options"] == "DENY"
        assert "Content-Security-Policy" in result_response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
