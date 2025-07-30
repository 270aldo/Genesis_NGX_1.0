"""
Configuración del servidor FastAPI.

Este módulo contiene la configuración central del servidor,
incluyendo CORS, documentación y configuración básica.
"""

from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from core.settings_lazy import settings
from core.rate_limit import limiter
from core.telemetry import instrument_fastapi


def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI.
    
    Returns:
        FastAPI: Aplicación configurada
    """
    # Configuración de la aplicación
    app = FastAPI(
        title="NGX Agents API",
        description="API para el sistema de agentes NGX de fitness y nutrición",
        version="2.0.0",
        docs_url=None,  # Deshabilitamos la documentación por defecto
        redoc_url=None,  # Deshabilitamos redoc por defecto
        openapi_url=None,  # Controlamos el acceso a openapi.json
    )
    
    # Agregar state a la aplicación
    app.state.limiter = limiter
    
    return app


def configure_cors(app: FastAPI) -> None:
    """
    Configura CORS para la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    # SECURITY: Configure CORS based on environment
    origins = []
    
    if settings.env == "development":
        # Only allow localhost in development
        origins = [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
        ]
    elif settings.env == "staging":
        origins = [
            "https://staging.genesis-ngx.com",
            "https://app-staging.genesis-ngx.com"
        ]
    elif settings.env == "production":
        origins = [
            "https://genesis-ngx.com",
            "https://www.genesis-ngx.com",
            "https://app.genesis-ngx.com"
        ]
    
    # Add configured frontend URL if exists
    if hasattr(settings, "frontend_url") and settings.frontend_url:
        origins.append(str(settings.frontend_url))
    
    # Remove duplicates and None values
    origins = list(filter(None, set(origins)))
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-Session-ID",
            "Accept",
            "Accept-Language",
            "Origin",
        ],
        expose_headers=[
            "X-Request-ID",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Response-Time",
        ],
        max_age=86400,  # 24 horas
    )


def configure_middleware(app: FastAPI) -> None:
    """
    Configura todos los middlewares de la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    # Configurar CORS
    configure_cors(app)
    
    # Middleware de hosts confiables
    # SECURITY: Configure allowed hosts based on environment
    allowed_hosts = ["localhost", "127.0.0.1"]
    
    if settings.env == "production":
        allowed_hosts = [
            "api.genesis-ngx.com",
            "genesis-ngx.com",
            "*.genesis-ngx.com"
        ]
    elif settings.env == "staging":
        allowed_hosts.extend([
            "staging.genesis-ngx.com",
            "api-staging.genesis-ngx.com"
        ])
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )
    
    # Compresión GZip
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # Comprimir respuestas mayores a 1KB
    )
    
    # Sesiones (para CSRF y otros)
    # SECURITY: No fallback for JWT secret - must be explicitly set
    if not hasattr(settings, "jwt_secret") or not settings.jwt_secret:
        raise ValueError("JWT_SECRET must be set in environment variables")
    
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.jwt_secret,
        session_cookie="ngx_session",
        max_age=86400,  # 24 horas
        same_site="lax",
        https_only=settings.env == "production",
    )
    
    # Instrumentación de telemetría
    if hasattr(settings, "telemetry_enabled") and settings.telemetry_enabled:
        instrument_fastapi(app)


def configure_security_headers(app: FastAPI) -> None:
    """
    Configura headers de seguridad para todas las respuestas.
    
    Args:
        app: Instancia de FastAPI
    """
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        
        # Headers de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' wss: https:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Additional security headers
        response.headers["Expect-CT"] = "max-age=86400, enforce"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        # HSTS solo en producción
        if settings.env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response