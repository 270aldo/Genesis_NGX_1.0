"""
Funciones de apagado del servidor.

Este módulo contiene las funciones que se ejecutan al detener el servidor,
incluyendo limpieza de recursos, guardado de estado y cierre de conexiones.
"""

import asyncio
from typing import Dict, Any

from fastapi import FastAPI
from core.logging_config import get_logger
from core.telemetry import shutdown_telemetry
from core.metrics import metrics_collector
from core.circuit_breaker import CircuitBreakerManager
from core.budget import budget_manager
from infrastructure.background_tasks import BackgroundTaskManager
from infrastructure.monitoring import MonitoringService
from infrastructure.a2a_server import A2AServer
from infrastructure.cache_warming import CacheWarmer
from infrastructure.adapters.state_manager_adapter import state_manager_adapter
from infrastructure.adapters.intent_analyzer_adapter import intent_analyzer_adapter
from agents.base.agent_registry import AgentRegistry
from clients.supabase_client import SupabaseClient
from core.redis_pool import close_redis_pool
from core.advanced_cache_manager import advanced_cache_manager


# Configurar logger
logger = get_logger(__name__)


async def save_system_state() -> Dict[str, Any]:
    """
    Guarda el estado actual del sistema antes del apagado.
    
    Returns:
        Dict con el estado guardado
    """
    state_saved = {}
    
    try:
        # 1. Guardar métricas actuales
        logger.info("📊 Guardando métricas...")
        metrics_data = await metrics_collector.get_all_metrics()
        await metrics_collector.save_to_storage(metrics_data)
        state_saved["metrics"] = len(metrics_data)
        
        # 2. Guardar estado de circuit breakers
        logger.info("🔒 Guardando estado de circuit breakers...")
        circuit_manager = CircuitBreakerManager.get_instance()
        breaker_states = circuit_manager.get_all_states()
        state_saved["circuit_breakers"] = len(breaker_states)
        
        # 3. Guardar presupuestos si están habilitados
        if hasattr(budget_manager, "is_initialized") and budget_manager.is_initialized:
            logger.info("💰 Guardando estado de presupuestos...")
            await budget_manager.save_state()
            state_saved["budgets"] = "saved"
        
        # 4. Guardar estado de adaptadores
        logger.info("🔌 Guardando estado de adaptadores...")
        await state_manager_adapter.save_state()
        state_saved["adapters"] = "saved"
        
        return state_saved
        
    except Exception as e:
        logger.error(f"Error al guardar el estado del sistema: {e}")
        state_saved["error"] = str(e)
        return state_saved


async def stop_background_services() -> None:
    """
    Detiene todos los servicios en segundo plano.
    """
    try:
        # 1. Detener tareas en segundo plano
        logger.info("🔄 Deteniendo tareas en segundo plano...")
        background_manager = BackgroundTaskManager.get_instance()
        await background_manager.stop()
        
        # 2. Detener cache warmer
        try:
            cache_warmer = CacheWarmer.get_instance()
            if cache_warmer:
                await cache_warmer.stop()
        except:
            pass
        
        # 3. Detener monitoreo
        logger.info("👁️ Deteniendo servicio de monitoreo...")
        monitoring = MonitoringService.get_instance()
        if monitoring:
            await monitoring.stop()
        
        # 4. Detener servidor A2A
        try:
            a2a_server = A2AServer.get_instance()
            if a2a_server:
                logger.info("🔗 Deteniendo servidor A2A...")
                await a2a_server.stop()
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error al detener servicios en segundo plano: {e}")


async def cleanup_resources() -> None:
    """
    Limpia recursos y cierra conexiones.
    """
    try:
        # 1. Limpiar registro de agentes
        logger.info("🤖 Limpiando registro de agentes...")
        registry = AgentRegistry.get_instance()
        await registry.cleanup()
        
        # 2. Cerrar conexiones de base de datos
        logger.info("🗄️ Cerrando conexiones de base de datos...")
        supabase = SupabaseClient.get_instance()
        if supabase:
            await supabase.close()
        
        # 3. Limpiar sistema de caché avanzado
        logger.info("🚀 Limpiando sistema de caché multi-capa...")
        try:
            # Obtener estadísticas finales antes de cerrar
            cache_stats = await advanced_cache_manager.get_comprehensive_statistics()
            logger.info(f"  📊 Estadísticas finales del caché: Hit ratio global: {cache_stats.get('global_statistics', {}).get('global_hit_ratio', 0):.2%}")
            
            # Limpiar caché
            await advanced_cache_manager.clear_all()
            logger.info("  ✅ Sistema de caché limpiado")
        except Exception as e:
            logger.error(f"  ❌ Error limpiando caché: {e}")
        
        # 4. Cerrar pool de Redis
        logger.info("🔴 Cerrando conexiones Redis...")
        try:
            await close_redis_pool()
            logger.info("  ✅ Pool de Redis cerrado")
        except Exception as e:
            logger.error(f"  ❌ Error cerrando Redis: {e}")
        
        # 5. Limpiar caché de adaptadores
        logger.info("🧹 Limpiando caché de adaptadores...")
        await state_manager_adapter.cleanup()
        await intent_analyzer_adapter.cleanup()
        
        # 6. Cerrar conexiones de telemetría
        if hasattr(shutdown_telemetry, "__call__"):
            logger.info("📊 Cerrando telemetría...")
            shutdown_telemetry()
            
    except Exception as e:
        logger.error(f"Error durante la limpieza de recursos: {e}")


async def graceful_shutdown(timeout: int = 30) -> None:
    """
    Realiza un apagado graceful con timeout.
    
    Args:
        timeout: Tiempo máximo en segundos para el apagado
    """
    try:
        # Crear tareas de apagado
        tasks = [
            asyncio.create_task(save_system_state()),
            asyncio.create_task(stop_background_services()),
            asyncio.create_task(cleanup_resources()),
        ]
        
        # Esperar con timeout
        done, pending = await asyncio.wait(
            tasks,
            timeout=timeout,
            return_when=asyncio.ALL_COMPLETED
        )
        
        # Cancelar tareas pendientes
        for task in pending:
            logger.warning(f"Cancelando tarea pendiente: {task.get_name()}")
            task.cancel()
            
    except Exception as e:
        logger.error(f"Error durante el apagado graceful: {e}")


async def shutdown_event(app: FastAPI) -> None:
    """
    Evento principal de apagado del servidor.
    
    Args:
        app: Instancia de FastAPI
    """
    try:
        logger.info("=" * 80)
        logger.info("🛑 NGX Agents API - Iniciando apagado del servidor...")
        logger.info("=" * 80)
        
        # Marcar como no listo para nuevas peticiones
        app.state.ready = False
        
        # 1. Guardar estado del sistema
        logger.info("\n💾 Fase 1: Guardando estado del sistema...")
        state_saved = await save_system_state()
        logger.info(f"Estado guardado: {state_saved}")
        
        # 2. Detener servicios en segundo plano
        logger.info("\n🛑 Fase 2: Deteniendo servicios...")
        await stop_background_services()
        
        # 3. Limpiar recursos
        logger.info("\n🧹 Fase 3: Limpiando recursos...")
        await cleanup_resources()
        
        # 4. Métricas finales
        logger.info("\n📊 Métricas finales del servidor:")
        if hasattr(app.state, "services_status"):
            logger.info(f"  - Servicios inicializados: {app.state.services_status}")
        if hasattr(metrics_collector, "get_summary"):
            summary = await metrics_collector.get_summary()
            logger.info(f"  - Resumen de métricas: {summary}")
        
        logger.info("\n✅ Servidor detenido correctamente")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"💥 Error durante el apagado: {e}")
        logger.error("Forzando apagado...")
        
    finally:
        # Asegurar que la telemetría se cierre
        try:
            shutdown_telemetry()
        except:
            pass