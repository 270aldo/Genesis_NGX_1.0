"""
Staging tests for Orchestrator agent with real GCP connection.

Tests the Orchestrator's ability to:
- Route requests to appropriate agents
- Coordinate multi-agent responses
- Manage conversation context
"""

import pytest

from agents.orchestrator.agent import OrchestratorAgent
from tests.staging.base_agent_test import BaseAgentStagingTest


@pytest.mark.staging
class TestOrchestratorStaging(BaseAgentStagingTest):
    """Staging tests for Orchestrator agent."""

    @property
    def agent_name(self) -> str:
        return "NEXUS Orchestrator"

    @property
    def agent_id(self) -> str:
        return "orchestrator"

    @property
    def agent_class(self):
        return OrchestratorAgent

    def validate_complex_response(self, content: str, prompt: str):
        """Validate Orchestrator's complex response quality."""
        # Orchestrator should identify multiple aspects
        assert any(
            word in content.lower() for word in ["entrenamiento", "nutrición", "plan"]
        ), "Orchestrator should identify training and nutrition aspects"

        # Should suggest involving multiple agents
        assert any(
            word in content.lower()
            for word in ["completo", "integral", "personalizado"]
        ), "Orchestrator should suggest comprehensive approach"

    def validate_edge_case_response(self, content: str, prompt: str):
        """Validate Orchestrator's edge case handling."""
        # Should ask clarifying questions
        assert any(
            word in content.lower()
            for word in ["objetivo", "meta", "específico", "ayudar"]
        ), "Orchestrator should ask for clarification on vague requests"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_intent_classification(self, agent_instance):
        """Test Orchestrator's ability to classify user intent."""
        test_cases = [
            {
                "prompt": "Quiero ganar músculo",
                "expected_agents": ["elite_training", "nutrition"],
                "expected_intent": "fitness_goal",
            },
            {
                "prompt": "¿Cómo está mi progreso esta semana?",
                "expected_agents": ["progress_tracker", "analytics"],
                "expected_intent": "progress_check",
            },
            {
                "prompt": "Necesito motivación para entrenar",
                "expected_agents": ["motivation"],
                "expected_intent": "motivation_request",
            },
        ]

        for test_case in test_cases:
            response = await agent_instance.process(test_case["prompt"])

            assert response is not None
            assert "content" in response

            # Check if response mentions expected agents or concepts
            content_lower = response["content"].lower()
            assert any(
                agent in content_lower
                or self._get_agent_keywords(agent) in content_lower
                for agent in test_case["expected_agents"]
            ), f"Response should reference {test_case['expected_agents']} for '{test_case['prompt']}'"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_multi_domain_request(self, agent_instance, metrics_collector):
        """Test handling requests that span multiple domains."""
        prompt = "Quiero un plan completo: ejercicios, dieta y seguimiento de progreso para 3 meses"

        response = await agent_instance.process(prompt)

        assert response is not None
        content_lower = response["content"].lower()

        # Should mention multiple domains
        domains = ["ejercicio", "nutrición", "progreso", "seguimiento"]
        mentioned_domains = sum(1 for domain in domains if domain in content_lower)

        assert (
            mentioned_domains >= 3
        ), f"Multi-domain request should mention at least 3 domains, found {mentioned_domains}"

        # Should suggest structured approach
        assert any(
            word in content_lower for word in ["plan", "programa", "estrategia"]
        ), "Should suggest structured approach for multi-domain request"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_conversation_context_management(self, agent_instance):
        """Test Orchestrator's ability to maintain conversation context."""
        # First message
        response1 = await agent_instance.process("Quiero perder peso")
        assert response1 is not None

        # Follow-up message (should remember context)
        response2 = await agent_instance.process("¿Cuántas calorías debo comer?")
        assert response2 is not None

        # Response should reference weight loss context
        content_lower = response2["content"].lower()
        assert any(
            word in content_lower for word in ["peso", "déficit", "objetivo"]
        ), "Follow-up response should maintain weight loss context"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_agent_coordination_suggestion(self, agent_instance):
        """Test Orchestrator's ability to suggest agent coordination."""
        prompt = "Tengo una lesión en la rodilla pero quiero seguir entrenando"

        response = await agent_instance.process(prompt)
        content_lower = response["content"].lower()

        # Should suggest careful approach
        assert any(
            word in content_lower
            for word in ["cuidado", "precaución", "adaptar", "modificar"]
        ), "Should suggest careful approach for injury"

        # Should mention recovery or alternative exercises
        assert any(
            word in content_lower
            for word in ["recuperación", "alternativ", "bajo impacto"]
        ), "Should suggest recovery-focused approach"

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    @pytest.mark.slow
    async def test_high_complexity_orchestration(
        self, agent_instance, performance_thresholds
    ):
        """Test orchestration of highly complex requests."""
        prompt = """Tengo 45 años, diabetes tipo 2, sobrepeso de 20kg.
        Quiero un plan integral que incluya: ejercicios seguros,
        dieta para controlar glucosa, suplementos, y seguimiento semanal.
        También me interesa el biohacking para mejorar mi salud."""

        import time

        start_time = time.time()

        response = await agent_instance.process(prompt)
        elapsed_time = time.time() - start_time

        assert response is not None
        content_lower = response["content"].lower()

        # Should address all mentioned aspects
        aspects = ["diabetes", "ejercicio", "dieta", "glucosa", "seguimiento", "salud"]
        addressed_aspects = sum(1 for aspect in aspects if aspect in content_lower)

        assert (
            addressed_aspects >= 4
        ), f"Complex request should address at least 4 aspects, found {addressed_aspects}"

        # Should emphasize safety
        assert any(
            word in content_lower
            for word in ["médico", "segur", "supervisión", "cuidado"]
        ), "Should emphasize medical supervision for complex health case"

        # Performance check (complex requests may take longer)
        assert (
            elapsed_time < performance_thresholds["complex_response_time"] * 1.5
        ), f"High complexity response time {elapsed_time:.2f}s exceeded extended threshold"

    def _get_agent_keywords(self, agent_id: str) -> str:
        """Get keywords associated with each agent for validation."""
        keywords = {
            "elite_training": "entrenamiento",
            "nutrition": "nutrición",
            "progress_tracker": "progreso",
            "analytics": "análisis",
            "motivation": "motivación",
            "wellness": "bienestar",
            "biohacking": "optimización",
            "genetic": "genética",
        }
        return keywords.get(agent_id, agent_id)
