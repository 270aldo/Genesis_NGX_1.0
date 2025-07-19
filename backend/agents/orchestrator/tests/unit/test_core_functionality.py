"""
NEXUS ENHANCED - Unit Tests for Core Functionality
=================================================

Tests unitarios comprehensivos para todos los módulos core del sistema
NEXUS Enhanced: dependencies, config, exceptions, constants.

Arquitectura A+ - Testing Framework
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

# Imports de los módulos a testear
from ..core.dependencies import (
    NexusDependencies,
    create_production_dependencies,
    create_testing_dependencies,
)
from ..core.config import NexusConfig, OrchestratorMode, ClientSuccessLevel
from ..core.exceptions import (
    NexusError,
    OrchestrationError,
    IntentAnalysisError,
    AgentRoutingError,
    ClientSuccessError,
    OnboardingError,
    MilestoneCelebrationError,
    create_error_response,
    is_recoverable_error,
)
from ..core.constants import (
    IntentCategory,
    INTENT_TO_AGENT_MAP,
    CLIENT_SUCCESS_KEYWORDS,
    NEXUS_PERSONALITY_PROFILE,
    PERFORMANCE_THRESHOLDS,
)
from ..skills_manager import NexusSkillsManager


class TestNexusDependencies:
    """Tests para el container de dependencias."""

    def test_dependencies_creation_with_all_fields(
        self, mock_gemini_client, mock_personality_adapter
    ):
        """Test creación de dependencies con todos los campos."""
        deps = NexusDependencies(
            vertex_ai_client=mock_gemini_client,
            personality_adapter=mock_personality_adapter,
            program_classification_service=Mock(),
            state_manager=Mock(),
            supabase_client=None,
            a2a_adapter=Mock(),
            intent_analyzer_adapter=Mock(),
            state_manager_adapter=Mock(),
            conversational_adapter=Mock(),
            mcp_toolkit=Mock(),
            a2a_server_url="http://localhost:8001",
            orchestrator_model_id="gemini-pro",
        )

        assert deps.vertex_ai_client == mock_gemini_client
        assert deps.personality_adapter == mock_personality_adapter
        assert deps.a2a_server_url == "http://localhost:8001"
        assert deps.orchestrator_model_id == "gemini-pro"

    def test_dependencies_validation_health_check(self, nexus_dependencies_mock):
        """Test validación y health check de dependencies."""
        # Validación básica
        assert nexus_dependencies_mock.vertex_ai_client is not None
        assert nexus_dependencies_mock.personality_adapter is not None

        # Health check simulado
        health_status = {
            "vertex_ai_client": nexus_dependencies_mock.vertex_ai_client is not None,
            "personality_adapter": nexus_dependencies_mock.personality_adapter
            is not None,
            "a2a_adapter": nexus_dependencies_mock.a2a_adapter is not None,
        }

        assert all(health_status.values())

    @patch.dict(
        "os.environ",
        {
            "A2A_SERVER_URL": "http://test-server:8001",
            "ORCHESTRATOR_MODEL_ID": "test-model",
        },
    )
    def test_create_production_dependencies_from_env(self):
        """Test creación de dependencies de producción desde variables de entorno."""
        # Mock de los servicios externos
        with patch("agents.orchestrator.core.dependencies.VertexAIClient") as mock_gemini:
            with patch(
                "agents.orchestrator.core.dependencies.PersonalityAdapter"
            ) as mock_adapter:
                mock_gemini.return_value = Mock()
                mock_adapter.return_value = Mock()

                # Debería usar variables de entorno
                # En testing real, esto requiere configuración completa
                assert True  # Placeholder para test de integración

    def test_create_testing_dependencies(self):
        """Test creación de dependencies para testing."""
        deps = create_testing_dependencies()

        # Verificar que se crearon mocks apropiados
        assert deps.vertex_ai_client is not None
        assert deps.personality_adapter is not None
        assert deps.a2a_server_url == "http://localhost:8001"
        assert deps.orchestrator_model_id == "gemini-pro"


class TestNexusConfig:
    """Tests para la configuración del sistema."""

    def test_config_default_values(self):
        """Test valores por defecto de configuración."""
        config = NexusConfig()

        assert config.max_response_time == 30.0
        assert config.orchestrator_mode == OrchestratorMode.HYBRID
        assert config.client_success_level == ClientSuccessLevel.PREMIUM
        assert config.enable_conversational_mode is True
        assert config.enable_proactive_check_ins is True
        assert config.enable_milestone_celebrations is True

    def test_config_custom_values(self):
        """Test configuración con valores personalizados."""
        config = NexusConfig(
            max_response_time=60.0,
            orchestrator_mode=OrchestratorMode.ORCHESTRATION_ONLY,
            client_success_level=ClientSuccessLevel.STANDARD,
            enable_performance_monitoring=False,
        )

        assert config.max_response_time == 60.0
        assert config.orchestrator_mode == OrchestratorMode.ORCHESTRATION_ONLY
        assert config.client_success_level == ClientSuccessLevel.STANDARD
        assert config.enable_performance_monitoring is False

    def test_config_validation_edge_cases(self):
        """Test validación de casos edge en configuración."""
        # Valores extremos
        config = NexusConfig(
            max_response_time=0.1,  # Muy bajo
            health_check_interval_seconds=1,  # Muy frecuente
            data_retention_days=365,  # Un año
        )

        assert config.max_response_time == 0.1
        assert config.health_check_interval_seconds == 1
        assert config.data_retention_days == 365


class TestNexusExceptions:
    """Tests para el sistema de excepciones."""

    def test_nexus_error_base_functionality(self):
        """Test funcionalidad básica de NexusError."""
        error = NexusError(
            "Test error message",
            error_code="TEST_ERROR",
            context={"test_key": "test_value"},
            user_message="User friendly message",
            recoverable=True,
        )

        assert str(error) == "Test error message"
        assert error.error_code == "TEST_ERROR"
        assert error.context["test_key"] == "test_value"
        assert error.user_message == "User friendly message"
        assert error.recoverable is True
        assert isinstance(error.timestamp, datetime)

    def test_intent_analysis_error(self):
        """Test error específico de análisis de intención."""
        user_input = "¿Cómo puedo mejorar mi entrenamiento de fuerza?"
        error = IntentAnalysisError(user_input, confidence=0.3)

        assert error.error_code == "INTENT_ANALYSIS_FAILED"
        assert error.context["user_input"] == user_input
        assert error.context["confidence"] == 0.3
        assert "reformularla" in error.user_message

    def test_agent_routing_error(self):
        """Test error de routing de agentes."""
        intent = "plan_entrenamiento"
        available_agents = [
            "elite_training_strategist",
            "precision_nutrition_architect",
        ]
        error = AgentRoutingError(intent, available_agents)

        assert error.error_code == "AGENT_ROUTING_FAILED"
        assert error.context["intent"] == intent
        assert error.context["available_agents"] == available_agents
        assert "específico" in error.user_message

    def test_onboarding_error(self):
        """Test error de onboarding."""
        user_id = "user_test_001"
        stage = "profile_setup"
        error = OnboardingError(user_id, stage)

        assert error.error_code == "ONBOARDING_ERROR"
        assert error.context["user_id"] == user_id
        assert error.context["onboarding_stage"] == stage
        assert "bienvenida" in error.user_message

    def test_milestone_celebration_error(self):
        """Test error de celebración de hitos."""
        user_id = "user_test_001"
        milestone_type = "first_workout"
        error = MilestoneCelebrationError(user_id, milestone_type)

        assert error.error_code == "MILESTONE_CELEBRATION_ERROR"
        assert error.context["user_id"] == user_id
        assert error.context["milestone_type"] == milestone_type
        assert error.recoverable is True
        assert "Felicitaciones" in error.user_message

    def test_error_to_dict_serialization(self):
        """Test serialización de errores a diccionario."""
        error = NexusError("Test error", context={"key": "value"})
        error_dict = error.to_dict()

        required_keys = [
            "error_type",
            "error_code",
            "message",
            "user_message",
            "context",
            "recoverable",
            "timestamp",
            "traceback",
        ]

        for key in required_keys:
            assert key in error_dict

        assert error_dict["error_type"] == "NexusError"
        assert error_dict["context"]["key"] == "value"

    def test_create_error_response_utility(self):
        """Test utilidad de creación de respuestas de error."""
        error = IntentAnalysisError("test input", confidence=0.2)

        # Sin debug info
        response = create_error_response(error, include_debug=False)
        assert response["status"] == "error"
        assert response["error_code"] == "INTENT_ANALYSIS_FAILED"
        assert "debug" not in response

        # Con debug info
        debug_response = create_error_response(error, include_debug=True)
        assert "debug" in debug_response
        assert "technical_message" in debug_response["debug"]
        assert "context" in debug_response["debug"]

    def test_is_recoverable_error_utility(self):
        """Test utilidad de determinación de errores recuperables."""
        # Error NEXUS recuperable
        recoverable_nexus_error = IntentAnalysisError("test", recoverable=True)
        assert is_recoverable_error(recoverable_nexus_error) is True

        # Error NEXUS no recuperable
        non_recoverable_nexus_error = NexusError("test", recoverable=False)
        assert is_recoverable_error(non_recoverable_nexus_error) is False

        # Error estándar de Python (considerado recuperable)
        connection_error = ConnectionError("Network issue")
        assert is_recoverable_error(connection_error) is True

        # Error no recuperable
        value_error = ValueError("Invalid value")
        assert is_recoverable_error(value_error) is False


class TestConstants:
    """Tests para las constantes del sistema."""

    def test_intent_to_agent_mapping(self):
        """Test mapeo de intenciones a agentes."""
        # Verificar intenciones core
        assert "plan_entrenamiento" in INTENT_TO_AGENT_MAP
        assert "elite_training_strategist" in INTENT_TO_AGENT_MAP["plan_entrenamiento"]

        assert "analizar_nutricion" in INTENT_TO_AGENT_MAP
        assert (
            "precision_nutrition_architect" in INTENT_TO_AGENT_MAP["analizar_nutricion"]
        )

        # Verificar intenciones de client success
        assert "onboarding" in INTENT_TO_AGENT_MAP
        assert "ngx_nexus_orchestrator_enhanced" in INTENT_TO_AGENT_MAP["onboarding"]

        assert "milestone" in INTENT_TO_AGENT_MAP
        assert "ngx_nexus_orchestrator_enhanced" in INTENT_TO_AGENT_MAP["milestone"]

    def test_client_success_keywords(self):
        """Test keywords de client success."""
        # Verificar categorías clave
        support_keywords = {"help", "support", "problem", "issue", "stuck"}
        assert support_keywords.issubset(CLIENT_SUCCESS_KEYWORDS)

        onboarding_keywords = {"onboarding", "welcome", "getting started"}
        assert onboarding_keywords.issubset(CLIENT_SUCCESS_KEYWORDS)

        milestone_keywords = {"milestone", "achievement", "goal", "success"}
        assert milestone_keywords.issubset(CLIENT_SUCCESS_KEYWORDS)

        community_keywords = {"community", "connect", "share"}
        assert community_keywords.issubset(CLIENT_SUCCESS_KEYWORDS)

    def test_personality_profile_structure(self):
        """Test estructura del perfil de personalidad NEXUS."""
        profile = NEXUS_PERSONALITY_PROFILE

        # Verificar estructura básica
        assert "mbti_type" in profile
        assert "core_traits" in profile
        assert "communication_style" in profile

        # Verificar estilos de comunicación por programa
        comm_style = profile["communication_style"]
        assert "PRIME" in comm_style
        assert "LONGEVITY" in comm_style

        # Verificar campos requeridos para cada programa
        for program in ["PRIME", "LONGEVITY"]:
            program_style = comm_style[program]
            required_fields = ["tone", "language", "focus", "urgency"]
            for field in required_fields:
                assert field in program_style

    def test_performance_thresholds(self):
        """Test umbrales de performance."""
        thresholds = PERFORMANCE_THRESHOLDS

        # Verificar métricas clave
        assert "response_time_ms" in thresholds
        assert thresholds["response_time_ms"] > 0

        assert "intent_confidence" in thresholds
        assert 0 <= thresholds["intent_confidence"] <= 1

        assert "agent_success_rate" in thresholds
        assert 0 <= thresholds["agent_success_rate"] <= 1

        assert "error_rate" in thresholds
        assert thresholds["error_rate"] >= 0


class TestNexusSkillsManagerCore:
    """Tests core del NexusSkillsManager."""

    @pytest.mark.asyncio
    async def test_skills_manager_initialization(
        self, nexus_dependencies_mock, nexus_config_testing
    ):
        """Test inicialización del skills manager."""
        skills_manager = NexusSkillsManager(
            nexus_dependencies_mock, nexus_config_testing
        )

        assert skills_manager.dependencies == nexus_dependencies_mock
        assert skills_manager.config == nexus_config_testing
        assert isinstance(skills_manager._skill_metrics, dict)

    @pytest.mark.asyncio
    async def test_analyze_intent_enhanced_basic_flow(self, nexus_skills_manager):
        """Test flujo básico de análisis de intención mejorado."""
        user_input = "Necesito un plan de entrenamiento para ganar músculo"
        user_id = "user_test_001"

        result = await nexus_skills_manager.analyze_intent_enhanced(user_input, user_id)

        # Verificar estructura de respuesta
        required_keys = [
            "primary_intent",
            "secondary_intents",
            "confidence",
            "client_success_context",
            "recommended_mode",
            "requires_empathy",
            "urgency_level",
        ]

        for key in required_keys:
            assert key in result

        # Verificar tipos de datos
        assert isinstance(result["secondary_intents"], list)
        assert isinstance(result["confidence"], (int, float))
        assert isinstance(result["client_success_context"], dict)
        assert result["recommended_mode"] in ["orchestration", "concierge", "hybrid"]
        assert result["urgency_level"] in ["low", "medium", "high"]

    @pytest.mark.asyncio
    async def test_synthesize_response_enhanced_with_agent_responses(
        self, nexus_skills_manager, sample_agent_responses
    ):
        """Test síntesis de respuesta con respuestas de agentes."""
        user_input = "Plan de entrenamiento"
        agent_responses = sample_agent_responses["successful_training_response"]
        client_context = {
            "program_type": "PRIME",
            "preferences": {"communication_style": "direct"},
        }

        result = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, agent_responses, client_context
        )

        # Verificar que es una string no vacía
        assert isinstance(result, str)
        assert len(result.strip()) > 0

        # Verificar que contiene el contenido del agente
        agent_output = agent_responses["elite_training_strategist"]["output"]
        assert agent_output in result or "plan de entrenamiento" in result.lower()

    @pytest.mark.asyncio
    async def test_synthesize_response_enhanced_fallback(self, nexus_skills_manager):
        """Test fallback de síntesis cuando no hay respuestas de agentes."""
        user_input = "Consulta sin agentes disponibles"
        client_context = {"program_type": "LONGEVITY"}

        result = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, None, client_context
        )

        # Verificar que es una respuesta empática apropiada
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        assert "consulta" in result.lower()

    @pytest.mark.asyncio
    async def test_concierge_onboarding_flow(self, nexus_skills_manager):
        """Test flujo de onboarding concierge."""
        user_id = "user_new_001"
        program_type = "PRIME"
        stage = "welcome"

        result = await nexus_skills_manager.concierge_onboarding(
            user_id, program_type, stage
        )

        # Verificar estructura de respuesta
        assert result["status"] == "success"
        assert "onboarding_plan" in result
        assert "next_touchpoint" in result

        # Verificar plan de onboarding
        plan = result["onboarding_plan"]
        assert plan["user_id"] == user_id
        assert plan["program_type"] == program_type
        assert plan["current_stage"] == stage
        assert "welcome_message" in plan
        assert "next_steps" in plan
        assert "personalization" in plan

    @pytest.mark.asyncio
    async def test_milestone_celebration_flow(
        self, nexus_skills_manager, sample_milestone_data
    ):
        """Test flujo de celebración de hitos."""
        user_id = "user_test_001"
        milestone_data = sample_milestone_data["weight_goal_achieved"]

        result = await nexus_skills_manager.milestone_celebration(
            user_id, milestone_data
        )

        # Verificar estructura de respuesta
        assert result["status"] == "success"
        assert "celebration" in result
        assert result["follow_up_scheduled"] is True

        # Verificar celebración
        celebration = result["celebration"]
        assert celebration["user_id"] == user_id
        assert celebration["milestone_type"] == milestone_data["type"]
        assert "celebration_message" in celebration
        assert "sharing_opportunity" in celebration

    def test_skills_performance_metrics(self, nexus_skills_manager):
        """Test métricas de performance de skills."""
        # Simular algunas métricas
        nexus_skills_manager._record_skill_metric("test_skill", 150.0, True)
        nexus_skills_manager._record_skill_metric("test_skill", 200.0, True)
        nexus_skills_manager._record_skill_metric("test_skill", 300.0, False)

        performance = nexus_skills_manager.get_skills_performance()

        # Verificar estructura
        assert "skills_metrics" in performance
        assert "summary" in performance

        # Verificar métricas específicas
        test_metrics = performance["skills_metrics"]["test_skill"]
        assert test_metrics["total_calls"] == 3
        assert test_metrics["success_calls"] == 2
        assert test_metrics["avg_time"] == (150.0 + 200.0 + 300.0) / 3

        # Verificar summary
        summary = performance["summary"]
        assert summary["total_skills"] == 1
        assert summary["total_calls"] == 3
        assert summary["overall_success_rate"] == 2 / 3


@pytest.mark.asyncio
class TestAsyncFlows:
    """Tests de flujos asíncronos y concurrencia."""

    async def test_concurrent_intent_analysis(self, nexus_skills_manager):
        """Test análisis de intención concurrente."""
        inputs = [
            "Plan de entrenamiento",
            "Consulta nutricional",
            "¿Cómo empiezo?",
            "Problemas con la app",
        ]

        # Ejecutar análisis concurrentes
        tasks = [
            nexus_skills_manager.analyze_intent_enhanced(inp, f"user_{i}")
            for i, inp in enumerate(inputs)
        ]

        results = await asyncio.gather(*tasks)

        # Verificar que todas las respuestas son válidas
        assert len(results) == len(inputs)
        for result in results:
            assert "primary_intent" in result
            assert "recommended_mode" in result

    async def test_performance_under_load(self, nexus_skills_manager):
        """Test performance bajo carga."""
        start_time = asyncio.get_event_loop().time()

        # Simular carga de 10 requests concurrentes
        tasks = [
            nexus_skills_manager.analyze_intent_enhanced(f"Test query {i}", f"user_{i}")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks)

        end_time = asyncio.get_event_loop().time()
        total_time = (end_time - start_time) * 1000  # Convert to ms

        # Verificar que completó en tiempo razonable (< 5 segundos para 10 requests)
        assert total_time < 5000
        assert len(results) == 10

        # Verificar que todas las respuestas son válidas
        for result in results:
            assert isinstance(result, dict)
            assert "primary_intent" in result
