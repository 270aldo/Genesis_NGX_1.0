"""
Testing Utilities for ADK
========================

Provides test fixtures, mocks, and utilities for testing
ADK-based agents.
"""

from .fixtures import (
    create_mock_request,
    create_mock_response,
    create_test_agent,
    mock_llm_client,
    mock_redis_client
)

from .mocks import (
    MockLLMClient,
    MockRedisClient,
    MockAgent,
    MockSkill
)

from .base import (
    AgentTestCase,
    AgentIntegrationTest,
    AsyncAgentTestCase
)

from .assertions import (
    assert_valid_response,
    assert_response_contains,
    assert_streaming_response,
    assert_metrics_valid
)

__all__ = [
    # Fixtures
    "create_mock_request",
    "create_mock_response",
    "create_test_agent",
    "mock_llm_client",
    "mock_redis_client",
    
    # Mocks
    "MockLLMClient",
    "MockRedisClient",
    "MockAgent",
    "MockSkill",
    
    # Base Classes
    "AgentTestCase",
    "AgentIntegrationTest",
    "AsyncAgentTestCase",
    
    # Assertions
    "assert_valid_response",
    "assert_response_contains",
    "assert_streaming_response",
    "assert_metrics_valid"
]