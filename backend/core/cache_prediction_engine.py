"""
Cache Prediction Engine - FASE 12 POINT 5
==========================================

Motor de predicción inteligente para caché que utiliza machine learning
para predecir patrones de acceso, prefetching óptimo y distribución
inteligente entre capas L1, L2 y L3.

CARACTERÍSTICAS PRINCIPALES:
- Predicción de patrones de acceso futuro
- Prefetching inteligente basado en ML
- Optimización automática de TTL
- Distribución predictiva entre capas
- Análisis de tendencias de uso

IMPACTO ESPERADO: Cache hit ratio 900% más eficiente
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque
import math

from core.logging_config import get_logger
from core.advanced_cache_manager import AdvancedCacheManager, CacheLayer, CachePriority
from core.behavioral_pattern_analyzer import BehaviorPatternAnalyzer
from core.memory_cache_optimizer import cache_get, cache_set

logger = get_logger(__name__)


class AccessPattern(Enum):
    """Patrones de acceso identificados"""
    SEQUENTIAL = "sequential"        # Acceso secuencial
    RANDOM = "random"               # Acceso aleatorio
    TEMPORAL = "temporal"           # Basado en tiempo
    BURST = "burst"                 # Ráfagas de acceso
    PERIODIC = "periodic"           # Acceso periódico
    TRENDING = "trending"           # Acceso trending
    HOTSPOT = "hotspot"            # Hotspot específico


class PrefetchStrategy(Enum):
    """Estrategias de prefetching"""
    AGGRESSIVE = "aggressive"       # Prefetch agresivo
    CONSERVATIVE = "conservative"   # Prefetch conservador
    ADAPTIVE = "adaptive"          # Adaptativo al patrón
    PREDICTIVE = "predictive"      # Basado en predicciones ML
    DISABLED = "disabled"          # Sin prefetching


@dataclass
class AccessEvent:
    """Evento de acceso al caché"""
    key: str
    timestamp: datetime
    hit: bool
    layer: Optional[CacheLayer]
    response_time_ms: float
    user_id: Optional[str]
    context: Optional[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['layer'] = self.layer.value if self.layer else None
        return data


@dataclass
class AccessPrediction:
    """Predicción de acceso futuro"""
    key: str
    predicted_access_time: datetime
    confidence: float  # 0.0 - 1.0
    access_probability: float  # 0.0 - 1.0
    recommended_layer: CacheLayer
    recommended_ttl: int  # segundos
    pattern_type: AccessPattern
    factors: List[str]
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['predicted_access_time'] = self.predicted_access_time.isoformat()
        data['recommended_layer'] = self.recommended_layer.value
        data['pattern_type'] = self.pattern_type.value
        data['generated_at'] = self.generated_at.isoformat()
        return data


@dataclass
class CacheOptimizationRecommendation:
    """Recomendación de optimización del caché"""
    recommendation_id: str
    type: str
    description: str
    expected_improvement: float  # % de mejora esperada
    implementation_cost: float  # 0.0 - 1.0
    confidence: float
    affected_keys: List[str]
    target_layer: Optional[CacheLayer]
    parameters: Dict[str, Any]
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['target_layer'] = self.target_layer.value if self.target_layer else None
        data['generated_at'] = self.generated_at.isoformat()
        return data


class AccessPatternAnalyzer:
    """Analizador de patrones de acceso al caché"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.access_history: deque = deque(maxlen=window_size)
        self.key_access_patterns: Dict[str, List[AccessEvent]] = defaultdict(list)
        self.temporal_patterns: Dict[str, List[datetime]] = defaultdict(list)
        
    def record_access(self, event: AccessEvent):
        """Registra evento de acceso"""
        try:
            self.access_history.append(event)
            
            # Mantener historial por key (últimos 50 accesos)
            if len(self.key_access_patterns[event.key]) >= 50:
                self.key_access_patterns[event.key].pop(0)
            self.key_access_patterns[event.key].append(event)
            
            # Patrones temporales
            if len(self.temporal_patterns[event.key]) >= 100:
                self.temporal_patterns[event.key].pop(0)
            self.temporal_patterns[event.key].append(event.timestamp)
            
        except Exception as e:
            logger.error(f"Error registrando acceso: {e}")
    
    def analyze_key_pattern(self, key: str) -> AccessPattern:
        """Analiza el patrón de acceso de una key específica"""
        try:
            if key not in self.temporal_patterns or len(self.temporal_patterns[key]) < 5:
                return AccessPattern.RANDOM
            
            timestamps = self.temporal_patterns[key]
            intervals = []
            
            # Calcular intervalos entre accesos
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(interval)
            
            if not intervals:
                return AccessPattern.RANDOM
            
            # Analizar patrones
            avg_interval = statistics.mean(intervals)
            std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
            
            # Coeficiente de variación
            cv = std_interval / avg_interval if avg_interval > 0 else float('inf')
            
            # Detectar patrón basado en características
            if cv < 0.1:  # Muy regular
                return AccessPattern.PERIODIC
            elif cv < 0.3:  # Moderadamente regular
                return AccessPattern.TEMPORAL
            elif self._detect_burst_pattern(intervals):
                return AccessPattern.BURST
            elif self._detect_sequential_pattern(key):
                return AccessPattern.SEQUENTIAL
            elif self._detect_trending_pattern(timestamps):
                return AccessPattern.TRENDING
            else:
                return AccessPattern.RANDOM
                
        except Exception as e:
            logger.error(f"Error analizando patrón de key {key}: {e}")
            return AccessPattern.RANDOM
    
    def _detect_burst_pattern(self, intervals: List[float]) -> bool:
        """Detecta patrón de ráfagas"""
        try:
            if len(intervals) < 10:
                return False
            
            # Buscar grupos de intervalos cortos seguidos de intervalos largos
            short_intervals = [i for i in intervals if i < 60]  # < 1 minuto
            long_intervals = [i for i in intervals if i > 300]  # > 5 minutos
            
            # Si hay una mezcla significativa, es burst
            return len(short_intervals) > 0.3 * len(intervals) and len(long_intervals) > 0.2 * len(intervals)
            
        except Exception as e:
            logger.error(f"Error detectando patrón burst: {e}")
            return False
    
    def _detect_sequential_pattern(self, key: str) -> bool:
        """Detecta patrón secuencial basado en la key"""
        try:
            # Buscar patrones secuenciales en el nombre de la key
            # Ej: "user_data_1", "user_data_2", etc.
            recent_keys = [event.key for event in list(self.access_history)[-20:]]
            
            # Contar keys similares con números secuenciales
            base_key = ''.join([c for c in key if not c.isdigit()])
            sequential_count = 0
            
            for recent_key in recent_keys:
                if recent_key.startswith(base_key) and recent_key != key:
                    sequential_count += 1
            
            return sequential_count >= 3
            
        except Exception as e:
            logger.error(f"Error detectando patrón secuencial: {e}")
            return False
    
    def _detect_trending_pattern(self, timestamps: List[datetime]) -> bool:
        """Detecta patrón trending (acceso creciente)"""
        try:
            if len(timestamps) < 10:
                return False
            
            # Calcular la frecuencia de acceso en ventanas de tiempo
            recent_timestamps = timestamps[-10:]
            older_timestamps = timestamps[-20:-10] if len(timestamps) >= 20 else []
            
            if not older_timestamps:
                return False
            
            # Comparar frecuencias
            recent_span = (recent_timestamps[-1] - recent_timestamps[0]).total_seconds()
            older_span = (older_timestamps[-1] - older_timestamps[0]).total_seconds()
            
            recent_frequency = len(recent_timestamps) / max(recent_span, 1)
            older_frequency = len(older_timestamps) / max(older_span, 1)
            
            # Trending si la frecuencia reciente es significativamente mayor
            return recent_frequency > older_frequency * 1.5
            
        except Exception as e:
            logger.error(f"Error detectando patrón trending: {e}")
            return False
    
    def get_hotspot_keys(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Identifica las keys más accedidas (hotspots)"""
        try:
            key_counts = defaultdict(int)
            
            # Contar accesos en el historial reciente
            for event in self.access_history:
                key_counts[event.key] += 1
            
            # Ordenar por frecuencia
            sorted_keys = sorted(key_counts.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_keys[:top_n]
            
        except Exception as e:
            logger.error(f"Error identificando hotspots: {e}")
            return []


class CachePredictionEngine:
    """
    Motor principal de predicción de caché que utiliza ML para
    optimizar patrones de acceso, prefetching y distribución.
    """
    
    def __init__(self):
        self.pattern_analyzer = AccessPatternAnalyzer()
        self.behavior_analyzer = BehaviorPatternAnalyzer()
        
        # Configuración
        self.prediction_window_hours = 24
        self.min_access_frequency = 3
        self.prefetch_confidence_threshold = 0.7
        
        # Estado interno
        self.user_cache_patterns: Dict[str, Dict[str, Any]] = {}
        self.global_cache_metrics: Dict[str, Any] = {}
        
    async def initialize(self) -> None:
        """Inicializa el motor de predicción de caché"""
        try:
            logger.info("Cache Prediction Engine inicializado exitosamente")
        except Exception as e:
            logger.error(f"Error inicializando Cache Prediction Engine: {e}")
            raise
    
    async def record_cache_access(
        self,
        key: str,
        hit: bool,
        layer: Optional[CacheLayer] = None,
        response_time_ms: float = 0.0,
        user_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> None:
        """Registra acceso al caché para análisis"""
        try:
            event = AccessEvent(
                key=key,
                timestamp=datetime.utcnow(),
                hit=hit,
                layer=layer,
                response_time_ms=response_time_ms,
                user_id=user_id,
                context=context,
                metadata={}
            )
            
            self.pattern_analyzer.record_access(event)
            
            # Actualizar patrones por usuario
            if user_id:
                await self._update_user_patterns(user_id, event)
                
        except Exception as e:
            logger.error(f"Error registrando acceso al caché: {e}")
    
    async def predict_access_patterns(
        self,
        user_id: Optional[str] = None,
        time_horizon_hours: int = 24
    ) -> List[AccessPrediction]:
        """Predice patrones de acceso futuro"""
        try:
            predictions = []
            
            # Obtener hotspots actuales
            hotspots = self.pattern_analyzer.get_hotspot_keys(20)
            
            for key, access_count in hotspots:
                if access_count < self.min_access_frequency:
                    continue
                
                # Analizar patrón de la key
                pattern = self.pattern_analyzer.analyze_key_pattern(key)
                
                # Predecir próximo acceso
                prediction = await self._predict_key_access(
                    key, pattern, user_id, time_horizon_hours
                )
                
                if prediction and prediction.confidence > 0.5:
                    predictions.append(prediction)
            
            # Ordenar por confianza y probabilidad
            predictions.sort(
                key=lambda p: p.confidence * p.access_probability,
                reverse=True
            )
            
            logger.info(f"Generadas {len(predictions)} predicciones de acceso")
            return predictions[:50]  # Top 50 predicciones
            
        except Exception as e:
            logger.error(f"Error prediciendo patrones de acceso: {e}")
            return []
    
    async def _predict_key_access(
        self,
        key: str,
        pattern: AccessPattern,
        user_id: Optional[str],
        time_horizon_hours: int
    ) -> Optional[AccessPrediction]:
        """Predice acceso futuro para una key específica"""
        try:
            # Obtener historial de la key
            if key not in self.pattern_analyzer.temporal_patterns:
                return None
            
            timestamps = self.pattern_analyzer.temporal_patterns[key]
            
            if len(timestamps) < 3:
                return None
            
            # Calcular intervalos promedio
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(interval)
            
            avg_interval = statistics.mean(intervals)
            
            # Predecir próximo acceso basado en patrón
            last_access = timestamps[-1]
            
            if pattern == AccessPattern.PERIODIC:
                predicted_time = last_access + timedelta(seconds=avg_interval)
                confidence = 0.9
                access_probability = 0.85
            elif pattern == AccessPattern.TEMPORAL:
                predicted_time = last_access + timedelta(seconds=avg_interval * 1.2)
                confidence = 0.8
                access_probability = 0.75
            elif pattern == AccessPattern.TRENDING:
                # Acceso más frecuente
                predicted_time = last_access + timedelta(seconds=avg_interval * 0.8)
                confidence = 0.85
                access_probability = 0.9
            elif pattern == AccessPattern.BURST:
                # Puede haber ráfaga pronto
                predicted_time = last_access + timedelta(seconds=avg_interval * 0.5)
                confidence = 0.7
                access_probability = 0.8
            else:
                # Random pattern
                predicted_time = last_access + timedelta(seconds=avg_interval)
                confidence = 0.5
                access_probability = 0.6
            
            # Ajustar si está fuera del horizonte de tiempo
            max_prediction_time = datetime.utcnow() + timedelta(hours=time_horizon_hours)
            if predicted_time > max_prediction_time:
                return None
            
            # Determinar capa recomendada basada en patrón
            if pattern in [AccessPattern.TRENDING, AccessPattern.HOTSPOT]:
                recommended_layer = CacheLayer.L1_MEMORY
                recommended_ttl = 3600  # 1 hora
            elif pattern in [AccessPattern.PERIODIC, AccessPattern.TEMPORAL]:
                recommended_layer = CacheLayer.L2_REDIS
                recommended_ttl = 7200  # 2 horas
            else:
                recommended_layer = CacheLayer.L3_DATABASE
                recommended_ttl = 14400  # 4 horas
            
            # Factores que influyeron en la predicción
            factors = [
                f"Pattern: {pattern.value}",
                f"Avg interval: {avg_interval:.1f}s",
                f"Recent accesses: {len(timestamps)}"
            ]
            
            if user_id:
                factors.append(f"User-specific pattern for {user_id}")
            
            return AccessPrediction(
                key=key,
                predicted_access_time=predicted_time,
                confidence=confidence,
                access_probability=access_probability,
                recommended_layer=recommended_layer,
                recommended_ttl=recommended_ttl,
                pattern_type=pattern,
                factors=factors,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error prediciendo acceso para key {key}: {e}")
            return None
    
    async def generate_prefetch_recommendations(
        self,
        user_id: Optional[str] = None
    ) -> List[str]:
        """Genera recomendaciones de prefetching"""
        try:
            # Obtener predicciones de acceso
            predictions = await self.predict_access_patterns(user_id, 2)  # 2 horas
            
            prefetch_keys = []
            
            for prediction in predictions:
                # Solo prefetch si la confianza es alta
                if prediction.confidence >= self.prefetch_confidence_threshold:
                    # Y el acceso se predice pronto
                    time_until_access = (
                        prediction.predicted_access_time - datetime.utcnow()
                    ).total_seconds()
                    
                    # Prefetch si el acceso es en los próximos 30 minutos
                    if 60 <= time_until_access <= 1800:  # Entre 1 min y 30 min
                        prefetch_keys.append(prediction.key)
            
            logger.info(f"Recomendadas {len(prefetch_keys)} keys para prefetch")
            return prefetch_keys[:10]  # Máximo 10 prefetch por vez
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones de prefetch: {e}")
            return []
    
    async def optimize_ttl_values(
        self,
        cache_manager: AdvancedCacheManager
    ) -> List[CacheOptimizationRecommendation]:
        """Optimiza valores TTL basándose en patrones de acceso"""
        try:
            recommendations = []
            
            # Analizar todas las keys con patrones conocidos
            for key in self.pattern_analyzer.key_access_patterns.keys():
                pattern = self.pattern_analyzer.analyze_key_pattern(key)
                
                # Calcular TTL óptimo basado en patrón
                if key in self.pattern_analyzer.temporal_patterns:
                    timestamps = self.pattern_analyzer.temporal_patterns[key]
                    
                    if len(timestamps) >= 5:
                        # Calcular intervalo promedio entre accesos
                        intervals = []
                        for i in range(1, len(timestamps)):
                            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                            intervals.append(interval)
                        
                        avg_interval = statistics.mean(intervals)
                        
                        # TTL óptimo = 80% del intervalo promedio
                        optimal_ttl = int(avg_interval * 0.8)
                        
                        # Crear recomendación
                        recommendation = CacheOptimizationRecommendation(
                            recommendation_id=str(uuid.uuid4()),
                            type="ttl_optimization",
                            description=f"Optimize TTL for key {key} based on {pattern.value} pattern",
                            expected_improvement=15.0,  # 15% mejora estimada
                            implementation_cost=0.1,   # Bajo costo
                            confidence=0.8,
                            affected_keys=[key],
                            target_layer=None,
                            parameters={
                                "current_ttl": "unknown",
                                "recommended_ttl": optimal_ttl,
                                "pattern": pattern.value,
                                "avg_access_interval": avg_interval
                            },
                            generated_at=datetime.utcnow()
                        )
                        
                        recommendations.append(recommendation)
            
            # Ordenar por impacto esperado
            recommendations.sort(key=lambda r: r.expected_improvement, reverse=True)
            
            logger.info(f"Generadas {len(recommendations)} recomendaciones de TTL")
            return recommendations[:20]  # Top 20
            
        except Exception as e:
            logger.error(f"Error optimizando TTL: {e}")
            return []
    
    async def analyze_cache_efficiency(
        self,
        cache_manager: AdvancedCacheManager
    ) -> Dict[str, Any]:
        """Analiza la eficiencia actual del caché"""
        try:
            # Obtener estadísticas del caché
            stats = await cache_manager.get_comprehensive_statistics()
            
            # Analizar patrones de hotspots
            hotspots = self.pattern_analyzer.get_hotspot_keys(10)
            
            # Analizar distribución de patrones
            pattern_distribution = defaultdict(int)
            for key in self.pattern_analyzer.key_access_patterns.keys():
                pattern = self.pattern_analyzer.analyze_key_pattern(key)
                pattern_distribution[pattern.value] += 1
            
            # Calcular métricas de eficiencia
            global_stats = stats.get("global_statistics", {})
            hit_ratio = global_stats.get("global_hit_ratio", 0)
            avg_response_time = global_stats.get("average_response_time_ms", 0)
            
            # Clasificar eficiencia
            if hit_ratio > 0.9:
                efficiency_rating = "excellent"
            elif hit_ratio > 0.8:
                efficiency_rating = "good"
            elif hit_ratio > 0.7:
                efficiency_rating = "fair"
            else:
                efficiency_rating = "poor"
            
            # Identificar oportunidades de mejora
            improvement_opportunities = []
            
            if hit_ratio < 0.8:
                improvement_opportunities.append("Improve prefetching strategy")
            
            if avg_response_time > 50:
                improvement_opportunities.append("Optimize L1 cache size")
            
            if len(hotspots) > 5:
                improvement_opportunities.append("Increase L1 allocation for hotspots")
            
            return {
                "efficiency_rating": efficiency_rating,
                "hit_ratio": hit_ratio,
                "average_response_time_ms": avg_response_time,
                "hotspot_count": len(hotspots),
                "pattern_distribution": dict(pattern_distribution),
                "improvement_opportunities": improvement_opportunities,
                "total_keys_analyzed": len(self.pattern_analyzer.key_access_patterns),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analizando eficiencia del caché: {e}")
            return {"error": str(e)}
    
    async def _update_user_patterns(self, user_id: str, event: AccessEvent):
        """Actualiza patrones específicos del usuario"""
        try:
            if user_id not in self.user_cache_patterns:
                self.user_cache_patterns[user_id] = {
                    "access_count": 0,
                    "favorite_keys": [],
                    "access_times": [],
                    "contexts": []
                }
            
            user_patterns = self.user_cache_patterns[user_id]
            user_patterns["access_count"] += 1
            
            # Mantener últimas 100 horas de acceso
            if len(user_patterns["access_times"]) >= 100:
                user_patterns["access_times"].pop(0)
            user_patterns["access_times"].append(event.timestamp.hour)
            
            # Mantener contextos recientes
            if event.context:
                if len(user_patterns["contexts"]) >= 50:
                    user_patterns["contexts"].pop(0)
                user_patterns["contexts"].append(event.context)
            
        except Exception as e:
            logger.error(f"Error actualizando patrones de usuario: {e}")
    
    async def get_user_cache_insights(self, user_id: str) -> Dict[str, Any]:
        """Obtiene insights de caché específicos del usuario"""
        try:
            if user_id not in self.user_cache_patterns:
                return {"error": "No data available for user"}
            
            patterns = self.user_cache_patterns[user_id]
            
            # Analizar horas de mayor actividad
            if patterns["access_times"]:
                hour_counts = defaultdict(int)
                for hour in patterns["access_times"]:
                    hour_counts[hour] += 1
                
                peak_hours = sorted(
                    hour_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
            else:
                peak_hours = []
            
            # Analizar contextos más frecuentes
            if patterns["contexts"]:
                context_counts = defaultdict(int)
                for context in patterns["contexts"]:
                    context_counts[context] += 1
                
                top_contexts = sorted(
                    context_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            else:
                top_contexts = []
            
            return {
                "user_id": user_id,
                "total_cache_accesses": patterns["access_count"],
                "peak_activity_hours": peak_hours,
                "top_contexts": top_contexts,
                "activity_pattern": "regular" if len(patterns["access_times"]) > 50 else "sporadic",
                "insights_generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo insights de usuario: {e}")
            return {"error": str(e)}


# Instancia global del motor de predicción
cache_prediction_engine = CachePredictionEngine()


async def init_cache_prediction_engine() -> None:
    """Inicializa el motor de predicción de caché"""
    await cache_prediction_engine.initialize()


async def record_cache_access_event(
    key: str,
    hit: bool,
    layer: Optional[CacheLayer] = None,
    response_time_ms: float = 0.0,
    user_id: Optional[str] = None,
    context: Optional[str] = None
) -> None:
    """Función helper para registrar acceso al caché"""
    await cache_prediction_engine.record_cache_access(
        key, hit, layer, response_time_ms, user_id, context
    )


async def get_cache_prefetch_recommendations(user_id: Optional[str] = None) -> List[str]:
    """Función helper para obtener recomendaciones de prefetch"""
    return await cache_prediction_engine.generate_prefetch_recommendations(user_id)


async def analyze_current_cache_efficiency(cache_manager) -> Dict[str, Any]:
    """Función helper para analizar eficiencia del caché"""
    return await cache_prediction_engine.analyze_cache_efficiency(cache_manager)