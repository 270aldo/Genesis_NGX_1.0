"""
Domain Specialized AI Models - NGX Agents Advanced AI
Modelos de IA especializados por dominio para personalización extrema.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

from clients.vertex_ai.vertex_ai_client import VertexAIClient
from core.telemetry import trace_async
from core.redis_pool import get_redis_client

logger = logging.getLogger(__name__)


class UserDomain(Enum):
    """Dominios de especialización de usuarios."""

    # Programa PRIME
    PRIME_BEGINNER = "prime_beginner"  # 0-6 meses experiencia
    PRIME_INTERMEDIATE = "prime_intermediate"  # 6-24 meses experiencia
    PRIME_ADVANCED = "prime_advanced"  # 2+ años experiencia
    PRIME_ATHLETE = "prime_athlete"  # Atletas competitivos

    # Programa LONGEVITY
    LONGEVITY_ACTIVE = "longevity_active"  # 45+ activos
    LONGEVITY_SENIOR = "longevity_senior"  # 60+ mantenimiento
    LONGEVITY_REHAB = "longevity_rehab"  # Rehabilitación/recuperación
    LONGEVITY_CHRONIC = "longevity_chronic"  # Condiciones crónicas

    # Especializaciones
    WEIGHT_LOSS = "weight_loss"  # Pérdida de peso primaria
    MUSCLE_GAIN = "muscle_gain"  # Ganancia muscular primaria
    ENDURANCE = "endurance"  # Resistencia/cardio
    STRENGTH = "strength"  # Fuerza pura
    WELLNESS = "wellness"  # Bienestar general
    PERFORMANCE = "performance"  # Alto rendimiento


class ModelSpecialization(Enum):
    """Tipos de especialización del modelo."""

    EXERCISE_PRESCRIPTION = "exercise_prescription"
    NUTRITION_PLANNING = "nutrition_planning"
    RECOVERY_OPTIMIZATION = "recovery_optimization"
    MOTIVATION_PSYCHOLOGY = "motivation_psychology"
    HABIT_FORMATION = "habit_formation"
    INJURY_PREVENTION = "injury_prevention"
    PROGRESS_TRACKING = "progress_tracking"
    LIFESTYLE_INTEGRATION = "lifestyle_integration"


@dataclass
class DomainProfile:
    """Perfil de dominio para un usuario."""

    user_id: str
    primary_domain: UserDomain
    secondary_domains: List[UserDomain]

    # Características demográficas
    age: int
    gender: str  # male, female, other
    fitness_level: str  # beginner, intermediate, advanced, elite

    # Condiciones y limitaciones
    medical_conditions: List[str]
    physical_limitations: List[str]
    dietary_restrictions: List[str]

    # Objetivos y preferencias
    primary_goals: List[str]
    secondary_goals: List[str]
    preferred_training_style: str
    available_time_per_week: int  # hours

    # Historial y contexto
    training_history_years: float
    injury_history: List[Dict[str, Any]]
    success_patterns: Dict[str, Any]
    failure_patterns: Dict[str, Any]

    # Psicográficos
    motivation_type: str  # intrinsic, extrinsic, mixed
    personality_traits: Dict[str, float]  # openness, conscientiousness, etc.
    stress_response: str  # thrives, manages, struggles
    social_preference: str  # solo, group, mixed


@dataclass
class SpecializedRecommendation:
    """Recomendación especializada por dominio."""

    recommendation_id: str
    user_id: str
    domain: UserDomain
    specialization: ModelSpecialization

    # Contenido de la recomendación
    title: str
    description: str
    rationale: str

    # Detalles específicos
    protocol_adjustments: Dict[str, Any]
    personalization_factors: List[str]
    expected_outcomes: Dict[str, Any]

    # Métricas y seguimiento
    confidence_score: float
    relevance_score: float
    priority_level: int  # 1-10

    # Timing
    recommended_duration_weeks: int
    review_frequency_days: int

    # Metadata
    created_at: datetime
    expires_at: Optional[datetime]
    based_on_evidence: List[Dict[str, str]]  # estudios, papers, etc.


class DomainSpecializedModels:
    """
    Sistema de modelos de IA especializados por dominio.
    Proporciona personalización extrema basada en características únicas del usuario.
    """

    def __init__(self, vertex_ai_client: Optional[VertexAIClient] = None):
        """Inicializar sistema de modelos especializados."""
        self.vertex_ai_client = vertex_ai_client or VertexAIClient()
        self.redis_client = get_redis_client()

        # Configuración de especialización por dominio
        self.domain_specializations = {
            UserDomain.PRIME_BEGINNER: [
                ModelSpecialization.HABIT_FORMATION,
                ModelSpecialization.INJURY_PREVENTION,
                ModelSpecialization.MOTIVATION_PSYCHOLOGY,
            ],
            UserDomain.PRIME_ADVANCED: [
                ModelSpecialization.EXERCISE_PRESCRIPTION,
                ModelSpecialization.PERFORMANCE,
                ModelSpecialization.RECOVERY_OPTIMIZATION,
            ],
            UserDomain.LONGEVITY_ACTIVE: [
                ModelSpecialization.INJURY_PREVENTION,
                ModelSpecialization.LIFESTYLE_INTEGRATION,
                ModelSpecialization.WELLNESS,
            ],
            UserDomain.WEIGHT_LOSS: [
                ModelSpecialization.NUTRITION_PLANNING,
                ModelSpecialization.HABIT_FORMATION,
                ModelSpecialization.MOTIVATION_PSYCHOLOGY,
            ],
            UserDomain.MUSCLE_GAIN: [
                ModelSpecialization.EXERCISE_PRESCRIPTION,
                ModelSpecialization.NUTRITION_PLANNING,
                ModelSpecialization.RECOVERY_OPTIMIZATION,
            ],
        }

        # Parámetros de personalización por dominio
        self.domain_parameters = self._initialize_domain_parameters()

        logger.info("Domain Specialized Models system initialized")

    def _initialize_domain_parameters(self) -> Dict[UserDomain, Dict[str, Any]]:
        """Inicializar parámetros específicos por dominio."""
        return {
            UserDomain.PRIME_BEGINNER: {
                "complexity_level": "simple",
                "progression_rate": "gradual",
                "focus_areas": ["form", "consistency", "foundation"],
                "risk_tolerance": "low",
                "variety_level": "moderate",
            },
            UserDomain.PRIME_ADVANCED: {
                "complexity_level": "high",
                "progression_rate": "aggressive",
                "focus_areas": ["intensity", "periodization", "specialization"],
                "risk_tolerance": "moderate",
                "variety_level": "high",
            },
            UserDomain.LONGEVITY_ACTIVE: {
                "complexity_level": "moderate",
                "progression_rate": "conservative",
                "focus_areas": ["mobility", "balance", "functional"],
                "risk_tolerance": "very_low",
                "variety_level": "moderate",
            },
            UserDomain.WEIGHT_LOSS: {
                "caloric_deficit": "moderate",
                "macro_emphasis": "balanced",
                "cardio_ratio": "high",
                "behavioral_focus": "habits",
                "tracking_intensity": "detailed",
            },
            UserDomain.MUSCLE_GAIN: {
                "caloric_surplus": "moderate",
                "macro_emphasis": "protein",
                "strength_ratio": "high",
                "volume_progression": "linear",
                "recovery_emphasis": "high",
            },
        }

    @trace_async("create_domain_profile")
    async def create_domain_profile(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> DomainProfile:
        """
        Crear perfil de dominio personalizado para el usuario.

        Args:
            user_id: ID del usuario
            user_data: Datos completos del usuario

        Returns:
            Perfil de dominio especializado
        """
        try:
            # Determinar dominio primario
            primary_domain = await self._determine_primary_domain(user_data)

            # Identificar dominios secundarios
            secondary_domains = await self._identify_secondary_domains(
                user_data, primary_domain
            )

            # Extraer características demográficas
            demographics = self._extract_demographics(user_data)

            # Analizar historial y patrones
            patterns = await self._analyze_user_patterns(user_id, user_data)

            # Evaluar psicográficos
            psychographics = await self._evaluate_psychographics(user_data)

            profile = DomainProfile(
                user_id=user_id,
                primary_domain=primary_domain,
                secondary_domains=secondary_domains,
                age=demographics["age"],
                gender=demographics["gender"],
                fitness_level=demographics["fitness_level"],
                medical_conditions=user_data.get("medical_conditions", []),
                physical_limitations=user_data.get("physical_limitations", []),
                dietary_restrictions=user_data.get("dietary_restrictions", []),
                primary_goals=user_data.get("primary_goals", []),
                secondary_goals=user_data.get("secondary_goals", []),
                preferred_training_style=user_data.get("training_style", "balanced"),
                available_time_per_week=user_data.get("available_hours", 5),
                training_history_years=user_data.get("training_years", 0),
                injury_history=user_data.get("injury_history", []),
                success_patterns=patterns["success"],
                failure_patterns=patterns["failure"],
                motivation_type=psychographics["motivation_type"],
                personality_traits=psychographics["personality_traits"],
                stress_response=psychographics["stress_response"],
                social_preference=psychographics["social_preference"],
            )

            # Cachear perfil
            await self._cache_domain_profile(profile)

            logger.info(
                f"Created domain profile for user {user_id}: {primary_domain.value}"
            )

            return profile

        except Exception as e:
            logger.error(f"Failed to create domain profile for user {user_id}: {e}")
            raise

    @trace_async("generate_specialized_recommendations")
    async def generate_specialized_recommendations(
        self,
        profile: DomainProfile,
        specialization: ModelSpecialization,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[SpecializedRecommendation]:
        """
        Generar recomendaciones especializadas basadas en el dominio del usuario.

        Args:
            profile: Perfil de dominio del usuario
            specialization: Tipo de especialización requerida
            context: Contexto adicional

        Returns:
            Lista de recomendaciones especializadas
        """
        try:
            recommendations = []

            # Obtener parámetros del dominio
            domain_params = self.domain_parameters.get(profile.primary_domain, {})

            # Generar prompt especializado
            prompt = await self._create_specialized_prompt(
                profile, specialization, domain_params, context
            )

            # Usar IA para generar recomendaciones
            if self.vertex_ai_client:
                ai_response = await self.vertex_ai_client.generate_content_async(prompt)
                ai_recommendations = json.loads(ai_response)

                # Procesar cada recomendación
                for ai_rec in ai_recommendations:
                    recommendation = await self._process_ai_recommendation(
                        ai_rec, profile, specialization
                    )
                    recommendations.append(recommendation)

            # Aplicar filtros específicos del dominio
            filtered_recommendations = await self._apply_domain_filters(
                recommendations, profile
            )

            # Priorizar según el dominio
            prioritized_recommendations = self._prioritize_by_domain(
                filtered_recommendations, profile
            )

            logger.info(
                f"Generated {len(prioritized_recommendations)} specialized recommendations "
                f"for user {profile.user_id} in {specialization.value}"
            )

            return prioritized_recommendations[:5]  # Top 5 recomendaciones

        except Exception as e:
            logger.error(f"Failed to generate specialized recommendations: {e}")
            raise

    async def _determine_primary_domain(self, user_data: Dict[str, Any]) -> UserDomain:
        """Determinar el dominio primario del usuario usando IA."""

        prompt = f"""
        Analiza estos datos de usuario y determina su dominio primario:
        
        Datos del usuario:
        - Programa: {user_data.get('program_type', 'PRIME')}
        - Edad: {user_data.get('age', 'unknown')}
        - Experiencia: {user_data.get('training_years', 0)} años
        - Objetivos: {user_data.get('primary_goals', [])}
        - Nivel fitness: {user_data.get('fitness_level', 'beginner')}
        - Condiciones médicas: {user_data.get('medical_conditions', [])}
        
        Dominios disponibles:
        - PRIME: prime_beginner, prime_intermediate, prime_advanced, prime_athlete
        - LONGEVITY: longevity_active, longevity_senior, longevity_rehab, longevity_chronic
        - ESPECIALIZACIONES: weight_loss, muscle_gain, endurance, strength, wellness, performance
        
        Considera:
        1. Edad y programa para determinar PRIME vs LONGEVITY
        2. Experiencia y nivel para sub-categorías
        3. Objetivos primarios para especializaciones
        4. Condiciones médicas para consideraciones especiales
        
        Devuelve SOLO el nombre del dominio (ej: "prime_beginner").
        """

        try:
            if self.vertex_ai_client:
                response = await self.vertex_ai_client.generate_content_async(prompt)
                domain_name = response.strip().lower()

                # Validar y convertir
                for domain in UserDomain:
                    if domain.value == domain_name:
                        return domain
        except Exception as e:
            logger.warning(f"AI domain determination failed: {e}")

        # Fallback lógico
        age = user_data.get("age", 30)
        program = user_data.get("program_type", "PRIME")

        if program == "LONGEVITY" or age >= 45:
            if age >= 60:
                return UserDomain.LONGEVITY_SENIOR
            else:
                return UserDomain.LONGEVITY_ACTIVE
        else:
            experience = user_data.get("training_years", 0)
            if experience < 0.5:
                return UserDomain.PRIME_BEGINNER
            elif experience < 2:
                return UserDomain.PRIME_INTERMEDIATE
            else:
                return UserDomain.PRIME_ADVANCED

    async def _identify_secondary_domains(
        self, user_data: Dict[str, Any], primary_domain: UserDomain
    ) -> List[UserDomain]:
        """Identificar dominios secundarios relevantes."""
        secondary_domains = []

        # Basado en objetivos
        goals = user_data.get("primary_goals", []) + user_data.get(
            "secondary_goals", []
        )

        for goal in goals:
            goal_lower = goal.lower()
            if "weight" in goal_lower or "fat" in goal_lower:
                secondary_domains.append(UserDomain.WEIGHT_LOSS)
            elif "muscle" in goal_lower or "strength" in goal_lower:
                secondary_domains.append(UserDomain.MUSCLE_GAIN)
            elif "endurance" in goal_lower or "cardio" in goal_lower:
                secondary_domains.append(UserDomain.ENDURANCE)
            elif "performance" in goal_lower or "athletic" in goal_lower:
                secondary_domains.append(UserDomain.PERFORMANCE)

        # Remover duplicados y dominio primario
        secondary_domains = list(set(secondary_domains))
        if primary_domain in secondary_domains:
            secondary_domains.remove(primary_domain)

        return secondary_domains[:2]  # Máximo 2 dominios secundarios

    def _extract_demographics(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extraer información demográfica del usuario."""
        return {
            "age": user_data.get("age", 30),
            "gender": user_data.get("gender", "other"),
            "fitness_level": user_data.get("fitness_level", "beginner"),
        }

    async def _analyze_user_patterns(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analizar patrones de éxito y fracaso del usuario."""

        # Obtener historial del usuario (si existe)
        historical_data = user_data.get("historical_data", {})

        prompt = f"""
        Analiza los patrones de éxito y fracaso de este usuario:
        
        Historial: {json.dumps(historical_data, indent=2)}
        
        Identifica:
        1. Patrones de éxito (qué funciona bien)
        2. Patrones de fracaso (qué no funciona)
        3. Triggers de abandono
        4. Factores motivacionales
        
        Devuelve un JSON con estructura:
        {{
            "success": {{
                "patterns": [],
                "conditions": [],
                "strategies": []
            }},
            "failure": {{
                "patterns": [],
                "triggers": [],
                "barriers": []
            }}
        }}
        """

        try:
            if self.vertex_ai_client and historical_data:
                response = await self.vertex_ai_client.generate_content_async(prompt)
                return json.loads(response)
        except Exception as e:
            logger.warning(f"Pattern analysis failed: {e}")

        # Fallback patterns
        return {
            "success": {
                "patterns": ["consistency", "gradual_progression"],
                "conditions": ["clear_goals", "social_support"],
                "strategies": ["habit_stacking", "reward_system"],
            },
            "failure": {
                "patterns": ["overambition", "inconsistency"],
                "triggers": ["time_pressure", "plateau"],
                "barriers": ["complexity", "lack_of_progress"],
            },
        }

    async def _evaluate_psychographics(
        self, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluar características psicográficas del usuario."""

        prompt = f"""
        Evalúa las características psicográficas basándote en estos datos:
        
        Respuestas a cuestionarios: {user_data.get('questionnaire_responses', {})}
        Comportamiento en app: {user_data.get('app_behavior', {})}
        Preferencias declaradas: {user_data.get('preferences', {})}
        
        Determina:
        1. Tipo de motivación (intrinsic/extrinsic/mixed)
        2. Rasgos de personalidad (Big 5: openness, conscientiousness, extraversion, agreeableness, neuroticism)
        3. Respuesta al estrés (thrives/manages/struggles)
        4. Preferencia social (solo/group/mixed)
        
        Devuelve JSON con esta estructura exacta.
        """

        try:
            if self.vertex_ai_client:
                response = await self.vertex_ai_client.generate_content_async(prompt)
                return json.loads(response)
        except Exception as e:
            logger.warning(f"Psychographic evaluation failed: {e}")

        # Fallback psychographics
        return {
            "motivation_type": "mixed",
            "personality_traits": {
                "openness": 0.6,
                "conscientiousness": 0.7,
                "extraversion": 0.5,
                "agreeableness": 0.6,
                "neuroticism": 0.4,
            },
            "stress_response": "manages",
            "social_preference": "mixed",
        }

    async def _create_specialized_prompt(
        self,
        profile: DomainProfile,
        specialization: ModelSpecialization,
        domain_params: Dict[str, Any],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """Crear prompt especializado para generación de recomendaciones."""

        # Mapeo de especialización a instrucciones
        specialization_instructions = {
            ModelSpecialization.EXERCISE_PRESCRIPTION: """
            Genera prescripciones de ejercicio altamente específicas considerando:
            - Nivel actual y progresión apropiada
            - Limitaciones físicas y médicas
            - Tiempo disponible y preferencias
            - Principios de periodización
            """,
            ModelSpecialization.NUTRITION_PLANNING: """
            Crea planes nutricionales personalizados considerando:
            - Objetivos calóricos y macronutrientes
            - Restricciones dietéticas
            - Preferencias culturales y gustos
            - Timing de nutrientes para rendimiento
            """,
            ModelSpecialization.RECOVERY_OPTIMIZATION: """
            Optimiza protocolos de recuperación considerando:
            - Edad y capacidad de recuperación
            - Intensidad del entrenamiento
            - Calidad del sueño y estrés
            - Técnicas de recuperación activa/pasiva
            """,
            ModelSpecialization.MOTIVATION_PSYCHOLOGY: """
            Desarrolla estrategias motivacionales basadas en:
            - Tipo de motivación del usuario
            - Patrones de éxito previos
            - Barreras psicológicas identificadas
            - Técnicas de cambio conductual
            """,
            ModelSpecialization.HABIT_FORMATION: """
            Diseña sistemas de formación de hábitos considerando:
            - Nivel actual de consistencia
            - Rutinas existentes
            - Principios de habit stacking
            - Refuerzo positivo apropiado
            """,
        }

        instructions = specialization_instructions.get(
            specialization, "Genera recomendaciones personalizadas apropiadas."
        )

        prompt = f"""
        Genera recomendaciones especializadas en {specialization.value} para este usuario:
        
        PERFIL DE DOMINIO:
        - Dominio primario: {profile.primary_domain.value}
        - Edad: {profile.age} años
        - Género: {profile.gender}
        - Nivel fitness: {profile.fitness_level}
        - Años entrenando: {profile.training_history_years}
        
        CONDICIONES Y LIMITACIONES:
        - Médicas: {profile.medical_conditions}
        - Físicas: {profile.physical_limitations}
        - Dietéticas: {profile.dietary_restrictions}
        
        OBJETIVOS:
        - Primarios: {profile.primary_goals}
        - Secundarios: {profile.secondary_goals}
        - Tiempo disponible: {profile.available_time_per_week} horas/semana
        
        PSICOGRÁFICOS:
        - Motivación: {profile.motivation_type}
        - Respuesta al estrés: {profile.stress_response}
        - Preferencia social: {profile.social_preference}
        
        PARÁMETROS DEL DOMINIO:
        {json.dumps(domain_params, indent=2)}
        
        INSTRUCCIONES ESPECÍFICAS:
        {instructions}
        
        CONTEXTO ADICIONAL:
        {json.dumps(context or {}, indent=2)}
        
        Genera 3-5 recomendaciones en formato JSON:
        [{{
            "title": "Título claro y motivador",
            "description": "Descripción detallada",
            "rationale": "Por qué esta recomendación para este usuario",
            "protocol_adjustments": {{}},
            "personalization_factors": [],
            "expected_outcomes": {{}},
            "confidence": 0.0-1.0,
            "relevance": 0.0-1.0,
            "priority": 1-10,
            "duration_weeks": número,
            "review_days": número,
            "evidence": []
        }}]
        """

        return prompt

    async def _process_ai_recommendation(
        self,
        ai_rec: Dict[str, Any],
        profile: DomainProfile,
        specialization: ModelSpecialization,
    ) -> SpecializedRecommendation:
        """Procesar recomendación de IA en formato estructurado."""

        recommendation_id = f"{profile.user_id}_{specialization.value}_{int(datetime.now().timestamp())}"

        return SpecializedRecommendation(
            recommendation_id=recommendation_id,
            user_id=profile.user_id,
            domain=profile.primary_domain,
            specialization=specialization,
            title=ai_rec.get("title", ""),
            description=ai_rec.get("description", ""),
            rationale=ai_rec.get("rationale", ""),
            protocol_adjustments=ai_rec.get("protocol_adjustments", {}),
            personalization_factors=ai_rec.get("personalization_factors", []),
            expected_outcomes=ai_rec.get("expected_outcomes", {}),
            confidence_score=ai_rec.get("confidence", 0.8),
            relevance_score=ai_rec.get("relevance", 0.9),
            priority_level=ai_rec.get("priority", 5),
            recommended_duration_weeks=ai_rec.get("duration_weeks", 4),
            review_frequency_days=ai_rec.get("review_days", 7),
            created_at=datetime.now(),
            expires_at=datetime.now()
            + timedelta(weeks=ai_rec.get("duration_weeks", 4)),
            based_on_evidence=ai_rec.get("evidence", []),
        )

    async def _apply_domain_filters(
        self, recommendations: List[SpecializedRecommendation], profile: DomainProfile
    ) -> List[SpecializedRecommendation]:
        """Aplicar filtros específicos del dominio."""

        filtered = []

        for rec in recommendations:
            # Filtros por dominio
            if profile.primary_domain in [
                UserDomain.LONGEVITY_SENIOR,
                UserDomain.LONGEVITY_REHAB,
            ]:
                # Filtrar recomendaciones de alta intensidad
                if "high_intensity" in str(rec.protocol_adjustments).lower():
                    continue

            elif profile.primary_domain == UserDomain.PRIME_BEGINNER:
                # Filtrar recomendaciones demasiado complejas
                if "advanced" in rec.title.lower() or rec.priority_level > 7:
                    rec.priority_level = min(7, rec.priority_level)

            # Filtros por condiciones médicas
            if profile.medical_conditions:
                # Verificar contraindicaciones
                if await self._check_medical_compatibility(
                    rec, profile.medical_conditions
                ):
                    filtered.append(rec)
            else:
                filtered.append(rec)

        return filtered

    async def _check_medical_compatibility(
        self, recommendation: SpecializedRecommendation, medical_conditions: List[str]
    ) -> bool:
        """Verificar compatibilidad con condiciones médicas."""

        # Lista de contraindicaciones conocidas
        contraindications = {
            "hypertension": ["valsalva", "heavy_lifting", "inverted"],
            "diabetes": ["extreme_fasting", "very_low_carb"],
            "arthritis": ["high_impact", "repetitive_joint_stress"],
            "heart_condition": ["max_effort", "breath_holding"],
        }

        rec_text = f"{recommendation.title} {recommendation.description}".lower()

        for condition in medical_conditions:
            condition_lower = condition.lower()
            if condition_lower in contraindications:
                for contraindicated in contraindications[condition_lower]:
                    if contraindicated in rec_text:
                        return False

        return True

    def _prioritize_by_domain(
        self, recommendations: List[SpecializedRecommendation], profile: DomainProfile
    ) -> List[SpecializedRecommendation]:
        """Priorizar recomendaciones según el dominio."""

        # Ajustar prioridades basadas en el dominio
        for rec in recommendations:
            # Boost para objetivos primarios
            for goal in profile.primary_goals:
                if (
                    goal.lower() in rec.title.lower()
                    or goal.lower() in rec.description.lower()
                ):
                    rec.priority_level = min(10, rec.priority_level + 2)

            # Ajustes por dominio
            if profile.primary_domain == UserDomain.PRIME_BEGINNER:
                if rec.specialization == ModelSpecialization.HABIT_FORMATION:
                    rec.priority_level = min(10, rec.priority_level + 1)

            elif profile.primary_domain == UserDomain.WEIGHT_LOSS:
                if rec.specialization == ModelSpecialization.NUTRITION_PLANNING:
                    rec.priority_level = min(10, rec.priority_level + 1)

        # Ordenar por prioridad
        return sorted(recommendations, key=lambda x: x.priority_level, reverse=True)

    async def _cache_domain_profile(self, profile: DomainProfile) -> None:
        """Cachear perfil de dominio."""
        try:
            cache_key = f"domain_profile:{profile.user_id}"
            cache_data = asdict(profile)

            # Convertir enums a strings
            cache_data["primary_domain"] = profile.primary_domain.value
            cache_data["secondary_domains"] = [
                d.value for d in profile.secondary_domains
            ]

            await self.redis_client.setex(
                cache_key,
                timedelta(days=30).total_seconds(),
                json.dumps(cache_data, default=str),
            )
        except Exception as e:
            logger.warning(f"Failed to cache domain profile: {e}")

    async def get_cached_profile(self, user_id: str) -> Optional[DomainProfile]:
        """Obtener perfil de dominio cacheado."""
        try:
            cache_key = f"domain_profile:{user_id}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                data = json.loads(cached_data)

                # Reconstruir enums
                data["primary_domain"] = UserDomain(data["primary_domain"])
                data["secondary_domains"] = [
                    UserDomain(d) for d in data["secondary_domains"]
                ]

                return DomainProfile(**data)

        except Exception as e:
            logger.warning(f"Failed to get cached profile: {e}")

        return None

    @trace_async("adapt_protocols_by_domain")
    async def adapt_protocols_by_domain(
        self, profile: DomainProfile, base_protocol: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adaptar protocolos base según el dominio del usuario.

        Args:
            profile: Perfil de dominio del usuario
            base_protocol: Protocolo base a adaptar

        Returns:
            Protocolo adaptado al dominio
        """
        try:
            adapted_protocol = base_protocol.copy()

            # Obtener adaptaciones específicas del dominio
            domain_adaptations = await self._get_domain_adaptations(profile)

            # Aplicar adaptaciones
            if profile.primary_domain in [UserDomain.PRIME_BEGINNER]:
                adapted_protocol = self._adapt_for_beginner(adapted_protocol, profile)

            elif profile.primary_domain in [
                UserDomain.LONGEVITY_SENIOR,
                UserDomain.LONGEVITY_ACTIVE,
            ]:
                adapted_protocol = self._adapt_for_longevity(adapted_protocol, profile)

            elif profile.primary_domain == UserDomain.WEIGHT_LOSS:
                adapted_protocol = self._adapt_for_weight_loss(
                    adapted_protocol, profile
                )

            elif profile.primary_domain == UserDomain.MUSCLE_GAIN:
                adapted_protocol = self._adapt_for_muscle_gain(
                    adapted_protocol, profile
                )

            # Aplicar restricciones médicas
            if profile.medical_conditions:
                adapted_protocol = await self._apply_medical_restrictions(
                    adapted_protocol, profile.medical_conditions
                )

            # Optimizar por tiempo disponible
            if profile.available_time_per_week < 3:
                adapted_protocol = self._optimize_for_limited_time(adapted_protocol)

            logger.info(f"Protocol adapted for domain {profile.primary_domain.value}")

            return adapted_protocol

        except Exception as e:
            logger.error(f"Failed to adapt protocol: {e}")
            return base_protocol

    def _adapt_for_beginner(
        self, protocol: Dict[str, Any], profile: DomainProfile
    ) -> Dict[str, Any]:
        """Adaptar protocolo para principiantes."""

        # Reducir volumen e intensidad
        if "volume" in protocol:
            protocol["volume"] = int(protocol["volume"] * 0.6)

        if "intensity" in protocol:
            protocol["intensity"] = min(protocol["intensity"], 0.7)

        # Enfoque en técnica
        protocol["focus_areas"] = ["form", "breathing", "mind_muscle_connection"]

        # Progresión más gradual
        protocol["progression_rate"] = "slow"
        protocol["deload_frequency"] = "every_3_weeks"

        return protocol

    def _adapt_for_longevity(
        self, protocol: Dict[str, Any], profile: DomainProfile
    ) -> Dict[str, Any]:
        """Adaptar protocolo para longevidad."""

        # Enfoque en movilidad y funcionalidad
        protocol["warmup_duration"] = 15  # minutos
        protocol["cooldown_duration"] = 10

        # Reducir impacto
        protocol["exercise_modifications"] = {
            "jumps": "step_ups",
            "running": "walking",
            "heavy_lifts": "moderate_resistance",
        }

        # Incluir trabajo de equilibrio
        protocol["balance_work"] = True
        protocol["flexibility_emphasis"] = "high"

        return protocol

    def _adapt_for_weight_loss(
        self, protocol: Dict[str, Any], profile: DomainProfile
    ) -> Dict[str, Any]:
        """Adaptar protocolo para pérdida de peso."""

        # Aumentar componente cardiovascular
        protocol["cardio_ratio"] = 0.6
        protocol["strength_ratio"] = 0.4

        # Enfoque metabólico
        protocol["rest_periods"] = "short"
        protocol["circuit_training"] = True
        protocol["metabolic_finishers"] = True

        # Tracking detallado
        protocol["track_calories"] = True
        protocol["weekly_measurements"] = True

        return protocol

    def _adapt_for_muscle_gain(
        self, protocol: Dict[str, Any], profile: DomainProfile
    ) -> Dict[str, Any]:
        """Adaptar protocolo para ganancia muscular."""

        # Enfoque en hipertrofia
        protocol["rep_range"] = "8-12"
        protocol["time_under_tension"] = "40-60s"
        protocol["rest_periods"] = "moderate"

        # Volumen progresivo
        protocol["volume_progression"] = "linear"
        protocol["frequency_per_muscle"] = 2

        # Nutrición específica
        protocol["protein_timing"] = "critical"
        protocol["post_workout_window"] = "30min"

        return protocol

    async def _get_domain_adaptations(self, profile: DomainProfile) -> Dict[str, Any]:
        """Obtener adaptaciones específicas del dominio."""

        # Esto podría venir de una base de datos de mejores prácticas
        # Por ahora, retornar adaptaciones básicas

        return {
            "volume_multiplier": 1.0,
            "intensity_cap": 1.0,
            "rest_adjustment": 1.0,
            "exercise_substitutions": {},
            "special_considerations": [],
        }

    async def _apply_medical_restrictions(
        self, protocol: Dict[str, Any], medical_conditions: List[str]
    ) -> Dict[str, Any]:
        """Aplicar restricciones médicas al protocolo."""

        for condition in medical_conditions:
            condition_lower = condition.lower()

            if "hypertension" in condition_lower:
                protocol["avoid_exercises"] = protocol.get("avoid_exercises", []) + [
                    "overhead_press",
                    "leg_press",
                    "inverted_rows",
                ]
                protocol["breathing_emphasis"] = "high"

            elif "diabetes" in condition_lower:
                protocol["blood_sugar_monitoring"] = True
                protocol["steady_state_cardio"] = True

            elif "arthritis" in condition_lower:
                protocol["low_impact"] = True
                protocol["joint_protection"] = True

        return protocol

    def _optimize_for_limited_time(self, protocol: Dict[str, Any]) -> Dict[str, Any]:
        """Optimizar protocolo para tiempo limitado."""

        protocol["workout_format"] = "full_body"
        protocol["frequency"] = "2-3x_week"
        protocol["duration_per_session"] = "30-45min"
        protocol["compound_movements"] = True
        protocol["isolation_exercises"] = "minimal"

        return protocol
