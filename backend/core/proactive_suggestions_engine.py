"""
Proactive Suggestions Engine - NGX Agents Advanced AI
Sistema inteligente de sugerencias proactivas basado en patrones de comportamiento,
contexto del usuario y predicciones de IA.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from clients.vertex_ai.vertex_ai_client import VertexAIClient
from core.telemetry import trace_async
from core.redis_pool import get_redis_client
from core.adherence_prediction_engine import AdherencePredictionEngine, AdherenceMetrics

logger = logging.getLogger(__name__)


class SuggestionType(Enum):
    """Tipos de sugerencias proactivas."""

    WORKOUT_OPTIMIZATION = "workout_optimization"
    NUTRITION_TIMING = "nutrition_timing"
    RECOVERY_REMINDER = "recovery_reminder"
    MOTIVATION_BOOST = "motivation_boost"
    HABIT_REINFORCEMENT = "habit_reinforcement"
    GOAL_ADJUSTMENT = "goal_adjustment"
    SOCIAL_ENGAGEMENT = "social_engagement"
    BIOMETRIC_INTERVENTION = "biometric_intervention"
    SEASONAL_ADAPTATION = "seasonal_adaptation"
    STRESS_MANAGEMENT = "stress_management"


class SuggestionPriority(Enum):
    """Prioridad de las sugerencias."""

    CRITICAL = "critical"  # Intervención inmediata requerida
    HIGH = "high"  # Importante para objetivos
    MEDIUM = "medium"  # Beneficioso pero no urgente
    LOW = "low"  # Optimización menor
    INFO = "info"  # Información educativa


class SuggestionTiming(Enum):
    """Momento óptimo para la sugerencia."""

    IMMEDIATE = "immediate"  # Ahora mismo
    WITHIN_HOUR = "within_hour"
    WITHIN_DAY = "within_day"
    NEXT_WORKOUT = "next_workout"
    NEXT_MEAL = "next_meal"
    WEEKLY_PLANNING = "weekly_planning"
    MONTHLY_REVIEW = "monthly_review"


@dataclass
class ProactiveSuggestion:
    """Modelo de sugerencia proactiva."""

    suggestion_id: str
    user_id: str
    agent_id: str
    suggestion_type: SuggestionType
    priority: SuggestionPriority
    timing: SuggestionTiming

    title: str
    message: str
    action_items: List[str]
    reasoning: str

    context: Dict[str, Any]
    confidence_score: float  # 0-1 scale

    # Métricas de impacto esperado
    expected_impact: Dict[str, float]  # adherence, performance, satisfaction

    # Timing y entrega
    created_at: datetime
    optimal_delivery_time: datetime
    expires_at: Optional[datetime]

    # Estado
    delivered: bool = False
    user_response: Optional[str] = None
    effectiveness_score: Optional[float] = None


@dataclass
class UserContext:
    """Contexto completo del usuario para sugerencias."""

    user_id: str
    program_type: str  # PRIME, LONGEVITY

    # Estado actual
    current_energy_level: float  # 0-1 scale
    stress_level: float  # 0-1 scale
    motivation_level: float  # 0-1 scale
    adherence_trend: str  # improving, stable, declining

    # Patrones temporales
    time_of_day: str
    day_of_week: str
    season: str

    # Contexto situacional
    location_type: str  # home, gym, office, travel
    social_context: str  # alone, family, friends, work
    upcoming_events: List[Dict[str, Any]]

    # Estado de objetivos
    active_goals: List[Dict[str, Any]]
    recent_achievements: List[Dict[str, Any]]
    current_challenges: List[str]

    # Preferencias y historial
    communication_preferences: Dict[str, Any]
    successful_interventions: List[str]
    failed_interventions: List[str]


class ProactiveSuggestionsEngine:
    """
    Motor de sugerencias proactivas que analiza patrones de comportamiento,
    contexto del usuario y datos biométricos para generar intervenciones
    inteligentes y oportunas.
    """

    def __init__(self, vertex_ai_client: Optional[VertexAIClient] = None):
        """Inicializar motor de sugerencias proactivas."""
        self.vertex_ai_client = vertex_ai_client or VertexAIClient()
        self.redis_client = get_redis_client()
        self.adherence_engine = AdherencePredictionEngine(vertex_ai_client)

        # Configuración de sugerencias
        self.suggestion_cooldowns = {
            SuggestionType.WORKOUT_OPTIMIZATION: 12,  # horas
            SuggestionType.NUTRITION_TIMING: 4,
            SuggestionType.RECOVERY_REMINDER: 24,
            SuggestionType.MOTIVATION_BOOST: 8,
            SuggestionType.HABIT_REINFORCEMENT: 48,
            SuggestionType.GOAL_ADJUSTMENT: 168,  # 1 semana
            SuggestionType.SOCIAL_ENGAGEMENT: 72,
            SuggestionType.BIOMETRIC_INTERVENTION: 6,
            SuggestionType.SEASONAL_ADAPTATION: 720,  # 1 mes
            SuggestionType.STRESS_MANAGEMENT: 2,
        }

        # Umbrales de confianza mínima por tipo
        self.confidence_thresholds = {
            SuggestionType.WORKOUT_OPTIMIZATION: 0.7,
            SuggestionType.NUTRITION_TIMING: 0.6,
            SuggestionType.RECOVERY_REMINDER: 0.8,
            SuggestionType.MOTIVATION_BOOST: 0.5,
            SuggestionType.HABIT_REINFORCEMENT: 0.7,
            SuggestionType.GOAL_ADJUSTMENT: 0.85,
            SuggestionType.SOCIAL_ENGAGEMENT: 0.6,
            SuggestionType.BIOMETRIC_INTERVENTION: 0.9,
            SuggestionType.SEASONAL_ADAPTATION: 0.7,
            SuggestionType.STRESS_MANAGEMENT: 0.8,
        }

        logger.info("Proactive Suggestions Engine initialized")

    @trace_async("generate_proactive_suggestions")
    async def generate_proactive_suggestions(
        self, user_context: UserContext, limit: int = 5
    ) -> List[ProactiveSuggestion]:
        """
        Generar sugerencias proactivas basadas en el contexto del usuario.

        Args:
            user_context: Contexto completo del usuario
            limit: Número máximo de sugerencias a generar

        Returns:
            Lista de sugerencias priorizadas
        """
        try:
            suggestions = []

            # 1. Analizar patrones de comportamiento
            behavior_insights = await self._analyze_behavior_patterns(user_context)

            # 2. Evaluar estado actual vs objetivos
            goal_analysis = await self._analyze_goal_progress(user_context)

            # 3. Detectar oportunidades contextuales
            contextual_opportunities = await self._detect_contextual_opportunities(
                user_context
            )

            # 4. Generar sugerencias por categoría
            suggestion_categories = [
                await self._generate_workout_suggestions(
                    user_context, behavior_insights
                ),
                await self._generate_nutrition_suggestions(
                    user_context, behavior_insights
                ),
                await self._generate_recovery_suggestions(
                    user_context, behavior_insights
                ),
                await self._generate_motivation_suggestions(
                    user_context, goal_analysis
                ),
                await self._generate_habit_suggestions(user_context, behavior_insights),
                await self._generate_goal_suggestions(user_context, goal_analysis),
                await self._generate_social_suggestions(
                    user_context, contextual_opportunities
                ),
                await self._generate_biometric_suggestions(user_context),
                await self._generate_seasonal_suggestions(user_context),
                await self._generate_stress_suggestions(user_context),
            ]

            # Combinar todas las sugerencias
            for category_suggestions in suggestion_categories:
                suggestions.extend(category_suggestions)

            # 5. Filtrar por cooldowns y umbrales de confianza
            filtered_suggestions = await self._filter_suggestions(
                suggestions, user_context
            )

            # 6. Priorizar y limitar
            prioritized_suggestions = self._prioritize_suggestions(filtered_suggestions)

            # 7. Optimizar timing de entrega
            optimized_suggestions = await self._optimize_delivery_timing(
                prioritized_suggestions[:limit], user_context
            )

            # 8. Cachear para tracking
            await self._cache_suggestions(optimized_suggestions)

            logger.info(
                f"Generated {len(optimized_suggestions)} proactive suggestions for user {user_context.user_id}"
            )

            return optimized_suggestions

        except Exception as e:
            logger.error(f"Failed to generate proactive suggestions: {e}")
            raise

    async def _analyze_behavior_patterns(
        self, user_context: UserContext
    ) -> Dict[str, Any]:
        """Analizar patrones de comportamiento del usuario."""

        # Obtener datos históricos del usuario
        historical_data = await self._get_user_historical_data(user_context.user_id)

        # Usar IA para análisis de patrones
        prompt = f"""
        Analiza los patrones de comportamiento de este usuario:
        
        Contexto: {asdict(user_context)}
        Datos históricos: {json.dumps(historical_data, indent=2)}
        
        Identifica:
        1. Patrones de actividad (horarios preferidos, duración, intensidad)
        2. Patrones nutricionales (horarios de comida, preferencias, adherencia)
        3. Patrones de recuperación (sueño, descanso, estrés)
        4. Patrones motivacionales (qué funciona, cuándo decae)
        5. Factores de éxito y fracaso
        6. Tendencias temporales (mejoras, decline, estabilidad)
        
        Devuelve insights accionables en formato JSON.
        """

        try:
            if self.vertex_ai_client:
                analysis = await self.vertex_ai_client.generate_content_async(prompt)
                return json.loads(analysis)
        except Exception as e:
            logger.warning(f"AI behavior analysis failed: {e}")

        # Fallback: análisis básico
        return {
            "activity_patterns": {
                "preferred_time": user_context.time_of_day,
                "consistency": "moderate",
            },
            "adherence_trend": user_context.adherence_trend,
            "energy_correlation": {
                "current_energy": user_context.current_energy_level,
                "optimal_times": ["morning", "early_evening"],
            },
        }

    async def _analyze_goal_progress(self, user_context: UserContext) -> Dict[str, Any]:
        """Analizar progreso hacia objetivos."""

        prompt = f"""
        Analiza el progreso hacia objetivos de este usuario:
        
        Objetivos activos: {json.dumps(user_context.active_goals, indent=2)}
        Logros recientes: {json.dumps(user_context.recent_achievements, indent=2)}
        Desafíos actuales: {user_context.current_challenges}
        Tendencia de adherencia: {user_context.adherence_trend}
        
        Evalúa:
        1. Velocidad de progreso vs expectativas
        2. Objetivos en riesgo de no cumplirse
        3. Oportunidades de aceleración
        4. Necesidad de ajustes en objetivos
        5. Momento óptimo para intervenciones
        
        Devuelve análisis en formato JSON.
        """

        try:
            if self.vertex_ai_client:
                analysis = await self.vertex_ai_client.generate_content_async(prompt)
                return json.loads(analysis)
        except Exception as e:
            logger.warning(f"AI goal analysis failed: {e}")

        # Fallback básico
        return {
            "progress_velocity": (
                "on_track" if user_context.adherence_trend == "improving" else "behind"
            ),
            "at_risk_goals": (
                user_context.active_goals
                if user_context.adherence_trend == "declining"
                else []
            ),
            "acceleration_opportunities": [
                "consistency_improvement",
                "intensity_optimization",
            ],
        }

    async def _detect_contextual_opportunities(
        self, user_context: UserContext
    ) -> Dict[str, Any]:
        """Detectar oportunidades contextuales para sugerencias."""

        opportunities = {
            "timing_opportunities": [],
            "social_opportunities": [],
            "environmental_opportunities": [],
            "seasonal_opportunities": [],
        }

        # Oportunidades temporales
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 9:
            opportunities["timing_opportunities"].append("morning_routine_optimization")
        elif 17 <= current_hour <= 19:
            opportunities["timing_opportunities"].append("evening_workout_window")
        elif 20 <= current_hour <= 22:
            opportunities["timing_opportunities"].append("recovery_preparation")

        # Oportunidades sociales
        if user_context.social_context in ["family", "friends"]:
            opportunities["social_opportunities"].append("social_activity_suggestion")

        # Oportunidades ambientales
        if user_context.location_type == "home":
            opportunities["environmental_opportunities"].append(
                "home_workout_optimization"
            )
        elif user_context.location_type == "gym":
            opportunities["environmental_opportunities"].append(
                "gym_session_enhancement"
            )

        # Oportunidades estacionales
        season_opportunities = {
            "winter": ["indoor_activity_boost", "vitamin_d_awareness"],
            "spring": ["outdoor_transition", "energy_renewal"],
            "summer": ["hydration_focus", "heat_adaptation"],
            "fall": ["routine_stabilization", "immune_support"],
        }
        opportunities["seasonal_opportunities"] = season_opportunities.get(
            user_context.season, []
        )

        return opportunities

    async def _generate_workout_suggestions(
        self, user_context: UserContext, behavior_insights: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias de optimización de entrenamientos."""
        suggestions = []

        # Sugerencia de timing óptimo
        if user_context.current_energy_level > 0.7 and user_context.time_of_day in [
            "morning",
            "afternoon",
        ]:
            suggestion = ProactiveSuggestion(
                suggestion_id=f"workout_timing_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="blaze_training_strategist",
                suggestion_type=SuggestionType.WORKOUT_OPTIMIZATION,
                priority=SuggestionPriority.HIGH,
                timing=SuggestionTiming.IMMEDIATE,
                title="🔥 Momento Óptimo para Entrenar",
                message=f"Tu nivel de energía está en {user_context.current_energy_level:.0%} - ¡perfecto para un entrenamiento de alta intensidad!",
                action_items=[
                    "Iniciar calentamiento dinámico de 5 minutos",
                    "Aprovechar energía para ejercicios compuestos",
                    "Mantener intensidad durante 25-30 minutos",
                ],
                reasoning=f"Energía alta ({user_context.current_energy_level:.0%}) + timing favorable = 23% mejor rendimiento",
                context={
                    "energy_level": user_context.current_energy_level,
                    "time_optimal": True,
                },
                confidence_score=0.85,
                expected_impact={
                    "adherence": 0.15,
                    "performance": 0.23,
                    "satisfaction": 0.18,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=2),
            )
            suggestions.append(suggestion)

        # Sugerencia de adaptación por estrés
        if user_context.stress_level > 0.6:
            suggestion = ProactiveSuggestion(
                suggestion_id=f"workout_stress_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="blaze_training_strategist",
                suggestion_type=SuggestionType.WORKOUT_OPTIMIZATION,
                priority=SuggestionPriority.MEDIUM,
                timing=SuggestionTiming.NEXT_WORKOUT,
                title="🧘 Entrenamiento Adaptado al Estrés",
                message=f"Estrés detectado ({user_context.stress_level:.0%}). Mejor optar por entrenamiento regenerativo.",
                action_items=[
                    "Reducir intensidad 30-40%",
                    "Enfocarse en movimientos fluidos",
                    "Incluir 10 minutos de estiramientos finales",
                ],
                reasoning="Estrés elevado requiere entrenamiento regenerativo para evitar cortisol adicional",
                context={
                    "stress_level": user_context.stress_level,
                    "adaptation_needed": True,
                },
                confidence_score=0.78,
                expected_impact={
                    "adherence": 0.20,
                    "performance": -0.05,
                    "satisfaction": 0.25,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now() + timedelta(hours=1),
                expires_at=datetime.now() + timedelta(hours=24),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_nutrition_suggestions(
        self, user_context: UserContext, behavior_insights: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias nutricionales."""
        suggestions = []

        current_hour = datetime.now().hour

        # Sugerencia de timing pre-entrenamiento
        if 15 <= current_hour <= 17 and user_context.current_energy_level < 0.5:
            suggestion = ProactiveSuggestion(
                suggestion_id=f"nutrition_preworkout_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="sage_nutrition_architect",
                suggestion_type=SuggestionType.NUTRITION_TIMING,
                priority=SuggestionPriority.HIGH,
                timing=SuggestionTiming.WITHIN_HOUR,
                title="⚡ Energía Pre-Entrenamiento",
                message="Tu energía está baja para el horario típico de entrenamiento. Un snack estratégico puede optimizar tu sesión.",
                action_items=[
                    "Consumir 15-20g carbohidratos de rápida absorción",
                    "Agregar 200mg cafeína si toleras bien",
                    "Hidratarse con 300-400ml agua",
                ],
                reasoning="Energía baja + timing pre-workout = oportunidad de optimización nutricional",
                context={
                    "energy_level": user_context.current_energy_level,
                    "pre_workout": True,
                },
                confidence_score=0.82,
                expected_impact={
                    "adherence": 0.18,
                    "performance": 0.30,
                    "satisfaction": 0.22,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now() + timedelta(minutes=15),
                expires_at=datetime.now() + timedelta(hours=3),
            )
            suggestions.append(suggestion)

        # Sugerencia de recuperación nocturna
        if 20 <= current_hour <= 22:
            suggestion = ProactiveSuggestion(
                suggestion_id=f"nutrition_recovery_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="sage_nutrition_architect",
                suggestion_type=SuggestionType.NUTRITION_TIMING,
                priority=SuggestionPriority.MEDIUM,
                timing=SuggestionTiming.WITHIN_HOUR,
                title="🌙 Nutrición para Recuperación",
                message="Momento ideal para optimizar tu recuperación nocturna con nutrientes específicos.",
                action_items=[
                    "Consumir 25-30g proteína caseína",
                    "Incluir magnesio (300-400mg) para relajación",
                    "Evitar carbohidratos simples las próximas 2 horas",
                ],
                reasoning="Timing nocturno + ventana de recuperación = optimización del sueño reparador",
                context={"night_time": True, "recovery_window": True},
                confidence_score=0.75,
                expected_impact={
                    "adherence": 0.12,
                    "performance": 0.15,
                    "satisfaction": 0.20,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now() + timedelta(minutes=30),
                expires_at=datetime.now() + timedelta(hours=3),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_recovery_suggestions(
        self, user_context: UserContext, behavior_insights: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias de recuperación."""
        suggestions = []

        # Sugerencia de recuperación por estrés
        if user_context.stress_level > 0.7:
            suggestion = ProactiveSuggestion(
                suggestion_id=f"recovery_stress_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="wave_recovery_analytics",
                suggestion_type=SuggestionType.RECOVERY_REMINDER,
                priority=SuggestionPriority.HIGH,
                timing=SuggestionTiming.IMMEDIATE,
                title="🛡️ Recuperación Activa por Estrés",
                message=f"Estrés elevado detectado ({user_context.stress_level:.0%}). Tu cuerpo necesita recuperación activa.",
                action_items=[
                    "Realizar 10 minutos de respiración profunda",
                    "Aplicar compresión/masaje en músculos tensos",
                    "Planificar sueño de 8+ horas esta noche",
                ],
                reasoning="Estrés >70% compromete recuperación y puede afectar rendimiento futuro",
                context={
                    "stress_level": user_context.stress_level,
                    "recovery_urgent": True,
                },
                confidence_score=0.88,
                expected_impact={
                    "adherence": 0.25,
                    "performance": 0.20,
                    "satisfaction": 0.30,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=6),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_motivation_suggestions(
        self, user_context: UserContext, goal_analysis: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias motivacionales."""
        suggestions = []

        # Sugerencia motivacional por baja adherencia
        if (
            user_context.adherence_trend == "declining"
            and user_context.motivation_level < 0.5
        ):
            suggestion = ProactiveSuggestion(
                suggestion_id=f"motivation_boost_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="spark_motivation_coach",
                suggestion_type=SuggestionType.MOTIVATION_BOOST,
                priority=SuggestionPriority.HIGH,
                timing=SuggestionTiming.IMMEDIATE,
                title="💪 Reencontrando Tu Motivación",
                message="He notado que tu adherencia ha disminuido. Recuerda por qué empezaste este journey.",
                action_items=[
                    "Revisar tus objetivos originales (2 minutos)",
                    "Visualizar tu 'por qué' principal",
                    "Comprometerte con una acción pequeña hoy",
                ],
                reasoning="Adherencia declinante + motivación baja = ventana crítica para intervención",
                context={"adherence_trend": "declining", "motivation_low": True},
                confidence_score=0.72,
                expected_impact={
                    "adherence": 0.35,
                    "performance": 0.15,
                    "satisfaction": 0.40,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=12),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_habit_suggestions(
        self, user_context: UserContext, behavior_insights: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias de refuerzo de hábitos."""
        suggestions = []

        # Sugerencia de habit stacking
        if (
            user_context.day_of_week in ["monday", "sunday"]
            and user_context.time_of_day == "evening"
        ):
            suggestion = ProactiveSuggestion(
                suggestion_id=f"habit_planning_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="spark_motivation_coach",
                suggestion_type=SuggestionType.HABIT_REINFORCEMENT,
                priority=SuggestionPriority.MEDIUM,
                timing=SuggestionTiming.WEEKLY_PLANNING,
                title="🔗 Planificación Semanal de Hábitos",
                message="Momento perfecto para planificar y reforzar tus hábitos clave para la semana.",
                action_items=[
                    "Revisar adherencia de la semana anterior",
                    "Identificar 1-2 hábitos a mejorar",
                    "Conectar nuevos hábitos con rutinas existentes",
                ],
                reasoning="Inicio/fin de semana = momento óptimo para planificación de hábitos",
                context={"weekly_planning": True, "habit_review": True},
                confidence_score=0.68,
                expected_impact={
                    "adherence": 0.28,
                    "performance": 0.12,
                    "satisfaction": 0.20,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now() + timedelta(hours=1),
                expires_at=datetime.now() + timedelta(days=2),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_goal_suggestions(
        self, user_context: UserContext, goal_analysis: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias de ajuste de objetivos."""
        suggestions = []

        # Si hay objetivos en riesgo según el análisis
        at_risk_goals = goal_analysis.get("at_risk_goals", [])
        if at_risk_goals and len(at_risk_goals) > 0:
            suggestion = ProactiveSuggestion(
                suggestion_id=f"goal_adjustment_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="stella_progress_tracker",
                suggestion_type=SuggestionType.GOAL_ADJUSTMENT,
                priority=SuggestionPriority.HIGH,
                timing=SuggestionTiming.WEEKLY_PLANNING,
                title="🎯 Ajuste Inteligente de Objetivos",
                message=f"He detectado {len(at_risk_goals)} objetivo(s) que podrían beneficiarse de un ajuste estratégico.",
                action_items=[
                    "Revisar timeline y expectativas realistas",
                    "Dividir objetivos grandes en micro-metas",
                    "Ajustar métricas de progreso si es necesario",
                ],
                reasoning="Objetivos en riesgo requieren intervención temprana para evitar frustración",
                context={
                    "at_risk_goals": len(at_risk_goals),
                    "adjustment_needed": True,
                },
                confidence_score=0.85,
                expected_impact={
                    "adherence": 0.30,
                    "performance": 0.20,
                    "satisfaction": 0.35,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now() + timedelta(hours=2),
                expires_at=datetime.now() + timedelta(days=7),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_social_suggestions(
        self, user_context: UserContext, opportunities: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias de engagement social."""
        suggestions = []

        # Si hay oportunidades sociales
        social_opps = opportunities.get("social_opportunities", [])
        if "social_activity_suggestion" in social_opps:
            suggestion = ProactiveSuggestion(
                suggestion_id=f"social_engagement_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="aura_client_success",
                suggestion_type=SuggestionType.SOCIAL_ENGAGEMENT,
                priority=SuggestionPriority.MEDIUM,
                timing=SuggestionTiming.WITHIN_DAY,
                title="👥 Oportunidad de Actividad Social",
                message=f"Estás con {user_context.social_context} - ¡momento perfecto para una actividad wellness compartida!",
                action_items=[
                    "Proponer caminata de 20-30 minutos",
                    "Preparar una comida saludable juntos",
                    "Compartir tus objetivos y progreso",
                ],
                reasoning="Contexto social + bienestar = refuerzo positivo y accountability",
                context={
                    "social_context": user_context.social_context,
                    "shared_activity": True,
                },
                confidence_score=0.65,
                expected_impact={
                    "adherence": 0.22,
                    "performance": 0.10,
                    "satisfaction": 0.30,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now() + timedelta(minutes=30),
                expires_at=datetime.now() + timedelta(hours=8),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_biometric_suggestions(
        self, user_context: UserContext
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias basadas en biométricos."""
        suggestions = []

        # Esta función se expandiría con datos biométricos reales
        # Por ahora, sugerencia basada en el contexto disponible

        return suggestions

    async def _generate_seasonal_suggestions(
        self, user_context: UserContext
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias estacionales."""
        suggestions = []

        seasonal_tips = {
            "winter": {
                "title": "❄️ Optimización de Invierno",
                "message": "El invierno requiere ajustes específicos para mantener el momentum.",
                "actions": [
                    "Incrementar vitamina D",
                    "Entrenamientos indoor variados",
                    "Cuidar hidratación",
                ],
            },
            "spring": {
                "title": "🌱 Renovación de Primavera",
                "message": "Primavera es perfecta para renovar rutinas y aprovechar energía natural.",
                "actions": [
                    "Transición a actividades outdoor",
                    "Reset de objetivos",
                    "Detox suave",
                ],
            },
            "summer": {
                "title": "☀️ Adaptación de Verano",
                "message": "El calor requiere estrategias específicas para mantener rendimiento.",
                "actions": [
                    "Hidratación intensiva",
                    "Entrenamientos tempranos",
                    "Electrolitos extra",
                ],
            },
            "fall": {
                "title": "🍂 Estabilización de Otoño",
                "message": "Momento ideal para establecer rutinas sólidas antes del invierno.",
                "actions": [
                    "Rutinas indoor consistentes",
                    "Boost inmunitario",
                    "Planificación de año",
                ],
            },
        }

        if user_context.season in seasonal_tips:
            season_info = seasonal_tips[user_context.season]
            suggestion = ProactiveSuggestion(
                suggestion_id=f"seasonal_{user_context.season}_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="nova_biohacking_innovator",
                suggestion_type=SuggestionType.SEASONAL_ADAPTATION,
                priority=SuggestionPriority.LOW,
                timing=SuggestionTiming.WEEKLY_PLANNING,
                title=season_info["title"],
                message=season_info["message"],
                action_items=season_info["actions"],
                reasoning=f"Adaptación estacional para optimizar bienestar en {user_context.season}",
                context={"season": user_context.season, "seasonal_optimization": True},
                confidence_score=0.70,
                expected_impact={
                    "adherence": 0.15,
                    "performance": 0.12,
                    "satisfaction": 0.18,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now() + timedelta(hours=4),
                expires_at=datetime.now() + timedelta(days=30),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _generate_stress_suggestions(
        self, user_context: UserContext
    ) -> List[ProactiveSuggestion]:
        """Generar sugerencias de manejo del estrés."""
        suggestions = []

        if user_context.stress_level > 0.6:
            suggestion = ProactiveSuggestion(
                suggestion_id=f"stress_management_{user_context.user_id}_{int(datetime.now().timestamp())}",
                user_id=user_context.user_id,
                agent_id="wave_recovery_analytics",
                suggestion_type=SuggestionType.STRESS_MANAGEMENT,
                priority=SuggestionPriority.HIGH,
                timing=SuggestionTiming.IMMEDIATE,
                title="🧘 Manejo Inmediato del Estrés",
                message=f"Estrés detectado al {user_context.stress_level:.0%}. Intervención recomendada.",
                action_items=[
                    "Técnica 4-7-8: respiración por 5 minutos",
                    "Caminar suave por 10-15 minutos",
                    "Hidratación con té herbal relajante",
                ],
                reasoning="Estrés >60% afecta recuperación, sueño y adherencia a largo plazo",
                context={
                    "stress_level": user_context.stress_level,
                    "immediate_intervention": True,
                },
                confidence_score=0.85,
                expected_impact={
                    "adherence": 0.20,
                    "performance": 0.15,
                    "satisfaction": 0.35,
                },
                created_at=datetime.now(),
                optimal_delivery_time=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=4),
            )
            suggestions.append(suggestion)

        return suggestions

    async def _filter_suggestions(
        self, suggestions: List[ProactiveSuggestion], user_context: UserContext
    ) -> List[ProactiveSuggestion]:
        """Filtrar sugerencias por cooldowns y umbrales de confianza."""
        filtered = []

        for suggestion in suggestions:
            # Verificar umbral de confianza
            min_confidence = self.confidence_thresholds.get(
                suggestion.suggestion_type, 0.6
            )
            if suggestion.confidence_score < min_confidence:
                continue

            # Verificar cooldown
            if await self._is_on_cooldown(
                user_context.user_id, suggestion.suggestion_type
            ):
                continue

            filtered.append(suggestion)

        return filtered

    def _prioritize_suggestions(
        self, suggestions: List[ProactiveSuggestion]
    ) -> List[ProactiveSuggestion]:
        """Priorizar sugerencias por impacto esperado y urgencia."""

        def priority_score(suggestion: ProactiveSuggestion) -> float:
            # Peso por prioridad
            priority_weights = {
                SuggestionPriority.CRITICAL: 1.0,
                SuggestionPriority.HIGH: 0.8,
                SuggestionPriority.MEDIUM: 0.6,
                SuggestionPriority.LOW: 0.4,
                SuggestionPriority.INFO: 0.2,
            }

            # Peso por timing
            timing_weights = {
                SuggestionTiming.IMMEDIATE: 1.0,
                SuggestionTiming.WITHIN_HOUR: 0.9,
                SuggestionTiming.WITHIN_DAY: 0.7,
                SuggestionTiming.NEXT_WORKOUT: 0.6,
                SuggestionTiming.NEXT_MEAL: 0.6,
                SuggestionTiming.WEEKLY_PLANNING: 0.4,
                SuggestionTiming.MONTHLY_REVIEW: 0.2,
            }

            # Calcular score
            priority_weight = priority_weights.get(suggestion.priority, 0.5)
            timing_weight = timing_weights.get(suggestion.timing, 0.5)
            confidence_weight = suggestion.confidence_score

            # Impacto esperado (promedio de las métricas)
            impact_weight = sum(suggestion.expected_impact.values()) / len(
                suggestion.expected_impact
            )

            return (
                priority_weight * 0.3
                + timing_weight * 0.2
                + confidence_weight * 0.3
                + impact_weight * 0.2
            )

        return sorted(suggestions, key=priority_score, reverse=True)

    async def _optimize_delivery_timing(
        self, suggestions: List[ProactiveSuggestion], user_context: UserContext
    ) -> List[ProactiveSuggestion]:
        """Optimizar timing de entrega basado en contexto del usuario."""

        for suggestion in suggestions:
            # Ajustar timing basado en preferencias del usuario
            preferred_hours = user_context.communication_preferences.get(
                "preferred_hours", [9, 18]
            )

            if suggestion.timing == SuggestionTiming.IMMEDIATE:
                suggestion.optimal_delivery_time = datetime.now()
            elif suggestion.timing == SuggestionTiming.WITHIN_HOUR:
                suggestion.optimal_delivery_time = datetime.now() + timedelta(
                    minutes=30
                )
            elif suggestion.timing == SuggestionTiming.WITHIN_DAY:
                # Buscar próxima hora preferida
                now = datetime.now()
                for hour in preferred_hours:
                    delivery_time = now.replace(
                        hour=hour, minute=0, second=0, microsecond=0
                    )
                    if delivery_time > now:
                        suggestion.optimal_delivery_time = delivery_time
                        break
                else:
                    # Si no hay hora preferida hoy, usar mañana
                    tomorrow = now + timedelta(days=1)
                    suggestion.optimal_delivery_time = tomorrow.replace(
                        hour=preferred_hours[0], minute=0, second=0, microsecond=0
                    )

        return suggestions

    async def _is_on_cooldown(
        self, user_id: str, suggestion_type: SuggestionType
    ) -> bool:
        """Verificar si el tipo de sugerencia está en cooldown."""
        try:
            cooldown_key = f"suggestion_cooldown:{user_id}:{suggestion_type.value}"
            cooldown_data = await self.redis_client.get(cooldown_key)
            return cooldown_data is not None
        except Exception as e:
            logger.warning(f"Cooldown check failed: {e}")
            return False

    async def _set_suggestion_cooldown(
        self, user_id: str, suggestion_type: SuggestionType
    ) -> None:
        """Establecer cooldown para tipo de sugerencia."""
        try:
            cooldown_key = f"suggestion_cooldown:{user_id}:{suggestion_type.value}"
            cooldown_hours = self.suggestion_cooldowns[suggestion_type]
            await self.redis_client.setex(
                cooldown_key, timedelta(hours=cooldown_hours).total_seconds(), "active"
            )
        except Exception as e:
            logger.warning(f"Setting cooldown failed: {e}")

    async def _cache_suggestions(self, suggestions: List[ProactiveSuggestion]) -> None:
        """Cachear sugerencias para tracking."""
        try:
            for suggestion in suggestions:
                cache_key = f"suggestion:{suggestion.suggestion_id}"
                cache_data = asdict(suggestion)
                # Convertir datetime a ISO string para JSON
                cache_data["created_at"] = suggestion.created_at.isoformat()
                cache_data["optimal_delivery_time"] = (
                    suggestion.optimal_delivery_time.isoformat()
                )
                if suggestion.expires_at:
                    cache_data["expires_at"] = suggestion.expires_at.isoformat()

                await self.redis_client.setex(
                    cache_key,
                    timedelta(days=7).total_seconds(),
                    json.dumps(cache_data, default=str),
                )
        except Exception as e:
            logger.warning(f"Failed to cache suggestions: {e}")

    async def _get_user_historical_data(self, user_id: str) -> Dict[str, Any]:
        """Obtener datos históricos del usuario."""
        try:
            # En implementación real, esto vendría de Supabase
            # Por ahora, retornar datos mock básicos
            return {
                "workout_frequency": "4-5 times per week",
                "preferred_times": ["morning", "evening"],
                "nutrition_adherence": 0.75,
                "avg_motivation": 0.68,
                "stress_patterns": ["monday_high", "friday_moderate"],
                "successful_interventions": ["morning_motivation", "nutrition_timing"],
                "goal_completion_rate": 0.82,
            }
        except Exception as e:
            logger.warning(f"Failed to get historical data: {e}")
            return {}

    async def mark_suggestion_delivered(
        self, suggestion_id: str, delivery_method: str = "app_notification"
    ) -> bool:
        """Marcar sugerencia como entregada."""
        try:
            cache_key = f"suggestion:{suggestion_id}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                suggestion_data = json.loads(cached_data)
                suggestion_data["delivered"] = True
                suggestion_data["delivery_method"] = delivery_method
                suggestion_data["delivered_at"] = datetime.now().isoformat()

                await self.redis_client.setex(
                    cache_key,
                    timedelta(days=7).total_seconds(),
                    json.dumps(suggestion_data, default=str),
                )

                # Establecer cooldown
                suggestion_type = SuggestionType(suggestion_data["suggestion_type"])
                await self._set_suggestion_cooldown(
                    suggestion_data["user_id"], suggestion_type
                )

                logger.info(f"Suggestion {suggestion_id} marked as delivered")
                return True
        except Exception as e:
            logger.error(f"Failed to mark suggestion as delivered: {e}")

        return False

    async def record_suggestion_feedback(
        self, suggestion_id: str, user_response: str, effectiveness_score: float
    ) -> bool:
        """Registrar feedback del usuario sobre la sugerencia."""
        try:
            cache_key = f"suggestion:{suggestion_id}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                suggestion_data = json.loads(cached_data)
                suggestion_data["user_response"] = user_response
                suggestion_data["effectiveness_score"] = effectiveness_score
                suggestion_data["feedback_at"] = datetime.now().isoformat()

                await self.redis_client.setex(
                    cache_key,
                    timedelta(days=30).total_seconds(),  # Extender TTL para análisis
                    json.dumps(suggestion_data, default=str),
                )

                logger.info(
                    f"Feedback recorded for suggestion {suggestion_id}: {effectiveness_score}"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to record suggestion feedback: {e}")

        return False
