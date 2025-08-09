"""
API principal de NGX Agents (Completamente Refactorizado).

Este es el punto de entrada principal de la aplicación FastAPI.
Toda la lógica ha sido modularizada para mantener este archivo limpio y simple.

Módulos:
- core/lifespan.py: Gestión del ciclo de vida
- core/middleware.py: Configuración de middlewares
- core/dependencies.py: Dependencias compartidas
- core/server.py: Configuración del servidor
- core/routes.py: Registro de rutas
- core/exceptions.py: Manejadores de excepciones
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.server import create_app
from app.core.lifespan import lifespan
from app.core.middleware import configure_all_middleware
from app.core.routes import register_routes, register_api_routes
from app.core.exceptions import configure_exception_handlers
from core.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)

# =============================================================================
# CREAR Y CONFIGURAR APLICACIÓN
# =============================================================================

# Crear aplicación con configuración base
app = create_app(lifespan=lifespan)

# Configurar todos los middlewares
configure_all_middleware(app)

# Configurar manejadores de excepciones
configure_exception_handlers(app)

# Registrar todas las rutas
register_routes(app)
register_api_routes(app)

# =============================================================================
# ENDPOINTS BÁSICOS
# =============================================================================


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API.
    
    Proporciona información básica sobre la API y enlaces útiles.
    """
    return JSONResponse(
        content={
            "name": "NGX Agents API",
            "version": "2.0.0",
            "status": "operational",
            "description": "AI-powered fitness and nutrition coaching system",
            "links": {
                "documentation": "/docs",
                "openapi": "/openapi.json",
                "health": "/health",
                "metrics": "/metrics",
                "agents": "/api/v1/agents"
            },
            "features": [
                "11 specialized AI agents",
                "Voice conversations with ElevenLabs",
                "Real-time coaching",
                "Personalized training plans",
                "Nutrition guidance",
                "Progress tracking",
                "Wearables integration"
            ]
        }
    )


@app.get("/ping", tags=["Health"])
async def ping():
    """
    Simple ping endpoint para verificación rápida.
    
    Returns:
        Mensaje pong
    """
    return {"ping": "pong"}


# =============================================================================
# PUNTO DE ENTRADA PARA DESARROLLO
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    from core.settings_lazy import settings
    
    logger.info("Starting NGX Agents API in development mode...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=True,
        use_colors=True,
        # Configuración adicional para desarrollo
        reload_dirs=["app", "agents", "core", "clients"] if settings.debug else None,
        reload_excludes=["*.pyc", "__pycache__", ".pytest_cache"] if settings.debug else None
    )