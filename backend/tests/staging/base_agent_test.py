"""
Base class for individual agent staging tests.

Provides common test patterns and utilities for testing agents
in the staging environment with real GCP connections.
"""

import asyncio
import time
from abc import ABC, abstractmethod

import pytest
from loguru import logger


class BaseAgentStagingTest(ABC):
    """Base class for agent staging tests."""

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the name of the agent being tested."""
        pass

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Return the ID of the agent being tested."""
        pass

    @property
    @abstractmethod
    def agent_class(self):
        """Return the agent class to instantiate."""
        pass

    @pytest.fixture
    async def agent_instance(self, agent_config, gcp_credentials):
        """Create an instance of the agent with staging configuration."""
        agent = self.agent_class(config=agent_config)

        # Initialize the agent
        await agent.initialize()

        yield agent

        # Cleanup
        if hasattr(agent, "cleanup"):
            await agent.cleanup()

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_agent_initialization(self, agent_instance):
        """Test that agent initializes correctly with staging config."""
        assert agent_instance is not None
        assert agent_instance.id == self.agent_id
        assert agent_instance.config is not None

        # Verify agent is ready
        if hasattr(agent_instance, "is_ready"):
            assert await agent_instance.is_ready()

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_agent_health_check(self, agent_instance):
        """Test agent health check endpoint."""
        health = await agent_instance.health_check()

        assert health["status"] == "healthy"
        assert health["agent_id"] == self.agent_id
        assert "timestamp" in health
        assert "version" in health

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_simple_prompt_response(
        self, agent_instance, test_prompts, performance_thresholds, metrics_collector
    ):
        """Test agent response to simple prompt."""
        prompt = test_prompts[self.agent_id]["simple"]

        start_time = time.time()
        try:
            response = await agent_instance.process(prompt)
            elapsed_time = time.time() - start_time

            # Record metrics
            tokens = response.get("usage", {}).get("total_tokens", 0)
            metrics_collector.record_response(self.agent_id, elapsed_time, tokens)

            # Validate response
            assert response is not None
            assert "content" in response
            assert len(response["content"]) > 0

            # Check performance
            assert (
                elapsed_time < performance_thresholds["simple_response_time"]
            ), f"Response time {elapsed_time:.2f}s exceeded threshold {performance_thresholds['simple_response_time']}s"

            # Log for analysis
            logger.info(
                f"{self.agent_name} simple response time: {elapsed_time:.2f}s, tokens: {tokens}"
            )

        except Exception as e:
            metrics_collector.record_error(self.agent_id, str(e))
            raise

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_complex_prompt_response(
        self, agent_instance, test_prompts, performance_thresholds, metrics_collector
    ):
        """Test agent response to complex prompt."""
        prompt = test_prompts[self.agent_id]["complex"]

        start_time = time.time()
        try:
            response = await agent_instance.process(prompt)
            elapsed_time = time.time() - start_time

            # Record metrics
            tokens = response.get("usage", {}).get("total_tokens", 0)
            metrics_collector.record_response(self.agent_id, elapsed_time, tokens)

            # Validate response
            assert response is not None
            assert "content" in response
            assert (
                len(response["content"]) > 100
            ), "Complex prompt should generate detailed response"

            # Check performance
            assert (
                elapsed_time < performance_thresholds["complex_response_time"]
            ), f"Response time {elapsed_time:.2f}s exceeded threshold {performance_thresholds['complex_response_time']}s"

            # Validate response quality
            self.validate_complex_response(response["content"], prompt)

            logger.info(
                f"{self.agent_name} complex response time: {elapsed_time:.2f}s, tokens: {tokens}"
            )

        except Exception as e:
            metrics_collector.record_error(self.agent_id, str(e))
            raise

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_edge_case_handling(
        self, agent_instance, test_prompts, metrics_collector
    ):
        """Test agent handling of edge cases."""
        prompt = test_prompts[self.agent_id]["edge_case"]

        try:
            response = await agent_instance.process(prompt)

            # Should handle gracefully
            assert response is not None
            assert "content" in response

            # Should provide helpful response even for edge cases
            self.validate_edge_case_response(response["content"], prompt)

            metrics_collector.record_response(self.agent_id, 0)

        except Exception as e:
            # Some edge cases might be expected to fail
            # but should fail gracefully
            logger.warning(f"{self.agent_name} edge case handling: {str(e)}")
            metrics_collector.record_error(self.agent_id, str(e))

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    @pytest.mark.slow
    async def test_concurrent_requests(
        self, agent_instance, test_prompts, performance_thresholds, metrics_collector
    ):
        """Test agent handling concurrent requests."""
        prompts = [
            test_prompts[self.agent_id]["simple"],
            test_prompts[self.agent_id]["simple"],
            test_prompts[self.agent_id]["simple"],
        ]

        start_time = time.time()

        # Send concurrent requests
        tasks = [agent_instance.process(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_time = time.time() - start_time

        # Validate all responses
        success_count = 0
        for response in responses:
            if isinstance(response, Exception):
                metrics_collector.record_error(self.agent_id, str(response))
            else:
                success_count += 1
                metrics_collector.record_response(
                    self.agent_id, elapsed_time / len(prompts)
                )

        # At least 2/3 should succeed
        assert (
            success_count >= 2
        ), f"Only {success_count}/3 concurrent requests succeeded"

        logger.info(
            f"{self.agent_name} concurrent requests: {success_count}/3 succeeded in {elapsed_time:.2f}s"
        )

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_streaming_response(
        self, agent_instance, test_prompts, performance_thresholds, metrics_collector
    ):
        """Test agent streaming response capability."""
        if not hasattr(agent_instance, "stream"):
            pytest.skip(f"{self.agent_name} does not support streaming")

        prompt = test_prompts[self.agent_id]["simple"]

        start_time = time.time()
        first_token_time = None
        chunks = []

        try:
            async for chunk in agent_instance.stream(prompt):
                if first_token_time is None:
                    first_token_time = time.time() - start_time
                chunks.append(chunk)

            total_time = time.time() - start_time

            # Validate streaming
            assert len(chunks) > 0, "No chunks received"
            assert (
                first_token_time < performance_thresholds["streaming_first_token"]
            ), f"First token time {first_token_time:.2f}s exceeded threshold"

            metrics_collector.record_response(self.agent_id, total_time)

            logger.info(
                f"{self.agent_name} streaming: first token in {first_token_time:.2f}s, "
                f"total {len(chunks)} chunks in {total_time:.2f}s"
            )

        except Exception as e:
            metrics_collector.record_error(self.agent_id, str(e))
            raise

    @pytest.mark.staging
    @pytest.mark.agent
    @pytest.mark.requires_gcp
    async def test_error_recovery(self, agent_instance, metrics_collector):
        """Test agent error recovery mechanisms."""
        # Test with invalid input
        invalid_inputs = [
            "",  # Empty prompt
            "x" * 10000,  # Very long prompt
            {"not": "a string"},  # Wrong type
        ]

        recovery_count = 0

        for invalid_input in invalid_inputs:
            try:
                # Should handle gracefully
                response = await agent_instance.process(invalid_input)
                if response and "error" not in response:
                    recovery_count += 1
            except Exception as e:
                # Should not crash completely
                logger.warning(f"{self.agent_name} handled error: {type(e).__name__}")
                recovery_count += 1

        # Should recover from all errors
        assert recovery_count == len(
            invalid_inputs
        ), f"Agent only recovered from {recovery_count}/{len(invalid_inputs)} errors"

    @pytest.mark.staging
    @pytest.mark.agent
    async def test_metrics_collection(
        self, agent_instance, test_prompts, metrics_collector
    ):
        """Test that agent properly reports metrics."""
        prompt = test_prompts[self.agent_id]["simple"]

        response = await agent_instance.process(prompt)

        # Should include usage metrics
        assert "usage" in response
        assert "prompt_tokens" in response["usage"]
        assert "completion_tokens" in response["usage"]
        assert "total_tokens" in response["usage"]

        # Should include timing metrics
        if "metrics" in response:
            assert "response_time" in response["metrics"]
            assert "model_time" in response["metrics"]

    def validate_complex_response(self, content: str, prompt: str):
        """Validate complex response quality - override in subclasses."""
        # Default validation
        assert len(content.split()) > 50, "Complex response should be detailed"
        assert any(
            word in content.lower()
            for word in ["paso", "primero", "segundo", "recomendar"]
        ), "Complex response should include structured steps"

    def validate_edge_case_response(self, content: str, prompt: str):
        """Validate edge case response - override in subclasses."""
        # Default validation
        assert (
            len(content) > 20
        ), "Should provide meaningful response even for edge cases"
        assert any(
            word in content.lower()
            for word in ["ayudar", "entender", "clarificar", "específico"]
        ), "Edge case response should be helpful"

    @pytest.fixture(scope="class", autouse=True)
    async def class_metrics_summary(self, metrics_collector):
        """Print metrics summary after all tests in class."""
        yield

        summary = metrics_collector.get_summary()
        logger.info(f"\n{self.agent_name} Test Summary:")
        logger.info(f"  Total Requests: {summary.get('total_requests', 0)}")
        logger.info(f"  Success Rate: {summary.get('success_rate', 0):.2%}")
        logger.info(f"  Avg Response Time: {summary.get('avg_response_time', 0):.2f}s")
        logger.info(f"  Total Tokens Used: {summary.get('total_tokens', 0)}")
        logger.info(f"  Errors: {summary.get('errors', 0)}")
