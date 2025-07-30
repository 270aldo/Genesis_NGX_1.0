"""
Router para métricas del Query Batch Processor - FASE 12 QUICK WIN #1

Proporciona endpoints para monitorear el rendimiento del sistema de batching
y obtener métricas en tiempo real de las optimizaciones.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from core.logging_config import get_logger
from core.auth import get_current_user

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/batch-metrics",
    tags=["batch-metrics", "monitoring", "fase12"]
)


@router.get("/", response_model=Dict[str, Any])
async def get_batch_metrics(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene métricas del Query Batch Processor.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con métricas de rendimiento del batch processor
    """
    try:
        from clients.supabase_client import get_batch_metrics
        
        metrics = await get_batch_metrics()
        
        if "error" in metrics:
            raise HTTPException(status_code=503, detail=metrics["error"])
        
        # Agregar información adicional
        response = {
            "status": "success",
            "metrics": metrics,
            "description": "FASE 12 QUICK WIN #1: Query Batching Metrics",
            "expected_improvement": "40% reduction in DB calls"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-summary", response_model=Dict[str, Any])
async def get_performance_summary(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene resumen de rendimiento del batch processor.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con resumen de rendimiento
    """
    try:
        from clients.supabase_client import get_batch_metrics
        
        metrics = await get_batch_metrics()
        
        if "error" in metrics:
            return {
                "status": "unavailable",
                "message": "Batch processor no disponible",
                "performance_impact": "N/A"
            }
        
        # Calcular resumen de rendimiento
        total_queries = metrics.get('total_queries', 0)
        batch_savings = metrics.get('batch_savings_percent', 0)
        avg_batch_size = metrics.get('avg_batch_size', 0)
        
        if total_queries > 0:
            performance_status = "excellent" if batch_savings > 35 else "good" if batch_savings > 20 else "moderate"
            
            summary = {
                "status": "active",
                "performance_status": performance_status,
                "total_queries_processed": total_queries,
                "database_calls_saved_percent": round(batch_savings, 2),
                "average_batch_size": round(avg_batch_size, 2),
                "efficiency_rating": _calculate_efficiency_rating(batch_savings, avg_batch_size),
                "quick_win_target": "40% DB call reduction",
                "current_achievement": f"{round(batch_savings, 1)}% DB call reduction"
            }
        else:
            summary = {
                "status": "initializing",
                "performance_status": "pending",
                "message": "Waiting for queries to process",
                "quick_win_target": "40% DB call reduction"
            }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de rendimiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-metrics", response_model=Dict[str, str])
async def reset_batch_metrics(
    current_user: str = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Reinicia las métricas del batch processor (solo para testing).
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con estado de la operación
    """
    try:
        # Esta operación solo está disponible en desarrollo
        from core.settings_lazy import settings
        
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=403, 
                detail="Reset de métricas no permitido en producción"
            )
        
        from core.query_batch_processor import batch_processor
        
        # Reiniciar métricas
        batch_processor.metrics = {
            'total_queries': 0,
            'batched_queries': 0,
            'individual_queries': 0,
            'batch_savings_percent': 0.0,
            'avg_batch_size': 0.0,
            'last_flush_time': batch_processor.metrics['last_flush_time']
        }
        
        logger.info("Métricas del batch processor reiniciadas")
        
        return {
            "status": "success",
            "message": "Métricas reiniciadas correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error reiniciando métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _calculate_efficiency_rating(savings_percent: float, avg_batch_size: float) -> str:
    """
    Calcula calificación de eficiencia basada en métricas.
    
    Args:
        savings_percent: Porcentaje de ahorro en DB calls
        avg_batch_size: Tamaño promedio de batch
        
    Returns:
        Calificación de eficiencia
    """
    # Algoritmo de calificación
    score = 0
    
    # Factor 1: Ahorro en DB calls (0-50 puntos)
    score += min(50, savings_percent * 1.25)
    
    # Factor 2: Tamaño de batch promedio (0-30 puntos)
    if avg_batch_size >= 10:
        score += 30
    elif avg_batch_size >= 5:
        score += 20
    elif avg_batch_size >= 2:
        score += 10
    
    # Factor 3: Consistencia (0-20 puntos)
    if savings_percent > 30 and avg_batch_size > 3:
        score += 20
    elif savings_percent > 20 and avg_batch_size > 2:
        score += 10
    
    # Determinar calificación
    if score >= 85:
        return "A+ (Excelente)"
    elif score >= 70:
        return "A (Muy Bueno)"
    elif score >= 55:
        return "B+ (Bueno)"
    elif score >= 40:
        return "B (Satisfactorio)"
    elif score >= 25:
        return "C (Moderado)"
    else:
        return "D (Necesita Mejora)"


@router.get("/health", response_model=Dict[str, Any])
async def get_batch_processor_health() -> Dict[str, Any]:
    """
    Verifica el estado de salud del batch processor.
    
    Returns:
        Dict con estado de salud
    """
    try:
        from core.query_batch_processor import batch_processor
        
        metrics = batch_processor.get_metrics()
        
        # Verificar estado de salud
        is_healthy = (
            batch_processor._running and
            metrics['total_queries'] >= 0 and
            len(batch_processor.pending_queries) < 1000  # Límite de seguridad
        )
        
        health_status = {
            "status": "healthy" if is_healthy else "unhealthy",
            "running": batch_processor._running,
            "pending_batches": len(batch_processor.pending_queries),
            "total_pending_queries": sum(len(bg.queries) for bg in batch_processor.pending_queries.values()),
            "uptime_seconds": metrics.get('uptime_seconds', 0),
            "last_check": "2025-06-09T22:00:00Z"
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error verificando salud del batch processor: {e}")
        return {
            "status": "error",
            "error": str(e),
            "last_check": "2025-06-09T22:00:00Z"
        }