"""
Example Tests for ADK
====================

Example tests demonstrating how to use the ADK testing utilities.
"""

import pytest
import asyncio
from typing import Dict, Any

from adk.core import BaseADKAgent, AgentRequest
from adk.testing import (
    AsyncAgentTestCase,
    create_mock_request,
    assert_valid_response,
    assert_response_contains,
    MockSkill
)
from adk.toolkit import cache_result
from adk.patterns import retry, circuit_breaker, StreamingMixin


class ExampleAgent(BaseADKAgent, StreamingMixin):
    """Example agent for testing."""
    
    agent_id = "example_agent"
    agent_name = "Example Agent"
    agent_type = "specialist"
    agent_version = "1.0.0"
    
    def _initialize_skills(self):
        """Initialize example skills."""
        self.register_skill("example_skill", MockSkill("example", "Skill result"))
    
    @cache_result(ttl=60)
    @retry(max_attempts=3)
    @circuit_breaker(failure_threshold=2)
    async def _execute_core(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute with all the patterns."""
        # Use skill
        skill_result = await self.get_skill("example_skill").execute({
            "input": request.prompt
        })
        
        # Generate response
        llm_response = await self.llm_client.generate(
            prompt=f"Process this: {request.prompt}",
            max_tokens=self.config.max_tokens
        )
        
        return {
            "content": llm_response["content"],
            "metadata": {
                "skill_result": skill_result,
                "patterns_used": ["cache", "retry", "circuit_breaker"]
            },
            "tokens_used": llm_response.get("tokens_used", 0)
        }
    
    async def stream_execute(self, request: AgentRequest):
        """Example streaming implementation."""
        async def generate_chunks():
            words = ["This", "is", "a", "streaming", "response", "example"]
            for word in words:
                yield word + " "
                await asyncio.sleep(0.1)
        
        async for event in self.stream_response(generate_chunks()):
            yield event


class TestExampleAgent(AsyncAgentTestCase):
    """Test cases for ExampleAgent."""
    
    agent_class = ExampleAgent
    agent_config = {
        "max_tokens": 500,
        "temperature": 0.5,
        "enable_caching": True
    }
    
    async def test_basic_execution(self):
        """Test basic agent execution."""
        # Create request
        request = self.create_request(
            prompt="Test prompt",
            user_id="test_user"
        )
        
        # Execute agent
        response = await self.agent.execute(request)
        
        # Validate response
        self.assert_valid_response(response)
        self.assertEqual(response.agent_id, "example_agent")
        self.assertTrue(response.success)
        self.assertIsNotNone(response.content)
    
    async def test_skill_execution(self):
        """Test that skills are executed properly."""
        request = self.create_request(prompt="Test skill execution")
        response = await self.agent.execute(request)
        
        self.assert_valid_response(response)
        
        # Check skill was executed
        skill = self.agent.get_skill("example_skill")
        self.assertEqual(skill.execution_count, 1)
        
        # Check skill result in metadata
        self.assertIn("skill_result", response.metadata)
        skill_result = response.metadata["skill_result"]
        self.assertEqual(skill_result["result"], "Skill result")
    
    async def test_caching(self):
        """Test that caching works."""
        request = self.create_request(prompt="Cached request")
        
        # First execution
        response1 = await self.agent.execute(request)
        self.assert_valid_response(response1)
        
        # Check LLM was called
        self.assertEqual(self.agent.llm_client.call_count, 1)
        
        # Second execution (should use cache)
        response2 = await self.agent.execute(request)
        self.assert_valid_response(response2)
        
        # LLM should not be called again
        self.assertEqual(self.agent.llm_client.call_count, 1)
        
        # Responses should be identical
        self.assertEqual(response1.content, response2.content)
    
    async def test_retry_on_failure(self):
        """Test retry pattern."""
        request = self.create_request(prompt="Retry test")
        
        # Make LLM fail twice then succeed
        self.agent.llm_client.fail_after(2)
        self.agent.llm_client.set_responses([
            "First attempt",
            "Second attempt", 
            "Success!"
        ])
        
        # Should succeed after retries
        response = await self.agent.execute(request)
        self.assert_valid_response(response)
        self.assertEqual(response.content, "Success!")
        
        # Check that it retried
        self.assertEqual(self.agent.llm_client.call_count, 3)
    
    async def test_circuit_breaker(self):
        """Test circuit breaker pattern."""
        # This would require more complex setup to test properly
        # Just verify the decorator is applied
        self.assertTrue(hasattr(self.agent._execute_core, '__wrapped__'))
    
    async def test_streaming(self):
        """Test streaming functionality."""
        request = self.create_request(
            prompt="Stream test",
            streaming=True
        )
        
        events = []
        async for event in self.agent.stream_execute(request):
            events.append(event)
        
        # Verify stream structure
        from adk.testing import assert_streaming_response
        assert_streaming_response(events, min_data_events=6)
        
        # Check data events
        data_events = [e for e in events if e.event_type.value == "data"]
        self.assertEqual(len(data_events), 6)
    
    async def test_error_handling(self):
        """Test error handling."""
        request = self.create_request(prompt="Error test")
        
        # Make LLM always fail
        self.agent.llm_client._should_fail = True
        
        # Should raise after retries exhausted
        with self.assertRaises(Exception):
            await self.agent.execute(request)
    
    async def test_metrics(self):
        """Test metrics collection."""
        # Execute a few requests
        for i in range(3):
            request = self.create_request(prompt=f"Test {i}")
            response = await self.agent.execute(request)
            self.assert_valid_response(response)
        
        # Get metrics
        metrics = self.agent.get_metrics()
        
        # Validate metrics
        from adk.testing import assert_metrics_valid
        assert_metrics_valid(metrics, "example_agent")
        
        # Check specific values
        self.assertEqual(metrics["request_count"], 3)
        self.assertEqual(metrics["error_count"], 0)
        self.assertEqual(metrics["error_rate"], 0.0)
    
    async def test_health_check(self):
        """Test health check functionality."""
        health = await self.agent.health_check()
        
        from adk.testing import assert_health_check_passed
        assert_health_check_passed(health)
        
        # Check specific components
        self.assertTrue(health["checks"]["agent"])
        self.assertTrue(health["checks"]["llm_client"])
        self.assertTrue(health["checks"]["redis"])


class TestADKPatterns(AsyncAgentTestCase):
    """Test ADK patterns in isolation."""
    
    agent_class = ExampleAgent
    
    async def test_retry_policy(self):
        """Test custom retry policies."""
        from adk.patterns.retry import RetryPolicy, CommonRetryPolicies
        
        # Test API retry policy
        policy = CommonRetryPolicies.api_calls()
        self.assertEqual(policy.max_attempts, 3)
        self.assertTrue(policy.should_retry(ConnectionError()))
        self.assertFalse(policy.should_retry(ValueError()))
        
        # Test custom policy
        custom_policy = RetryPolicy(
            max_attempts=5,
            initial_delay=0.5,
            retry_on=(IOError, ConnectionError),
            dont_retry_on=(KeyboardInterrupt,)
        )
        
        self.assertTrue(custom_policy.should_retry(IOError()))
        self.assertFalse(custom_policy.should_retry(KeyboardInterrupt()))
    
    async def test_streaming_events(self):
        """Test streaming event creation."""
        from adk.patterns.streaming import StreamEvent, StreamEventType
        
        # Create event
        event = StreamEvent(
            event_type=StreamEventType.DATA,
            data={"message": "Test data"},
            sequence=1
        )
        
        # Test SSE format
        sse = event.to_sse()
        self.assertIn("event: data", sse)
        self.assertIn("data: {", sse)
        self.assertIn("id: 1", sse)
        
        # Test JSON format
        json_str = event.to_json()
        self.assertIn('"type": "data"', json_str)
        self.assertIn('"message": "Test data"', json_str)


# Performance test example
class TestExampleAgentPerformance(AsyncAgentTestCase):
    """Performance tests for ExampleAgent."""
    
    agent_class = ExampleAgent
    
    @pytest.mark.performance
    async def test_response_time(self):
        """Test agent response time."""
        from adk.testing.base import PerformanceTestCase
        
        # Create performance test instance
        perf_test = PerformanceTestCase()
        perf_test.agent = self.agent
        perf_test.max_response_time = 1.0  # 1 second max
        
        # Run performance test
        request = create_mock_request(prompt="Performance test")
        await perf_test.assert_performance(request, iterations=5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])