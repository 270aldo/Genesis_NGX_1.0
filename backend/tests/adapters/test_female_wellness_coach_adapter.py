"""
Tests para el adaptador del Female Wellness Coach.

Este módulo contiene pruebas unitarias e integración para el adaptador
del Female Wellness Coach, verificando su funcionalidad específica
de salud femenina y protocolo A2A.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from infrastructure.adapters.female_wellness_coach_adapter import (
    FemaleWellnessCoachAdapter,
)
from agents.female_wellness_coach.schemas import (
    AnalyzeMenstrualCycleInput,
    CreateCycleBasedWorkoutInput,
    HormonalNutritionPlanInput,
)


class TestFemaleWellnessCoachAdapter:
    """Clase de pruebas para el FemaleWellnessCoachAdapter."""

    @pytest.fixture
    def adapter(self):
        """Fixture para crear una instancia del adaptador."""
        return FemaleWellnessCoachAdapter()

    @pytest.fixture
    def mock_agent(self):
        """Fixture para mockear el agente interno."""
        with patch(
            "infrastructure.adapters.female_wellness_coach_adapter.FemaleWellnessCoach"
        ) as mock:
            mock_agent = Mock()
            mock_agent._analyze_menstrual_cycle = AsyncMock()
            mock_agent._create_cycle_based_workout = AsyncMock()
            mock_agent._hormonal_nutrition_plan = AsyncMock()
            mock_agent.run_async = AsyncMock()
            mock.return_value = mock_agent
            yield mock_agent

    def test_initialization(self, adapter):
        """Prueba la inicialización correcta del adaptador."""
        assert adapter.fallback_keywords is not None
        assert len(adapter.fallback_keywords) > 0
        assert "ciclo menstrual" in adapter.fallback_keywords
        assert "menopausia" in adapter.fallback_keywords
        assert "salud femenina" in adapter.fallback_keywords

        assert adapter.excluded_keywords is not None
        assert "masculino" in adapter.excluded_keywords
        assert "testosterona" in adapter.excluded_keywords

    def test_create_default_context(self, adapter):
        """Prueba la creación del contexto por defecto."""
        context = adapter._create_default_context()

        assert "conversation_history" in context
        assert "user_profile" in context
        assert "cycle_analyses" in context
        assert "workout_plans" in context
        assert "nutrition_plans" in context
        assert "menopause_support" in context
        assert "bone_health_assessments" in context
        assert "emotional_wellness_sessions" in context
        assert "last_updated" in context

        # Verificar estructura del perfil de usuario
        user_profile = context["user_profile"]
        assert "age" in user_profile
        assert "life_stage" in user_profile
        assert user_profile["life_stage"] == "reproductive"
        assert "menstrual_data" in user_profile
        assert "health_conditions" in user_profile
        assert "medications" in user_profile
        assert "lifestyle_factors" in user_profile

    def test_intent_mapping(self, adapter):
        """Prueba el mapeo de intenciones específico."""
        mapping = adapter._get_intent_to_query_type_mapping()

        # Verificar mapeos específicos de salud femenina
        assert mapping["menstrual_cycle"] == "analyze_menstrual_cycle"
        assert mapping["cycle_analysis"] == "analyze_menstrual_cycle"
        assert mapping["period_tracking"] == "analyze_menstrual_cycle"

        assert mapping["hormonal_workout"] == "create_cycle_based_workout"
        assert mapping["female_training"] == "create_cycle_based_workout"
        assert mapping["cycle_fitness"] == "create_cycle_based_workout"

        assert mapping["hormonal_nutrition"] == "hormonal_nutrition_plan"
        assert mapping["female_nutrition"] == "hormonal_nutrition_plan"
        assert mapping["women_diet"] == "hormonal_nutrition_plan"

        assert mapping["menopause"] == "manage_menopause"
        assert mapping["perimenopause"] == "manage_menopause"
        assert mapping["hot_flashes"] == "manage_menopause"

        assert mapping["bone_health"] == "assess_bone_health"
        assert mapping["osteoporosis"] == "assess_bone_health"
        assert mapping["calcium_needs"] == "assess_bone_health"

        assert mapping["emotional_wellness"] == "emotional_wellness_support"
        assert mapping["mood_support"] == "emotional_wellness_support"
        assert mapping["hormonal_mood"] == "emotional_wellness_support"

    @pytest.mark.asyncio
    async def test_classification_with_female_keywords(self, adapter):
        """Prueba la clasificación con palabras clave femeninas."""
        # Mock del método padre
        with patch.object(
            adapter.__class__.__bases__[1], "_classify_query", return_value=(0.5, {})
        ) as mock_base:
            # Consulta con palabras clave de alta prioridad
            score, metadata = await adapter._classify_query(
                "Tengo problemas con mi ciclo menstrual", "user123"
            )

            # Debe tener boost por palabras clave específicas
            assert score > 0.5  # Mayor que el score base
            assert metadata["female_health_keywords_detected"] is True
            assert metadata["keyword_boost"] > 0
            assert metadata["agent_specialization"] == "female_wellness"

    @pytest.mark.asyncio
    async def test_classification_without_female_keywords(self, adapter):
        """Prueba la clasificación sin palabras clave femeninas."""
        with patch.object(
            adapter.__class__.__bases__[1], "_classify_query", return_value=(0.5, {})
        ) as mock_base:
            # Consulta sin palabras clave específicas
            score, metadata = await adapter._classify_query(
                "¿Cómo hacer ejercicio?", "user123"
            )

            # No debe tener boost
            assert score == 0.5  # Igual al score base
            assert metadata["female_health_keywords_detected"] is False
            assert metadata["keyword_boost"] == 0

    def test_score_adjustment_with_context(self, adapter):
        """Prueba el ajuste de score basado en contexto."""
        # Contexto con datos de salud femenina
        context = {
            "cycle_data": {"last_period": "2024-01-01"},
            "life_stage": "perimenopause",
            "hormonal_symptoms": ["hot_flashes", "mood_swings"],
            "user_profile": {"gender": "female", "age": 45},
        }

        # Score base
        base_score = 0.5
        adjusted_score = adapter._adjust_score_based_on_context(base_score, context)

        # Debe ser significativamente mayor por múltiples factores
        assert adjusted_score > base_score
        assert adjusted_score <= 1.0  # No debe exceder 1.0

    def test_score_adjustment_without_context(self, adapter):
        """Prueba el ajuste de score sin contexto relevante."""
        context = {"random_data": "value"}

        base_score = 0.5
        adjusted_score = adapter._adjust_score_based_on_context(base_score, context)

        # Debe mantenerse igual o con ajuste mínimo
        assert adjusted_score == base_score

    @pytest.mark.asyncio
    async def test_determine_consultation_type_menstrual(self, adapter):
        """Prueba la determinación del tipo de consulta para ciclo menstrual."""
        consultation_type = adapter._determine_consultation_type(
            "Mi período está irregular", {}
        )
        assert consultation_type == "menstrual_cycle"

    @pytest.mark.asyncio
    async def test_determine_consultation_type_workout(self, adapter):
        """Prueba la determinación del tipo de consulta para entrenamiento."""
        consultation_type = adapter._determine_consultation_type(
            "¿Qué ejercicios puedo hacer durante la menstruación?", {}
        )
        assert consultation_type == "workout_planning"

    @pytest.mark.asyncio
    async def test_determine_consultation_type_nutrition(self, adapter):
        """Prueba la determinación del tipo de consulta para nutrición."""
        consultation_type = adapter._determine_consultation_type(
            "¿Qué suplementos necesito durante la menopausia?", {}
        )
        assert consultation_type == "nutrition"

    @pytest.mark.asyncio
    async def test_determine_consultation_type_menopause(self, adapter):
        """Prueba la determinación del tipo de consulta para menopausia."""
        consultation_type = adapter._determine_consultation_type(
            "Tengo sofocos muy fuertes", {}
        )
        assert consultation_type == "menopause"

    @pytest.mark.asyncio
    async def test_determine_consultation_type_bone_health(self, adapter):
        """Prueba la determinación del tipo de consulta para salud ósea."""
        consultation_type = adapter._determine_consultation_type(
            "Me preocupa la osteoporosis", {}
        )
        assert consultation_type == "bone_health"

    @pytest.mark.asyncio
    async def test_determine_consultation_type_emotional(self, adapter):
        """Prueba la determinación del tipo de consulta para bienestar emocional."""
        consultation_type = adapter._determine_consultation_type(
            "Me siento muy estresada y mi estado de ánimo cambia mucho", {}
        )
        assert consultation_type == "emotional_wellness"

    @pytest.mark.asyncio
    async def test_determine_consultation_type_with_context(self, adapter):
        """Prueba la determinación del tipo con contexto específico."""
        consultation_type = adapter._determine_consultation_type(
            "Necesito ayuda", {"cycle_data": {"phase": "luteal"}}
        )
        assert consultation_type == "menstrual_cycle"

    def test_fallback_keywords_coverage(self, adapter):
        """Prueba que las palabras clave cubran todos los aspectos importantes."""
        keywords = [kw.lower() for kw in adapter.fallback_keywords]

        # Verificar cobertura de temas principales
        cycle_keywords = any(
            kw in keywords for kw in ["ciclo", "menstruación", "período"]
        )
        hormone_keywords = any(
            kw in keywords for kw in ["hormonas", "estrógeno", "progesterona"]
        )
        menopause_keywords = any(
            kw in keywords for kw in ["menopausia", "perimenopausia", "sofocos"]
        )
        health_keywords = any(kw in keywords for kw in ["salud femenina", "mujer"])
        nutrition_keywords = any(
            kw in keywords for kw in ["hierro", "calcio", "ácido fólico"]
        )

        assert cycle_keywords, "Faltan palabras clave de ciclo menstrual"
        assert hormone_keywords, "Faltan palabras clave hormonales"
        assert menopause_keywords, "Faltan palabras clave de menopausia"
        assert health_keywords, "Faltan palabras clave de salud femenina"
        assert nutrition_keywords, "Faltan palabras clave nutricionales"

    def test_excluded_keywords_appropriate(self, adapter):
        """Prueba que las palabras excluidas sean apropiadas."""
        excluded = [kw.lower() for kw in adapter.excluded_keywords]

        # Verificar que excluya términos masculinos relevantes
        assert "masculino" in excluded or "hombre" in excluded
        assert "testosterona" in excluded
        assert "próstata" in excluded

    @pytest.mark.asyncio
    async def test_classification_with_multiple_keywords(self, adapter):
        """Prueba la clasificación con múltiples palabras clave."""
        with patch.object(
            adapter.__class__.__bases__[1], "_classify_query", return_value=(0.3, {})
        ) as mock_base:
            # Consulta con múltiples palabras clave de diferentes prioridades
            score, metadata = await adapter._classify_query(
                "Durante mi ciclo menstrual como mujer necesito hierro y calcio",
                "user123",
            )

            # Debe tener boost significativo por múltiples keywords
            assert score > 0.3
            assert metadata["keyword_boost"] > 0.3  # Múltiples keywords
            assert metadata["female_health_keywords_detected"] is True
