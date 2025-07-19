"""
Manejadores de excepciones globales.

Este módulo contiene los manejadores de excepciones y errores
para toda la aplicación.
"""

import time
import traceback
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from pydantic import ValidationError

from core.logging_config import get_logger
from core.telemetry import get_tracer
from core.metrics import error_counter, response_time_histogram


# Configurar logger
logger = get_logger(__name__)
tracer = get_tracer(__name__)


def configure_exception_handlers(app: FastAPI) -> None:
    """
    Configura todos los manejadores de excepciones de la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        """Manejador para excepciones de rate limiting."""
        response_time = time.time() - request.state.start_time
        response_time_histogram.labels(
            method=request.method,
            endpoint=request.url.path,
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        ).observe(response_time)
        
        error_counter.labels(
            method=request.method,
            endpoint=request.url.path,
            error_type="rate_limit",
        ).inc()
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Demasiadas solicitudes. Por favor, intenta más tarde.",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": exc.retry_after if hasattr(exc, "retry_after") else 60,
            },
            headers={
                "Retry-After": str(exc.retry_after if hasattr(exc, "retry_after") else 60),
                "X-RateLimit-Limit": str(getattr(exc, "limit", "N/A")),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(getattr(exc, "reset", "N/A")),
            },
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Manejador mejorado para HTTPException con más contexto."""
        response_time = time.time() - request.state.start_time
        response_time_histogram.labels(
            method=request.method,
            endpoint=request.url.path,
            status=exc.status_code,
        ).observe(response_time)
        
        error_counter.labels(
            method=request.method,
            endpoint=request.url.path,
            error_type="http_exception",
        ).inc()
        
        # Log del error con contexto
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": getattr(request.state, "request_id", "N/A"),
                "user_id": getattr(request.state, "user_id", "N/A"),
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
                "request_id": getattr(request.state, "request_id", "N/A"),
            },
            headers=exc.headers,
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """Manejador para errores de validación de Pydantic."""
        error_counter.labels(
            method=request.method,
            endpoint=request.url.path,
            error_type="validation_error",
        ).inc()
        
        # Formatear errores de validación
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        
        logger.warning(
            f"Validation Error: {request.url.path}",
            extra={
                "request_id": getattr(request.state, "request_id", "N/A"),
                "errors": errors,
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Error de validación en los datos enviados",
                "error_code": "VALIDATION_ERROR",
                "errors": errors,
                "request_id": getattr(request.state, "request_id", "N/A"),
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Manejador global para excepciones no capturadas."""
        # Registrar métrica
        error_counter.labels(
            method=request.method,
            endpoint=request.url.path,
            error_type="unhandled_exception",
        ).inc()
        
        # Log detallado del error
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
            exc_info=True,
            extra={
                "request_id": getattr(request.state, "request_id", "N/A"),
                "user_id": getattr(request.state, "user_id", "N/A"),
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc(),
            }
        )
        
        # Intentar enviar alerta si es crítico
        if _is_critical_error(exc):
            await _send_error_alert(request, exc)
        
        # Respuesta genérica para el cliente
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Error interno del servidor",
                "error_code": "INTERNAL_SERVER_ERROR",
                "error_type": type(exc).__name__,
                "request_id": getattr(request.state, "request_id", "N/A"),
            }
        )


def _is_critical_error(exc: Exception) -> bool:
    """
    Determina si un error es crítico y requiere alerta inmediata.
    
    Args:
        exc: La excepción a evaluar
        
    Returns:
        True si el error es crítico
    """
    critical_exceptions = (
        ConnectionError,
        TimeoutError,
        MemoryError,
        SystemError,
        RuntimeError,
    )
    
    critical_keywords = [
        "database",
        "connection",
        "memory",
        "disk",
        "critical",
        "fatal",
    ]
    
    # Verificar tipo de excepción
    if isinstance(exc, critical_exceptions):
        return True
    
    # Verificar palabras clave en el mensaje
    error_message = str(exc).lower()
    return any(keyword in error_message for keyword in critical_keywords)


async def _send_error_alert(request: Request, exc: Exception) -> None:
    """
    Envía una alerta para errores críticos.
    
    Args:
        request: Request de FastAPI
        exc: La excepción que ocurrió
    """
    try:
        # Aquí se integraría con un sistema de alertas (PagerDuty, Slack, etc.)
        alert_data = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "request_path": request.url.path,
            "request_method": request.method,
            "request_id": getattr(request.state, "request_id", "N/A"),
            "user_id": getattr(request.state, "user_id", "N/A"),
            "timestamp": time.time(),
            "traceback": traceback.format_exc()[-1000:],  # Últimos 1000 caracteres
        }
        
        # Log de la alerta
        logger.critical(
            f"CRITICAL ERROR ALERT: {type(exc).__name__}",
            extra=alert_data
        )
        
        # TODO: Implementar envío real de alertas
        # await alert_service.send_critical_alert(alert_data)
        
    except Exception as alert_error:
        logger.error(f"Error al enviar alerta: {alert_error}")