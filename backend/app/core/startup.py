"""
Funciones de inicialización del servidor.

Este módulo contiene las funciones que se ejecutan al iniciar el servidor,
incluyendo inicialización de servicios, verificaciones de salud y configuración.
"""

import asyncio
import os
from typing import Dict, Any

from fastapi import FastAPI
from core.logging_config import configure_logging, get_logger
from core.google_credentials import init_google_credentials
from core.telemetry import initialize_telemetry
from core.settings import settings
from core.metrics import metrics_collector
from core.circuit_breaker import CircuitBreakerManager
from core.budget import budget_manager
from infrastructure.health import HealthCheck
from infrastructure.cache_warming import CacheWarmer
from infrastructure.background_tasks import BackgroundTaskManager
from infrastructure.monitoring import MonitoringService
from infrastructure.a2a_server import A2AServer
from clients.supabase_client import SupabaseClient
from agents.base.agent_registry import AgentRegistry
from infrastructure.adapters.state_manager_adapter import state_manager_adapter
from infrastructure.adapters.intent_analyzer_adapter import intent_analyzer_adapter
from core.advanced_cache_manager import init_advanced_cache_manager
from core.redis_pool import redis_pool_manager


# Configurar logger
logger = configure_logging(__name__)


async def initialize_core_services() -> Dict[str, Any]:
    """
    Inicializa los servicios principales del sistema.
    
    Returns:
        Dict con el estado de los servicios inicializados
    """
    services_status = {}
    
    try:
        # 1. Configurar credenciales de Google Cloud
        logger.info("🔐 Configurando credenciales de Google Cloud...")
        init_google_credentials()
        services_status["google_credentials"] = "initialized"
        
        # 2. Inicializar telemetría
        if settings.telemetry_enabled:
            logger.info("📊 Inicializando telemetría...")
            initialize_telemetry(
                service_name="ngx-agents-api",
                service_version="2.0.0",
                environment=settings.env,
            )
            services_status["telemetry"] = "enabled"
        else:
            logger.info("📊 Telemetría deshabilitada")
            services_status["telemetry"] = "disabled"
        
        # 3. Inicializar cliente de Supabase
        logger.info("🗄️ Inicializando conexión con Supabase...")
        supabase = SupabaseClient()
        await supabase.test_connection()
        services_status["supabase"] = "connected"
        
        # 4. Inicializar Redis y sistema de caché avanzado
        logger.info("🚀 Inicializando Redis y sistema de caché multi-capa...")
        try:
            # Inicializar pool de Redis
            redis_initialized = await redis_pool_manager.initialize()
            if redis_initialized:
                services_status["redis"] = "connected"
                logger.info("  ✅ Redis pool conectado")
                
                # Inicializar sistema de caché avanzado
                await init_advanced_cache_manager()
                services_status["advanced_cache"] = "initialized"
                logger.info("  ✅ Sistema de caché multi-capa (L1/L2/L3) inicializado")
            else:
                services_status["redis"] = "unavailable"
                services_status["advanced_cache"] = "degraded"
                logger.warning("  ⚠️ Redis no disponible - usando solo caché en memoria")
        except Exception as e:
            logger.error(f"  ❌ Error inicializando sistema de caché: {e}")
            services_status["redis"] = "error"
            services_status["advanced_cache"] = "error"
        
        # 5. Inicializar adaptadores
        logger.info("🔌 Inicializando adaptadores...")
        await state_manager_adapter.initialize()
        await intent_analyzer_adapter.initialize()
        services_status["adapters"] = "initialized"
        
        # 6. Configurar métricas
        logger.info("📈 Configurando sistema de métricas...")
        await metrics_collector.initialize()
        services_status["metrics"] = "initialized"
        
        # 7. Inicializar circuit breakers
        logger.info("🔒 Configurando circuit breakers...")
        circuit_manager = CircuitBreakerManager.get_instance()
        circuit_manager.initialize_default_breakers()
        services_status["circuit_breakers"] = "configured"
        
        # 8. Inicializar gestor de presupuestos
        if settings.enable_budgets:
            logger.info("💰 Inicializando gestor de presupuestos...")
            await budget_manager.initialize()
            services_status["budget_manager"] = "initialized"
        else:
            services_status["budget_manager"] = "disabled"
        
        return services_status
        
    except Exception as e:
        logger.error(f"Error durante la inicialización: {e}")
        services_status["error"] = str(e)
        raise


async def start_background_services() -> None:
    """
    Inicia los servicios en segundo plano.
    """
    try:
        # 1. Iniciar tareas en segundo plano
        logger.info("🔄 Iniciando tareas en segundo plano...")
        background_manager = BackgroundTaskManager()
        await background_manager.start()
        
        # 2. Calentar caché si está habilitado
        if hasattr(settings, "cache_warming_enabled") and settings.cache_warming_enabled:
            logger.info("🔥 Calentando caché...")
            cache_warmer = CacheWarmer()
            asyncio.create_task(cache_warmer.start())
        
        # 3. Iniciar monitoreo
        logger.info("👁️ Iniciando servicio de monitoreo...")
        monitoring = MonitoringService()
        await monitoring.start()
        
        # 4. Iniciar servidor A2A si está configurado
        if hasattr(settings, "a2a_enabled") and settings.a2a_enabled:
            logger.info("🔗 Iniciando servidor A2A...")
            a2a_server = A2AServer()
            asyncio.create_task(a2a_server.start())
            
    except Exception as e:
        logger.error(f"Error al iniciar servicios en segundo plano: {e}")
        # No lanzamos la excepción para no detener el servidor


async def verify_system_health() -> Dict[str, Any]:
    """
    Verifica la salud del sistema antes de aceptar tráfico.
    
    Returns:
        Dict con el estado de salud de cada componente
    """
    health_check = HealthCheck()
    
    # Verificar componentes críticos
    checks = {
        "database": await health_check.check_database(),
        "vertex_ai": await health_check.check_vertex_ai(),
        "redis": await health_check.check_redis(),
        "agents": await health_check.check_agents(),
    }
    
    # Registrar resultados
    for component, result in checks.items():
        status, message = result
        if status:
            logger.info(f"✅ {component}: {message}")
        else:
            logger.warning(f"⚠️ {component}: {message}")
    
    return checks


async def register_agents() -> None:
    """
    Registra todos los agentes disponibles en el sistema.
    """
    try:
        logger.info("🤖 Registrando agentes...")
        registry = AgentRegistry.get_instance()
        
        # Lista de agentes a registrar
        agents_to_register = [
            "orchestrator",
            "elite_training_strategist",
            "precision_nutrition_architect",
            "progress_tracker",
            "motivation_behavior_coach",
            "female_wellness_coach",
            "nova_biohacking_innovator",
            "wave_performance_analytics",
            "code_genetic_specialist",
        ]
        
        for agent_id in agents_to_register:
            try:
                # Importar dinámicamente el agente
                module = __import__(f"agents.{agent_id}.agent", fromlist=["get_agent_instance"])
                if hasattr(module, "get_agent_instance"):
                    agent_instance = module.get_agent_instance()
                    registry.register(agent_id, agent_instance)
                    logger.info(f"  ✅ Registrado: {agent_id}")
            except Exception as e:
                logger.error(f"  ❌ Error al registrar {agent_id}: {e}")
                
        logger.info(f"📊 Total agentes registrados: {len(registry.list_agents())}")
        
    except Exception as e:
        logger.error(f"Error al registrar agentes: {e}")


async def startup_event(app: FastAPI) -> None:
    """
    Evento principal de inicio del servidor.
    
    Args:
        app: Instancia de FastAPI
    """
    try:
        logger.info("=" * 80)
        logger.info("🚀 NGX Agents API v2.0.0 - Iniciando servidor...")
        logger.info(f"📍 Entorno: {settings.env}")
        logger.info(f"🔧 Debug: {settings.debug}")
        logger.info("=" * 80)
        
        # 1. Inicializar servicios principales
        logger.info("\n📦 Fase 1: Inicializando servicios principales...")
        services_status = await initialize_core_services()
        app.state.services_status = services_status
        
        # 2. Verificar salud del sistema
        logger.info("\n🏥 Fase 2: Verificando salud del sistema...")
        health_status = await verify_system_health()
        app.state.health_status = health_status
        
        # 3. Registrar agentes
        logger.info("\n🤖 Fase 3: Registrando agentes...")
        await register_agents()
        
        # 4. Iniciar servicios en segundo plano
        logger.info("\n🔄 Fase 4: Iniciando servicios en segundo plano...")
        await start_background_services()
        
        # 5. Configuración final
        logger.info("\n✅ Servidor iniciado correctamente")
        logger.info(f"📡 API disponible en: http://{settings.host}:{settings.port}")
        logger.info(f"📚 Documentación en: http://{settings.host}:{settings.port}/docs")
        logger.info("=" * 80)
        
        # Marcar como listo
        app.state.ready = True
        
    except Exception as e:
        logger.error(f"💥 Error crítico durante el inicio: {e}")
        logger.error("El servidor se iniciará en modo degradado")
        app.state.ready = False
        app.state.startup_error = str(e)