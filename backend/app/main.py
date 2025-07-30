"""
API principal de NGX Agents (Refactorizado).

Este módulo es el punto de entrada principal de la aplicación FastAPI.
La lógica ha sido modularizada en los siguientes componentes:
- core/server.py: Configuración del servidor
- core/startup.py: Lógica de inicialización
- core/shutdown.py: Lógica de apagado
- core/routes.py: Registro de rutas
- core/exceptions.py: Manejadores de excepciones
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from core.rate_limit import limiter, rate_limit_exceeded_handler
from core.advanced_rate_limit import advanced_limiter, ip_blocker, check_ip_block
from core.security_middleware import SecurityValidationMiddleware, APIKeyValidationMiddleware
from app.core.server import create_app, configure_middleware, configure_security_headers
from app.core.startup import startup_event
from app.core.shutdown import shutdown_event
from app.core.routes import register_routes, register_api_routes
from app.core.exceptions import configure_exception_handlers
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Gestor de contexto para el ciclo de vida de la aplicación.
    Reemplaza los eventos on_event("startup") y on_event("shutdown").
    """
    # Startup
    await startup_event(app)
    
    yield
    
    # Shutdown
    await shutdown_event(app)


# Crear aplicación con el nuevo gestor de ciclo de vida
app = create_app()
app.state.limiter = limiter
app.state.advanced_limiter = advanced_limiter

# Configurar lifespan
app.router.lifespan_context = lifespan

# Configurar middleware
configure_middleware(app)
configure_security_headers(app)

# Add security middleware
app.add_middleware(SecurityValidationMiddleware)
app.add_middleware(APIKeyValidationMiddleware)

# Add IP blocking middleware
app.add_middleware("http", middleware_class=check_ip_block)

# Configurar manejadores de excepciones
configure_exception_handlers(app)

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Registrar rutas
register_routes(app)
register_api_routes(app)


# Middleware para tracking de requests
@app.middleware("http")
async def add_request_tracking(request, call_next):
    """Agrega tracking básico a cada request."""
    import time
    import uuid
    
    # Generar request ID
    request.state.request_id = str(uuid.uuid4())
    request.state.start_time = time.time()
    
    # Procesar request
    response = await call_next(request)
    
    # Agregar headers de respuesta
    process_time = time.time() - request.state.start_time
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Ruta raíz
@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz de la API."""
    return {
        "message": "NGX Agents API v2.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


if __name__ == "__main__":
    import uvicorn
    from core.settings_lazy import settings
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=True,
        use_colors=True,
    )