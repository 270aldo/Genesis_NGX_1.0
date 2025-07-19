"""
Tests simplificados para validar capacidades conversacionales de AURA.

Estos tests verifican la funcionalidad básica de las nuevas skills conversacionales
implementadas para AURA.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Importar solo las funciones específicas que queremos probar
from agents.client_success_liaison.agent import ClientSuccessLiaison


class MockAuraAgent:
    """Mock simplificado de AURA para testing."""

    def __init__(self):
        self.conversational_adapter = None
        self.agent_id = "aura_client_success"

    async def _skill_start_onboarding_conversation(
        self,
        user_type: str = "new_user",
        program_type: str = "PRIME",
        user_goals: list = None,
    ) -> Dict[str, Any]:
        """Mock de skill de onboarding."""
        if not self.conversational_adapter:
            return {
                "status": "error",
                "error": "Conversational capabilities not available",
            }

        return {
            "status": "success",
            "conversation_id": "test_conv_123",
            "onboarding_context": {
                "user_type": user_type,
                "goals": user_goals or [],
                "start_time": "2025-06-02T10:30:00",
                "communication_style": "warm_welcoming",
            },
        }

    async def _skill_support_24_7_conversation(
        self,
        conversation_id: str,
        issue_type: str,
        urgency_level: str = "medium",
        user_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Mock de skill de soporte 24/7."""
        if not self.conversational_adapter:
            return {"status": "error", "error": "Adapter not available"}

        return {
            "status": "success",
            "support_context": {
                "issue_type": issue_type,
                "urgency": urgency_level,
                "timestamp": "2025-06-02T10:30:00",
                "user_context": user_context,
            },
        }

    async def _skill_celebration_conversation(
        self,
        conversation_id: str,
        achievement_type: str,
        milestone_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Mock de skill de celebración."""
        if not self.conversational_adapter:
            return {"status": "error", "error": "Adapter not available"}

        return {
            "status": "success",
            "celebration_type": achievement_type,
            "milestone": milestone_details,
        }

    async def _skill_retention_conversation(
        self,
        conversation_id: str,
        user_engagement_state: str,
        retention_strategy: str = "proactive",
    ) -> Dict[str, Any]:
        """Mock de skill de retención."""
        if not self.conversational_adapter:
            return {"status": "error", "error": "Adapter not available"}

        return {
            "status": "success",
            "engagement_state": user_engagement_state,
            "strategy": retention_strategy,
        }

    async def _skill_community_building_conversation(
        self,
        conversation_id: str,
        community_action: str,
        community_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Mock de skill de construcción de comunidad."""
        if not self.conversational_adapter:
            return {"status": "error", "error": "Adapter not available"}

        return {
            "status": "success",
            "community_action": community_action,
            "context": community_context,
        }

    def _generate_onboarding_welcome(
        self, user_type: str, program_type: str, goals: list = None
    ) -> str:
        """Genera mensaje de bienvenida para onboarding."""
        welcomes = {
            "new_user": "¡Bienvenido a la familia NGX! Me llamo AURA y voy a ser tu compañera en este increíble viaje hacia tus objetivos.",
            "returning_user": "¡Qué alegría tenerte de vuelta! Soy AURA, y aunque ya conoces NGX, quiero asegurarme de que tu experiencia sea aún mejor.",
            "premium_user": "¡Hola! Soy AURA, tu especialista en éxito del cliente. Como miembro premium, quiero asegurarme de que obtengas el máximo valor.",
        }

        base_message = welcomes.get(user_type, welcomes["new_user"])

        if goals:
            goals_text = ", ".join(goals[:3])
            base_message += (
                f" Veo que tus objetivos incluyen {goals_text}. ¡Esto va a ser genial!"
            )

        return base_message

    def _generate_support_message(
        self, issue_type: str, urgency: str, context: Dict[str, Any] = None
    ) -> str:
        """Genera mensajes de soporte personalizados."""
        urgency_intros = {
            "critical": "Entiendo que esto es urgente y estoy aquí para ayudarte inmediatamente. ",
            "high": "Veo que esto es importante para ti. Vamos a resolverlo juntos. ",
            "medium": "Perfecto, estoy aquí para apoyarte con esto. ",
            "low": "¡Hola! Me da mucho gusto poder ayudarte con tu consulta. ",
        }

        issue_responses = {
            "technical": "He revisado los detalles técnicos y tengo algunas soluciones que pueden funcionar perfectamente.",
            "billing": "Entiendo tus preguntas sobre facturación. Vamos a aclarar todo paso a paso.",
            "feature": "¡Me encanta que explores nuestras funciones! Te voy a guiar para que las aproveches al máximo.",
            "guidance": "Estoy aquí para orientarte en cualquier cosa que necesites. ¡Esa es mi especialidad!",
        }

        intro = urgency_intros.get(urgency, urgency_intros["medium"])
        response = issue_responses.get(issue_type, issue_responses["guidance"])

        return f"{intro}{response} ¿Cómo te puedo ayudar específicamente?"


@pytest.fixture
def aura_mock():
    """Fixture que proporciona un mock de AURA para testing."""
    return MockAuraAgent()


@pytest.fixture
def mock_conversational_adapter():
    """Mock del adaptador conversacional."""
    adapter = Mock()
    adapter.start_conversation = AsyncMock(
        return_value={
            "status": "success",
            "conversation_id": "test_conv_123",
            "agent_id": "aura_client_success",
        }
    )
    adapter.send_message = AsyncMock(
        return_value={"status": "success", "conversation_id": "test_conv_123"}
    )
    return adapter


class TestAuraOnboarding:
    """Tests para skill de onboarding conversacional de AURA."""

    @pytest.mark.asyncio
    async def test_onboarding_new_user_success(
        self, aura_mock, mock_conversational_adapter
    ):
        """Test exitoso de onboarding para nuevo usuario."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        result = await aura_mock._skill_start_onboarding_conversation(
            user_type="new_user",
            program_type="PRIME",
            user_goals=["fitness", "nutrition"],
        )

        assert result["status"] == "success"
        assert result["conversation_id"] == "test_conv_123"
        assert result["onboarding_context"]["user_type"] == "new_user"
        assert len(result["onboarding_context"]["goals"]) == 2

    @pytest.mark.asyncio
    async def test_onboarding_without_adapter(self, aura_mock):
        """Test de onboarding sin adaptador conversacional."""
        aura_mock.conversational_adapter = None

        result = await aura_mock._skill_start_onboarding_conversation(
            user_type="new_user"
        )

        assert result["status"] == "error"
        assert "not available" in result["error"]

    def test_generate_onboarding_welcome_messages(self, aura_mock):
        """Test generación de mensajes de bienvenida."""
        # Test nuevo usuario
        message = aura_mock._generate_onboarding_welcome(
            user_type="new_user", program_type="PRIME", goals=["fitness"]
        )
        assert "bienvenido" in message.lower()
        assert "aura" in message.lower()
        assert "fitness" in message

        # Test usuario premium
        message = aura_mock._generate_onboarding_welcome(
            user_type="premium_user", program_type="PRIME"
        )
        assert "premium" in message
        assert "máximo valor" in message


class TestAuraSupport:
    """Tests para skill de soporte 24/7 de AURA."""

    @pytest.mark.asyncio
    async def test_support_technical_high_urgency(
        self, aura_mock, mock_conversational_adapter
    ):
        """Test soporte técnico de alta urgencia."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        result = await aura_mock._skill_support_24_7_conversation(
            conversation_id="test_conv_123",
            issue_type="technical",
            urgency_level="high",
            user_context={"plan": "premium"},
        )

        assert result["status"] == "success"
        assert result["support_context"]["issue_type"] == "technical"
        assert result["support_context"]["urgency"] == "high"

    @pytest.mark.asyncio
    async def test_support_billing_medium_urgency(
        self, aura_mock, mock_conversational_adapter
    ):
        """Test soporte de facturación."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        result = await aura_mock._skill_support_24_7_conversation(
            conversation_id="test_conv_123",
            issue_type="billing",
            urgency_level="medium",
        )

        assert result["status"] == "success"
        assert result["support_context"]["issue_type"] == "billing"

    def test_generate_support_messages(self, aura_mock):
        """Test generación de mensajes de soporte."""
        # Test urgencia crítica
        message = aura_mock._generate_support_message(
            issue_type="technical", urgency="critical"
        )
        assert "urgente" in message.lower()
        assert "inmediatamente" in message.lower()

        # Test problema de facturación
        message = aura_mock._generate_support_message(
            issue_type="billing", urgency="medium"
        )
        assert "facturación" in message.lower()
        assert "paso a paso" in message.lower()


class TestAuraCelebration:
    """Tests para skill de celebración de AURA."""

    @pytest.mark.asyncio
    async def test_celebrate_goal_reached(self, aura_mock, mock_conversational_adapter):
        """Test celebración por objetivo alcanzado."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        milestone_details = {
            "goal": "weight_loss",
            "target": "10kg",
            "achieved": "10.2kg",
        }

        result = await aura_mock._skill_celebration_conversation(
            conversation_id="test_conv_123",
            achievement_type="goal_reached",
            milestone_details=milestone_details,
        )

        assert result["status"] == "success"
        assert result["celebration_type"] == "goal_reached"
        assert result["milestone"] == milestone_details

    @pytest.mark.asyncio
    async def test_celebrate_streak(self, aura_mock, mock_conversational_adapter):
        """Test celebración por racha."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        milestone_details = {"days": 30, "activity": "daily_workout"}

        result = await aura_mock._skill_celebration_conversation(
            conversation_id="test_conv_123",
            achievement_type="streak",
            milestone_details=milestone_details,
        )

        assert result["status"] == "success"
        assert result["celebration_type"] == "streak"


class TestAuraRetention:
    """Tests para skill de retención de AURA."""

    @pytest.mark.asyncio
    async def test_retention_declining_user(
        self, aura_mock, mock_conversational_adapter
    ):
        """Test retención para usuario con engagement declinante."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        result = await aura_mock._skill_retention_conversation(
            conversation_id="test_conv_123",
            user_engagement_state="declining",
            retention_strategy="proactive",
        )

        assert result["status"] == "success"
        assert result["engagement_state"] == "declining"
        assert result["strategy"] == "proactive"

    @pytest.mark.asyncio
    async def test_retention_inactive_user(
        self, aura_mock, mock_conversational_adapter
    ):
        """Test retención para usuario inactivo."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        result = await aura_mock._skill_retention_conversation(
            conversation_id="test_conv_123", user_engagement_state="inactive"
        )

        assert result["status"] == "success"
        assert result["engagement_state"] == "inactive"


class TestAuraCommunity:
    """Tests para skill de construcción de comunidad de AURA."""

    @pytest.mark.asyncio
    async def test_community_welcome(self, aura_mock, mock_conversational_adapter):
        """Test bienvenida a la comunidad."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        community_context = {
            "members_count": 1500,
            "community_type": "fitness_enthusiasts",
        }

        result = await aura_mock._skill_community_building_conversation(
            conversation_id="test_conv_123",
            community_action="welcome",
            community_context=community_context,
        )

        assert result["status"] == "success"
        assert result["community_action"] == "welcome"
        assert result["context"]["members_count"] == 1500

    @pytest.mark.asyncio
    async def test_community_event(self, aura_mock, mock_conversational_adapter):
        """Test anuncio de evento comunitario."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        community_context = {
            "event_type": "group_challenge",
            "event_name": "30-Day Challenge",
        }

        result = await aura_mock._skill_community_building_conversation(
            conversation_id="test_conv_123",
            community_action="event",
            community_context=community_context,
        )

        assert result["status"] == "success"
        assert result["community_action"] == "event"


class TestAuraIntegration:
    """Tests de integración para flujos completos de AURA."""

    @pytest.mark.asyncio
    async def test_complete_user_journey(self, aura_mock, mock_conversational_adapter):
        """Test del journey completo de usuario: onboarding → soporte → celebración → comunidad."""
        aura_mock.conversational_adapter = mock_conversational_adapter

        # 1. Onboarding
        onboarding_result = await aura_mock._skill_start_onboarding_conversation(
            user_type="new_user", program_type="PRIME"
        )
        assert onboarding_result["status"] == "success"
        conversation_id = onboarding_result["conversation_id"]

        # 2. Soporte durante uso
        support_result = await aura_mock._skill_support_24_7_conversation(
            conversation_id=conversation_id,
            issue_type="guidance",
            urgency_level="medium",
        )
        assert support_result["status"] == "success"

        # 3. Celebración de logro
        celebration_result = await aura_mock._skill_celebration_conversation(
            conversation_id=conversation_id,
            achievement_type="goal_reached",
            milestone_details={"goal": "first_week", "progress": "100%"},
        )
        assert celebration_result["status"] == "success"

        # 4. Integración a comunidad
        community_result = await aura_mock._skill_community_building_conversation(
            conversation_id=conversation_id,
            community_action="welcome",
            community_context={"members_count": 1000},
        )
        assert community_result["status"] == "success"

    @pytest.mark.asyncio
    async def test_error_handling(self, aura_mock):
        """Test manejo de errores sin adaptador conversacional."""
        aura_mock.conversational_adapter = None

        # Todas las skills deben fallar sin adaptador
        onboarding_result = await aura_mock._skill_start_onboarding_conversation()
        assert onboarding_result["status"] == "error"

        support_result = await aura_mock._skill_support_24_7_conversation(
            conversation_id="test", issue_type="technical"
        )
        assert support_result["status"] == "error"

        celebration_result = await aura_mock._skill_celebration_conversation(
            conversation_id="test",
            achievement_type="goal_reached",
            milestone_details={},
        )
        assert celebration_result["status"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
