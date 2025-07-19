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

from core.settings import settings
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
    # Configuración de CORS
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "https://ngx-agents.app",
        "https://www.ngx-agents.app",
        "https://api.ngx-agents.app",
    ]
    
    # Agregar origen adicional si está configurado
    if hasattr(settings, "frontend_url"):
        origins.append(str(settings.frontend_url))
    
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
            "X-User-ID",
            "X-Agent-ID",
            "Accept",
            "Accept-Language",
            "Content-Language",
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
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # En producción, especificar hosts permitidos
    )
    
    # Compresión GZip
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # Comprimir respuestas mayores a 1KB
    )
    
    # Sesiones (para CSRF y otros)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.jwt_secret if hasattr(settings, "jwt_secret") else "dev-secret-key",
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
        
        # HSTS solo en producción
        if settings.env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP básico
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.ngx-agents.app wss://api.ngx-agents.app"
        )
        
        return response