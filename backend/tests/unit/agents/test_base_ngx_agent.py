"""
Tests unitarios para BaseNGXAgent.

Este módulo contiene pruebas completas para la clase base BaseNGXAgent,
asegurando que todos los agentes que heredan de ella funcionen correctamente.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

from agents.base.base_ngx_agent import BaseNGXAgent
from core.settings import settings


@pytest.fixture
def mock_vertex_client():
    """Mock del cliente de Vertex AI."""
    client = AsyncMock()
    client.generate_response = AsyncMock(return_value="Test response")
    client.generate_structured_output = AsyncMock(return_value={"result": "test"})
    client.stream_response = AsyncMock()
    return client


@pytest.fixture
def mock_supabase_client():
    """Mock del cliente de Supabase."""
    client = AsyncMock()
    client.execute_query = AsyncMock(return_value={"data": [], "count": 0})
    client.get_or_create_user_by_api_key = AsyncMock(
        return_value={"id": "test-user-id", "api_key": "test-key"}
    )
    return client


@pytest.fixture
def base_agent(mock_vertex_client, mock_supabase_client):
    """Fixture que proporciona una instancia de BaseNGXAgent para testing."""
    with patch('agents.base.base_ngx_agent.get_vertex_ai_client', return_value=mock_vertex_client):
        with patch('agents.base.base_ngx_agent.supabase_client', mock_supabase_client):
            agent = BaseNGXAgent(
                agent_id="test_agent",
                agent_name="Test Agent",
                agent_type="test",
                personality_type="PRIME",
                model_id="gemini-pro",
                temperature=0.7
            )
            agent.vertex_client = mock_vertex_client
            agent.supabase_client = mock_supabase_client
            return agent


class TestBaseNGXAgent:
    """Tests para BaseNGXAgent."""
    
    def test_initialization(self, base_agent):
        """Test de inicialización correcta."""
        assert base_agent.agent_id == "test_agent"
        assert base_agent.agent_name == "Test Agent"
        assert base_agent.agent_type == "test"
        assert base_agent.personality_type == "PRIME"
        assert base_agent.model_id == "gemini-pro"
        assert base_agent.temperature == 0.7
    
    def test_agent_metadata(self, base_agent):
        """Test de metadata del agente."""
        metadata = base_agent.get_agent_metadata()
        
        assert metadata["agent_id"] == "test_agent"
        assert metadata["agent_name"] == "Test Agent"
        assert metadata["agent_type"] == "test"
        assert metadata["personality_type"] == "PRIME"
        assert metadata["capabilities"] == []
        assert "version" in metadata
        assert "created_at" in metadata
    
    async def test_process_request_basic(self, base_agent, mock_vertex_client):
        """Test de procesamiento básico de request."""
        request = {
            "user_input": "Test input",
            "context": {"key": "value"}
        }
        
        response = await base_agent.process_request(request)
        
        assert response is not None
        assert mock_vertex_client.generate_response.called
        assert response == "Test response"
    
    async def test_process_request_with_history(self, base_agent, mock_vertex_client):
        """Test de procesamiento con historial de conversación."""
        request = {
            "user_input": "Test input",
            "context": {"conversation_history": ["Previous message"]}
        }
        
        response = await base_agent.process_request(request)
        
        assert response is not None
        call_args = mock_vertex_client.generate_response.call_args
        assert "conversation_history" in call_args[1]["context"]
    
    async def test_streaming_response(self, base_agent, mock_vertex_client):
        """Test de respuesta en streaming."""
        # Mock del generador async
        async def mock_stream():
            yield "chunk1"
            yield "chunk2"
            yield "chunk3"
        
        mock_vertex_client.stream_response.return_value = mock_stream()
        
        request = {
            "user_input": "Test input",
            "stream": True
        }
        
        chunks = []
        async for chunk in base_agent.stream_response(request):
            chunks.append(chunk)
        
        assert len(chunks) == 3
        assert chunks == ["chunk1", "chunk2", "chunk3"]
    
    def test_personality_context(self, base_agent):
        """Test de contexto de personalidad."""
        # Test PRIME personality
        context = base_agent._get_personality_context()
        assert "ejecutivo" in context.lower() or "efficiency" in context.lower()
        
        # Test LONGEVITY personality
        base_agent.personality_type = "LONGEVITY"
        context = base_agent._get_personality_context()
        assert "bienestar" in context.lower() or "wellness" in context.lower()
    
    async def test_error_handling(self, base_agent, mock_vertex_client):
        """Test de manejo de errores."""
        mock_vertex_client.generate_response.side_effect = Exception("Test error")
        
        request = {"user_input": "Test input"}
        
        with pytest.raises(Exception) as exc_info:
            await base_agent.process_request(request)
        
        assert "Test error" in str(exc_info.value)
    
    async def test_structured_output(self, base_agent, mock_vertex_client):
        """Test de salida estructurada."""
        expected_output = {
            "plan": "Test plan",
            "steps": ["Step 1", "Step 2"]
        }
        mock_vertex_client.generate_structured_output.return_value = expected_output
        
        result = await base_agent.generate_structured_output("Generate a plan")
        
        assert result == expected_output
        mock_vertex_client.generate_structured_output.assert_called_once()
    
    def test_security_prompt_inclusion(self, base_agent):
        """Test de inclusión del prompt de seguridad."""
        prompt = base_agent._build_prompt("User input", {})
        
        # Verificar que se incluye el template de seguridad
        assert "seguridad" in prompt.lower() or "security" in prompt.lower()
    
    async def test_telemetry_integration(self, base_agent, mock_vertex_client):
        """Test de integración con telemetría."""
        with patch('agents.base.base_ngx_agent.logger') as mock_logger:
            request = {"user_input": "Test input"}
            await base_agent.process_request(request)
            
            # Verificar que se registran logs
            assert mock_logger.info.called
    
    def test_capability_registration(self, base_agent):
        """Test de registro de capacidades."""
        # Agregar capacidades
        base_agent.register_capability("test_capability", "Test description")
        
        capabilities = base_agent.get_capabilities()
        assert len(capabilities) == 1
        assert capabilities[0]["name"] == "test_capability"
        assert capabilities[0]["description"] == "Test description"
    
    async def test_context_enrichment(self, base_agent):
        """Test de enriquecimiento de contexto."""
        original_context = {"key": "value"}
        enriched = await base_agent._enrich_context(original_context)
        
        assert "key" in enriched
        assert "agent_id" in enriched
        assert "personality_type" in enriched
        assert "timestamp" in enriched
    
    def test_voice_id_assignment(self, base_agent):
        """Test de asignación de voice_id."""
        # Por defecto no debe tener voice_id
        assert base_agent.voice_id is None
        
        # Asignar voice_id
        base_agent.voice_id = "test_voice_123"
        metadata = base_agent.get_agent_metadata()
        assert metadata["voice_id"] == "test_voice_123"


@pytest.mark.asyncio
class TestBaseNGXAgentAsync:
    """Tests asíncronos para BaseNGXAgent."""
    
    async def test_concurrent_requests(self, base_agent, mock_vertex_client):
        """Test de manejo de requests concurrentes."""
        import asyncio
        
        requests = [
            {"user_input": f"Test input {i}"}
            for i in range(5)
        ]
        
        # Procesar requests concurrentemente
        tasks = [base_agent.process_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        assert all(r == "Test response" for r in responses)
        assert mock_vertex_client.generate_response.call_count == 5
    
    async def test_request_timeout(self, base_agent, mock_vertex_client):
        """Test de timeout en requests."""
        import asyncio
        
        # Mock que simula demora
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(10)
            return "Slow response"
        
        mock_vertex_client.generate_response = slow_response
        
        request = {"user_input": "Test input", "timeout": 0.1}
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                base_agent.process_request(request),
                timeout=0.1
            )