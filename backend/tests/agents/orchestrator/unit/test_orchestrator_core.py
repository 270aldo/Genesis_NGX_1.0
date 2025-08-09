"""
Tests unitarios para el Orchestrator Agent.

Este módulo contiene tests exhaustivos para el agente orquestador,
incluyendo routing, coordinación y manejo de errores.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.orchestrator.agent import NGXNexusOrchestrator
from core.exceptions import AgentError, ValidationError


class TestOrchestratorCore:
    """Tests principales del Orchestrator"""

    @pytest.fixture
    def orchestrator(self, mock_vertex_ai_client, mock_mcp_toolkit, mock_logger):
        """Fixture del orchestrator con dependencias mockeadas"""
        with patch("agents.orchestrator.agent.get_logger", return_value=mock_logger):
            with patch(
                "agents.orchestrator.agent.VertexAIClient",
                return_value=mock_vertex_ai_client,
            ):
                agent = NGXNexusOrchestrator(mcp_toolkit=mock_mcp_toolkit)
                return agent

    @pytest.mark.asyncio
    async def test_initialization(self, orchestrator):
        """Test de inicialización correcta del orchestrator"""
        assert orchestrator.agent_id == "orchestrator"
        assert orchestrator.name == "NEXUS Orchestrator"
        assert orchestrator.personality == "prime"
        assert orchestrator.model == "gemini-1.5-flash-002"
        assert orchestrator.temperature == 0.7

    @pytest.mark.asyncio
    async def test_route_request_to_nutrition(
        self, orchestrator, mock_vertex_ai_client
    ):
        """Test de routing a agente de nutrición"""
        # Configurar respuesta del LLM
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps(
                {
                    "agent": "precision_nutrition_architect",
                    "confidence": 0.95,
                    "reasoning": "Pregunta sobre alimentación",
                }
            ),
            "finish_reason": "STOP",
        }

        # Ejecutar routing
        result = await orchestrator.route_request(
            prompt="¿Qué debo comer antes de entrenar?", user_context={"user_id": "123"}
        )

        # Verificar resultado
        assert result["agent"] == "precision_nutrition_architect"
        assert result["confidence"] == 0.95
        assert "reasoning" in result

        # Verificar que se llamó al LLM
        mock_vertex_ai_client.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_route_request_to_training(self, orchestrator, mock_vertex_ai_client):
        """Test de routing a agente de entrenamiento"""
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps(
                {
                    "agent": "elite_training_strategist",
                    "confidence": 0.92,
                    "reasoning": "Pregunta sobre ejercicios",
                }
            ),
            "finish_reason": "STOP",
        }

        result = await orchestrator.route_request(
            prompt="¿Cómo mejorar mi sentadilla?", user_context={"user_id": "123"}
        )

        assert result["agent"] == "elite_training_strategist"
        assert result["confidence"] == 0.92

    @pytest.mark.asyncio
    async def test_coordinate_multiple_agents(
        self, orchestrator, mock_vertex_ai_client
    ):
        """Test de coordinación de múltiples agentes"""
        # Mock de agentes disponibles
        mock_sage = MagicMock()
        mock_sage.process = AsyncMock(
            return_value={"response": "Consume 30g de proteína", "confidence": 0.9}
        )

        mock_nexus = MagicMock()
        mock_nexus.process = AsyncMock(
            return_value={
                "response": "Realiza 4 series de 12 repeticiones",
                "confidence": 0.88,
            }
        )

        with patch("agents.orchestrator.agent.AgentRegistry") as mock_registry:
            mock_registry.get_instance.return_value.get_agent.side_effect = {
                "precision_nutrition_architect": mock_sage,
                "elite_training_strategist": mock_nexus,
            }.get

            # Configurar respuesta del orchestrator
            mock_vertex_ai_client.generate_content.return_value = {
                "text": json.dumps(
                    {
                        "agents_needed": [
                            "precision_nutrition_architect",
                            "elite_training_strategist",
                        ],
                        "coordination_plan": "Combinar nutrición y entrenamiento",
                    }
                ),
                "finish_reason": "STOP",
            }

            result = await orchestrator.coordinate_agents(
                prompt="Plan completo para ganar músculo",
                agents=["precision_nutrition_architect", "elite_training_strategist"],
                user_context={"user_id": "123"},
            )

            assert "responses" in result
            assert len(result["responses"]) == 2
            assert result["coordination_plan"] == "Combinar nutrición y entrenamiento"

    @pytest.mark.asyncio
    async def test_handle_ambiguous_request(self, orchestrator, mock_vertex_ai_client):
        """Test de manejo de solicitudes ambiguas"""
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps(
                {
                    "agent": "unknown",
                    "confidence": 0.3,
                    "reasoning": "Solicitud poco clara",
                    "clarification_needed": True,
                    "suggested_questions": [
                        "¿Te refieres a nutrición o entrenamiento?",
                        "¿Podrías ser más específico?",
                    ],
                }
            ),
            "finish_reason": "STOP",
        }

        result = await orchestrator.route_request(
            prompt="Ayúdame", user_context={"user_id": "123"}
        )

        assert result["confidence"] < 0.5
        assert result["clarification_needed"] is True
        assert len(result["suggested_questions"]) > 0

    @pytest.mark.asyncio
    async def test_error_handling_invalid_json(
        self, orchestrator, mock_vertex_ai_client
    ):
        """Test de manejo de errores con JSON inválido"""
        mock_vertex_ai_client.generate_content.return_value = {
            "text": "Respuesta no JSON",
            "finish_reason": "STOP",
        }

        with pytest.raises(AgentError) as exc_info:
            await orchestrator.route_request(
                prompt="Test", user_context={"user_id": "123"}
            )

        assert "Error parsing" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fallback_on_llm_error(self, orchestrator, mock_vertex_ai_client):
        """Test de fallback cuando falla el LLM"""
        mock_vertex_ai_client.generate_content.side_effect = Exception("LLM Error")

        # Debe usar lógica de fallback
        result = await orchestrator.route_request(
            prompt="¿Qué debo comer?", user_context={"user_id": "123"}
        )

        # Verificar que usa fallback (análisis por keywords)
        assert result["agent"] in ["precision_nutrition_architect", "unknown"]
        assert result["confidence"] <= 0.5
        assert result.get("fallback") is True

    @pytest.mark.asyncio
    async def test_streaming_response(self, orchestrator, mock_vertex_ai_client):
        """Test de respuesta en streaming"""

        # Simular chunks de streaming
        async def mock_stream():
            chunks = ["Plan ", "de ", "entrenamiento ", "completo"]
            for chunk in chunks:
                yield {"text": chunk}

        mock_vertex_ai_client.generate_content_stream.return_value = mock_stream()

        chunks_received = []
        async for chunk in orchestrator.stream_response(
            prompt="Dame un plan", user_context={"user_id": "123"}
        ):
            chunks_received.append(chunk)

        assert len(chunks_received) == 4
        assert "".join(chunks_received) == "Plan de entrenamiento completo"

    @pytest.mark.asyncio
    async def test_agent_selection_with_context(
        self, orchestrator, mock_vertex_ai_client
    ):
        """Test de selección de agente basada en contexto del usuario"""
        user_context = {
            "user_id": "123",
            "gender": "female",
            "current_agent_preference": "female_wellness_coach",
        }

        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps(
                {
                    "agent": "female_wellness_coach",
                    "confidence": 0.98,
                    "reasoning": "Usuario prefiere coach femenino",
                }
            ),
            "finish_reason": "STOP",
        }

        result = await orchestrator.route_request(
            prompt="Necesito ayuda con mi ciclo", user_context=user_context
        )

        assert result["agent"] == "female_wellness_coach"
        assert result["confidence"] > 0.95

    @pytest.mark.asyncio
    async def test_multi_turn_conversation_tracking(self, orchestrator):
        """Test de tracking de conversación multi-turno"""
        conversation_id = "conv_123"

        # Primera interacción
        await orchestrator.track_conversation_turn(
            conversation_id=conversation_id,
            turn={
                "prompt": "Hola",
                "agent": "orchestrator",
                "response": "Hola, ¿en qué puedo ayudarte?",
            },
        )

        # Segunda interacción
        await orchestrator.track_conversation_turn(
            conversation_id=conversation_id,
            turn={
                "prompt": "Quiero un plan de nutrición",
                "agent": "precision_nutrition_architect",
                "response": "Te prepararé un plan personalizado",
            },
        )

        # Verificar historial
        history = await orchestrator.get_conversation_history(conversation_id)
        assert len(history) == 2
        assert history[0]["agent"] == "orchestrator"
        assert history[1]["agent"] == "precision_nutrition_architect"

    @pytest.mark.asyncio
    async def test_capability_aggregation(self, orchestrator):
        """Test de agregación de capacidades de todos los agentes"""
        with patch("agents.orchestrator.agent.AgentRegistry") as mock_registry:
            mock_registry.get_instance.return_value.list_agents.return_value = [
                {
                    "agent_id": "sage",
                    "capabilities": ["nutrition_planning", "meal_prep"],
                },
                {
                    "agent_id": "nexus",
                    "capabilities": ["workout_planning", "form_check"],
                },
            ]

            capabilities = await orchestrator.get_all_capabilities()

            assert "nutrition_planning" in capabilities
            assert "workout_planning" in capabilities
            assert len(capabilities) == 4

    @pytest.mark.asyncio
    async def test_priority_routing(self, orchestrator, mock_vertex_ai_client):
        """Test de routing con prioridades"""
        # Simular emergencia médica
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps(
                {
                    "agent": "emergency_protocol",
                    "confidence": 1.0,
                    "priority": "critical",
                    "reasoning": "Posible emergencia médica detectada",
                }
            ),
            "finish_reason": "STOP",
        }

        result = await orchestrator.route_request(
            prompt="Me duele mucho el pecho al entrenar",
            user_context={"user_id": "123"},
        )

        assert result["priority"] == "critical"
        assert result["agent"] == "emergency_protocol"
        assert result["confidence"] == 1.0


class TestOrchestratorValidation:
    """Tests de validación del Orchestrator"""

    @pytest.fixture
    def orchestrator(self, mock_vertex_ai_client, mock_mcp_toolkit):
        """Orchestrator para tests de validación"""
        return NGXNexusOrchestrator(mcp_toolkit=mock_mcp_toolkit)

    @pytest.mark.asyncio
    async def test_validate_empty_prompt(self, orchestrator):
        """Test de validación con prompt vacío"""
        with pytest.raises(ValidationError) as exc_info:
            await orchestrator.route_request(prompt="", user_context={"user_id": "123"})

        assert "empty prompt" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_validate_missing_user_context(self, orchestrator):
        """Test de validación sin contexto de usuario"""
        with pytest.raises(ValidationError) as exc_info:
            await orchestrator.route_request(prompt="Test", user_context=None)

        assert "user context" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_validate_agent_availability(self, orchestrator):
        """Test de validación de disponibilidad de agentes"""
        with patch("agents.orchestrator.agent.AgentRegistry") as mock_registry:
            mock_registry.get_instance.return_value.get_agent.return_value = None

            result = await orchestrator.validate_agent_availability(
                "non_existent_agent"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_max_prompt_length(self, orchestrator):
        """Test de validación de longitud máxima del prompt"""
        long_prompt = "x" * 10000  # Prompt muy largo

        with pytest.raises(ValidationError) as exc_info:
            await orchestrator.route_request(
                prompt=long_prompt, user_context={"user_id": "123"}
            )

        assert "too long" in str(exc_info.value).lower()


class TestOrchestratorMetrics:
    """Tests de métricas del Orchestrator"""

    @pytest.fixture
    def orchestrator(self, mock_vertex_ai_client, mock_mcp_toolkit):
        """Orchestrator para tests de métricas"""
        return NGXNexusOrchestrator(mcp_toolkit=mock_mcp_toolkit)

    @pytest.mark.asyncio
    async def test_track_routing_metrics(self, orchestrator, mock_vertex_ai_client):
        """Test de tracking de métricas de routing"""
        mock_vertex_ai_client.generate_content.return_value = {
            "text": json.dumps(
                {"agent": "precision_nutrition_architect", "confidence": 0.95}
            ),
            "finish_reason": "STOP",
        }

        # Realizar varios routings
        for _ in range(5):
            await orchestrator.route_request(
                prompt="¿Qué comer?", user_context={"user_id": "123"}
            )

        metrics = await orchestrator.get_routing_metrics()

        assert metrics["total_requests"] == 5
        assert metrics["agents"]["precision_nutrition_architect"] == 5
        assert metrics["average_confidence"] >= 0.9

    @pytest.mark.asyncio
    async def test_performance_metrics(self, orchestrator):
        """Test de métricas de rendimiento"""
        import time

        start_time = time.time()

        # Simular procesamiento
        await orchestrator.track_performance_metric(
            metric_name="routing_time", value=time.time() - start_time
        )

        perf_metrics = await orchestrator.get_performance_metrics()

        assert "routing_time" in perf_metrics
        assert perf_metrics["routing_time"]["count"] == 1
        assert perf_metrics["routing_time"]["average"] >= 0
