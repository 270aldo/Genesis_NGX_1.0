"""
Test Fixtures for ADK
====================

Common fixtures for testing ADK agents.
"""

from typing import Dict, Any, Optional, Type
import uuid
from datetime import datetime
import pytest

from ..core import AgentRequest, AgentResponse, BaseADKAgent
from ..core.types import ConversationContext, AgentType
from .mocks import MockLLMClient, MockRedisClient


def create_mock_request(
    prompt: str = "Test prompt",
    user_id: str = "test_user",
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    streaming: bool = False,
    timeout: int = 30
) -> AgentRequest:
    """Create a mock agent request for testing."""
    return AgentRequest(
        prompt=prompt,
        user_id=user_id,
        session_id=session_id or str(uuid.uuid4()),
        metadata=metadata or {},
        streaming=streaming,
        timeout=timeout
    )


def create_mock_response(
    success: bool = True,
    agent_id: str = "test_agent",
    agent_name: str = "Test Agent",
    content: Any = "Test response",
    error: Optional[str] = None,
    processing_time: float = 0.1,
    tokens_used: int = 100
) -> AgentResponse:
    """Create a mock agent response for testing."""
    return AgentResponse(
        success=success,
        agent_id=agent_id,
        agent_name=agent_name,
        content=content,
        error=error,
        processing_time=processing_time,
        tokens_used=tokens_used,
        session_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow()
    )


def create_test_agent(
    agent_class: Type[BaseADKAgent],
    **config_overrides
) -> BaseADKAgent:
    """
    Create a test instance of an agent with mocked dependencies.
    
    Args:
        agent_class: The agent class to instantiate
        **config_overrides: Configuration overrides
    
    Returns:
        Agent instance with mocked dependencies
    """
    # Default test configuration
    config = {
        "max_tokens": 1000,
        "temperature": 0.5,
        "enable_caching": False,  # Disable caching in tests by default
        "enable_monitoring": False,  # Disable monitoring in tests
    }
    config.update(config_overrides)
    
    # Create agent instance
    agent = agent_class(config=config, debug=True)
    
    # Replace real clients with mocks
    agent.llm_client = MockLLMClient()
    agent.redis_client = MockRedisClient()
    
    return agent


@pytest.fixture
def mock_request():
    """Pytest fixture for mock request."""
    return create_mock_request()


@pytest.fixture
def mock_llm_client():
    """Pytest fixture for mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def mock_redis_client():
    """Pytest fixture for mock Redis client."""
    return MockRedisClient()


@pytest.fixture
def conversation_context():
    """Pytest fixture for conversation context."""
    context = ConversationContext(
        conversation_id=str(uuid.uuid4()),
        messages=[
            {
                "role": "user",
                "content": "Hello",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "role": "assistant",
                "content": "Hello! How can I help you?",
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        user_profile={
            "name": "Test User",
            "preferences": {"language": "en"}
        }
    )
    return context


@pytest.fixture
def sample_training_request():
    """Pytest fixture for sample training agent request."""
    return create_mock_request(
        prompt="Create a workout plan",
        metadata={
            "workout_type": "strength",
            "fitness_level": "intermediate",
            "duration_minutes": 45,
            "equipment": ["dumbbells", "barbell"],
            "goals": ["muscle_gain", "strength"]
        }
    )


@pytest.fixture
def sample_nutrition_request():
    """Pytest fixture for sample nutrition agent request."""
    return create_mock_request(
        prompt="Create a meal plan",
        metadata={
            "diet_type": "balanced",
            "calories_target": 2000,
            "meals_per_day": 4,
            "allergies": ["nuts"],
            "preferences": ["high_protein"]
        }
    )


class AgentTestFixtures:
    """Collection of test fixtures for different agent types."""
    
    @staticmethod
    def get_test_config(agent_type: AgentType) -> Dict[str, Any]:
        """Get test configuration for specific agent type."""
        base_config = {
            "max_tokens": 1000,
            "temperature": 0.5,
            "enable_caching": False,
            "enable_monitoring": False,
            "timeout": 5
        }
        
        # Type-specific overrides
        if agent_type == AgentType.ORCHESTRATOR:
            base_config.update({
                "max_agents": 5,
                "coordination_timeout": 10
            })
        elif agent_type == AgentType.SPECIALIST:
            base_config.update({
                "specialized_model": "test-model",
                "skill_timeout": 3
            })
        
        return base_config
    
    @staticmethod
    def get_sample_request(agent_type: AgentType) -> AgentRequest:
        """Get sample request for specific agent type."""
        if agent_type == AgentType.ORCHESTRATOR:
            return create_mock_request(
                prompt="Analyze user fitness goals and create comprehensive plan",
                metadata={
                    "user_goals": ["weight_loss", "endurance"],
                    "context_type": "multi_agent"
                }
            )
        elif agent_type == AgentType.SPECIALIST:
            return create_mock_request(
                prompt="Generate specialized response",
                metadata={
                    "specialty": "fitness",
                    "detail_level": "high"
                }
            )
        else:
            return create_mock_request()
    
    @staticmethod
    def get_expected_response(agent_type: AgentType) -> Dict[str, Any]:
        """Get expected response structure for agent type."""
        base_response = {
            "success": True,
            "has_content": True,
            "has_metadata": True
        }
        
        if agent_type == AgentType.ORCHESTRATOR:
            base_response.update({
                "agents_used": ["training", "nutrition"],
                "coordination_time": 2.5
            })
        
        return base_response