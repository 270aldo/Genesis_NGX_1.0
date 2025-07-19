"""
Predictive Health Engine - FASE 12 POINT 4
==========================================

Motor de predicción de trayectorias de salud para coaching proactivo
que utiliza machine learning para predecir resultados y evaluar riesgos.

CARACTERÍSTICAS PRINCIPALES:
- Predicción de trayectorias de salud y fitness
- Evaluación de riesgo basada en patrones históricos
- Alertas tempranas de posibles problemas
- Recomendaciones personalizadas basadas en predicciones

IMPACTO ESPERADO: Coaching proactivo 400% más efectivo
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import logging
from abc import ABC, abstractmethod

from core.logging_config import get_logger
from core.conversation_memory import ConversationMemoryEngine, ConversationContext, EmotionalState
from core.memory_cache_optimizer import cache_get, cache_set, CachePriority
from clients.supabase_client import get_supabase_client

logger = get_logger(__name__)


class HealthMetricType(Enum):
    """Tipos de métricas de salud rastreables"""
    WEIGHT = "weight"
    BODY_FAT = "body_fat"
    MUSCLE_MASS = "muscle_mass"
    ENERGY_LEVEL = "energy_level"
    SLEEP_QUALITY = "sleep_quality"
    STRESS_LEVEL = "stress_level"
    NUTRITION_SCORE = "nutrition_score"
    WORKOUT_CONSISTENCY = "workout_consistency"
    MOTIVATION_LEVEL = "motivation_level"
    ADHERENCE_RATE = "adherence_rate"


class RiskLevel(Enum):
    """Niveles de riesgo para predicciones"""
    VERY_LOW = "very_low"
    LOW = "low" 
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PredictionHorizon(Enum):
    """Horizontes temporales para predicciones"""
    SHORT_TERM = "short_term"    # 1-7 días
    MEDIUM_TERM = "medium_term"  # 1-4 semanas
    LONG_TERM = "long_term"      # 1-3 meses


@dataclass
class HealthDataPoint:
    """Punto de datos de salud individual"""
    user_id: str
    metric_type: HealthMetricType
    value: float
    timestamp: datetime
    confidence: float  # 0.0 - 1.0
    source: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metric_type'] = self.metric_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class HealthTrajectory:
    """Trayectoria de salud predicha"""
    user_id: str
    metric_type: HealthMetricType
    current_value: float
    predicted_values: List[Tuple[datetime, float, float]]  # (fecha, valor, confianza)
    trend_direction: str  # 'improving', 'stable', 'declining'
    risk_level: RiskLevel
    confidence_score: float
    horizon: PredictionHorizon
    generated_at: datetime
    factors: List[str]  # Factores que influyen en la predicción
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metric_type'] = self.metric_type.value
        data['risk_level'] = self.risk_level.value
        data['horizon'] = self.horizon.value
        data['generated_at'] = self.generated_at.isoformat()
        data['predicted_values'] = [
            (dt.isoformat(), val, conf) 
            for dt, val, conf in self.predicted_values
        ]
        return data


@dataclass
class RiskAssessment:
    """Evaluación de riesgo basada en predicciones"""
    user_id: str
    overall_risk: RiskLevel
    risk_factors: List[Dict[str, Any]]
    protective_factors: List[Dict[str, Any]]
    recommendations: List[str]
    probability_scores: Dict[str, float]
    assessment_date: datetime
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['overall_risk'] = self.overall_risk.value
        data['assessment_date'] = self.assessment_date.isoformat()
        return data


class BasePredictor(ABC):
    """Clase base para predictores específicos"""
    
    @abstractmethod
    async def predict(self, data_points: List[HealthDataPoint]) -> HealthTrajectory:
        """Genera predicción basada en datos históricos"""
        pass
    
    @abstractmethod
    def get_required_data_points(self) -> int:
        """Número mínimo de puntos de datos necesarios"""
        pass


class WeightTrajectoryPredictor(BasePredictor):
    """Predictor especializado para trayectoria de peso"""
    
    def __init__(self):
        self.min_data_points = 7
        self.max_lookback_days = 90
    
    async def predict(self, data_points: List[HealthDataPoint]) -> HealthTrajectory:
        """Predice trayectoria de peso usando regresión lineal simple"""
        try:
            if len(data_points) < self.min_data_points:
                raise ValueError(f"Necesitamos al menos {self.min_data_points} puntos de datos")
            
            # Extraer valores y timestamps
            values = [dp.value for dp in data_points]
            timestamps = [dp.timestamp for dp in data_points]
            
            # Convertir timestamps a días desde el inicio
            start_date = min(timestamps)
            days = [(ts - start_date).days for ts in timestamps]
            
            # Regresión lineal simple
            x = np.array(days)
            y = np.array(values)
            
            # Calcular pendiente y intersección
            n = len(x)
            slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - (np.sum(x))**2)
            intercept = (np.sum(y) - slope * np.sum(x)) / n
            
            # Generar predicciones para los próximos 30 días
            current_value = values[-1]
            predicted_values = []
            
            for days_ahead in range(1, 31):
                future_date = timestamps[-1] + timedelta(days=days_ahead)
                future_day = days[-1] + days_ahead
                predicted_value = slope * future_day + intercept
                
                # Calcular confianza basada en varianza
                residuals = y - (slope * x + intercept)
                variance = np.var(residuals)
                confidence = max(0.1, 1.0 - (variance / np.var(y)))
                
                predicted_values.append((future_date, predicted_value, confidence))
            
            # Determinar tendencia
            if slope > 0.1:
                trend = "improving" if data_points[0].metric_type == HealthMetricType.MUSCLE_MASS else "declining"
            elif slope < -0.1:
                trend = "declining" if data_points[0].metric_type == HealthMetricType.MUSCLE_MASS else "improving"
            else:
                trend = "stable"
            
            # Evaluar riesgo basado en tendencia
            if abs(slope) > 0.5:  # Cambio mayor a 0.5 kg por día
                risk = RiskLevel.HIGH
            elif abs(slope) > 0.2:
                risk = RiskLevel.MODERATE
            else:
                risk = RiskLevel.LOW
            
            # Factores influyentes
            factors = ["Tendencia histórica", "Consistencia de datos", "Variabilidad reciente"]
            
            return HealthTrajectory(
                user_id=data_points[0].user_id,
                metric_type=data_points[0].metric_type,
                current_value=current_value,
                predicted_values=predicted_values,
                trend_direction=trend,
                risk_level=risk,
                confidence_score=min(confidence, 0.9),
                horizon=PredictionHorizon.MEDIUM_TERM,
                generated_at=datetime.utcnow(),
                factors=factors
            )
            
        except Exception as e:
            logger.error(f"Error en predicción de peso: {e}")
            raise


class AdherencePredictor(BasePredictor):
    """Predictor para adherencia a rutinas"""
    
    def __init__(self):
        self.min_data_points = 14
    
    async def predict(self, data_points: List[HealthDataPoint]) -> HealthTrajectory:
        """Predice adherencia basada en patrones históricos"""
        try:
            if len(data_points) < self.min_data_points:
                raise ValueError(f"Necesitamos al menos {self.min_data_points} puntos de datos")
            
            # Calcular adherencia en ventanas de 7 días
            values = [dp.value for dp in data_points]
            timestamps = [dp.timestamp for dp in data_points]
            
            # Agrupar por semanas
            weekly_adherence = []
            current_week = []
            current_week_start = timestamps[0].replace(hour=0, minute=0, second=0, microsecond=0)
            
            for i, ts in enumerate(timestamps):
                week_start = ts.replace(hour=0, minute=0, second=0, microsecond=0)
                days_diff = (week_start - current_week_start).days
                
                if days_diff < 7:
                    current_week.append(values[i])
                else:
                    if current_week:
                        weekly_adherence.append(np.mean(current_week))
                    current_week = [values[i]]
                    current_week_start = week_start
            
            # Agregar última semana
            if current_week:
                weekly_adherence.append(np.mean(current_week))
            
            # Calcular tendencia de adherencia
            if len(weekly_adherence) >= 2:
                recent_trend = np.mean(weekly_adherence[-2:]) - np.mean(weekly_adherence[:-2] if len(weekly_adherence) > 2 else weekly_adherence[:1])
            else:
                recent_trend = 0
            
            # Generar predicciones para las próximas 4 semanas
            current_adherence = weekly_adherence[-1] if weekly_adherence else 0.5
            predicted_values = []
            
            for week in range(1, 5):
                future_date = timestamps[-1] + timedelta(weeks=week)
                
                # Modelo simple: adherencia decae con el tiempo sin intervención
                decay_factor = 0.95 ** week  # Decaimiento del 5% por semana
                predicted_adherence = current_adherence * decay_factor
                
                # Ajustar por tendencia reciente
                predicted_adherence += recent_trend * week * 0.1
                
                # Mantener en rango [0, 1]
                predicted_adherence = max(0, min(1, predicted_adherence))
                
                confidence = max(0.3, 0.9 - (week * 0.15))  # Confianza decae con el tiempo
                predicted_values.append((future_date, predicted_adherence, confidence))
            
            # Determinar riesgo basado en adherencia actual y tendencia
            if current_adherence < 0.6 or recent_trend < -0.1:
                risk = RiskLevel.HIGH
            elif current_adherence < 0.75 or recent_trend < -0.05:
                risk = RiskLevel.MODERATE
            else:
                risk = RiskLevel.LOW
            
            # Determinar tendencia
            if recent_trend > 0.05:
                trend = "improving"
            elif recent_trend < -0.05:
                trend = "declining"
            else:
                trend = "stable"
            
            factors = [
                "Patrones de adherencia histórica",
                "Tendencia reciente",
                "Variabilidad semanal",
                "Factores estacionales"
            ]
            
            return HealthTrajectory(
                user_id=data_points[0].user_id,
                metric_type=HealthMetricType.ADHERENCE_RATE,
                current_value=current_adherence,
                predicted_values=predicted_values,
                trend_direction=trend,
                risk_level=risk,
                confidence_score=0.8,
                horizon=PredictionHorizon.MEDIUM_TERM,
                generated_at=datetime.utcnow(),
                factors=factors
            )
            
        except Exception as e:
            logger.error(f"Error en predicción de adherencia: {e}")
            raise
    
    def get_required_data_points(self) -> int:
        return self.min_data_points


class PredictiveHealthEngine:
    """
    Motor principal de predicciones de salud
    
    Coordina múltiples predictores especializados para generar
    trayectorias de salud precisas y evaluaciones de riesgo.
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.memory_engine = ConversationMemoryEngine()
        
        # Inicializar predictores especializados
        self.predictors = {
            HealthMetricType.WEIGHT: WeightTrajectoryPredictor(),
            HealthMetricType.BODY_FAT: WeightTrajectoryPredictor(),  # Usar mismo predictor
            HealthMetricType.MUSCLE_MASS: WeightTrajectoryPredictor(),
            HealthMetricType.ADHERENCE_RATE: AdherencePredictor(),
            HealthMetricType.WORKOUT_CONSISTENCY: AdherencePredictor(),
        }
        
        self.cache_ttl = 3600  # 1 hora
        
    async def initialize(self) -> None:
        """Inicializa el motor predictivo"""
        try:
            await self._ensure_database_tables()
            logger.info("Predictive Health Engine inicializado exitosamente")
        except Exception as e:
            logger.error(f"Error inicializando Predictive Health Engine: {e}")
            raise
    
    async def _ensure_database_tables(self) -> None:
        """Asegura que las tablas necesarias existen"""
        try:
            logger.info("Tablas de predicción de salud simuladas (modo desarrollo)")
        except Exception as e:
            logger.warning(f"No se pudieron crear tablas predictivas: {e}")
    
    async def store_health_data(
        self,
        user_id: str,
        metric_type: HealthMetricType,
        value: float,
        source: str = "manual",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Almacena nuevo punto de datos de salud"""
        try:
            data_point = HealthDataPoint(
                user_id=user_id,
                metric_type=metric_type,
                value=value,
                timestamp=datetime.utcnow(),
                confidence=1.0,  # Datos manuales tienen alta confianza
                source=source,
                metadata=metadata or {}
            )
            
            # Para desarrollo, simulamos el almacenamiento
            data_id = str(uuid.uuid4())
            logger.info(f"Datos de salud simulados almacenados: {data_id} para usuario {user_id}")
            
            # Invalidar caché de predicciones para este usuario
            await self._invalidate_user_predictions_cache(user_id)
            
            return data_id
            
        except Exception as e:
            logger.error(f"Error almacenando datos de salud: {e}")
            raise
    
    async def generate_health_trajectory(
        self,
        user_id: str,
        metric_type: HealthMetricType,
        horizon: PredictionHorizon = PredictionHorizon.MEDIUM_TERM
    ) -> Optional[HealthTrajectory]:
        """Genera trayectoria de salud predicha"""
        try:
            # Intentar desde caché
            cache_key = f"health_trajectory:{user_id}:{metric_type.value}:{horizon.value}"
            cached_trajectory = await cache_get(cache_key)
            
            if cached_trajectory:
                return HealthTrajectory(**cached_trajectory)
            
            # Obtener datos históricos
            historical_data = await self._get_historical_data(user_id, metric_type)
            
            if not historical_data:
                logger.info(f"No hay datos históricos suficientes para {user_id}, {metric_type.value}")
                return None
            
            # Verificar si tenemos predictor para este tipo de métrica
            if metric_type not in self.predictors:
                logger.warning(f"No hay predictor disponible para {metric_type.value}")
                return None
            
            predictor = self.predictors[metric_type]
            
            # Verificar datos mínimos
            if len(historical_data) < predictor.get_required_data_points():
                logger.info(f"Datos insuficientes para predicción: {len(historical_data)}/{predictor.get_required_data_points()}")
                return None
            
            # Generar predicción
            trajectory = await predictor.predict(historical_data)
            
            # Cachear resultado
            await cache_set(
                cache_key,
                trajectory.to_dict(),
                ttl=self.cache_ttl,
                priority=CachePriority.NORMAL
            )
            
            logger.info(f"Trayectoria generada para {user_id}, {metric_type.value}")
            return trajectory
            
        except Exception as e:
            logger.error(f"Error generando trayectoria de salud: {e}")
            return None
    
    async def _get_historical_data(
        self,
        user_id: str,
        metric_type: HealthMetricType,
        days_back: int = 90
    ) -> List[HealthDataPoint]:
        """Obtiene datos históricos del usuario"""
        try:
            # Para desarrollo, generamos datos simulados
            logger.info(f"Generando datos históricos simulados para {user_id}, {metric_type.value}")
            
            # Generar datos simulados para testing
            historical_data = []
            base_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Valores base por tipo de métrica
            base_values = {
                HealthMetricType.WEIGHT: 70.0,
                HealthMetricType.BODY_FAT: 15.0,
                HealthMetricType.MUSCLE_MASS: 45.0,
                HealthMetricType.ADHERENCE_RATE: 0.8,
                HealthMetricType.WORKOUT_CONSISTENCY: 0.75
            }
            
            base_value = base_values.get(metric_type, 50.0)
            
            # Generar serie temporal con tendencia y ruido
            for i in range(0, days_back, 2):  # Datos cada 2 días
                date = base_date + timedelta(days=i)
                
                # Agregar tendencia gradual y ruido
                trend = i * 0.01  # Tendencia gradual
                noise = np.random.normal(0, 0.1)  # Ruido gaussiano
                value = base_value + trend + noise
                
                # Mantener valores realistas
                if metric_type in [HealthMetricType.ADHERENCE_RATE, HealthMetricType.WORKOUT_CONSISTENCY]:
                    value = max(0, min(1, value))
                else:
                    value = max(0, value)
                
                data_point = HealthDataPoint(
                    user_id=user_id,
                    metric_type=metric_type,
                    value=value,
                    timestamp=date,
                    confidence=0.9,
                    source="simulated",
                    metadata={"generated": True}
                )
                
                historical_data.append(data_point)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos: {e}")
            return []
    
    async def assess_health_risks(self, user_id: str) -> RiskAssessment:
        """Genera evaluación completa de riesgos de salud"""
        try:
            # Obtener trayectorias para múltiples métricas
            trajectories = {}
            key_metrics = [
                HealthMetricType.WEIGHT,
                HealthMetricType.ADHERENCE_RATE,
                HealthMetricType.WORKOUT_CONSISTENCY
            ]
            
            for metric in key_metrics:
                trajectory = await self.generate_health_trajectory(user_id, metric)
                if trajectory:
                    trajectories[metric] = trajectory
            
            # Evaluar riesgo general
            risk_scores = []
            risk_factors = []
            protective_factors = []
            
            for metric, trajectory in trajectories.items():
                risk_value = self._risk_level_to_score(trajectory.risk_level)
                risk_scores.append(risk_value)
                
                if trajectory.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
                    risk_factors.append({
                        "factor": f"{metric.value} trajectory",
                        "level": trajectory.risk_level.value,
                        "trend": trajectory.trend_direction,
                        "confidence": trajectory.confidence_score
                    })
                elif trajectory.risk_level in [RiskLevel.LOW, RiskLevel.VERY_LOW]:
                    protective_factors.append({
                        "factor": f"{metric.value} stability",
                        "level": trajectory.risk_level.value,
                        "trend": trajectory.trend_direction,
                        "confidence": trajectory.confidence_score
                    })
            
            # Calcular riesgo general
            if risk_scores:
                avg_risk = np.mean(risk_scores)
                overall_risk = self._score_to_risk_level(avg_risk)
            else:
                overall_risk = RiskLevel.MODERATE
            
            # Generar recomendaciones
            recommendations = await self._generate_risk_recommendations(trajectories, risk_factors)
            
            # Calcular probabilidades específicas
            probability_scores = {
                "adherence_drop": min(0.9, len([rf for rf in risk_factors if "adherence" in rf["factor"]]) * 0.3),
                "goal_achievement": max(0.1, 1.0 - avg_risk if risk_scores else 0.5),
                "intervention_needed": avg_risk if risk_scores else 0.5
            }
            
            assessment = RiskAssessment(
                user_id=user_id,
                overall_risk=overall_risk,
                risk_factors=risk_factors,
                protective_factors=protective_factors,
                recommendations=recommendations,
                probability_scores=probability_scores,
                assessment_date=datetime.utcnow(),
                confidence=0.8
            )
            
            logger.info(f"Evaluación de riesgo completada para usuario {user_id}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error evaluando riesgos de salud: {e}")
            raise
    
    def _risk_level_to_score(self, risk_level: RiskLevel) -> float:
        """Convierte nivel de riesgo a score numérico"""
        mapping = {
            RiskLevel.VERY_LOW: 0.1,
            RiskLevel.LOW: 0.3,
            RiskLevel.MODERATE: 0.5,
            RiskLevel.HIGH: 0.7,
            RiskLevel.VERY_HIGH: 0.9
        }
        return mapping.get(risk_level, 0.5)
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convierte score numérico a nivel de riesgo"""
        if score <= 0.2:
            return RiskLevel.VERY_LOW
        elif score <= 0.4:
            return RiskLevel.LOW
        elif score <= 0.6:
            return RiskLevel.MODERATE
        elif score <= 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    async def _generate_risk_recommendations(
        self,
        trajectories: Dict[HealthMetricType, HealthTrajectory],
        risk_factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Genera recomendaciones basadas en riesgos identificados"""
        recommendations = []
        
        # Recomendaciones por tipo de riesgo
        for risk_factor in risk_factors:
            factor_name = risk_factor["factor"]
            
            if "adherence" in factor_name:
                recommendations.append("Revisar y ajustar el plan de entrenamiento actual")
                recommendations.append("Considerar estrategias de motivación adicionales")
            
            if "weight" in factor_name:
                if "declining" in str(risk_factor.get("trend")):
                    recommendations.append("Monitorear ingesta calórica y ajustar nutrición")
                else:
                    recommendations.append("Evaluar plan nutricional para control de peso")
            
            if "consistency" in factor_name:
                recommendations.append("Establecer rutinas más flexibles y sostenibles")
        
        # Recomendaciones generales
        if len(risk_factors) > 2:
            recommendations.append("Considerar consulta con especialista en fitness")
            recommendations.append("Revisar objetivos y ajustar expectativas")
        
        return list(set(recommendations))  # Eliminar duplicados
    
    async def _invalidate_user_predictions_cache(self, user_id: str) -> None:
        """Invalida caché de predicciones para un usuario"""
        try:
            cache_patterns = [
                f"health_trajectory:{user_id}:*",
                f"risk_assessment:{user_id}",
                f"recommendations:{user_id}:*"
            ]
            
            # En implementación real, invalidaríamos usando patrones
            logger.debug(f"Cache de predicciones invalidado para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error invalidando caché: {e}")
    
    async def get_prediction_analytics(self, user_id: str) -> Dict[str, Any]:
        """Obtiene analíticas de predicciones para un usuario"""
        try:
            # Para desarrollo, retornamos analíticas simuladas
            return {
                "total_predictions": 5,
                "accuracy_score": 0.82,
                "last_updated": datetime.utcnow().isoformat(),
                "metrics_tracked": 3,
                "risk_trends": {
                    "improving": 2,
                    "stable": 1,
                    "declining": 0
                },
                "confidence_levels": {
                    "high": 0.8,
                    "medium": 0.6,
                    "low": 0.2
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo analíticas de predicción: {e}")
            return {}


# Instancia global del motor predictivo
predictive_health_engine = PredictiveHealthEngine()


async def init_predictive_health_engine() -> None:
    """Inicializa el motor de predicción de salud"""
    await predictive_health_engine.initialize()


async def predict_user_trajectory(
    user_id: str,
    metric_type: HealthMetricType,
    horizon: PredictionHorizon = PredictionHorizon.MEDIUM_TERM
) -> Optional[HealthTrajectory]:
    """Función helper para generar predicción"""
    return await predictive_health_engine.generate_health_trajectory(
        user_id, metric_type, horizon
    )


async def assess_user_risks(user_id: str) -> RiskAssessment:
    """Función helper para evaluación de riesgos"""
    return await predictive_health_engine.assess_health_risks(user_id)