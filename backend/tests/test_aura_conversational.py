"""
Tests de capacidades conversacionales para AURA (Client Success Liaison).

Este módulo prueba las 5 skills conversacionales implementadas para AURA:
1. Onboarding conversations
2. 24/7 Support conversations
3. Celebration conversations
4. Retention conversations
5. Community building conversations
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Importar AURA y componentes relacionados
from agents.client_success_liaison.agent import ClientSuccessLiaison
from infrastructure.adapters.conversational_voice_adapter import (
    ConversationalVoiceAdapter,
    ConversationalMode,
)


@pytest.fixture
def aura_agent():
    """Fixture que proporciona una instancia de AURA para testing."""
    with (
        patch.multiple(
            "agents.client_success_liaison.agent",
            VertexAIClient=Mock(),
            SupabaseClient=Mock(),
            MCPToolkit=Mock(),
            ConversationalVoiceAdapter=Mock(),
            aiplatform=Mock(),
        ),
        patch("infrastructure.adapters.hybrid_voice_adapter.hybrid_voice_adapter"),
        patch("core.vision_processor.VisionProcessor"),
        patch("infrastructure.adapters.multimodal_adapter.MultimodalAdapter"),
    ):
        agent = ClientSuccessLiaison()
        agent.conversational_adapter = None  # Will be set by tests
        return agent


@pytest.fixture
def mock_conversational_adapter():
    """Mock del adaptador conversacional para testing."""
    adapter = Mock(spec=ConversationalVoiceAdapter)

    # Mock start_conversation
    adapter.start_conversation = AsyncMock(
        return_value={
            "status": "success",
            "conversation_id": "test_conv_123",
            "agent_id": "aura_client_success",
            "state": "conversation_active",
            "duration": 0.5,
            "websocket_connected": True,
        }
    )

    # Mock send_message
    adapter.send_message = AsyncMock(
        return_value={
            "status": "success",
            "conversation_id": "test_conv_123",
            "message_sent": "Test message",
            "type": "conversational",
        }
    )

    return adapter


@pytest.fixture
def test_user_data():
    """Datos de usuario para testing."""
    return {
        "user_id": "test_user_123",
        "user_type": "new_user",
        "program_type": "PRIME",
        "goals": ["weight_loss", "muscle_building", "improved_health"],
    }


class TestAuraOnboardingConversations:
    """Tests para conversaciones de onboarding con AURA."""

    @pytest.mark.asyncio
    async def test_start_onboarding_conversation_new_user(
        self, aura_agent, mock_conversational_adapter, test_user_data
    ):
        """Test onboarding para nuevo usuario."""
        # Setup
        aura_agent.conversational_adapter = mock_conversational_adapter

        # Execute
        result = await aura_agent._skill_start_onboarding_conversation(
            user_type="new_user",
            program_type="PRIME",
            user_goals=["weight_loss", "fitness"],
        )

        # Verify
        assert result["status"] == "success"
        assert result["conversation_id"] == "test_conv_123"
        assert "onboarding_context" in result
        assert result["onboarding_context"]["user_type"] == "new_user"

        # Verify adapter was called
        mock_conversational_adapter.start_conversation.assert_called_once()
        mock_conversational_adapter.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_onboarding_conversation_returning_user(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test onboarding para usuario que regresa."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        result = await aura_agent._skill_start_onboarding_conversation(
            user_type="returning_user", program_type="LONGEVITY"
        )

        assert result["status"] == "success"
        assert result["onboarding_context"]["user_type"] == "returning_user"

    @pytest.mark.asyncio
    async def test_start_onboarding_conversation_premium_user(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test onboarding para usuario premium."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        result = await aura_agent._skill_start_onboarding_conversation(
            user_type="premium_user",
            program_type="PRIME",
            user_goals=["executive_wellness", "stress_management"],
        )

        assert result["status"] == "success"
        assert result["onboarding_context"]["user_type"] == "premium_user"
        assert len(result["onboarding_context"]["goals"]) == 2

    @pytest.mark.asyncio
    async def test_onboarding_without_conversational_adapter(self, aura_agent):
        """Test que maneja correctamente la ausencia del adaptador conversacional."""
        aura_agent.conversational_adapter = None

        result = await aura_agent._skill_start_onboarding_conversation(
            user_type="new_user", program_type="PRIME"
        )

        assert result["status"] == "error"
        assert "not available" in result["error"]


class TestAuraSupport24_7Conversations:
    """Tests para conversaciones de soporte 24/7 con AURA."""

    @pytest.mark.asyncio
    async def test_support_technical_issue_high_urgency(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test soporte para problema técnico de alta urgencia."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        result = await aura_agent._skill_support_24_7_conversation(
            conversation_id="test_conv_123",
            issue_type="technical",
            urgency_level="high",
            user_context={"plan": "premium", "last_login": "2025-06-02"},
        )

        assert result["status"] == "success"
        assert result["support_context"]["issue_type"] == "technical"
        assert result["support_context"]["urgency"] == "high"
        mock_conversational_adapter.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_support_billing_issue_medium_urgency(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test soporte para problema de facturación."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        result = await aura_agent._skill_support_24_7_conversation(
            conversation_id="test_conv_123",
            issue_type="billing",
            urgency_level="medium",
        )

        assert result["status"] == "success"
        assert result["support_context"]["issue_type"] == "billing"

    @pytest.mark.asyncio
    async def test_support_guidance_request(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test soporte para solicitud de orientación."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        result = await aura_agent._skill_support_24_7_conversation(
            conversation_id="test_conv_123",
            issue_type="guidance",
            urgency_level="low",
            user_context={"experience_level": "beginner"},
        )

        assert result["status"] == "success"
        assert result["support_context"]["issue_type"] == "guidance"


class TestAuraCelebrationConversations:
    """Tests para conversaciones de celebración con AURA."""

    @pytest.mark.asyncio
    async def test_celebrate_goal_reached(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test celebración por objetivo alcanzado."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        milestone_details = {
            "goal": "weight_loss",
            "target": "10kg",
            "achieved": "10.2kg",
            "duration": "3 months",
        }

        result = await aura_agent._skill_celebration_conversation(
            conversation_id="test_conv_123",
            achievement_type="goal_reached",
            milestone_details=milestone_details,
        )

        assert result["status"] == "success"
        assert result["celebration_type"] == "goal_reached"
        assert result["milestone"] == milestone_details

    @pytest.mark.asyncio
    async def test_celebrate_streak_achievement(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test celebración por racha de días consecutivos."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        milestone_details = {
            "days": 30,
            "activity": "daily_workout",
            "streak_type": "workout_consistency",
        }

        result = await aura_agent._skill_celebration_conversation(
            conversation_id="test_conv_123",
            achievement_type="streak",
            milestone_details=milestone_details,
        )

        assert result["status"] == "success"
        assert result["celebration_type"] == "streak"

    @pytest.mark.asyncio
    async def test_celebrate_program_completion(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test celebración por completar programa."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        milestone_details = {
            "program": "NGX PRIME Starter",
            "duration": "12 weeks",
            "completion_rate": "100%",
        }

        result = await aura_agent._skill_celebration_conversation(
            conversation_id="test_conv_123",
            achievement_type="completion",
            milestone_details=milestone_details,
        )

        assert result["status"] == "success"
        assert result["celebration_type"] == "completion"


class TestAuraRetentionConversations:
    """Tests para conversaciones de retención con AURA."""

    @pytest.mark.asyncio
    async def test_retention_declining_user(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test retención para usuario con engagement declinante."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        result = await aura_agent._skill_retention_conversation(
            conversation_id="test_conv_123",
            user_engagement_state="declining",
            retention_strategy="proactive",
        )

        assert result["status"] == "success"
        assert result["engagement_state"] == "declining"
        assert result["strategy"] == "proactive"

    @pytest.mark.asyncio
    async def test_retention_inactive_user(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test retención para usuario inactivo."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        result = await aura_agent._skill_retention_conversation(
            conversation_id="test_conv_123",
            user_engagement_state="inactive",
            retention_strategy="reactive",
        )

        assert result["status"] == "success"
        assert result["engagement_state"] == "inactive"

    @pytest.mark.asyncio
    async def test_retention_at_risk_user(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test retención para usuario en riesgo."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        result = await aura_agent._skill_retention_conversation(
            conversation_id="test_conv_123",
            user_engagement_state="at_risk",
            retention_strategy="win_back",
        )

        assert result["status"] == "success"
        assert result["engagement_state"] == "at_risk"


class TestAuraCommunityBuildingConversations:
    """Tests para conversaciones de construcción de comunidad con AURA."""

    @pytest.mark.asyncio
    async def test_community_welcome_new_member(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test bienvenida a nuevo miembro de la comunidad."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        community_context = {
            "members_count": 1500,
            "community_type": "fitness_enthusiasts",
            "user_interests": ["strength_training", "nutrition"],
        }

        result = await aura_agent._skill_community_building_conversation(
            conversation_id="test_conv_123",
            community_action="welcome",
            community_context=community_context,
        )

        assert result["status"] == "success"
        assert result["community_action"] == "welcome"
        assert result["context"] == community_context

    @pytest.mark.asyncio
    async def test_community_event_announcement(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test anuncio de evento comunitario."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        community_context = {
            "event_type": "group_challenge",
            "event_name": "30-Day Wellness Challenge",
            "start_date": "2025-07-01",
        }

        result = await aura_agent._skill_community_building_conversation(
            conversation_id="test_conv_123",
            community_action="event",
            community_context=community_context,
        )

        assert result["status"] == "success"
        assert result["community_action"] == "event"

    @pytest.mark.asyncio
    async def test_community_connection_facilitation(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test facilitación de conexiones entre miembros."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        community_context = {
            "connection_type": "workout_buddy",
            "shared_interests": ["morning_workouts", "strength_training"],
            "location": "similar_timezone",
        }

        result = await aura_agent._skill_community_building_conversation(
            conversation_id="test_conv_123",
            community_action="connection",
            community_context=community_context,
        )

        assert result["status"] == "success"
        assert result["community_action"] == "connection"


class TestAuraMessageGeneration:
    """Tests para la generación de mensajes personalizados de AURA."""

    def test_generate_onboarding_welcome_new_user(self, aura_agent):
        """Test generación de mensaje de bienvenida para nuevo usuario."""
        message = aura_agent._generate_onboarding_welcome(
            user_type="new_user", program_type="PRIME", goals=["fitness", "nutrition"]
        )

        assert "bienvenido" in message.lower()
        assert "aura" in message
        assert "fitness" in message
        assert "nutrition" in message

    def test_generate_support_message_critical_urgency(self, aura_agent):
        """Test generación de mensaje de soporte para urgencia crítica."""
        message = aura_agent._generate_support_message(
            issue_type="technical", urgency="critical"
        )

        assert "urgente" in message.lower()
        assert "inmediatamente" in message.lower()

    def test_generate_celebration_message_goal_reached(self, aura_agent):
        """Test generación de mensaje de celebración por objetivo alcanzado."""
        milestone_details = {"goal": "weight_loss", "amount": "5kg"}

        message = aura_agent._generate_celebration_message(
            achievement_type="goal_reached", details=milestone_details
        )

        assert "increíble" in message.lower() or "fantástico" in message.lower()
        assert "orgullosa" in message.lower()

    def test_generate_retention_message_inactive_user(self, aura_agent):
        """Test generación de mensaje de retención para usuario inactivo."""
        message = aura_agent._generate_retention_message(
            engagement_state="inactive", strategy="proactive"
        )

        assert "extrañamos" in message.lower()
        assert "apoyo" in message.lower()


class TestAuraIntegrationScenarios:
    """Tests de escenarios de integración completos con AURA."""

    @pytest.mark.asyncio
    async def test_complete_onboarding_to_community_flow(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test flujo completo: onboarding → soporte → celebración → comunidad."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        # Step 1: Onboarding
        onboarding_result = await aura_agent._skill_start_onboarding_conversation(
            user_type="new_user", program_type="PRIME"
        )
        assert onboarding_result["status"] == "success"
        conversation_id = onboarding_result["conversation_id"]

        # Step 2: Support request
        support_result = await aura_agent._skill_support_24_7_conversation(
            conversation_id=conversation_id,
            issue_type="guidance",
            urgency_level="medium",
        )
        assert support_result["status"] == "success"

        # Step 3: Celebration of first achievement
        celebration_result = await aura_agent._skill_celebration_conversation(
            conversation_id=conversation_id,
            achievement_type="goal_reached",
            milestone_details={"goal": "first_week_complete", "progress": "100%"},
        )
        assert celebration_result["status"] == "success"

        # Step 4: Community integration
        community_result = await aura_agent._skill_community_building_conversation(
            conversation_id=conversation_id,
            community_action="welcome",
            community_context={"members_count": 1000},
        )
        assert community_result["status"] == "success"

    @pytest.mark.asyncio
    async def test_error_handling_scenarios(self, aura_agent):
        """Test manejo de errores en diferentes escenarios."""
        # Sin adaptador conversacional
        aura_agent.conversational_adapter = None

        # Test onboarding error
        onboarding_result = await aura_agent._skill_start_onboarding_conversation()
        assert onboarding_result["status"] == "error"

        # Mock adaptador que falla
        failed_adapter = Mock(spec=ConversationalVoiceAdapter)
        failed_adapter.send_message = AsyncMock(
            return_value={"status": "error", "error": "Connection failed"}
        )
        aura_agent.conversational_adapter = failed_adapter

        # Test support error
        support_result = await aura_agent._skill_support_24_7_conversation(
            conversation_id="test_conv", issue_type="technical", urgency_level="high"
        )
        assert support_result["status"] == "error"


@pytest.mark.performance
class TestAuraPerformance:
    """Tests de rendimiento para AURA conversacional."""

    @pytest.mark.asyncio
    async def test_response_time_onboarding(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test tiempo de respuesta para onboarding."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        start_time = time.time()
        result = await aura_agent._skill_start_onboarding_conversation(
            user_type="new_user", program_type="PRIME"
        )
        end_time = time.time()

        assert result["status"] == "success"
        assert (end_time - start_time) < 2.0  # Menos de 2 segundos

    @pytest.mark.asyncio
    async def test_concurrent_conversations(
        self, aura_agent, mock_conversational_adapter
    ):
        """Test conversaciones concurrentes de AURA."""
        aura_agent.conversational_adapter = mock_conversational_adapter

        # Simular 5 conversaciones concurrentes
        tasks = []
        for i in range(5):
            task = aura_agent._skill_start_onboarding_conversation(
                user_type="new_user", program_type="PRIME"
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Verificar que todas las conversaciones fueron exitosas
        for result in results:
            assert result["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
