"""
Security middleware for request validation and suspicious pattern detection.

This middleware provides:
- Input validation and sanitization
- SQL injection detection
- XSS attempt detection
- Path traversal detection
- Request size validation
- Suspicious pattern logging
"""

import re
import json
from typing import List, Pattern, Dict, Any
from urllib.parse import unquote

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.security_logger import log_suspicious_request, SecurityEventType
from core.logging_config import get_logger

logger = get_logger(__name__)


class SecurityValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating requests and detecting security threats."""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_request_size = max_request_size
        
        # Compile regex patterns for better performance
        self.sql_injection_patterns: List[Pattern] = [
            re.compile(r"(?i)(union.*select|select.*from|insert.*into|delete.*from|drop.*table|update.*set)", re.IGNORECASE),
            re.compile(r"(?i)(exec\(|execute|declare.*@|cast\(|convert\()", re.IGNORECASE),
            re.compile(r"(?i)(waitfor.*delay|benchmark\(|sleep\()", re.IGNORECASE),
            re.compile(r"(?i)(;.*shutdown|;.*xp_cmdshell)", re.IGNORECASE),
        ]
        
        self.xss_patterns: List[Pattern] = [
            re.compile(r"(?i)(<script[^>]*>|</script>|javascript:|vbscript:)", re.IGNORECASE),
            re.compile(r"(?i)(onload=|onerror=|onclick=|onmouseover=)", re.IGNORECASE),
            re.compile(r"(?i)(<iframe|<object|<embed|<applet)", re.IGNORECASE),
            re.compile(r"(?i)(document\.|window\.|eval\(|alert\()", re.IGNORECASE),
        ]
        
        self.path_traversal_patterns: List[Pattern] = [
            re.compile(r"(?i)(\.\.\/|\.\.\\\\)", re.IGNORECASE),
            re.compile(r"(?i)(\/etc\/passwd|\/windows\/system32)", re.IGNORECASE),
            re.compile(r"(?i)(%2e%2e%2f|%252e%252e%252f)", re.IGNORECASE),
        ]
        
        self.command_injection_patterns: List[Pattern] = [
            re.compile(r"(?i)(\||;|&|`|\$\(|\))", re.IGNORECASE),
            re.compile(r"(?i)(nc\s+-|bash\s+-|sh\s+-|cmd\.exe|powershell)", re.IGNORECASE),
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through security validation."""
        try:
            # Check request size
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.max_request_size:
                return JSONResponse(
                    status_code=413,
                    content={"error": "Request entity too large"}
                )
            
            # Validate path
            path_validation = await self._validate_path(request)
            if not path_validation["valid"]:
                return JSONResponse(
                    status_code=400,
                    content={"error": path_validation["error"]}
                )
            
            # Validate query parameters
            query_validation = await self._validate_query_params(request)
            if not query_validation["valid"]:
                return JSONResponse(
                    status_code=400,
                    content={"error": query_validation["error"]}
                )
            
            # For POST/PUT/PATCH, validate body
            if request.method in ["POST", "PUT", "PATCH"]:
                body_validation = await self._validate_body(request)
                if not body_validation["valid"]:
                    return JSONResponse(
                        status_code=400,
                        content={"error": body_validation["error"]}
                    )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers to response
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
    
    async def _validate_path(self, request: Request) -> Dict[str, Any]:
        """Validate request path for security threats."""
        path = unquote(str(request.url.path))
        
        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if pattern.search(path):
                await log_suspicious_request(
                    request,
                    "path_traversal",
                    {"path": path, "pattern": pattern.pattern}
                )
                return {
                    "valid": False,
                    "error": "Invalid path"
                }
        
        return {"valid": True}
    
    async def _validate_query_params(self, request: Request) -> Dict[str, Any]:
        """Validate query parameters for security threats."""
        for param_name, param_value in request.query_params.items():
            # Decode parameter
            decoded_value = unquote(str(param_value))
            
            # Check all patterns
            threats_found = []
            
            for pattern in self.sql_injection_patterns:
                if pattern.search(decoded_value):
                    threats_found.append("sql_injection")
                    break
            
            for pattern in self.xss_patterns:
                if pattern.search(decoded_value):
                    threats_found.append("xss")
                    break
            
            for pattern in self.command_injection_patterns:
                if pattern.search(decoded_value):
                    threats_found.append("command_injection")
                    break
            
            if threats_found:
                await log_suspicious_request(
                    request,
                    threats_found[0],
                    {
                        "parameter": param_name,
                        "value": decoded_value[:100],  # Truncate for logging
                        "threats": threats_found
                    }
                )
                return {
                    "valid": False,
                    "error": "Invalid query parameter"
                }
        
        return {"valid": True}
    
    async def _validate_body(self, request: Request) -> Dict[str, Any]:
        """Validate request body for security threats."""
        try:
            # Read body
            body = await request.body()
            if not body:
                return {"valid": True}
            
            # Try to parse as JSON
            try:
                json_body = json.loads(body)
                return await self._validate_json_recursive(request, json_body)
            except json.JSONDecodeError:
                # If not JSON, validate as string
                body_str = body.decode("utf-8", errors="ignore")
                return await self._validate_string_content(request, body_str, "body")
            
        except Exception as e:
            logger.error(f"Body validation error: {str(e)}")
            return {"valid": True}  # Don't block on validation errors
    
    async def _validate_json_recursive(self, request: Request, data: Any, 
                                     path: str = "") -> Dict[str, Any]:
        """Recursively validate JSON data."""
        if isinstance(data, dict):
            for key, value in data.items():
                result = await self._validate_json_recursive(
                    request, value, f"{path}.{key}" if path else key
                )
                if not result["valid"]:
                    return result
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                result = await self._validate_json_recursive(
                    request, item, f"{path}[{i}]"
                )
                if not result["valid"]:
                    return result
        
        elif isinstance(data, str):
            return await self._validate_string_content(request, data, path)
        
        return {"valid": True}
    
    async def _validate_string_content(self, request: Request, content: str, 
                                     field: str) -> Dict[str, Any]:
        """Validate string content for security threats."""
        threats_found = []
        
        # Check all patterns
        for pattern in self.sql_injection_patterns:
            if pattern.search(content):
                threats_found.append("sql_injection")
                break
        
        for pattern in self.xss_patterns:
            if pattern.search(content):
                threats_found.append("xss")
                break
        
        if threats_found:
            await log_suspicious_request(
                request,
                threats_found[0],
                {
                    "field": field,
                    "content_preview": content[:100],
                    "threats": threats_found
                }
            )
            return {
                "valid": False,
                "error": f"Invalid content in field: {field}"
            }
        
        return {"valid": True}


class APIKeyValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for API key validation and tracking."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate API keys and track usage."""
        # Skip validation for public endpoints
        public_paths = ["/", "/health", "/docs", "/openapi.json", "/auth/"]
        if any(str(request.url.path).startswith(path) for path in public_paths):
            return await call_next(request)
        
        # Check for API key in headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # TODO: Validate API key against database
            # For now, just log the attempt
            logger.info(f"API key used: {api_key[:8]}...")
        
        return await call_next(request)