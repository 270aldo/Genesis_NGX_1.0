"""
Shared fixtures for A2A integration tests.

Provides common test infrastructure for all A2A tests.
"""

import asyncio
import os
import sys
from typing import Any, AsyncGenerator, Dict

import pytest

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from core.logging_config import get_logger
from infrastructure.adapters.a2a_adapter import A2AAdapter
from tests.integration.a2a.utils.agent_simulator import AgentSimulator, SimulatedAgent
from tests.integration.a2a.utils.test_server import TestA2AServer

logger = get_logger(__name__)


@pytest.fixture(scope="function")
async def test_a2a_server() -> AsyncGenerator[TestA2AServer, None]:
    """
    Provides an isolated A2A test server for each test.

    The server runs on a dynamically allocated port to avoid conflicts.
    """
    server = TestA2AServer()
    # Set a reasonable timeout to avoid hanging tests
    await asyncio.wait_for(server.start(), timeout=10.0)

    yield server

    # Cleanup
    await server.stop()


@pytest.fixture(scope="function")
async def agent_simulator() -> AgentSimulator:
    """
    Provides an agent simulator with all standard GENESIS agents.
    """
    return AgentSimulator()


@pytest.fixture(scope="function")
async def a2a_adapter(test_a2a_server: TestA2AServer) -> A2AAdapter:
    """
    Provides an A2A adapter connected to the test server.
    """
    # Create adapter with test server configuration
    adapter = A2AAdapter()

    # Override the server URL to point to test server
    import infrastructure.a2a_optimized as a2a_module

    original_server = a2a_module.a2a_server

    # Replace with test server
    a2a_module.a2a_server = test_a2a_server.server

    yield adapter

    # Restore original server
    a2a_module.a2a_server = original_server


@pytest.fixture(scope="function")
async def registered_agents(
    test_a2a_server: TestA2AServer, agent_simulator: AgentSimulator
) -> Dict[str, SimulatedAgent]:
    """
    Provides a set of pre-registered simulated agents.

    Returns a dictionary of agent_id -> SimulatedAgent.
    """
    # Register all agents with the test server
    await agent_simulator.register_all_with_server(test_a2a_server)

    # Wait for all agents to be registered
    agent_ids = list(agent_simulator.agents.keys())
    success = await test_a2a_server.wait_for_agents(agent_ids, timeout=5.0)

    if not success:
        pytest.fail("Failed to register all agents within timeout")

    return agent_simulator.agents


@pytest.fixture(scope="function")
async def orchestrator_agent(
    registered_agents: Dict[str, SimulatedAgent]
) -> SimulatedAgent:
    """
    Provides the orchestrator agent for coordination tests.
    """
    return registered_agents["orchestrator"]


@pytest.fixture(scope="function")
def sample_messages() -> Dict[str, Dict[str, Any]]:
    """
    Provides sample messages for testing.
    """
    return {
        "simple_training": {
            "user_input": "I need a training plan",
            "context": {"user_id": "test_user_1"},
        },
        "complex_request": {
            "user_input": "I'm frustrated with my training and nutrition. Need help!",
            "context": {
                "user_id": "test_user_2",
                "emotion": "frustrated",
                "topics": ["training", "nutrition"],
            },
        },
        "emergency": {
            "user_input": "I'm having chest pain during exercise",
            "context": {"user_id": "test_user_3", "urgency": "high", "medical": True},
        },
        "genetic_inquiry": {
            "user_input": "How do my genes affect my training?",
            "context": {"user_id": "test_user_4", "has_genetic_data": True},
        },
    }


@pytest.fixture(scope="function")
def performance_metrics() -> Dict[str, Any]:
    """
    Provides a structure for collecting performance metrics.
    """
    return {
        "latencies": [],
        "throughput": 0,
        "errors": 0,
        "success_rate": 0.0,
        "max_latency_ms": 0,
        "min_latency_ms": float("inf"),
        "avg_latency_ms": 0,
    }


@pytest.fixture(scope="function")
async def cleanup_agents():
    """
    Ensures all agents are cleaned up after tests.
    """
    agents_to_cleanup = []

    yield agents_to_cleanup

    # Cleanup any remaining agents
    for agent in agents_to_cleanup:
        try:
            if hasattr(agent, "cleanup"):
                await agent.cleanup()
        except Exception as e:
            logger.warning(f"Error cleaning up agent: {e}")


# Pytest configuration for async tests
def pytest_configure(config):
    """Configure pytest for async testing."""
    # Ensure we're using asyncio mode
    config.option.asyncio_mode = "auto"


# Custom markers
def pytest_collection_modifyitems(config, items):
    """Add custom markers to tests."""
    for item in items:
        # Add integration marker to all tests in this directory
        item.add_marker(pytest.mark.integration)

        # Add a2a marker
        item.add_marker(pytest.mark.a2a)


# Async test helpers
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Timeout configuration
@pytest.fixture
def default_timeout() -> float:
    """Default timeout for async operations."""
    return 10.0


@pytest.fixture
def long_timeout() -> float:
    """Long timeout for complex operations."""
    return 30.0


# Test environment configuration
@pytest.fixture(scope="session")
def test_env():
    """Configure test environment variables."""
    original_env = os.environ.copy()

    # Set test-specific environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["A2A_TEST_MODE"] = "true"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
