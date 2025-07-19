"""
Router para métricas del Response Compression - FASE 12 QUICK WIN #2

Proporciona endpoints para monitorear el rendimiento del sistema de compresión
y obtener métricas en tiempo real del ahorro de ancho de banda.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, Optional
import json

from core.logging_config import get_logger
from core.auth import get_current_user
from core.response_compression import (
    get_compression_metrics,
    estimate_bandwidth_savings,
    response_compressor,
    CompressionType
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/v1/compression-metrics",
    tags=["compression-metrics", "monitoring", "fase12"]
)


@router.get("/", response_model=Dict[str, Any])
async def get_metrics(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene métricas del sistema de compresión de respuestas.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con métricas de rendimiento del sistema de compresión
    """
    try:
        metrics = get_compression_metrics()
        
        # Agregar información adicional
        response = {
            "status": "success",
            "metrics": metrics,
            "description": "FASE 12 QUICK WIN #2: Response Compression Metrics",
            "expected_improvement": "60% reduction in bandwidth",
            "actual_improvement": f"{metrics.get('bandwidth_saved_percent', 0):.1f}% reduction"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de compresión: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=Dict[str, Any])
async def get_compression_summary(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene resumen ejecutivo del rendimiento de compresión.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con resumen de rendimiento
    """
    try:
        metrics = get_compression_metrics()
        
        # Calcular estadísticas adicionales
        total_mb_saved = metrics.get('total_bytes_original', 0) - metrics.get('total_bytes_compressed', 0)
        total_mb_saved = total_mb_saved / (1024 * 1024)  # Convertir a MB
        
        # Determinar estado de rendimiento
        bandwidth_saved = metrics.get('bandwidth_saved_percent', 0)
        if bandwidth_saved >= 55:
            performance_status = "excellent"
        elif bandwidth_saved >= 40:
            performance_status = "good"
        elif bandwidth_saved >= 25:
            performance_status = "moderate"
        else:
            performance_status = "needs_improvement"
        
        summary = {
            "status": "active",
            "performance_status": performance_status,
            "total_compressions": metrics.get('total_compressions', 0),
            "bandwidth_saved_percent": round(bandwidth_saved, 2),
            "total_mb_saved": round(total_mb_saved, 2),
            "average_compression_time_ms": round(metrics.get('average_compression_time', 0) * 1000, 2),
            "cache_hit_rate_percent": round(metrics.get('cache_hit_rate', 0), 2),
            "most_used_algorithm": _get_most_used_algorithm(metrics.get('algorithms_used', {})),
            "quick_win_target": "60% bandwidth reduction",
            "current_achievement": f"{round(bandwidth_saved, 1)}% bandwidth reduction",
            "efficiency_rating": _calculate_efficiency_rating(bandwidth_saved, metrics.get('average_compression_time', 0))
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generando resumen de compresión: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-compression", response_model=Dict[str, Any])
async def test_compression(
    data: Dict[str, Any],
    algorithm: Optional[str] = Query(None, description="Algoritmo específico: gzip, br, zstd"),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Prueba la compresión con datos específicos.
    
    Args:
        data: Datos para comprimir
        algorithm: Algoritmo específico a usar (opcional)
        current_user: Usuario autenticado
        
    Returns:
        Dict con resultados de la prueba
    """
    try:
        # Convertir datos a JSON string
        json_data = json.dumps(data, separators=(',', ':'))
        original_size = len(json_data.encode('utf-8'))
        
        # Determinar algoritmo
        force_algorithm = None
        if algorithm:
            algorithm_map = {
                "gzip": CompressionType.GZIP,
                "br": CompressionType.BROTLI,
                "zstd": CompressionType.ZSTD
            }
            force_algorithm = algorithm_map.get(algorithm.lower())
        
        # Comprimir
        compressed_data, used_algorithm = response_compressor.compress_response(
            data,
            accept_encoding="gzip, br, zstd",
            force_algorithm=force_algorithm
        )
        
        compressed_size = len(compressed_data)
        
        # Calcular estimaciones
        savings = estimate_bandwidth_savings(original_size, compressed_size)
        
        return {
            "test_results": {
                "original_size_bytes": original_size,
                "compressed_size_bytes": compressed_size,
                "algorithm_used": used_algorithm.value,
                "compression_ratio": savings['compression_ratio'],
                "bandwidth_saved_percent": savings['savings_percent'],
                "size_reduction": f"{savings['savings_bytes']} bytes"
            },
            "performance_impact": savings['bandwidth_impact'],
            "recommendation": _get_compression_recommendation(savings['savings_percent'])
        }
        
    except Exception as e:
        logger.error(f"Error en test de compresión: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/algorithm-stats", response_model=Dict[str, Any])
async def get_algorithm_statistics(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Obtiene estadísticas detalladas por algoritmo de compresión.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con estadísticas por algoritmo
    """
    try:
        metrics = get_compression_metrics()
        algorithms_used = metrics.get('algorithms_used', {})
        
        # Calcular estadísticas por algoritmo
        total_uses = sum(algorithms_used.values())
        
        algorithm_stats = {}
        for algo, count in algorithms_used.items():
            if count > 0:
                percentage = (count / total_uses * 100) if total_uses > 0 else 0
                algorithm_stats[algo] = {
                    "usage_count": count,
                    "usage_percent": round(percentage, 2),
                    "description": _get_algorithm_description(algo)
                }
        
        return {
            "total_compressions": total_uses,
            "algorithms": algorithm_stats,
            "recommendations": _get_algorithm_recommendations(algorithm_stats)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de algoritmos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache", response_model=Dict[str, str])
async def clear_compression_cache(
    current_user: str = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Limpia el caché de respuestas comprimidas.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Dict con estado de la operación
    """
    try:
        response_compressor.clear_cache()
        
        return {
            "status": "success",
            "message": "Caché de compresión limpiado correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error limpiando caché: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def get_compression_health() -> Dict[str, Any]:
    """
    Verifica el estado de salud del sistema de compresión.
    
    Returns:
        Dict con estado de salud
    """
    try:
        metrics = get_compression_metrics()
        
        # Verificar salud basada en métricas
        is_healthy = (
            metrics.get('total_compressions', 0) >= 0 and
            metrics.get('average_compression_time', 1) < 0.1  # < 100ms promedio
        )
        
        # Verificar algoritmos disponibles
        available_algorithms = []
        if response_compressor._available_algorithms.get(CompressionType.GZIP):
            available_algorithms.append("gzip")
        if response_compressor._available_algorithms.get(CompressionType.BROTLI):
            available_algorithms.append("brotli")
        if response_compressor._available_algorithms.get(CompressionType.ZSTD):
            available_algorithms.append("zstandard")
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "available_algorithms": available_algorithms,
            "cache_enabled": response_compressor.cache_enabled,
            "cache_size": len(response_compressor._cache),
            "average_compression_time_ms": round(metrics.get('average_compression_time', 0) * 1000, 2),
            "bandwidth_savings_percent": round(metrics.get('bandwidth_saved_percent', 0), 2)
        }
        
    except Exception as e:
        logger.error(f"Error verificando salud: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


def _get_most_used_algorithm(algorithms_used: Dict[str, int]) -> str:
    """Obtiene el algoritmo más usado."""
    if not algorithms_used:
        return "none"
    
    # Excluir 'none' del análisis
    filtered = {k: v for k, v in algorithms_used.items() if k != "none"}
    if not filtered:
        return "none"
    
    return max(filtered, key=filtered.get)


def _calculate_efficiency_rating(bandwidth_saved: float, avg_time: float) -> str:
    """Calcula calificación de eficiencia."""
    score = 0
    
    # Factor 1: Ahorro de ancho de banda (0-60 puntos)
    score += min(60, bandwidth_saved)
    
    # Factor 2: Velocidad de compresión (0-40 puntos)
    if avg_time < 0.001:  # < 1ms
        score += 40
    elif avg_time < 0.005:  # < 5ms
        score += 30
    elif avg_time < 0.01:  # < 10ms
        score += 20
    elif avg_time < 0.05:  # < 50ms
        score += 10
    
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


def _get_compression_recommendation(savings_percent: float) -> str:
    """Genera recomendación basada en ahorro."""
    if savings_percent >= 60:
        return "✅ Excelente compresión. Objetivo de 60% alcanzado."
    elif savings_percent >= 45:
        return "👍 Buena compresión. Cerca del objetivo de 60%."
    elif savings_percent >= 30:
        return "⚡ Compresión moderada. Considerar algoritmos más agresivos."
    else:
        return "⚠️ Compresión baja. Verificar tipo de datos y algoritmos."


def _get_algorithm_description(algorithm: str) -> str:
    """Obtiene descripción del algoritmo."""
    descriptions = {
        "none": "Sin compresión (datos muy pequeños)",
        "gzip": "Compresión estándar, rápida y ampliamente soportada",
        "br": "Brotli - Mayor compresión, ideal para datos grandes",
        "zstd": "Zstandard - Balance óptimo entre velocidad y compresión"
    }
    return descriptions.get(algorithm, "Algoritmo desconocido")


def _get_algorithm_recommendations(stats: Dict[str, Any]) -> list:
    """Genera recomendaciones basadas en uso de algoritmos."""
    recommendations = []
    
    # Si gzip es usado más del 80%, sugerir otros algoritmos
    gzip_usage = stats.get("gzip", {}).get("usage_percent", 0)
    if gzip_usage > 80:
        recommendations.append(
            "Considerar habilitar Brotli o Zstandard para mejor compresión en clientes modernos"
        )
    
    # Si no se usa brotli pero está disponible
    if "br" not in stats and response_compressor._available_algorithms.get(CompressionType.BROTLI):
        recommendations.append(
            "Brotli está disponible pero no se está usando. Verificar Accept-Encoding de clientes"
        )
    
    return recommendations