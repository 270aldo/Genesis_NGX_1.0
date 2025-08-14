"""
Configuración centralizada de middleware para la aplicación.

Este módulo gestiona todos los middlewares de la aplicación,
incluyendo seguridad, rate limiting, tracking y CORS.
"""

import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.middleware.circuit_breaker_middleware import CircuitBreakerMiddleware
from app.middleware.security_headers import setup_security_headers_middleware
from core.advanced_rate_limit import advanced_limiter, check_ip_block
from core.granular_rate_limiter import (
    GranularRateLimitMiddleware,
    initialize_granular_rate_limiter,
)
from core.logging_config import get_logger
from core.rate_limit import limiter, rate_limit_exceeded_handler
from core.security_middleware import (
    APIKeyValidationMiddleware,
    SecurityValidationMiddleware,
)

logger = get_logger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para tracking de requests.

    Agrega:
    - Request ID único para cada petición
    - Medición de tiempo de procesamiento
    - Headers de respuesta con metadata
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesa cada request agregando tracking."""
        # Generar request ID único
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.time()

        # Log de entrada
        logger.debug(
            f"Request started: {request.method} {request.url.path} "
            f"[ID: {request_id}]"
        )

        # Procesar request
        response = await call_next(request)

        # Calcular tiempo de procesamiento
        process_time = time.time() - request.state.start_time

        # Agregar headers de respuesta
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        # Log de salida
        logger.debug(
            f"Request completed: {request.method} {request.url.path} "
            f"[ID: {request_id}] [Status: {response.status_code}] "
            f"[Time: {process_time:.3f}s]"
        )

        return response


def configure_cors(app: FastAPI) -> None:
    """
    Configura CORS para la aplicación.

    Args:
        app: Instancia de FastAPI
    """
    from core.settings_lazy import settings

    origins = (
        getattr(settings, "cors_origins", "*").split(",")
        if getattr(settings, "cors_origins", None)
        else ["*"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-Request-ID",
            "X-Process-Time",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
    )

    logger.info(f"CORS configurado para origins: {origins}")


def configure_security_middleware(app: FastAPI) -> None:
    """
    Configura middleware de seguridad.

    Args:
        app: Instancia de FastAPI
    """
    from core.settings_lazy import settings

    # Trusted hosts (previene Host header injection)
    if getattr(settings, "trusted_hosts", None):
        hosts = settings.trusted_hosts.split(",")
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
        logger.info(f"Trusted hosts configurados: {hosts}")

    # Security headers
    setup_security_headers_middleware(app)

    # Validación de seguridad
    app.add_middleware(SecurityValidationMiddleware)

    # Validación de API key
    if getattr(settings, "require_api_key", False):
        app.add_middleware(APIKeyValidationMiddleware)
        logger.info("API Key validation middleware activado")

    logger.info("Middleware de seguridad configurado")


def configure_rate_limiting(app: FastAPI) -> None:
    """
    Configura rate limiting para la aplicación.

    Args:
        app: Instancia de FastAPI
    """
    # Configurar limiters en el estado de la app
    app.state.limiter = limiter
    app.state.advanced_limiter = advanced_limiter

    # Inicializar rate limiter granular con Redis si está disponible
    try:
        from core.redis_pool import get_redis_pool

        redis_client = get_redis_pool()
        initialize_granular_rate_limiter(redis_client)

        # Agregar middleware de rate limiting granular
        app.add_middleware(GranularRateLimitMiddleware, redis_client=redis_client)
        logger.info("Rate limiting granular configurado con Redis")
    except Exception as e:
        logger.warning(f"Redis no disponible para rate limiting granular: {e}")
        # Inicializar sin Redis (usando memoria local)
        initialize_granular_rate_limiter(None)
        app.add_middleware(GranularRateLimitMiddleware, redis_client=None)
        logger.info("Rate limiting granular configurado con memoria local")

    # Agregar handler de excepciones para rate limit
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # IP blocking middleware
    app.middleware("http")(check_ip_block)

    logger.info("Rate limiting configurado")


def configure_request_tracking(app: FastAPI) -> None:
    """
    Configura tracking de requests.

    Args:
        app: Instancia de FastAPI
    """
    app.add_middleware(RequestTrackingMiddleware)
    logger.info("Request tracking configurado")


def configure_all_middleware(app: FastAPI) -> None:
    """
    Configura todos los middlewares de la aplicación.

    IMPORTANTE: El orden importa. Los middlewares se ejecutan
    en orden inverso al que se agregan.

    Args:
        app: Instancia de FastAPI
    """
    logger.info("Configurando middlewares...")

    # 1. Request tracking (debe ser primero para capturar todo)
    configure_request_tracking(app)

    # 2. CORS (necesario temprano para preflight requests)
    configure_cors(app)

    # 3. Security (headers, validation, API keys)
    configure_security_middleware(app)

    # 4. Rate limiting (después de auth para aplicar por usuario)
    configure_rate_limiting(app)

    # 5. Circuit breaker (para prevenir cascadas de fallos)
    app.add_middleware(CircuitBreakerMiddleware)
    logger.info("Circuit breaker middleware configurado")

    logger.info("✅ Todos los middlewares configurados")
