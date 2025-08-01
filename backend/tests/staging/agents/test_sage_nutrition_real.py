"""
Staging tests for SAGE (Precision Nutrition Architect) with real GCP connection.

Tests SAGE's ability to:
- Create personalized meal plans
- Calculate macronutrients
- Handle dietary restrictions
- Provide supplement recommendations
"""

import pytest

from agents.precision_nutrition_architect.agent import PrecisionNutritionArchitect
from tests.staging.base_agent_test import BaseAgentStagingTest


@pytest.mark.staging
class TestSageNutritionStaging(BaseAgentStagingTest):
    """Staging tests for SAGE Nutrition agent."""

    @property
    def agent_name(self) -> str:
        return "SAGE Precision Nutrition"

    @property
    def agent_id(self) -> str:
        return "nutrition"

    @property
    def agent_class(self):
        return PrecisionNutritionArchitect

    def validate_complex_response(self, content: str, prompt: str):
        """Validate SAGE's meal plan quality."""
        # Should include macronutrient breakdown
        assert any(
            word in content.lower()
            for word in ["proteína", "carbohidrato", "grasa", "calorías"]
        ), "Meal plan should include macronutrient information"

        # Should provide specific meals
        assert any(
            word in content.lower()
            for word in ["desayuno", "almuerzo", "cena", "comida"]
        ), "Should include specific meal timing"

        # Should mention portions or quantities
        assert any(
            word in content.lower()
            for word in ["gramos", "taza", "porción", "cantidad"]
        ), "Should include specific portions"

    def validate_edge_case_response(self, content: str, prompt: str):
        """Validate SAGE's allergy handling."""
        # Should acknowledge restrictions
        assert any(
            word in content.lower()
            for word in ["alergia", "evitar", "alternativa", "sustituir"]
        ), "Should acknowledge dietary restrictions"

        # Should provide alternatives
        assert any(
            word in content.lower() for word in ["lugar", "cambiar", "opción", "puede"]
        ), "Should suggest alternatives"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_macro_calculation(self, agent_instance):
        """Test SAGE's macronutrient calculation abilities."""
        prompt = "Peso 70kg, quiero ganar músculo. ¿Cuántas proteínas necesito al día?"

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should provide specific protein recommendation
        assert any(
            char in content_lower for char in ["g", "gramo"]
        ), "Should provide specific gram measurements"

        # Should mention protein per kg bodyweight
        assert any(
            word in content_lower for word in ["kg", "peso", "corporal"]
        ), "Should relate protein to body weight"

        # Should provide a range or specific number
        import re

        numbers = re.findall(r"\d+", content_lower)
        assert len(numbers) > 0, "Should include specific numerical recommendations"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_dietary_restriction_handling(self, agent_instance):
        """Test SAGE's handling of dietary restrictions."""
        restrictions = {
            "vegano": ["planta", "vegetal", "legumbre", "tofu"],
            "sin gluten": ["gluten", "arroz", "quinoa", "maíz"],
            "keto": ["grasa", "carbohidrato", "cetosis", "bajo"],
        }

        for diet_type, expected_keywords in restrictions.items():
            prompt = f"Necesito un plan de comidas {diet_type} de 2000 calorías"
            response = await agent_instance.process(prompt)
            content_lower = response["content"].lower()

            # Should acknowledge the dietary restriction
            assert diet_type in content_lower or any(
                word in diet_type.split() for word in content_lower.split()
            ), f"Should acknowledge {diet_type} dietary requirement"

            # Should include relevant foods
            keywords_found = sum(
                1 for keyword in expected_keywords if keyword in content_lower
            )
            assert (
                keywords_found >= 2
            ), f"{diet_type} plan should mention at least 2 relevant foods/concepts"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_meal_timing_optimization(self, agent_instance):
        """Test SAGE's meal timing recommendations."""
        prompt = "Entreno a las 6am, ¿cómo debo organizar mis comidas?"

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should address pre-workout nutrition
        assert any(
            word in content_lower for word in ["antes", "pre-entreno", "previo"]
        ), "Should mention pre-workout nutrition"

        # Should address post-workout nutrition
        assert any(
            word in content_lower for word in ["después", "post-entreno", "posterior"]
        ), "Should mention post-workout nutrition"

        # Should provide specific timing
        assert any(
            word in content_lower for word in ["minutos", "hora", "tiempo"]
        ), "Should include specific timing recommendations"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_supplement_recommendations(self, agent_instance):
        """Test SAGE's supplement guidance."""
        prompt = "¿Qué suplementos recomiendas para ganar masa muscular?"

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should mention evidence-based supplements
        common_supplements = [
            "creatina",
            "proteína",
            "whey",
            "bcaa",
            "vitamina",
            "omega",
        ]
        supplements_mentioned = sum(
            1 for supp in common_supplements if supp in content_lower
        )
        assert (
            supplements_mentioned >= 2
        ), f"Should mention at least 2 common supplements, found {supplements_mentioned}"

        # Should include dosage or timing
        assert any(
            word in content_lower for word in ["dosis", "cantidad", "gramos", "día"]
        ), "Should include dosage information"

        # Should mention food-first approach
        assert any(
            word in content_lower for word in ["alimento", "comida", "dieta", "natural"]
        ), "Should emphasize food-first approach"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_caloric_deficit_planning(self, agent_instance):
        """Test SAGE's weight loss nutrition planning."""
        prompt = (
            "Quiero perder 10kg, peso 90kg y mido 1.80m. ¿Cuántas calorías debo comer?"
        )

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should calculate caloric needs
        assert any(
            word in content_lower for word in ["calorías", "déficit", "metabolismo"]
        ), "Should discuss caloric calculations"

        # Should provide specific numbers
        import re

        calorie_numbers = re.findall(r"\d{3,4}", content_lower)
        assert len(calorie_numbers) > 0, "Should provide specific calorie targets"

        # Should mention safe weight loss rate
        assert any(
            word in content_lower
            for word in ["gradual", "semana", "saludable", "sostenible"]
        ), "Should emphasize safe weight loss rate"

        # Should address macronutrient balance
        assert any(
            word in content_lower for word in ["proteína", "macro", "equilibrio"]
        ), "Should maintain macronutrient balance during deficit"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_hydration_guidance(self, agent_instance):
        """Test SAGE's hydration recommendations."""
        prompt = "¿Cuánta agua debo tomar si entreno 2 horas al día?"

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should provide specific water recommendations
        assert any(
            word in content_lower for word in ["litro", "ml", "vaso", "agua"]
        ), "Should provide specific hydration amounts"

        # Should consider training
        assert any(
            word in content_lower
            for word in ["entrenamiento", "ejercicio", "sudor", "pérdida"]
        ), "Should adjust for training demands"

        # Should mention electrolytes
        assert any(
            word in content_lower for word in ["electrolito", "sodio", "mineral", "sal"]
        ), "Should mention electrolyte considerations"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    @pytest.mark.slow
    async def test_comprehensive_nutrition_plan(self, agent_instance):
        """Test SAGE's comprehensive nutrition planning."""
        prompt = """Mujer, 28 años, 65kg, 1.65m.
        Entreno CrossFit 5 días/semana.
        Vegetariana, intolerante a lactosa.
        Objetivo: mejorar rendimiento y composición corporal.
        Crea un plan nutricional completo."""

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should address all constraints
        assert (
            "vegetarian" in content_lower
            or "plant" in content_lower
            or "vegetal" in content_lower
        ), "Should acknowledge vegetarian requirement"

        assert any(
            word in content_lower for word in ["lactosa", "lácteo", "alternativa"]
        ), "Should address lactose intolerance"

        # Should calculate appropriate calories
        assert any(
            word in content_lower for word in ["calorías", "energía", "total"]
        ), "Should provide caloric recommendations"

        # Should structure meal plan
        meal_times = ["desayuno", "almuerzo", "cena", "snack", "merienda"]
        meals_mentioned = sum(1 for meal in meal_times if meal in content_lower)
        assert (
            meals_mentioned >= 3
        ), f"Comprehensive plan should include at least 3 meal times, found {meals_mentioned}"

        # Should address performance nutrition
        assert any(
            word in content_lower for word in ["rendimiento", "energía", "recuperación"]
        ), "Should address performance nutrition for CrossFit"
