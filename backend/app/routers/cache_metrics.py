"""
Router para métricas del Memory Cache Optimizer - FASE 12 QUICK WIN #3

Proporciona endpoints para monitorear el rendimiento del sistema de caché
y obtener métricas en tiempo real de la mejora en tiempo de respuesta.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, List, Optional
import time

from core.logging_config import get_logger
from core.auth import get_current_user
from core.memory_cache_optimizer import (
    memory_cache,
    cache_stats,
    cache_invalidate,
    CachePriority
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/cache-metrics",
    tags=["cache-metrics", "monitoring", "fase12"]
)


@router.get("/", response_model=Dict[str, Any])
async def get_cache_metrics(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene métricas del Memory Cache Optimizer.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con métricas de rendimiento del sistema de caché
    """
    try:
        metrics = cache_stats()
        
        # Agregar información adicional
        response = {
            "status": "success",
            "metrics": metrics,
            "description": "FASE 12 QUICK WIN #3: Memory Cache Optimizer Metrics",
            "expected_improvement": "25% reduction in response time",
            "actual_improvement": _calculate_response_time_improvement(metrics)
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de caché: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=Dict[str, Any])
async def get_cache_summary(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene resumen ejecutivo del rendimiento del caché.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con resumen de rendimiento
    """
    try:
        metrics = cache_stats()
        
        # Calcular mejora en tiempo de respuesta
        avg_hit_time = metrics.get('avg_hit_time_ms', 0)
        avg_miss_time = metrics.get('avg_miss_time_ms', 0)
        hit_rate = float(metrics.get('hit_rate', '0').rstrip('%'))
        
        if avg_miss_time > 0:
            time_saved_per_hit = avg_miss_time - avg_hit_time
            overall_time_saved = (time_saved_per_hit * hit_rate / 100)
            response_time_improvement = (overall_time_saved / avg_miss_time * 100) if avg_miss_time > 0 else 0
        else:
            response_time_improvement = 0
        
        # Determinar estado de rendimiento
        if hit_rate >= 80:
            performance_status = "excellent"
        elif hit_rate >= 60:
            performance_status = "good"
        elif hit_rate >= 40:
            performance_status = "moderate"
        else:
            performance_status = "needs_improvement"
        
        summary = {
            "status": "active",
            "performance_status": performance_status,
            "hit_rate_percent": hit_rate,
            "response_time_improvement_percent": round(response_time_improvement, 2),
            "average_hit_time_ms": round(avg_hit_time, 2),
            "average_miss_time_ms": round(avg_miss_time, 2),
            "cache_utilization_percent": metrics.get('utilization', '0%'),
            "total_entries": metrics.get('entry_count', 0),
            "memory_used_mb": round(metrics.get('total_size_mb', 0), 2),
            "quick_win_target": "25% response time reduction",
            "current_achievement": f"{round(response_time_improvement, 1)}% response time reduction",
            "efficiency_rating": _calculate_efficiency_rating(hit_rate, response_time_improvement)
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generando resumen de caché: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-entries", response_model=Dict[str, Any])
async def get_top_cache_entries(
    limit: int = 10,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene las entradas más accedidas del caché.
    
    Args:
        limit: Número máximo de entradas a devolver
        current_user: Usuario autenticado
        
    Returns:
        Dict con las top entradas del caché
    """
    try:
        # Obtener todas las entradas
        entries = []
        for key, entry in memory_cache._cache.items():
            entries.append({
                "key": key,
                "access_count": entry.access_count,
                "size_bytes": entry.size_bytes,
                "age_seconds": time.time() - entry.created_at,
                "last_accessed_seconds_ago": time.time() - entry.last_accessed,
                "priority": entry.priority.name
            })
        
        # Ordenar por accesos
        entries.sort(key=lambda x: x['access_count'], reverse=True)
        
        return {
            "top_entries": entries[:limit],
            "total_entries": len(entries)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo top entradas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate", response_model=Dict[str, str])
async def invalidate_cache_entry(
    key: str = Body(..., description="Clave a invalidar"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Invalida una entrada específica del caché.
    
    Args:
        key: Clave de la entrada a invalidar
        current_user: Usuario autenticado
        
    Returns:
        Dict con estado de la operación
    """
    try:
        success = cache_invalidate(key)
        
        if success:
            return {
                "status": "success",
                "message": f"Entrada '{key}' invalidada correctamente"
            }
        else:
            return {
                "status": "not_found",
                "message": f"Entrada '{key}' no encontrada en caché"
            }
        
    except Exception as e:
        logger.error(f"Error invalidando entrada: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invalidate-pattern", response_model=Dict[str, Any])
async def invalidate_cache_pattern(
    pattern: str = Body(..., description="Patrón regex para invalidar"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Invalida todas las entradas que coincidan con un patrón.
    
    Args:
        pattern: Patrón regex para buscar claves
        current_user: Usuario autenticado
        
    Returns:
        Dict con número de entradas invalidadas
    """
    try:
        count = memory_cache.invalidate_pattern(pattern)
        
        return {
            "status": "success",
            "pattern": pattern,
            "invalidated_count": count,
            "message": f"Invalidadas {count} entradas con patrón '{pattern}'"
        }
        
    except Exception as e:
        logger.error(f"Error invalidando patrón: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear", response_model=Dict[str, str])
async def clear_cache(
    current_user: str = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Limpia completamente el caché.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con estado de la operación
    """
    try:
        # Solo permitir en desarrollo
        from core.settings import settings
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=403,
                detail="Clear de caché no permitido en producción"
            )
        
        memory_cache.clear()
        
        return {
            "status": "success",
            "message": "Caché limpiado completamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error limpiando caché: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategy-info", response_model=Dict[str, Any])
async def get_cache_strategy_info(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene información sobre la estrategia de caché actual.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con información de estrategia
    """
    try:
        strategy = memory_cache.strategy
        
        strategy_info = {
            "current_strategy": strategy.value,
            "strategy_description": _get_strategy_description(strategy.value),
            "configuration": {
                "max_size_mb": memory_cache.max_size_bytes / (1024 * 1024),
                "default_ttl_seconds": memory_cache.default_ttl,
                "prewarming_enabled": memory_cache.enable_prewarming
            },
            "recommendations": _get_strategy_recommendations(strategy.value, cache_stats())
        }
        
        return strategy_info
        
    except Exception as e:
        logger.error(f"Error obteniendo info de estrategia: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def get_cache_health() -> Dict[str, Any]:
    """
    Verifica el estado de salud del sistema de caché.
    
    Returns:
        Dict con estado de salud
    """
    try:
        metrics = cache_stats()
        
        # Verificar salud basada en métricas
        hit_rate = float(metrics.get('hit_rate', '0').rstrip('%'))
        utilization = float(metrics.get('utilization', '0').rstrip('%'))
        
        is_healthy = (
            hit_rate > 20 and  # Al menos 20% de hit rate
            utilization < 95   # No está al límite de capacidad
        )
        
        warnings = []
        if hit_rate < 40:
            warnings.append("Hit rate bajo - considerar precalentamiento")
        if utilization > 80:
            warnings.append("Alta utilización de memoria - considerar aumentar límite")
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "cache_enabled": True,
            "hit_rate_percent": hit_rate,
            "memory_utilization_percent": utilization,
            "response_time_savings_ms": metrics.get('avg_miss_time_ms', 0) - metrics.get('avg_hit_time_ms', 0),
            "warnings": warnings
        }
        
    except Exception as e:
        logger.error(f"Error verificando salud del caché: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# Funciones auxiliares

def _calculate_response_time_improvement(metrics: Dict[str, Any]) -> str:
    """Calcula la mejora en tiempo de respuesta."""
    avg_hit_time = metrics.get('avg_hit_time_ms', 0)
    avg_miss_time = metrics.get('avg_miss_time_ms', 0)
    hit_rate = float(metrics.get('hit_rate', '0').rstrip('%'))
    
    if avg_miss_time > 0 and hit_rate > 0:
        time_saved_per_hit = avg_miss_time - avg_hit_time
        overall_improvement = (time_saved_per_hit * hit_rate / 100) / avg_miss_time * 100
        return f"{overall_improvement:.1f}% reduction"
    
    return "0% reduction"


def _calculate_efficiency_rating(hit_rate: float, time_improvement: float) -> str:
    """Calcula calificación de eficiencia del caché."""
    score = 0
    
    # Factor 1: Hit rate (0-50 puntos)
    score += min(50, hit_rate * 0.5)
    
    # Factor 2: Mejora en tiempo (0-50 puntos)
    score += min(50, time_improvement * 2)
    
    # Determinar calificación
    if score >= 90:
        return "A+ (Excelente)"
    elif score >= 75:
        return "A (Muy Bueno)"
    elif score >= 60:
        return "B+ (Bueno)"
    elif score >= 45:
        return "B (Satisfactorio)"
    elif score >= 30:
        return "C (Moderado)"
    else:
        return "D (Necesita Mejora)"


def _get_strategy_description(strategy: str) -> str:
    """Obtiene descripción de la estrategia de caché."""
    descriptions = {
        "lru": "Least Recently Used - Evicta las entradas menos recientemente usadas",
        "lfu": "Least Frequently Used - Evicta las entradas menos frecuentemente usadas",
        "ttl": "Time To Live - Evicta entradas basándose en su antigüedad",
        "adaptive": "Adaptativo - Combina múltiples factores para decisiones inteligentes"
    }
    return descriptions.get(strategy, "Estrategia desconocida")


def _get_strategy_recommendations(strategy: str, metrics: Dict[str, Any]) -> List[str]:
    """Genera recomendaciones basadas en la estrategia y métricas."""
    recommendations = []
    
    hit_rate = float(metrics.get('hit_rate', '0').rstrip('%'))
    
    if hit_rate < 50:
        recommendations.append(
            "Hit rate bajo - considerar precalentamiento de entradas frecuentes"
        )
    
    if strategy != "adaptive" and hit_rate < 70:
        recommendations.append(
            "Considerar cambiar a estrategia 'adaptive' para mejor rendimiento"
        )
    
    utilization = float(metrics.get('utilization', '0').rstrip('%'))
    if utilization > 80:
        recommendations.append(
            "Alta utilización de memoria - considerar aumentar el límite de caché"
        )
    
    if utilization < 20 and hit_rate > 80:
        recommendations.append(
            "Baja utilización con alto hit rate - el caché está bien dimensionado"
        )
    
    return recommendations