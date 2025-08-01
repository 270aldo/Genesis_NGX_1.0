"""
Staging tests for BLAZE (Elite Training Strategist) with real GCP connection.

Tests BLAZE's ability to:
- Generate personalized training plans
- Adapt exercises for injuries
- Optimize performance strategies
- Provide exercise form guidance
"""

import pytest

from agents.elite_training_strategist.agent import EliteTrainingStrategist
from tests.staging.base_agent_test import BaseAgentStagingTest


@pytest.mark.staging
class TestBlazeTrainingStaging(BaseAgentStagingTest):
    """Staging tests for BLAZE Elite Training agent."""

    @property
    def agent_name(self) -> str:
        return "BLAZE Elite Training"

    @property
    def agent_id(self) -> str:
        return "elite_training"

    @property
    def agent_class(self):
        return EliteTrainingStrategist

    def validate_complex_response(self, content: str, prompt: str):
        """Validate BLAZE's training plan quality."""
        # Should include structured plan
        assert any(
            word in content.lower() for word in ["semana", "día", "sesión"]
        ), "Training plan should include temporal structure"

        # Should mention specific exercises
        assert any(
            word in content.lower()
            for word in ["ejercicio", "serie", "repetición", "descanso"]
        ), "Should include specific exercise parameters"

        # Should include progression
        assert any(
            word in content.lower()
            for word in ["progres", "aument", "intensidad", "gradual"]
        ), "Should mention progression strategy"

    def validate_edge_case_response(self, content: str, prompt: str):
        """Validate BLAZE's injury adaptation response."""
        # Should prioritize safety
        assert any(
            word in content.lower()
            for word in ["segur", "cuidado", "evitar", "alternativ"]
        ), "Injury response should prioritize safety"

        # Should suggest modifications
        assert any(
            word in content.lower() for word in ["modific", "adapt", "sustitu"]
        ), "Should suggest exercise modifications"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_beginner_training_plan(self, agent_instance):
        """Test BLAZE's ability to create beginner-friendly plans."""
        prompt = "Soy principiante, nunca he hecho ejercicio. ¿Por dónde empiezo?"

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should emphasize gradual start
        assert any(
            word in content_lower
            for word in ["gradual", "poco a poco", "básico", "principiante"]
        ), "Beginner plan should emphasize gradual progression"

        # Should include fundamental exercises
        assert any(
            word in content_lower
            for word in ["caminar", "básico", "fundamental", "sencillo"]
        ), "Should include basic exercises for beginners"

        # Should mention form and technique
        assert any(
            word in content_lower
            for word in ["técnica", "forma", "correcto", "postura"]
        ), "Beginner guidance should emphasize proper form"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_advanced_performance_optimization(self, agent_instance):
        """Test BLAZE's advanced training optimization."""
        prompt = (
            "Soy atleta avanzado, quiero mejorar mi 1RM en sentadilla de 180kg a 200kg"
        )

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should include advanced concepts
        assert any(
            word in content_lower
            for word in ["periodización", "volumen", "intensidad", "rm"]
        ), "Advanced plan should use technical training concepts"

        # Should mention specific percentages or loads
        assert any(
            char in content_lower for char in ["%", "kg", "peso"]
        ), "Should include specific loading parameters"

        # Should include recovery strategies
        assert any(
            word in content_lower for word in ["recuperación", "descanso", "nutrición"]
        ), "Advanced plan should address recovery"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_injury_specific_adaptations(self, agent_instance):
        """Test BLAZE's injury adaptation capabilities."""
        injuries = [
            "Tengo dolor lumbar crónico",
            "Me lesioné el hombro derecho",
            "Tengo fascitis plantar",
        ]

        for injury_prompt in injuries:
            response = await agent_instance.process(
                injury_prompt + ", ¿qué ejercicios puedo hacer?"
            )
            content_lower = response["content"].lower()

            # Should acknowledge the injury
            assert any(
                word in injury_prompt.lower().split() for word in content_lower.split()
            ), f"Should acknowledge the specific injury: {injury_prompt}"

            # Should provide alternatives
            assert any(
                word in content_lower
                for word in ["evitar", "lugar de", "alternativ", "modific"]
            ), "Should provide exercise alternatives"

            # Should recommend professional consultation
            assert any(
                word in content_lower
                for word in ["médico", "fisioterapeuta", "profesional", "especialista"]
            ), "Should recommend professional consultation for injuries"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_sport_specific_training(self, agent_instance):
        """Test BLAZE's sport-specific training capabilities."""
        sports = {
            "fútbol": ["velocidad", "agilidad", "resistencia"],
            "powerlifting": ["fuerza", "técnica", "peso"],
            "maratón": ["resistencia", "ritmo", "largo"],
        }

        for sport, expected_keywords in sports.items():
            prompt = f"Necesito un plan de entrenamiento para mejorar en {sport}"
            response = await agent_instance.process(prompt)
            content_lower = response["content"].lower()

            # Should mention sport-specific elements
            keywords_found = sum(
                1 for keyword in expected_keywords if keyword in content_lower
            )
            assert (
                keywords_found >= 2
            ), f"Sport-specific plan for {sport} should mention at least 2 relevant concepts"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_exercise_form_guidance(self, agent_instance):
        """Test BLAZE's exercise form instruction capabilities."""
        prompt = "¿Cómo hago correctamente una sentadilla?"

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should include step-by-step instructions
        assert any(
            word in content_lower for word in ["paso", "primero", "luego", "finalmente"]
        ), "Form guidance should include step-by-step instructions"

        # Should mention key form points
        form_points = ["espalda", "rodilla", "pie", "cadera", "peso", "posición"]
        points_mentioned = sum(1 for point in form_points if point in content_lower)
        assert (
            points_mentioned >= 3
        ), f"Form guidance should mention at least 3 form points, found {points_mentioned}"

        # Should include safety tips
        assert any(
            word in content_lower for word in ["evitar", "no ", "cuidado", "importante"]
        ), "Should include safety warnings or tips"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    @pytest.mark.slow
    async def test_comprehensive_fitness_assessment(self, agent_instance):
        """Test BLAZE's comprehensive fitness planning."""
        prompt = """Tengo 35 años, peso 85kg, mido 1.75m.
        Puedo hacer 10 dominadas, corro 5km en 28 minutos.
        Quiero competir en CrossFit en 6 meses.
        Diseña un plan completo de preparación."""

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should analyze current fitness level
        assert any(
            word in content_lower
            for word in ["nivel", "actual", "base", "punto de partida"]
        ), "Should assess current fitness level"

        # Should create periodized plan
        assert any(
            word in content_lower for word in ["mes", "fase", "periodo", "etapa"]
        ), "Should create periodized training plan"

        # Should address CrossFit-specific elements
        crossfit_elements = ["fuerza", "resistencia", "gimnasia", "olímpico", "metcon"]
        elements_mentioned = sum(
            1 for element in crossfit_elements if element in content_lower
        )
        assert (
            elements_mentioned >= 3
        ), f"CrossFit plan should mention at least 3 specific elements, found {elements_mentioned}"

        # Should include competition preparation
        assert any(
            word in content_lower for word in ["competencia", "competir", "preparación"]
        ), "Should address competition preparation"
