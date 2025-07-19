"""
Ejemplo de uso del sistema de caché avanzado en GENESIS
======================================================

Este archivo muestra cómo utilizar el sistema de caché multi-capa
(L1 Memory, L2 Redis, L3 Database) en los diferentes componentes.
"""

from typing import Any, Optional
from datetime import datetime
import asyncio

from core.advanced_cache_manager import (
    advanced_cache_manager,
    get_cached_value,
    set_cached_value,
    get_cache_analytics,
    CachePriority
)
from core.cache_strategies import (
    cached,
    standard_cache,
    swr_cache,
    tagged_cache,
    personalized_cache
)


# =============================================================================
# EJEMPLO 1: Uso básico del caché avanzado
# =============================================================================

async def ejemplo_basico():
    """Ejemplo básico de get/set en el caché"""
    
    # Guardar un valor en caché
    key = "user:123:profile"
    user_profile = {
        "id": "123",
        "name": "John Doe",
        "preferences": {"theme": "dark", "language": "es"}
    }
    
    # Set con TTL de 1 hora y prioridad alta
    success = await set_cached_value(
        key=key,
        value=user_profile,
        ttl=3600,  # 1 hora
        priority=CachePriority.HIGH
    )
    print(f"✅ Valor guardado en caché: {success}")
    
    # Obtener valor del caché
    cached_profile = await get_cached_value(key)
    print(f"📦 Valor obtenido del caché: {cached_profile}")
    
    # Ver analíticas del caché
    analytics = await get_cache_analytics()
    print(f"📊 Analíticas del caché: {analytics}")


# =============================================================================
# EJEMPLO 2: Uso con decoradores
# =============================================================================

@cached(ttl=1800, key_prefix="agent_response")
async def get_agent_response(agent_id: str, prompt: str) -> dict:
    """
    Función que simula una respuesta costosa de un agente.
    El decorador automáticamente cachea el resultado.
    """
    print(f"💰 Calculando respuesta costosa para {agent_id}...")
    # Simular procesamiento costoso
    await asyncio.sleep(2)
    
    return {
        "agent_id": agent_id,
        "response": f"Respuesta del agente {agent_id} a: {prompt}",
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# EJEMPLO 3: Caché personalizado por usuario
# =============================================================================

async def ejemplo_cache_personalizado():
    """Ejemplo de caché personalizado por usuario"""
    
    # Guardar preferencias personalizadas por usuario
    await personalized_cache.set(
        key="workout_plan",
        value={
            "exercises": ["squats", "bench_press", "deadlifts"],
            "sets": 4,
            "reps": 12
        },
        ttl=86400,  # 24 horas
        user_id="user_456"
    )
    
    # Obtener plan personalizado
    user_plan = await personalized_cache.get(
        key="workout_plan",
        user_id="user_456"
    )
    print(f"🏋️ Plan personalizado: {user_plan}")
    
    # También se puede usar por segmento
    await personalized_cache.set(
        key="nutrition_tips",
        value=["Eat protein", "Stay hydrated", "Avoid sugar"],
        ttl=3600,
        segment="athletes"
    )


# =============================================================================
# EJEMPLO 4: Caché con tags para invalidación grupal
# =============================================================================

async def ejemplo_cache_con_tags():
    """Ejemplo de caché con tags para invalidación masiva"""
    
    # Guardar varios artículos con tags
    articles = [
        {"id": "1", "title": "Nutrición para atletas", "tags": ["nutrition", "sports"]},
        {"id": "2", "title": "Rutinas de fuerza", "tags": ["training", "sports"]},
        {"id": "3", "title": "Suplementos básicos", "tags": ["nutrition", "supplements"]}
    ]
    
    for article in articles:
        await tagged_cache.set(
            key=f"article:{article['id']}",
            value=article,
            ttl=7200,
            tags=article["tags"]
        )
    
    # Invalidar todos los artículos con tag "nutrition"
    deleted_count = await tagged_cache.delete_by_tag("nutrition")
    print(f"🗑️ Artículos eliminados con tag 'nutrition': {deleted_count}")


# =============================================================================
# EJEMPLO 5: Stale-While-Revalidate para contenido dinámico
# =============================================================================

async def fetch_latest_metrics():
    """Función que obtiene métricas actualizadas (simulado)"""
    print("📊 Obteniendo métricas frescas...")
    await asyncio.sleep(1)  # Simular latencia
    return {
        "active_users": 1234,
        "requests_per_minute": 567,
        "timestamp": datetime.utcnow().isoformat()
    }

async def ejemplo_swr_cache():
    """Ejemplo de caché SWR para servir contenido stale mientras se actualiza"""
    
    key = "dashboard:metrics"
    
    # Primera vez - no hay caché, se obtiene fresco
    metrics = await swr_cache.get(key, revalidate_func=fetch_latest_metrics)
    if metrics is None:
        metrics = await fetch_latest_metrics()
        await swr_cache.set(key, metrics)
    
    print(f"📈 Métricas (primera vez): {metrics}")
    
    # Segunda vez - datos frescos
    await asyncio.sleep(1)
    metrics = await swr_cache.get(key, revalidate_func=fetch_latest_metrics)
    print(f"📈 Métricas (frescas): {metrics}")
    
    # Esperar hasta que los datos sean stale pero aún utilizables
    await asyncio.sleep(301)  # Más de 5 minutos (fresh_ttl)
    
    # Tercera vez - datos stale, pero se sirven mientras se revalidan
    metrics = await swr_cache.get(key, revalidate_func=fetch_latest_metrics)
    print(f"📈 Métricas (stale, revalidando): {metrics}")


# =============================================================================
# EJEMPLO 6: Uso en un router de FastAPI
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

router = APIRouter()

@router.get("/api/v1/cached/user/{user_id}")
async def get_user_profile_cached(user_id: str) -> Dict[str, Any]:
    """
    Endpoint que usa el caché avanzado para perfiles de usuario.
    
    El caché multi-capa funciona así:
    1. L1 (Memory): Respuesta inmediata para usuarios frecuentes
    2. L2 (Redis): Respuesta rápida para usuarios menos frecuentes
    3. L3 (Database): Respaldo persistente
    """
    cache_key = f"user_profile:{user_id}"
    
    # Intentar obtener del caché
    profile = await get_cached_value(cache_key)
    
    if profile:
        # Cache hit - agregar metadata
        profile["_cache_hit"] = True
        return profile
    
    # Cache miss - obtener de la base de datos
    # (aquí simularíamos la consulta a Supabase)
    profile = {
        "id": user_id,
        "name": f"Usuario {user_id}",
        "created_at": datetime.utcnow().isoformat(),
        "_cache_hit": False
    }
    
    # Guardar en caché con prioridad basada en actividad
    await set_cached_value(
        key=cache_key,
        value=profile,
        ttl=3600,  # 1 hora
        priority=CachePriority.NORMAL
    )
    
    return profile


@router.get("/api/v1/cached/agent/{agent_id}/capabilities")
@cached(ttl=7200, key_prefix="agent_capabilities")  # Cache por 2 horas
async def get_agent_capabilities(agent_id: str) -> Dict[str, Any]:
    """
    Endpoint con decorador de caché para capacidades de agentes.
    Las capacidades cambian poco, así que pueden cachearse por más tiempo.
    """
    # Este código solo se ejecuta en cache miss
    return {
        "agent_id": agent_id,
        "capabilities": ["chat", "analysis", "recommendations"],
        "version": "2.0",
        "last_updated": datetime.utcnow().isoformat()
    }


# =============================================================================
# EJEMPLO 7: Optimización del caché
# =============================================================================

async def ejemplo_optimizacion_cache():
    """Ejemplo de cómo optimizar la distribución del caché"""
    
    # Obtener estadísticas completas
    stats = await advanced_cache_manager.get_comprehensive_statistics()
    
    print("📊 Estadísticas del Sistema de Caché:")
    print(f"  - Hit ratio global: {stats['global_statistics']['global_hit_ratio']:.2%}")
    print(f"  - Tiempo de respuesta promedio: {stats['global_statistics']['average_response_time_ms']:.2f}ms")
    
    # Estadísticas por capa
    for layer, layer_stats in stats['layer_statistics'].items():
        print(f"\n  {layer.upper()}:")
        print(f"    - Entries: {layer_stats['entries']}")
        print(f"    - Hit ratio: {layer_stats['hit_ratio']:.2%}")
        print(f"    - Tamaño: {layer_stats['size_bytes'] / 1024 / 1024:.2f}MB")
    
    # Optimizar distribución automáticamente
    optimization_result = await advanced_cache_manager.optimize_cache_distribution()
    print(f"\n🔧 Optimización ejecutada: {optimization_result}")


# =============================================================================
# MAIN: Ejecutar ejemplos
# =============================================================================

async def main():
    """Ejecutar todos los ejemplos"""
    
    print("=" * 80)
    print("🚀 EJEMPLOS DE USO DEL SISTEMA DE CACHÉ AVANZADO")
    print("=" * 80)
    
    # Inicializar el sistema de caché
    from core.advanced_cache_manager import init_advanced_cache_manager
    await init_advanced_cache_manager()
    
    print("\n1️⃣ EJEMPLO BÁSICO")
    await ejemplo_basico()
    
    print("\n2️⃣ EJEMPLO CON DECORADORES")
    # Primera llamada - cache miss
    result1 = await get_agent_response("nexus", "¿Cómo mejorar mi rutina?")
    print(f"Primera llamada: {result1}")
    
    # Segunda llamada - cache hit
    result2 = await get_agent_response("nexus", "¿Cómo mejorar mi rutina?")
    print(f"Segunda llamada (desde caché): {result2}")
    
    print("\n3️⃣ EJEMPLO CACHÉ PERSONALIZADO")
    await ejemplo_cache_personalizado()
    
    print("\n4️⃣ EJEMPLO CACHÉ CON TAGS")
    await ejemplo_cache_con_tags()
    
    print("\n5️⃣ EJEMPLO STALE-WHILE-REVALIDATE")
    await ejemplo_swr_cache()
    
    print("\n7️⃣ EJEMPLO OPTIMIZACIÓN")
    await ejemplo_optimizacion_cache()
    
    print("\n✅ Todos los ejemplos completados!")


if __name__ == "__main__":
    asyncio.run(main())