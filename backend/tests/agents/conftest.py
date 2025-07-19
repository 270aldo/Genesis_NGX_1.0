"""
Fixtures compartidos para tests de agentes.

Este módulo proporciona fixtures comunes que pueden ser utilizados
por todos los tests de agentes.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.schemas.chat import AgentResponse
from core.agent_collaboration_hub import AgentCapability
from core.logging_config import get_logger
from clients.vertex_ai.client import VertexAIClient


# ============================================================================
# FIXTURES DE CLIENTES Y SERVICIOS
# ============================================================================

@pytest.fixture
def mock_vertex_ai_client():
    """Mock del cliente Vertex AI"""
    client = MagicMock(spec=VertexAIClient)
    
    # Configurar respuestas por defecto
    client.generate_content = AsyncMock(return_value={
        "text": "Respuesta generada por IA",
        "finish_reason": "STOP",
        "safety_ratings": []
    })
    
    client.generate_content_stream = AsyncMock()
    client.generate_with_functions = AsyncMock(return_value={
        "text": "Respuesta con funciones",
        "function_calls": []
    })
    
    return client


@pytest.fixture
def mock_supabase_client():
    """Mock del cliente Supabase"""
    client = MagicMock()
    
    # Configurar tablas mock
    client.table = MagicMock(return_value=MagicMock(
        select=MagicMock(return_value=MagicMock(
            execute=AsyncMock(return_value=MagicMock(data=[]))
        )),
        insert=MagicMock(return_value=MagicMock(
            execute=AsyncMock(return_value=MagicMock(data=[{"id": "123"}]))
        )),
        update=MagicMock(return_value=MagicMock(
            eq=MagicMock(return_value=MagicMock(
                execute=AsyncMock(return_value=MagicMock(data=[]))
            ))
        ))
    ))
    
    return client


@pytest.fixture
def mock_cache_manager():
    """Mock del gestor de caché avanzado"""
    cache = MagicMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=True)
    cache.get_comprehensive_statistics = AsyncMock(return_value={
        "global_statistics": {
            "total_requests": 1000,
            "total_hits": 850,
            "global_hit_ratio": 0.85
        }
    })
    return cache


@pytest.fixture
def mock_mcp_toolkit():
    """Mock del MCP toolkit"""
    toolkit = MagicMock()
    
    # Configurar herramientas disponibles
    toolkit.available_tools = {
        "calculate_calories": MagicMock(),
        "get_exercise_info": MagicMock(),
        "analyze_biometrics": MagicMock()
    }
    
    toolkit.execute_tool = AsyncMock(return_value={
        "success": True,
        "result": {"data": "Tool result"}
    })
    
    return toolkit


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA
# ============================================================================

@pytest.fixture
def sample_user_context():
    """Contexto de usuario de ejemplo"""
    return {
        "user_id": "test_user_123",
        "age": 30,
        "gender": "male",
        "fitness_level": "intermediate",
        "goals": ["muscle_gain", "endurance"],
        "preferences": {
            "personality": "prime",
            "language": "es",
            "units": "metric"
        },
        "restrictions": ["vegetarian"],
        "timezone": "America/Mexico_City"
    }


# TODO: Actualizar cuando AgentMetadata esté definido
# @pytest.fixture
# def sample_agent_metadata():
#     """Metadata de agente de ejemplo"""
#     return AgentMetadata(
#         agent_id="test_agent",
#         name="Test Agent",
#         version="1.0.0",
#         capabilities=[
#             AgentCapability(
#                 name="test_capability",
#                 description="Test capability"
#             )
#         ],
#         model="gemini-1.5-flash-002",
#         temperature=0.7,
#         max_tokens=1024,
#         personality="prime",
#         created_at=datetime.utcnow(),
#         updated_at=datetime.utcnow()
#     )


@pytest.fixture
def sample_agent_response():
    """Respuesta de agente de ejemplo"""
    return AgentResponse(
        agent_id="test_agent",
        response="Esta es una respuesta de prueba",
        confidence=0.95,
        metadata={
            "tokens_used": 150,
            "response_time": 1.2,
            "model": "gemini-1.5-flash-002"
        }
    )


# ============================================================================
# FIXTURES DE CONFIGURACIÓN
# ============================================================================

@pytest.fixture
def mock_settings():
    """Mock de configuración"""
    settings = MagicMock()
    settings.vertex_ai_project = "test-project"
    settings.vertex_ai_location = "us-central1"
    settings.enable_streaming = True
    settings.enable_caching = True
    settings.debug = True
    settings.env = "test"
    return settings


@pytest.fixture
def mock_logger():
    """Mock del logger"""
    logger = MagicMock()
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    return logger


# ============================================================================
# FIXTURES DE AGENTES MOCK
# ============================================================================

@pytest.fixture
def mock_base_agent():
    """Mock de un agente base"""
    agent = MagicMock()
    agent.agent_id = "mock_agent"
    agent.name = "Mock Agent"
    agent.process = AsyncMock(return_value={
        "response": "Mock response",
        "confidence": 0.9
    })
    agent.get_capabilities = MagicMock(return_value=[
        {"name": "capability_1", "description": "Test capability"}
    ])
    return agent


@pytest.fixture
def mock_orchestrator():
    """Mock del orchestrator"""
    orchestrator = MagicMock()
    orchestrator.agent_id = "orchestrator"
    orchestrator.route_request = AsyncMock(return_value={
        "agent": "precision_nutrition_architect",
        "confidence": 0.95
    })
    orchestrator.coordinate_agents = AsyncMock(return_value={
        "responses": [
            {"agent": "sage", "response": "Nutrition advice"},
            {"agent": "nexus", "response": "Training advice"}
        ]
    })
    return orchestrator


# ============================================================================
# FIXTURES DE UTILIDADES
# ============================================================================

@pytest.fixture
def async_mock_context():
    """Context manager para mocks asíncronos"""
    class AsyncMockContext:
        def __init__(self, target, **kwargs):
            self.target = target
            self.kwargs = kwargs
            self.patcher = None
            
        async def __aenter__(self):
            self.patcher = patch(self.target, **self.kwargs)
            return self.patcher.__enter__()
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.patcher.__exit__(exc_type, exc_val, exc_tb)
    
    return AsyncMockContext


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singletons antes de cada test"""
    # Aquí podríamos resetear cualquier singleton si fuera necesario
    yield
    # Cleanup después del test
    pass


# ============================================================================
# MARCADORES Y CONFIGURACIÓN
# ============================================================================

def pytest_configure(config):
    """Configurar marcadores personalizados"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "agents: marks tests specific to agents"
    )