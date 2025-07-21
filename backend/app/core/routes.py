"""
Configuración de rutas de la aplicación.

Este módulo centraliza el registro de todos los routers de la aplicación.
"""

from fastapi import FastAPI
from app.routers import (
    auth,
    agents,
    chat,
    a2a,
    a2a_standard,
    budget,
    prompt_analyzer,
    domain_cache,
    async_processor,
    batch_processor,
    batch_metrics,
    compression_metrics,
    cache_metrics,
    request_prioritizer,
    circuit_breaker,
    degraded_mode,
    chaos_testing,
    stream,
    stream_v2,  # Enhanced streaming with ADK
    feedback,
    audio,
    visualization,
    wearables,
    nutrition_vision,
    ecosystem,  # NEW: Ecosystem gateway
    feature_flags,  # Feature flag management
    # audio_coaching,  # TODO: implement
    # voice_synthesis,  # TODO: implement
    # conversation_history,  # TODO: implement
    # export,  # TODO: implement
    health,
    metrics,
    # personality,  # TODO: implement
    # legacy,  # TODO: implement
)


def register_routes(app: FastAPI) -> None:
    """
    Registra todos los routers de la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    # API v1 - Rutas principales
    api_v1_prefix = "/api/v1"
    
    # Autenticación y usuarios
    app.include_router(auth.router, prefix=api_v1_prefix)
    app.include_router(agents.router, prefix=api_v1_prefix)
    app.include_router(chat.router, prefix=api_v1_prefix)
    
    # A2A (Agent-to-Agent)
    app.include_router(a2a.router, prefix=api_v1_prefix)
    app.include_router(a2a_standard.router)  # Sin prefijo, usa rutas estándar
    
    # Gestión y análisis
    app.include_router(budget.router, prefix=api_v1_prefix)
    app.include_router(prompt_analyzer.router, prefix=api_v1_prefix)
    app.include_router(domain_cache.router, prefix=api_v1_prefix)
    
    # Procesamiento
    app.include_router(async_processor.router, prefix=api_v1_prefix)
    app.include_router(batch_processor.router, prefix=api_v1_prefix)
    
    # Métricas
    app.include_router(batch_metrics.router, prefix=api_v1_prefix)
    app.include_router(compression_metrics.router, prefix=api_v1_prefix)
    app.include_router(cache_metrics.router, prefix=api_v1_prefix)
    
    # Resiliencia
    app.include_router(request_prioritizer.router, prefix=api_v1_prefix)
    app.include_router(circuit_breaker.router, prefix=api_v1_prefix)
    app.include_router(degraded_mode.router, prefix=api_v1_prefix)
    app.include_router(chaos_testing.router, prefix=api_v1_prefix)
    
    # Streaming y feedback
    app.include_router(stream.router, prefix=api_v1_prefix)
    app.include_router(stream_v2.router, prefix="/api")  # v2 streaming with ADK
    app.include_router(feedback.router, prefix=api_v1_prefix)
    
    # Multimodal
    app.include_router(audio.router, prefix=api_v1_prefix)
    app.include_router(visualization.router, prefix=api_v1_prefix)
    app.include_router(wearables.router, prefix=api_v1_prefix)
    app.include_router(nutrition_vision.router, prefix=api_v1_prefix)
    # app.include_router(audio_coaching.router, prefix=api_v1_prefix)  # TODO
    # app.include_router(voice_synthesis.router, prefix=api_v1_prefix)  # TODO
    
    # Ecosystem Gateway - Central API for all NGX tools
    app.include_router(ecosystem.router, prefix=api_v1_prefix)
    
    # Feature Flags
    app.include_router(feature_flags.router, prefix=api_v1_prefix)
    
    # Datos y exportación
    # app.include_router(conversation_history.router, prefix=api_v1_prefix)  # TODO
    # app.include_router(export.router, prefix=api_v1_prefix)  # TODO
    
    # Sistema
    app.include_router(health.router)  # Sin prefijo para health checks
    app.include_router(metrics.router)  # Sin prefijo para métricas Prometheus
    # app.include_router(personality.router, prefix=api_v1_prefix)  # TODO
    
    # Rutas legacy (compatibilidad hacia atrás)
    # app.include_router(legacy.router, prefix=api_v1_prefix)  # TODO


def register_api_routes(app: FastAPI) -> None:
    """
    Registra rutas específicas de la API (docs, openapi, etc).
    
    Args:
        app: Instancia de FastAPI
    """
    from fastapi.openapi.docs import get_swagger_ui_html
    from fastapi.openapi.utils import get_openapi
    from fastapi import Depends, HTTPException, status
    from core.auth import get_current_user
    
    @app.get("/docs", tags=["documentación"])
    async def get_documentation(user_id: str = Depends(get_current_user)):
        """
        Endpoint personalizado para la documentación Swagger UI.
        Requiere autenticación para acceder.
        """
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="NGX Agents API - Documentación",
            oauth2_redirect_url="/docs/oauth2-redirect",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
            swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        )
    
    @app.get("/openapi.json", tags=["documentación"])
    async def get_openapi_schema(user_id: str = Depends(get_current_user)):
        """
        Endpoint para obtener el esquema OpenAPI.
        Requiere autenticación para acceder.
        """
        if not app.openapi_schema:
            app.openapi_schema = get_openapi(
                title="NGX Agents API",
                version="2.0.0",
                description="API para el sistema de agentes NGX de fitness y nutrición",
                routes=app.routes,
                tags=[
                    {"name": "auth", "description": "Autenticación y gestión de usuarios"},
                    {"name": "agents", "description": "Gestión de agentes NGX"},
                    {"name": "chat", "description": "Interacción con agentes"},
                    {"name": "a2a", "description": "Comunicación Agent-to-Agent"},
                    {"name": "stream", "description": "Streaming de respuestas"},
                    {"name": "ecosystem", "description": "Gateway para herramientas del ecosistema NGX"},
                    {"name": "metrics", "description": "Métricas y monitoreo"},
                    {"name": "health", "description": "Health checks"},
                ],
            )
        return app.openapi_schema