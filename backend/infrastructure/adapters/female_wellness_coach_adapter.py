"""
Adaptador para el agente FemaleWellnessCoach que utiliza los componentes optimizados.

Este adaptador extiende el agente FemaleWellnessCoach original y sobrescribe los métodos
necesarios para utilizar el sistema A2A optimizado y el cliente Vertex AI optimizado.
"""

from typing import Dict, Any
from datetime import datetime

from agents.female_wellness_coach.agent import FemaleWellnessCoach
from infrastructure.adapters.base_agent_adapter import BaseAgentAdapter
from core.logging_config import get_logger

# Configurar logger
logger = get_logger(__name__)


class FemaleWellnessCoachAdapter(FemaleWellnessCoach, BaseAgentAdapter):
    """
    Adaptador para el agente FemaleWellnessCoach que utiliza los componentes optimizados.

    Este adaptador extiende el agente FemaleWellnessCoach original y utiliza la clase
    BaseAgentAdapter para implementar métodos comunes.
    """

    def __init__(self, **kwargs):
        """
        Inicializa el adaptador del Female Wellness Coach.

        Args:
            **kwargs: Argumentos adicionales para la inicialización
        """
        # Configurar palabras clave específicas para salud femenina
        self.fallback_keywords = [
            "ciclo menstrual",
            "menstruación",
            "período",
            "regla",
            "ovulación",
            "hormonas femeninas",
            "estrógeno",
            "progesterona",
            "perimenopausia",
            "menopausia",
            "sofocos",
            "salud femenina",
            "mujer",
            "embarazo",
            "postparto",
            "lactancia",
            "anticonceptivos",
            "síndrome premenstrual",
            "salud ósea",
            "osteoporosis",
            "calcio",
            "hierro",
            "ácido fólico",
            "entrenamiento femenino",
            "ejercicio menstruación",
            "deporte mujer",
        ]

        self.excluded_keywords = [
            "masculino",
            "hombre",
            "testosterona",
            "próstata",
            "calvicie masculina",
        ]

        # Inicializar el agente padre
        super().__init__(**kwargs)

        logger.info("FemaleWellnessCoachAdapter inicializado con protocolo A2A")

    def _create_default_context(self) -> Dict[str, Any]:
        """
        Crea un contexto predeterminado para el agente FemaleWellnessCoach.

        Returns:
            Dict[str, Any]: Contexto predeterminado específico para salud femenina
        """
        return {
            "conversation_history": [],
            "user_profile": {
                "age": None,
                "life_stage": "reproductive",
                "menstrual_data": {},
                "health_conditions": [],
                "medications": [],
                "lifestyle_factors": {},
            },
            "cycle_analyses": [],
            "workout_plans": [],
            "nutrition_plans": [],
            "menopause_support": [],
            "bone_health_assessments": [],
            "emotional_wellness_sessions": [],
            "last_updated": datetime.now().isoformat(),
        }

    def _get_intent_to_query_type_mapping(self) -> Dict[str, str]:
        """
        Obtiene el mapeo de intenciones a tipos de consulta específico para FemaleWellnessCoach.

        Returns:
            Dict[str, str]: Mapeo de intenciones a tipos de consulta
        """
        return {
            "menstrual_cycle": "analyze_menstrual_cycle",
            "cycle_analysis": "analyze_menstrual_cycle",
            "period_tracking": "analyze_menstrual_cycle",
            "hormonal_workout": "create_cycle_based_workout",
            "female_training": "create_cycle_based_workout",
            "cycle_fitness": "create_cycle_based_workout",
            "hormonal_nutrition": "hormonal_nutrition_plan",
            "female_nutrition": "hormonal_nutrition_plan",
            "women_diet": "hormonal_nutrition_plan",
            "menopause": "manage_menopause",
            "perimenopause": "manage_menopause",
            "hot_flashes": "manage_menopause",
            "bone_health": "assess_bone_health",
            "osteoporosis": "assess_bone_health",
            "calcium_needs": "assess_bone_health",
            "emotional_wellness": "emotional_wellness_support",
            "mood_support": "emotional_wellness_support",
            "hormonal_mood": "emotional_wellness_support",
        }

    def _adjust_score_based_on_context(
        self, score: float, context: Dict[str, Any]
    ) -> float:
        """
        Ajusta la puntuación de clasificación basada en el contexto específico de salud femenina.

        Args:
            score: Puntuación de clasificación original
            context: Contexto adicional para la clasificación

        Returns:
            Puntuación ajustada basada en indicadores de salud femenina
        """
        adjusted_score = score

        # Aumentar score si hay datos específicos de salud femenina en el contexto
        if context:
            # Verificar si hay datos del ciclo menstrual
            if context.get("cycle_data") or context.get("menstrual_data"):
                adjusted_score *= 1.3

            # Verificar si hay información sobre etapa de vida femenina
            life_stage = context.get("life_stage")
            if life_stage in ["perimenopause", "menopause", "postmenopause"]:
                adjusted_score *= 1.4

            # Verificar si hay síntomas hormonales reportados
            hormonal_symptoms = context.get("hormonal_symptoms", [])
            if hormonal_symptoms:
                adjusted_score *= 1.2

            # Verificar si el usuario está marcado como femenino
            user_profile = context.get("user_profile", {})
            if (
                user_profile.get("gender") == "female"
                or user_profile.get("sex") == "female"
            ):
                adjusted_score *= 1.2

            # Verificar edad para ajustar relevancia
            age = user_profile.get("age")
            if age:
                if 15 <= age <= 55:  # Edad reproductiva típica
                    adjusted_score *= 1.1
                elif age > 45:  # Perimenopausia/menopausia
                    adjusted_score *= 1.2

        # Asegurar que no exceda 1.0
        return min(1.0, adjusted_score)

    async def _classify_query(
        self, query: str, user_id: str = None, context: Dict[str, Any] = None
    ) -> tuple[float, Dict[str, Any]]:
        """
        Clasifica una consulta específicamente para temas de salud femenina.

        Args:
            query: La consulta del usuario a clasificar
            user_id: ID del usuario (opcional)
            context: Contexto adicional para la clasificación (opcional)

        Returns:
            Tupla con la puntuación de clasificación y metadatos
        """
        # Usar la clasificación base
        base_score, metadata = await super()._classify_query(query, user_id, context)

        # Agregar clasificación específica para salud femenina
        query_lower = query.lower()

        # Palabras clave específicas de alta prioridad
        high_priority_keywords = [
            "ciclo menstrual",
            "menstruación",
            "período",
            "menopausia",
            "perimenopausia",
            "sofocos",
            "hormonas femeninas",
            "embarazo",
            "postparto",
            "lactancia",
            "salud femenina",
        ]

        # Palabras clave de prioridad media
        medium_priority_keywords = [
            "mujer",
            "femenino",
            "regla",
            "ovulación",
            "estrógeno",
            "progesterona",
            "calcio",
            "hierro",
            "ácido fólico",
        ]

        # Calcular boost por palabras clave específicas
        keyword_boost = 0.0

        for keyword in high_priority_keywords:
            if keyword in query_lower:
                keyword_boost += 0.3

        for keyword in medium_priority_keywords:
            if keyword in query_lower:
                keyword_boost += 0.1

        # Aplicar boost limitado
        boosted_score = min(1.0, base_score + keyword_boost)

        # Actualizar metadata
        metadata.update(
            {
                "female_health_keywords_detected": keyword_boost > 0,
                "keyword_boost": keyword_boost,
                "specialized_score": boosted_score,
                "agent_specialization": "female_wellness",
            }
        )

        logger.debug(
            f"Clasificación FemaleWellnessCoach - Base: {base_score:.3f}, "
            f"Boost: {keyword_boost:.3f}, Final: {boosted_score:.3f}"
        )

        return boosted_score, metadata


# Instancia global del adaptador siguiendo el patrón establecido
female_wellness_coach_adapter = FemaleWellnessCoachAdapter()
