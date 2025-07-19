"""
NEXUS ENHANCED - Integration Tests for Full Flows
===============================================

Tests de integración end-to-end para validar flujos completos del sistema
NEXUS Enhanced incluyendo orchestration y client success workflows.

Arquitectura A+ - Testing Framework
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Imports para testing de integración
from ..core.dependencies import NexusDependencies
from ..core.config import NexusConfig, OrchestratorMode, ClientSuccessLevel
from ..core.exceptions import NexusError, IntentAnalysisError, AgentRoutingError
from ..skills_manager import NexusSkillsManager


@pytest.mark.asyncio
class TestOrchestrationFlows:
    """Tests de flujos de orchestration completos."""

    async def test_complete_training_request_flow(
        self, nexus_skills_manager, sample_agent_responses
    ):
        """Test flujo completo: usuario solicita plan de entrenamiento."""
        user_input = "Necesito un plan de entrenamiento para ganar músculo y fuerza"
        user_id = "user_prime_001"

        # 1. Análisis de intención
        intent_result = await nexus_skills_manager.analyze_intent_enhanced(
            user_input, user_id
        )

        # Verificar detección correcta
        assert intent_result["primary_intent"] == "plan_entrenamiento"
        assert intent_result["recommended_mode"] == "orchestration"
        assert intent_result["urgency_level"] in ["low", "medium", "high"]

        # 2. Síntesis de respuesta con datos de agente
        agent_responses = sample_agent_responses["successful_training_response"]
        client_context = {
            "program_type": "PRIME",
            "preferences": {"communication_style": "direct"},
            "goals": ["muscle_gain", "strength"],
        }

        final_response = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, agent_responses, client_context
        )

        # Verificar síntesis apropiada
        assert isinstance(final_response, str)
        assert len(final_response.strip()) > 0
        assert "entrenamiento" in final_response.lower()

        # Verificar métricas registradas
        performance = nexus_skills_manager.get_skills_performance()
        assert "analyze_intent_enhanced" in performance["skills_metrics"]
        assert "synthesize_response_enhanced" in performance["skills_metrics"]

    async def test_complex_multi_agent_orchestration(
        self, nexus_skills_manager, sample_agent_responses
    ):
        """Test orquestación compleja con múltiples agentes."""
        user_input = (
            "Quiero un plan completo: entrenamiento, nutrición y análisis de progreso"
        )
        user_id = "user_comprehensive_001"

        # Simular respuestas de múltiples agentes
        multi_agent_responses = {
            "elite_training_strategist": {
                "status": "success",
                "output": "Plan de entrenamiento de 8 semanas diseñado para objetivos específicos...",
                "artifacts": ["training_plan.pdf"],
                "execution_time": 2.1,
            },
            "precision_nutrition_architect": {
                "status": "success",
                "output": "Plan nutricional personalizado con 2400 calorías diarias...",
                "artifacts": ["meal_plan.json", "grocery_list.pdf"],
                "execution_time": 1.8,
            },
            "progress_tracker": {
                "status": "success",
                "output": "Sistema de tracking configurado con métricas clave...",
                "artifacts": ["tracking_dashboard.html"],
                "execution_time": 1.2,
            },
        }

        # Análisis de intención
        intent_result = await nexus_skills_manager.analyze_intent_enhanced(
            user_input, user_id
        )
        assert intent_result["recommended_mode"] == "orchestration"

        # Síntesis con múltiples agentes
        client_context = {
            "program_type": "PRIME",
            "preferences": {"detail_level": "comprehensive"},
        }
        final_response = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, multi_agent_responses, client_context
        )

        # Verificar coordinación de múltiples respuestas
        assert "entrenamiento" in final_response.lower()
        assert "nutric" in final_response.lower()
        assert "progreso" in final_response.lower()
        assert len(final_response.split("\n")) > 5  # Respuesta estructurada

    async def test_orchestration_with_partial_failures(
        self, nexus_skills_manager, sample_agent_responses
    ):
        """Test manejo de fallos parciales en orchestration."""
        user_input = "Plan de entrenamiento y nutrición"

        # Simular respuesta mixta (un agente falla)
        mixed_responses = sample_agent_responses["mixed_responses"]
        client_context = {"program_type": "LONGEVITY"}

        final_response = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, mixed_responses, client_context
        )

        # Verificar que maneja fallos gracefully
        assert isinstance(final_response, str)
        assert len(final_response.strip()) > 0
        # Debe incluir información del agente exitoso
        assert "entrenamiento" in final_response.lower()
        # Debe ser empático respecto al fallo
        assert any(
            word in final_response.lower()
            for word in ["temporal", "momento", "reintenta"]
        )


@pytest.mark.asyncio
class TestClientSuccessFlows:
    """Tests de flujos de client success completos."""

    async def test_complete_onboarding_flow(self, nexus_skills_manager):
        """Test flujo completo de onboarding."""
        user_id = "user_onboarding_001"
        program_type = "PRIME"

        # Stage 1: Welcome
        onboarding_result = await nexus_skills_manager.concierge_onboarding(
            user_id, program_type, "welcome"
        )

        assert onboarding_result["status"] == "success"
        assert "onboarding_plan" in onboarding_result

        plan = onboarding_result["onboarding_plan"]
        assert plan["user_id"] == user_id
        assert plan["program_type"] == program_type
        assert plan["current_stage"] == "welcome"
        assert "welcome_message" in plan
        assert "next_steps" in plan

        # Verificar personalización apropiada
        personalization = plan["personalization"]
        assert personalization["tone"] == "warm_professional"  # PRIME
        assert personalization["pace"] == "efficient"  # PRIME
        assert personalization["focus"] == "results_optimization"  # PRIME

    async def test_milestone_celebration_flow(
        self, nexus_skills_manager, sample_milestone_data
    ):
        """Test flujo completo de celebración de hitos."""
        user_id = "user_achiever_001"
        milestone_data = sample_milestone_data["weight_goal_achieved"]

        celebration_result = await nexus_skills_manager.milestone_celebration(
            user_id, milestone_data
        )

        assert celebration_result["status"] == "success"
        assert "celebration" in celebration_result
        assert celebration_result["follow_up_scheduled"] is True

        celebration = celebration_result["celebration"]
        assert celebration["user_id"] == user_id
        assert celebration["milestone_type"] == "weight_goal"
        assert "celebration_message" in celebration
        assert "sharing_opportunity" in celebration
        assert "reward_unlock" in celebration

        # Verificar oportunidades de sharing
        sharing = celebration["sharing_opportunity"]
        assert sharing["enabled"] is True
        assert "community" in sharing["platforms"]
        assert isinstance(sharing["message"], str)

    async def test_client_success_escalation_flow(self, nexus_skills_manager):
        """Test flujo de escalación en client success."""
        user_input = (
            "Estoy muy frustrado, la app no funciona y no puedo acceder a mis planes"
        )
        user_id = "user_frustrated_001"

        # Análisis de contexto client success
        intent_result = await nexus_skills_manager.analyze_intent_enhanced(
            user_input, user_id
        )

        # Debe detectar problema de retención/soporte
        client_context = intent_result["client_success_context"]
        assert client_context["needs_support"] is True
        assert client_context["retention_risk"] is True
        assert client_context["emotional_indicators"] is True

        # Debe recomendar modo concierge
        assert intent_result["recommended_mode"] == "concierge"
        assert intent_result["urgency_level"] == "high"

        # Respuesta empática apropiada
        fallback_response = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, None, {"program_type": "PRIME"}
        )

        assert isinstance(fallback_response, str)
        assert any(
            word in fallback_response.lower()
            for word in ["entiendo", "ayuda", "soporte"]
        )


@pytest.mark.asyncio
class TestHybridFlows:
    """Tests de flujos híbridos (orchestration + client success)."""

    async def test_onboarding_with_first_request_flow(
        self, nexus_skills_manager, sample_agent_responses
    ):
        """Test usuario nuevo que hace primera consulta técnica."""
        # Usuario nuevo solicita información técnica
        user_input = "Soy nuevo, ¿puedes ayudarme a crear un plan de entrenamiento?"
        user_id = "user_new_technical_001"

        # Análisis debe detectar ambos contextos
        intent_result = await nexus_skills_manager.analyze_intent_enhanced(
            user_input, user_id
        )

        client_context = intent_result["client_success_context"]
        assert client_context["needs_onboarding"] is True

        # Debe recomendar modo híbrido
        assert intent_result["recommended_mode"] in ["hybrid", "concierge"]

        # 1. Primero onboarding
        onboarding_result = await nexus_skills_manager.concierge_onboarding(
            user_id, "PRIME", "welcome"
        )
        assert onboarding_result["status"] == "success"

        # 2. Luego información técnica
        agent_responses = sample_agent_responses["successful_training_response"]
        technical_response = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, agent_responses, {"program_type": "PRIME", "new_user": True}
        )

        # Verificar respuesta híbrida
        assert (
            "bienven" in technical_response.lower()
            or "nuevo" in technical_response.lower()
        )
        assert "entrenamiento" in technical_response.lower()

    async def test_milestone_with_next_goal_flow(
        self, nexus_skills_manager, sample_milestone_data, sample_agent_responses
    ):
        """Test celebración de hito seguida de siguiente objetivo."""
        user_id = "user_progressing_001"
        milestone_data = sample_milestone_data["consistency_milestone"]

        # 1. Celebración de hito
        celebration_result = await nexus_skills_manager.milestone_celebration(
            user_id, milestone_data
        )
        assert celebration_result["status"] == "success"

        # 2. Usuario pide siguiente objetivo
        next_goal_input = (
            "¡Gracias por la celebración! ¿Cuál debería ser mi próximo objetivo?"
        )

        intent_result = await nexus_skills_manager.analyze_intent_enhanced(
            next_goal_input, user_id
        )

        # Debe detectar oportunidad de celebración + consulta técnica
        client_context = intent_result["client_success_context"]
        assert client_context["celebration_opportunity"] is True

        # Síntesis híbrida
        agent_responses = sample_agent_responses["successful_training_response"]
        hybrid_response = await nexus_skills_manager.synthesize_response_enhanced(
            next_goal_input,
            agent_responses,
            {"program_type": "PRIME", "recent_milestone": True},
        )

        assert isinstance(hybrid_response, str)
        assert any(
            word in hybrid_response.lower()
            for word in ["próximo", "objetivo", "continúa"]
        )


@pytest.mark.asyncio
class TestErrorRecoveryFlows:
    """Tests de flujos de recuperación de errores."""

    async def test_intent_analysis_failure_recovery(self, nexus_skills_manager):
        """Test recuperación cuando falla análisis de intención."""
        # Input muy ambiguo que podría causar fallo
        user_input = "xyz abc 123 !!!"
        user_id = "user_test_001"

        # Mock para simular fallo en intent analyzer
        with patch.object(
            nexus_skills_manager.dependencies.intent_analyzer_adapter,
            "analyze_intent",
            side_effect=Exception("Intent analysis service down"),
        ):

            # Debe manejar el error gracefully
            try:
                intent_result = await nexus_skills_manager.analyze_intent_enhanced(
                    user_input, user_id
                )
                # Si no lanza excepción, verificar estructura de respuesta de fallback
                assert "primary_intent" in intent_result
                assert intent_result["recommended_mode"] in ["hybrid", "concierge"]
            except IntentAnalysisError as e:
                # Error específico esperado
                assert e.error_code == "INTENT_ANALYSIS_FAILED"
                assert user_input[:50] in str(e)

    async def test_agent_timeout_recovery(self, nexus_skills_manager):
        """Test recuperación cuando agentes especializados no responden a tiempo."""
        user_input = "Plan de entrenamiento urgente"

        # Simular timeout en agente
        timeout_responses = {
            "elite_training_strategist": {
                "status": "timeout",
                "error": "Agent response timeout after 30s",
                "execution_time": 30.0,
            }
        }

        client_context = {"program_type": "PRIME", "urgency": "high"}

        # Debe generar respuesta de fallback empática
        fallback_response = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, timeout_responses, client_context
        )

        assert isinstance(fallback_response, str)
        assert len(fallback_response.strip()) > 0
        assert any(
            word in fallback_response.lower()
            for word in ["tiempo", "temporal", "momento"]
        )

    async def test_cascading_failure_recovery(self, nexus_skills_manager):
        """Test recuperación cuando múltiples componentes fallan."""
        user_input = "Ayuda con todo mi plan de fitness"
        user_id = "user_test_002"

        # Simular fallos en cascada
        with patch.object(
            nexus_skills_manager.dependencies.intent_analyzer_adapter,
            "analyze_intent",
            side_effect=Exception("Intent service down"),
        ):
            with patch.object(
                nexus_skills_manager.dependencies.vertex_ai_client,
                "generate_text",
                side_effect=Exception("AI service down"),
            ):

                # Sistema debe tener fallback final
                try:
                    result = await nexus_skills_manager.analyze_intent_enhanced(
                        user_input, user_id
                    )
                    # Si logra responder, debe ser respuesta de emergencia
                    assert isinstance(result, dict)
                    assert "primary_intent" in result
                except NexusError as e:
                    # Error controlado esperado
                    assert e.recoverable is True
                    assert hasattr(e, "user_message")


@pytest.mark.asyncio
class TestPerformanceFlows:
    """Tests de performance bajo diferentes cargas."""

    async def test_concurrent_user_flows(self, nexus_skills_manager):
        """Test múltiples usuarios simultáneos."""
        # Simular 5 usuarios concurrentes
        user_inputs = [
            ("user_001", "Plan de entrenamiento", "PRIME"),
            ("user_002", "Ayuda con nutrición", "LONGEVITY"),
            ("user_003", "¿Cómo empiezo?", "PRIME"),
            ("user_004", "Tengo problemas", "LONGEVITY"),
            ("user_005", "¡Alcancé mi meta!", "PRIME"),
        ]

        start_time = time.time()

        # Ejecutar análisis concurrente
        tasks = [
            nexus_skills_manager.analyze_intent_enhanced(user_input, user_id)
            for user_id, user_input, program_type in user_inputs
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # ms

        # Verificar que completó en tiempo razonable
        assert total_time < 3000  # Menos de 3 segundos para 5 usuarios

        # Verificar que todas las respuestas son válidas
        successful_results = [r for r in results if isinstance(r, dict)]
        assert len(successful_results) >= 4  # Al menos 4 de 5 exitosos

        for result in successful_results:
            assert "primary_intent" in result
            assert "recommended_mode" in result

    async def test_high_frequency_interactions(self, nexus_skills_manager):
        """Test interacciones de alta frecuencia de un usuario."""
        user_id = "user_high_frequency"

        # 10 interacciones rápidas del mismo usuario
        interactions = [
            "Hola",
            "Plan de entrenamiento",
            "¿Qué ejercicios?",
            "¿Cuántas repeticiones?",
            "¿Qué como antes?",
            "¿Y después?",
            "¿Cómo descanso?",
            "¿Cada cuánto entreno?",
            "¿Veo progreso cuándo?",
            "Gracias",
        ]

        start_time = time.time()

        # Ejecutar secuencialmente (simula chat rápido)
        results = []
        for interaction in interactions:
            result = await nexus_skills_manager.analyze_intent_enhanced(
                interaction, user_id
            )
            results.append(result)

        end_time = time.time()
        avg_time = ((end_time - start_time) * 1000) / len(interactions)

        # Verificar performance promedio por interacción
        assert avg_time < 500  # Menos de 500ms promedio por interacción
        assert len(results) == len(interactions)

        # Verificar que todas las respuestas son válidas
        for result in results:
            assert isinstance(result, dict)
            assert "recommended_mode" in result


@pytest.mark.asyncio
class TestComplexScenarios:
    """Tests de escenarios complejos del mundo real."""

    async def test_returning_user_journey(
        self, nexus_skills_manager, sample_milestone_data
    ):
        """Test journey completo de usuario que regresa después de tiempo."""
        user_id = "user_returning_001"

        # Escenario: Usuario regresa después de 30 días inactivo
        user_input = "Hola, estuve ausente un mes. ¿Cómo retomo mi rutina?"

        # Análisis debe detectar necesidad de re-engagement
        intent_result = await nexus_skills_manager.analyze_intent_enhanced(
            user_input, user_id
        )

        client_context = intent_result["client_success_context"]
        # Puede detectar patterns de returning user
        assert intent_result["recommended_mode"] in ["concierge", "hybrid"]

        # Celebrar que regresó + ayuda práctica
        comeback_milestone = {
            "type": "user_return",
            "achievement": "Regresó después de pausa",
            "previous_streak": 45,
            "pause_duration": 30,
        }

        celebration_result = await nexus_skills_manager.milestone_celebration(
            user_id, comeback_milestone
        )

        assert celebration_result["status"] == "success"
        celebration = celebration_result["celebration"]
        assert (
            "regreso" in celebration["celebration_message"].lower()
            or "vuelta" in celebration["celebration_message"].lower()
        )

    async def test_crisis_intervention_scenario(self, nexus_skills_manager):
        """Test intervención en crisis (usuario muy frustrado/at risk)."""
        user_input = (
            "Nada funciona, quiero cancelar todo, esto es una pérdida de tiempo"
        )
        user_id = "user_crisis_001"

        # Análisis debe detectar crisis de retención
        intent_result = await nexus_skills_manager.analyze_intent_enhanced(
            user_input, user_id
        )

        client_context = intent_result["client_success_context"]
        assert client_context["retention_risk"] is True
        assert client_context["emotional_indicators"] is True
        assert intent_result["urgency_level"] == "high"
        assert intent_result["recommended_mode"] == "concierge"

        # Respuesta debe ser empática y dirigida a retención
        crisis_response = await nexus_skills_manager.synthesize_response_enhanced(
            user_input, None, {"program_type": "PRIME", "crisis_mode": True}
        )

        assert isinstance(crisis_response, str)
        # Debe contener elementos de comprensión y apoyo
        assert any(
            word in crisis_response.lower() for word in ["entiendo", "ayuda", "apoyo"]
        )
        # No debe contener elementos técnicos/promocionales
        assert "plan" not in crisis_response.lower()

    async def test_multi_language_adaptation(self, nexus_skills_manager):
        """Test adaptación a diferentes estilos de comunicación."""
        user_id = "user_multilingual_001"

        # Input muy formal
        formal_input = "Estimado sistema, solicito información detallada sobre protocolos de entrenamiento"
        formal_result = await nexus_skills_manager.analyze_intent_enhanced(
            formal_input, user_id
        )

        # Input muy casual
        casual_input = "ey, qué onda con el gym?"
        casual_result = await nexus_skills_manager.analyze_intent_enhanced(
            casual_input, user_id
        )

        # Ambos deben ser procesados correctamente
        assert formal_result["primary_intent"] in ["plan_entrenamiento", "general"]
        assert casual_result["primary_intent"] in ["plan_entrenamiento", "general"]

        # Contextos pueden ser diferentes
        assert (
            formal_result["client_success_context"]
            != casual_result["client_success_context"]
        )


# Fixtures específicas para integration tests
@pytest.fixture
def complex_user_profile():
    """Perfil de usuario complejo para testing avanzado."""
    return {
        "user_id": "user_complex_001",
        "program_type": "PRIME",
        "demographics": {"age": 35, "occupation": "CEO", "timezone": "US/Pacific"},
        "goals": ["muscle_gain", "stress_reduction", "performance_optimization"],
        "constraints": ["limited_time", "travel_frequent"],
        "preferences": {
            "communication_style": "direct_but_supportive",
            "workout_style": "efficient_intense",
            "nutrition_approach": "flexible_tracking",
        },
        "history": {
            "previous_programs": ["weight_loss", "general_fitness"],
            "success_patterns": ["morning_workouts", "meal_prep"],
            "challenge_areas": ["consistency", "nutrition_tracking"],
        },
    }


@pytest.fixture
def conversation_history():
    """Historial de conversación para testing contextual."""
    return [
        {
            "timestamp": (datetime.now() - timedelta(days=7)).isoformat(),
            "user": "Quiero empezar un programa de fitness",
            "assistant": "Perfecto, analicemos tus objetivos...",
            "intent": "onboarding",
            "mode": "concierge",
        },
        {
            "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
            "user": "Plan de entrenamiento para ganar músculo",
            "assistant": "He creado un plan personalizado...",
            "intent": "plan_entrenamiento",
            "mode": "orchestration",
        },
        {
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
            "user": "¿Qué debo comer antes del entreno?",
            "assistant": "Para maximizar tu rendimiento...",
            "intent": "analizar_nutricion",
            "mode": "orchestration",
        },
    ]
