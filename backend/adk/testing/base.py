"""
Base Test Classes for ADK
========================

Base classes for testing ADK agents with common setup and utilities.
"""

import unittest
import asyncio
from typing import Type, Optional, Any, Dict
from abc import ABC

import pytest

from ..core import BaseADKAgent, AgentRequest, AgentResponse
from .fixtures import create_test_agent, create_mock_request
from .assertions import assert_valid_response


class AgentTestCase(unittest.TestCase, ABC):
    """
    Base test case for ADK agents.
    
    Provides common setup, teardown, and utility methods for testing agents.
    """
    
    # Override in subclasses
    agent_class: Type[BaseADKAgent] = None
    agent_config: Dict[str, Any] = {}
    
    def setUp(self):
        """Set up test agent."""
        if not self.agent_class:
            raise NotImplementedError("Subclasses must define agent_class")
        
        self.agent = create_test_agent(
            self.agent_class,
            **self.agent_config
        )
    
    def tearDown(self):
        """Clean up after tests."""
        # Reset any agent state
        if hasattr(self.agent, 'shutdown'):
            asyncio.run(self.agent.shutdown())
    
    def assert_valid_response(self, response: AgentResponse):
        """Assert that response is valid."""
        assert_valid_response(response)
    
    def create_request(self, **kwargs) -> AgentRequest:
        """Create a test request."""
        return create_mock_request(**kwargs)
    
    async def execute_agent(self, request: AgentRequest) -> AgentResponse:
        """Execute agent with request."""
        return await self.agent.execute(request)
    
    def run_async(self, coro):
        """Run async coroutine in test."""
        return asyncio.run(coro)


class AsyncAgentTestCase(unittest.IsolatedAsyncioTestCase, ABC):
    """
    Async test case for ADK agents.
    
    Use this for tests that need proper async context.
    """
    
    # Override in subclasses
    agent_class: Type[BaseADKAgent] = None
    agent_config: Dict[str, Any] = {}
    
    async def asyncSetUp(self):
        """Set up test agent."""
        if not self.agent_class:
            raise NotImplementedError("Subclasses must define agent_class")
        
        self.agent = create_test_agent(
            self.agent_class,
            **self.agent_config
        )
    
    async def asyncTearDown(self):
        """Clean up after tests."""
        if hasattr(self.agent, 'shutdown'):
            await self.agent.shutdown()
    
    def assert_valid_response(self, response: AgentResponse):
        """Assert that response is valid."""
        assert_valid_response(response)
    
    def create_request(self, **kwargs) -> AgentRequest:
        """Create a test request."""
        return create_mock_request(**kwargs)


class AgentIntegrationTest(AsyncAgentTestCase):
    """
    Base class for integration tests with real services.
    
    These tests interact with actual LLM and Redis services.
    """
    
    use_real_llm: bool = False
    use_real_redis: bool = False
    
    async def asyncSetUp(self):
        """Set up with real or mock services based on flags."""
        await super().asyncSetUp()
        
        if not self.use_real_llm:
            # Already using mock from parent setUp
            pass
        else:
            # Import and use real LLM client
            from clients.vertex_ai.client import VertexAIClient
            self.agent.llm_client = VertexAIClient()
        
        if not self.use_real_redis:
            # Already using mock from parent setUp
            pass
        else:
            # Import and use real Redis client
            from core.redis_pool import RedisPoolManager
            self.agent.redis_client = RedisPoolManager().get_connection()
    
    @pytest.mark.integration
    async def test_real_llm_integration(self):
        """Test with real LLM (skipped by default)."""
        if not self.use_real_llm:
            self.skipTest("Real LLM integration disabled")
        
        request = self.create_request(prompt="Test integration")
        response = await self.agent.execute(request)
        self.assert_valid_response(response)


class PerformanceTestCase(AsyncAgentTestCase):
    """Base class for performance testing."""
    
    # Performance thresholds
    max_response_time: float = 5.0  # seconds
    max_memory_usage: int = 100 * 1024 * 1024  # 100MB
    
    async def measure_performance(
        self,
        request: AgentRequest,
        iterations: int = 10
    ) -> Dict[str, float]:
        """Measure agent performance over multiple iterations."""
        import time
        import psutil
        import statistics
        
        process = psutil.Process()
        response_times = []
        memory_usage = []
        
        for _ in range(iterations):
            # Measure memory before
            mem_before = process.memory_info().rss
            
            # Measure response time
            start = time.time()
            response = await self.agent.execute(request)
            elapsed = time.time() - start
            
            # Measure memory after
            mem_after = process.memory_info().rss
            
            response_times.append(elapsed)
            memory_usage.append(mem_after - mem_before)
            
            # Validate response
            self.assert_valid_response(response)
        
        return {
            "avg_response_time": statistics.mean(response_times),
            "max_response_time": max(response_times),
            "min_response_time": min(response_times),
            "p95_response_time": sorted(response_times)[int(len(response_times) * 0.95)],
            "avg_memory_delta": statistics.mean(memory_usage),
            "max_memory_delta": max(memory_usage)
        }
    
    async def assert_performance(
        self,
        request: AgentRequest,
        iterations: int = 10
    ):
        """Assert that agent meets performance requirements."""
        metrics = await self.measure_performance(request, iterations)
        
        self.assertLessEqual(
            metrics["avg_response_time"],
            self.max_response_time,
            f"Average response time {metrics['avg_response_time']:.2f}s "
            f"exceeds threshold {self.max_response_time}s"
        )
        
        self.assertLessEqual(
            metrics["max_memory_delta"],
            self.max_memory_usage,
            f"Max memory usage {metrics['max_memory_delta'] / 1024 / 1024:.2f}MB "
            f"exceeds threshold {self.max_memory_usage / 1024 / 1024:.2f}MB"
        )