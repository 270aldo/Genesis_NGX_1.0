"""
NEXUS ENHANCED - Test Configuration and Fixtures
===============================================

Configuración centralizada de testing para NEXUS Enhanced con fixtures
comprehensivas para orchestration y client success testing.

Arquitectura A+ - Testing Framework
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Testing fixtures para NEXUS Enhanced
from ..core.dependencies import NexusDependencies
from ..core.config import NexusConfig, OrchestratorMode, ClientSuccessLevel
from ..core.exceptions import NexusError, IntentAnalysisError
from ..skills_manager import NexusSkillsManager


@pytest.fixture(scope="session")
def event_loop():
    """Fixture para event loop de asyncio."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_gemini_client():
    """Mock del cliente Gemini para testing."""
    mock = Mock()
    mock.generate_text = AsyncMock(return_value="Mock AI response")
    mock.set_current_agent = Mock()
    return mock


@pytest.fixture
def mock_personality_adapter():
    """Mock del PersonalityAdapter para testing."""
    mock = Mock()
    mock.adapt_response = Mock(
        return_value={
            "adapted_message": "Mock adapted response",
            "program_type": "PRIME",
            "adaptation_metrics": {"confidence": 0.9},
        }
    )
    return mock


@pytest.fixture
def mock_program_classification_service():
    """Mock del servicio de clasificación de programas."""
    mock = Mock()
    mock.classify_program_from_text = AsyncMock(
        return_value={
            "program_type": "PRIME",
            "confidence": 0.8,
            "indicators": ["executive", "performance"],
        }
    )
    return mock


@pytest.fixture
def mock_intent_analyzer():
    """Mock del analizador de intención."""
    mock = MagicMock()
    mock.analyze_intent = AsyncMock(
        return_value={
            "primary_intent": "plan_entrenamiento",
            "secondary_intents": ["motivation"],
            "confidence": 0.85,
        }
    )
    return mock


@pytest.fixture
def mock_a2a_adapter():
    """Mock del adaptador A2A."""
    mock = MagicMock()
    mock.call_agent = AsyncMock(
        return_value={
            "status": "success",
            "output": "Mock agent response",
            "agent_id": "elite_training_strategist",
        }
    )
    mock.call_multiple_agents = AsyncMock(
        return_value={
            "elite_training_strategist": {
                "status": "success",
                "output": "Training plan generated",
                "artifacts": [],
            }
        }
    )
    return mock


@pytest.fixture
def mock_conversational_adapter():
    """Mock del adaptador conversacional ElevenLabs."""
    mock = Mock()
    mock.start_conversation = AsyncMock(
        return_value={
            "status": "success",
            "conversation_id": "conv_123",
            "websocket_url": "wss://api.elevenlabs.io/v1/convai/conversation",
        }
    )
    mock.send_message = AsyncMock(
        return_value={"status": "success", "message_id": "msg_123"}
    )
    mock.end_conversation = AsyncMock(return_value={"status": "success"})
    return mock


@pytest.fixture
def mock_state_manager():
    """Mock del StateManager."""
    mock = Mock()
    mock.load_state = AsyncMock(
        return_value={
            "conversation_history": [],
            "user_profile": {"program_type": "PRIME"},
        }
    )
    mock.save_state = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_mcp_toolkit():
    """Mock del MCP Toolkit."""
    mock = Mock()
    mock.execute_skill = AsyncMock(return_value="Mock skill result")
    return mock


@pytest.fixture
def sample_user_contexts():
    """Contextos de usuario de ejemplo para testing."""
    return {
        "prime_executive": {
            "user_id": "user_prime_001",
            "program_type": "PRIME",
            "preferences": {"communication_style": "direct", "urgency": "high"},
            "demographics": {"age": 35, "occupation": "executive"},
            "goals": ["performance_optimization", "time_efficiency"],
        },
        "longevity_wellness": {
            "user_id": "user_longevity_001",
            "program_type": "LONGEVITY",
            "preferences": {"communication_style": "supportive", "pace": "gradual"},
            "demographics": {"age": 55, "lifestyle": "wellness_focused"},
            "goals": ["health_maintenance", "sustainable_habits"],
        },
        "new_user_onboarding": {
            "user_id": "user_new_001",
            "program_type": "PRIME",
            "onboarding_stage": "welcome",
            "signup_date": datetime.now().isoformat(),
            "needs_support": True,
        },
        "at_risk_user": {
            "user_id": "user_atrisk_001",
            "program_type": "LONGEVITY",
            "last_interaction": (datetime.now() - timedelta(days=14)).isoformat(),
            "engagement_score": 0.3,
            "churn_risk": True,
        },
    }


@pytest.fixture
def sample_intent_scenarios():
    """Escenarios de intención para testing comprehensivo."""
    return {
        "training_request": {
            "user_input": "Necesito un plan de entrenamiento para ganar músculo",
            "expected_intent": "plan_entrenamiento",
            "expected_agents": ["elite_training_strategist"],
            "expected_mode": "orchestration",
        },
        "nutrition_query": {
            "user_input": "¿Qué debo comer antes del entrenamiento?",
            "expected_intent": "analizar_nutricion",
            "expected_agents": ["precision_nutrition_architect"],
            "expected_mode": "orchestration",
        },
        "support_request": {
            "user_input": "Tengo problemas con la app, necesito ayuda",
            "expected_intent": "support",
            "expected_agents": ["ngx_nexus_orchestrator_enhanced"],
            "expected_mode": "concierge",
        },
        "celebration_moment": {
            "user_input": "¡Logré mi objetivo de peso después de 3 meses!",
            "expected_intent": "milestone",
            "expected_agents": ["ngx_nexus_orchestrator_enhanced"],
            "expected_mode": "concierge",
        },
        "onboarding_help": {
            "user_input": "Soy nuevo, ¿cómo empiezo?",
            "expected_intent": "onboarding",
            "expected_agents": ["ngx_nexus_orchestrator_enhanced"],
            "expected_mode": "concierge",
        },
    }


@pytest.fixture
def sample_milestone_data():
    """Datos de ejemplo para milestone celebrations."""
    return {
        "weight_goal_achieved": {
            "type": "weight_goal",
            "achievement": "Perdió 5kg en 2 meses",
            "target": "75kg",
            "achieved": "75kg",
            "timeline": "8 semanas",
            "difficulty": "moderate",
        },
        "consistency_milestone": {
            "type": "consistency_week",
            "achievement": "7 días consecutivos de ejercicio",
            "streak_length": 7,
            "previous_best": 4,
            "improvement": "75%",
        },
        "first_workout": {
            "type": "first_workout",
            "achievement": "Completó su primer entrenamiento",
            "workout_type": "strength_training",
            "duration": "45 minutos",
            "difficulty": "beginner",
        },
    }


@pytest.fixture
def sample_agent_responses():
    """Respuestas de ejemplo de agentes especializados."""
    return {
        "successful_training_response": {
            "elite_training_strategist": {
                "status": "success",
                "output": "He creado un plan de entrenamiento personalizado de 4 semanas...",
                "artifacts": ["training_plan.pdf"],
                "agent_name": "BLAZE - Elite Training Strategist",
            }
        },
        "successful_nutrition_response": {
            "precision_nutrition_architect": {
                "status": "success",
                "output": "Recomiendo una comida pre-entreno rica en carbohidratos...",
                "artifacts": ["meal_recommendations.json"],
                "agent_name": "SAGE - Precision Nutrition Architect",
            }
        },
        "mixed_responses": {
            "elite_training_strategist": {
                "status": "success",
                "output": "Plan de entrenamiento creado exitosamente",
                "artifacts": [],
            },
            "precision_nutrition_architect": {
                "status": "error",
                "error": "Servicio temporalmente no disponible",
                "output": "Error procesando solicitud nutricional",
            },
        },
        "empty_responses": {},
    }


@pytest.fixture
def mock_orchestration_security_service():
    """Mock del servicio de seguridad."""
    mock = Mock()
    mock.sanitize_input = Mock(return_value=("sanitized input", []))
    mock.encrypt_conversation = Mock(return_value="encrypted_data")
    mock.decrypt_conversation = Mock(return_value={"test": "data"})
    mock.log_orchestration_event = Mock(return_value="log_id_123")
    mock.check_compliance_requirements = Mock(
        return_value={"compliant": True, "requirements": [], "actions_required": []}
    )
    return mock


@pytest.fixture
def nexus_dependencies_mock(
    mock_gemini_client,
    mock_personality_adapter,
    mock_program_classification_service,
    mock_intent_analyzer,
    mock_a2a_adapter,
    mock_conversational_adapter,
    mock_state_manager,
    mock_mcp_toolkit,
):
    """Dependencies mock completo para NEXUS Enhanced."""
    return NexusDependencies(
        vertex_ai_client=mock_gemini_client,
        personality_adapter=mock_personality_adapter,
        program_classification_service=mock_program_classification_service,
        state_manager=mock_state_manager,
        supabase_client=None,
        a2a_adapter=mock_a2a_adapter,
        intent_analyzer_adapter=mock_intent_analyzer,
        state_manager_adapter=mock_state_manager,
        conversational_adapter=mock_conversational_adapter,
        mcp_toolkit=mock_mcp_toolkit,
        a2a_server_url="http://localhost:8001",
        orchestrator_model_id="gemini-pro",
    )


@pytest.fixture
def nexus_config_testing():
    """Configuración de testing para NEXUS Enhanced."""
    return NexusConfig(
        max_response_time=60.0,  # Timeouts relajados para testing
        orchestrator_mode=OrchestratorMode.HYBRID,
        client_success_level=ClientSuccessLevel.PREMIUM,
        enable_conversational_mode=True,
        enable_proactive_check_ins=True,
        enable_milestone_celebrations=True,
        enable_performance_monitoring=False,  # Disable en testing
        enable_audit_logging=False,  # Disable en testing
        health_check_interval_seconds=5,
        data_retention_days=1,  # Minimal para testing
    )


@pytest.fixture
def nexus_skills_manager(nexus_dependencies_mock, nexus_config_testing):
    """Skills manager configurado para testing."""
    return NexusSkillsManager(
        dependencies=nexus_dependencies_mock, config=nexus_config_testing
    )


@pytest.fixture
def error_scenarios():
    """Escenarios de error para testing robusto."""
    return {
        "intent_analysis_timeout": {
            "error_type": "timeout",
            "operation": "intent_analysis",
            "expected_fallback": True,
        },
        "agent_communication_failure": {
            "error_type": "communication",
            "operation": "agent_routing",
            "expected_fallback": True,
        },
        "invalid_user_input": {
            "error_type": "validation",
            "operation": "input_processing",
            "expected_fallback": True,
        },
        "dependency_unavailable": {
            "error_type": "dependency",
            "operation": "service_initialization",
            "expected_fallback": False,
        },
    }


@pytest.fixture
def performance_benchmarks():
    """Benchmarks de performance para testing."""
    return {
        "intent_analysis_max_time_ms": 500,
        "response_synthesis_max_time_ms": 1000,
        "concierge_onboarding_max_time_ms": 800,
        "milestone_celebration_max_time_ms": 600,
        "overall_response_max_time_ms": 3000,
        "min_confidence_threshold": 0.7,
        "max_error_rate": 0.01,
    }


@pytest.fixture
def conversation_flows():
    """Flujos de conversación para testing de integración."""
    return {
        "new_user_journey": [
            {"user": "Soy nuevo, ¿cómo empiezo?", "expected_mode": "concierge"},
            {
                "user": "Quiero un plan de entrenamiento",
                "expected_mode": "orchestration",
            },
            {"user": "¿Qué debo comer?", "expected_mode": "orchestration"},
            {"user": "Gracias por la ayuda", "expected_mode": "concierge"},
        ],
        "milestone_celebration_flow": [
            {"user": "¡Logré mi objetivo de peso!", "expected_mode": "concierge"},
            {
                "user": "¿Cuál debería ser mi próximo objetivo?",
                "expected_mode": "orchestration",
            },
            {
                "user": "Quiero compartir esto con la comunidad",
                "expected_mode": "concierge",
            },
        ],
        "support_escalation_flow": [
            {"user": "Tengo un problema con la app", "expected_mode": "concierge"},
            {"user": "No puedo acceder a mi plan", "expected_mode": "concierge"},
            {"user": "Esto es muy frustrante", "expected_mode": "concierge"},
        ],
    }


# Test helpers


def assert_response_time(actual_time_ms: float, max_time_ms: float, operation: str):
    """Helper para verificar tiempos de respuesta."""
    assert (
        actual_time_ms <= max_time_ms
    ), f"{operation} tardó {actual_time_ms}ms, máximo {max_time_ms}ms"


def assert_intent_accuracy(
    predicted: str, expected: str, confidence: float, min_confidence: float = 0.7
):
    """Helper para verificar precisión de intent analysis."""
    assert predicted == expected, f"Intent predicho: {predicted}, esperado: {expected}"
    assert (
        confidence >= min_confidence
    ), f"Confidence {confidence} menor que mínimo {min_confidence}"


def assert_empathetic_response(response: str, context: Dict[str, Any]):
    """Helper para verificar que la respuesta es apropiadamente empática."""
    program_type = context.get("program_type", "PRIME")

    if program_type == "PRIME":
        # Verificar elementos de comunicación ejecutiva
        executive_indicators = [
            "estratégico",
            "optimización",
            "eficiencia",
            "ROI",
            "objetivos",
        ]
        assert any(
            indicator in response.lower() for indicator in executive_indicators
        ), "Respuesta no contiene elementos apropiados para PRIME"
    else:
        # Verificar elementos de comunicación de bienestar
        wellness_indicators = ["bienestar", "journey", "cuidado", "gradual", "balance"]
        assert any(
            indicator in response.lower() for indicator in wellness_indicators
        ), "Respuesta no contiene elementos apropiados para LONGEVITY"


def create_mock_conversation_state(
    user_id: str, messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """Helper para crear estado de conversación mock."""
    return {
        "user_id": user_id,
        "session_id": f"session_{user_id}",
        "conversation_history": [
            {
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": datetime.now().isoformat(),
            }
            for msg in messages
        ],
        "context": {"program_type": "PRIME", "conversation_length": len(messages)},
    }
