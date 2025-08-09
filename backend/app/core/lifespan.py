"""
Gestión del ciclo de vida de la aplicación FastAPI.

Este módulo maneja los eventos de startup y shutdown de la aplicación,
centralizando toda la lógica de inicialización y limpieza.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import time

from fastapi import FastAPI
from core.logging_config import get_logger
from app.core.startup import startup_event
from app.core.shutdown import shutdown_event

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Gestor de contexto para el ciclo de vida de la aplicación.
    
    Maneja:
    - Inicialización de recursos al arranque
    - Configuración de conexiones
    - Limpieza de recursos al apagado
    - Cierre ordenado de conexiones
    
    Args:
        app: Instancia de FastAPI
        
    Yields:
        Control a la aplicación durante su ejecución
    """
    start_time = time.time()
    
    # ===== STARTUP =====
    logger.info("🚀 Iniciando aplicación NGX Agents...")
    
    try:
        await startup_event(app)
        
        startup_time = time.time() - start_time
        logger.info(f"✅ Aplicación iniciada exitosamente en {startup_time:.2f}s")
        
        # Log de información del sistema
        _log_system_info(app)
        
    except Exception as e:
        logger.error(f"❌ Error durante el arranque: {e}", exc_info=True)
        raise
    
    # Ceder control a la aplicación
    yield
    
    # ===== SHUTDOWN =====
    logger.info("🔄 Iniciando proceso de apagado...")
    shutdown_start = time.time()
    
    try:
        await shutdown_event(app)
        
        shutdown_time = time.time() - shutdown_start
        logger.info(f"✅ Aplicación apagada correctamente en {shutdown_time:.2f}s")
        
    except Exception as e:
        logger.error(f"⚠️ Error durante el apagado: {e}", exc_info=True)
        # No re-lanzamos para permitir apagado gracioso


def _log_system_info(app: FastAPI) -> None:
    """
    Registra información del sistema al inicio.
    
    Args:
        app: Instancia de FastAPI
    """
    info_lines = [
        "=" * 60,
        "NGX AGENTS SYSTEM INFORMATION",
        "=" * 60,
        f"Version: {getattr(app, 'version', '2.0.0')}",
        f"Environment: {getattr(app.state, 'environment', 'development')}",
        f"Debug Mode: {getattr(app, 'debug', False)}",
    ]
    
    # Agregar información de agentes si está disponible
    if hasattr(app.state, 'agents_registry'):
        agent_count = len(app.state.agents_registry)
        info_lines.append(f"Registered Agents: {agent_count}")
    
    # Agregar información de conexiones
    if hasattr(app.state, 'redis_pool'):
        info_lines.append("Redis: Connected ✅")
    
    if hasattr(app.state, 'supabase_client'):
        info_lines.append("Supabase: Connected ✅")
    
    if hasattr(app.state, 'vertex_ai_client'):
        info_lines.append("Vertex AI: Connected ✅")
    
    info_lines.append("=" * 60)
    
    for line in info_lines:
        logger.info(line)