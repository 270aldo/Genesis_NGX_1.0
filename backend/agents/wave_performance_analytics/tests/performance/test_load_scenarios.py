"""
Performance tests for WAVE Performance Analytics Agent.
A+ testing framework with load testing and performance benchmarks.
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import concurrent.futures
from typing import List, Dict, Any

from agents.wave_performance_analytics.agent_optimized import (
    WavePerformanceAnalyticsAgent,
)


class TestResponseTimePerformance:
    """Test response time performance under various loads."""

    @pytest.mark.asyncio
    async def test_single_request_performance(
        self, wave_agent, sample_context, performance_benchmarks
    ):
        """Test single request response time."""
        message = "How is my recovery today?"

        # Mock fast skills manager response
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "general_recovery",
                "status": "good",
            }
        )

        # Measure response time
        start_time = time.time()
        result = await wave_agent._run_async_impl(message, sample_context)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Verify performance meets benchmark
        benchmark = (
            performance_benchmarks["response_times"]["simple_query"] * 1000
        )  # Convert to ms
        assert (
            response_time < benchmark
        ), f"Response time {response_time}ms exceeds benchmark {benchmark}ms"
        assert result["success"] is True

        # Verify response time is recorded in result
        if "usage_stats" in result:
            assert "response_time_ms" in result["usage_stats"]

    @pytest.mark.asyncio
    async def test_complex_analysis_performance(
        self,
        wave_agent,
        sample_user_data,
        sample_biometric_data,
        performance_benchmarks,
    ):
        """Test complex analysis response time."""
        context = {
            **sample_user_data,
            "biometric_data": sample_biometric_data,
            "recovery_data": {"protocols": ["sleep", "mobility"]},
            "program_type": "PRIME",
            "session_id": "perf_test_complex",
        }

        message = "Provide comprehensive fusion analysis with injury prediction"

        # Mock complex analysis response
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "recovery_analytics_fusion",
                "fusion_analysis": {
                    "holistic_insights": ["insight1", "insight2"],
                    "analytical_insights": ["data1", "data2"],
                    "recommendations": ["rec1", "rec2"],
                },
                "prediction": {"injury_risk": 0.15},
                "confidence": 0.87,
            }
        )

        start_time = time.time()
        result = await wave_agent._run_async_impl(message, context)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000

        # Verify complex analysis benchmark
        benchmark = performance_benchmarks["response_times"]["complex_analysis"] * 1000
        assert (
            response_time < benchmark
        ), f"Complex analysis time {response_time}ms exceeds benchmark {benchmark}ms"
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_fusion_analysis_performance(
        self, wave_agent, sample_fusion_request, performance_benchmarks
    ):
        """Test fusion analysis performance."""
        message = sample_fusion_request["message"]
        context = sample_fusion_request["context"]

        # Mock fusion analysis with realistic complexity
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "recovery_analytics_fusion",
                "fusion_analysis": {
                    "fusion_confidence": 0.89,
                    "cross_domain_insights": ["insight1", "insight2", "insight3"],
                    "optimization_recommendations": ["opt1", "opt2", "opt3"],
                    "predictive_indicators": {"risk": 0.12, "readiness": 0.88},
                },
            }
        )

        start_time = time.time()
        result = await wave_agent._run_async_impl(message, context)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000

        # Verify fusion analysis benchmark
        benchmark = performance_benchmarks["response_times"]["fusion_analysis"] * 1000
        assert (
            response_time < benchmark
        ), f"Fusion analysis time {response_time}ms exceeds benchmark {benchmark}ms"
        assert result["success"] is True


class TestConcurrentRequestPerformance:
    """Test performance under concurrent request loads."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_low_load(
        self, wave_agent, performance_benchmarks
    ):
        """Test performance with low concurrent load (5 requests)."""
        num_requests = 5
        contexts = [
            {
                "user_id": f"user_{i}",
                "session_id": f"session_{i}",
                "program_type": "PRIME",
                "timestamp": datetime.now().isoformat(),
            }
            for i in range(num_requests)
        ]

        messages = [
            f"Analyze my recovery status - request {i}" for i in range(num_requests)
        ]

        # Mock consistent responses
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "general_recovery",
                "analysis": "mock_analysis",
            }
        )

        # Execute concurrent requests
        start_time = time.time()
        tasks = [
            wave_agent._run_async_impl(message, context)
            for message, context in zip(messages, contexts)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_request = (total_time / num_requests) * 1000  # ms

        # Verify all requests succeeded
        assert len(results) == num_requests
        for result in results:
            assert result["success"] is True

        # Verify average response time under load
        benchmark = (
            performance_benchmarks["response_times"]["simple_query"] * 1000 * 1.5
        )  # 50% overhead allowed
        assert (
            avg_time_per_request < benchmark
        ), f"Avg time {avg_time_per_request}ms exceeds benchmark {benchmark}ms"

        # Verify request counter
        assert wave_agent.request_count == num_requests

    @pytest.mark.asyncio
    async def test_concurrent_requests_medium_load(
        self, wave_agent, performance_benchmarks
    ):
        """Test performance with medium concurrent load (20 requests)."""
        num_requests = 20
        contexts = [
            {
                "user_id": f"user_{i}",
                "session_id": f"session_{i}",
                "program_type": "LONGEVITY" if i % 2 == 0 else "PRIME",
                "timestamp": datetime.now().isoformat(),
            }
            for i in range(num_requests)
        ]

        # Mix of request types
        messages = [
            (
                "Quick recovery check"
                if i % 3 == 0
                else (
                    "Analyze biometric data"
                    if i % 3 == 1
                    else "Fusion analysis request"
                )
            )
            for i in range(num_requests)
        ]

        # Mock varied response times
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "mixed_analysis",
                "data": "mock_data",
            }
        )

        start_time = time.time()
        tasks = [
            wave_agent._run_async_impl(message, context)
            for message, context in zip(messages, contexts)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_request = (total_time / num_requests) * 1000

        # Verify all requests succeeded
        assert len(results) == num_requests
        success_count = sum(1 for result in results if result["success"])
        assert success_count == num_requests

        # Verify performance under medium load (allow 2x overhead)
        benchmark = performance_benchmarks["response_times"]["simple_query"] * 1000 * 2
        assert (
            avg_time_per_request < benchmark
        ), f"Medium load avg time {avg_time_per_request}ms exceeds {benchmark}ms"

    @pytest.mark.asyncio
    async def test_concurrent_requests_high_load(
        self, wave_agent, performance_benchmarks
    ):
        """Test performance with high concurrent load (50 requests)."""
        num_requests = 50

        # Create diverse request contexts
        contexts = []
        for i in range(num_requests):
            contexts.append(
                {
                    "user_id": f"user_{i}",
                    "session_id": f"session_{i}",
                    "program_type": "PRIME" if i % 2 == 0 else "LONGEVITY",
                    "timestamp": datetime.now().isoformat(),
                    "biometric_data": {"hrv": 40 + (i % 20)} if i % 5 == 0 else None,
                }
            )

        # Varied message types
        message_templates = [
            "Quick health check",
            "Analyze my recovery",
            "Biometric analysis",
            "Fusion insights",
            "Injury risk assessment",
        ]
        messages = [
            message_templates[i % len(message_templates)] for i in range(num_requests)
        ]

        # Mock responses with slight variations
        async def mock_process_message(message, context):
            # Simulate slight processing delay
            await asyncio.sleep(0.001)  # 1ms
            return {
                "success": True,
                "skill": "load_test_skill",
                "user_id": context["user_id"],
                "response_data": "processed",
            }

        wave_agent.skills_manager.process_message = mock_process_message

        start_time = time.time()
        tasks = [
            wave_agent._run_async_impl(message, context)
            for message, context in zip(messages, contexts)
        ]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_request = (total_time / num_requests) * 1000

        # Verify all requests succeeded
        assert len(results) == num_requests
        success_count = sum(1 for result in results if result["success"])
        success_rate = success_count / num_requests

        # Allow up to 5% failure rate under high load
        assert (
            success_rate >= 0.95
        ), f"Success rate {success_rate:.2%} below 95% threshold"

        # Verify performance under high load (allow 3x overhead)
        benchmark = performance_benchmarks["response_times"]["simple_query"] * 1000 * 3
        assert (
            avg_time_per_request < benchmark
        ), f"High load avg time {avg_time_per_request}ms exceeds {benchmark}ms"

        # Verify no excessive request count (due to retries)
        assert wave_agent.request_count <= num_requests * 1.1  # Allow 10% overhead


class TestMemoryPerformance:
    """Test memory usage performance."""

    def test_agent_initialization_memory(
        self, mock_dependencies, mock_config, performance_benchmarks
    ):
        """Test memory usage during agent initialization."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Initialize agent
        agent = WavePerformanceAnalyticsAgent(mock_dependencies, mock_config)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Verify memory usage within benchmark
        benchmark = performance_benchmarks["memory_usage"]["agent_initialization"]
        assert (
            memory_increase < benchmark
        ), f"Memory increase {memory_increase}MB exceeds benchmark {benchmark}MB"

        # Cleanup
        del agent

    @pytest.mark.asyncio
    async def test_processing_memory_usage(
        self, wave_agent, sample_context, performance_benchmarks
    ):
        """Test memory usage during message processing."""
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Mock skills manager
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "memory_test",
                "large_data": "x" * 1000,  # 1KB of data
            }
        )

        # Process multiple requests to test memory accumulation
        for i in range(10):
            context = {**sample_context, "session_id": f"memory_test_{i}"}
            await wave_agent._run_async_impl(f"Test message {i}", context)

        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - baseline_memory

        # Verify memory usage within benchmark
        benchmark = performance_benchmarks["memory_usage"]["processing_peak"]
        assert (
            memory_increase < benchmark
        ), f"Memory increase {memory_increase}MB exceeds benchmark {benchmark}MB"

    @pytest.mark.asyncio
    async def test_memory_cleanup_after_processing(self, wave_agent, sample_context):
        """Test memory cleanup after processing."""
        import psutil
        import os
        import gc

        process = psutil.Process(os.getpid())

        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Mock skills manager with large response
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "cleanup_test",
                "large_data": ["large_item"] * 10000,  # Substantial data
            }
        )

        # Process requests
        for i in range(5):
            context = {**sample_context, "session_id": f"cleanup_test_{i}"}
            result = await wave_agent._run_async_impl(f"Cleanup test {i}", context)
            del result  # Explicit cleanup

        # Force garbage collection
        gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory

        # Memory should not increase significantly after cleanup
        assert (
            memory_increase < 20
        ), f"Memory not cleaned up properly: {memory_increase}MB increase"


class TestThroughputPerformance:
    """Test throughput performance metrics."""

    @pytest.mark.asyncio
    async def test_requests_per_second(self, wave_agent, performance_benchmarks):
        """Test requests per second throughput."""
        num_requests = 30
        test_duration = 3.0  # seconds

        # Create request contexts
        contexts = [
            {
                "user_id": f"throughput_user_{i}",
                "session_id": f"throughput_session_{i}",
                "program_type": "PRIME",
                "timestamp": datetime.now().isoformat(),
            }
            for i in range(num_requests)
        ]

        messages = [f"Throughput test request {i}" for i in range(num_requests)]

        # Mock fast responses
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "throughput_test",
                "processed": True,
            }
        )

        # Execute requests over time period
        start_time = time.time()
        tasks = []

        for i in range(num_requests):
            if i > 0:
                # Distribute requests over test duration
                await asyncio.sleep(test_duration / num_requests)

            task = asyncio.create_task(
                wave_agent._run_async_impl(messages[i], contexts[i])
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        actual_duration = end_time - start_time
        requests_per_second = len(results) / actual_duration

        # Verify throughput meets benchmark
        benchmark = performance_benchmarks["throughput"]["requests_per_second"]
        assert (
            requests_per_second >= benchmark * 0.8
        ), f"Throughput {requests_per_second:.1f} RPS below benchmark {benchmark} RPS"

        # Verify all requests succeeded
        success_count = sum(1 for result in results if result["success"])
        assert success_count == num_requests

    @pytest.mark.asyncio
    async def test_concurrent_user_simulation(self, wave_agent, performance_benchmarks):
        """Test performance with simulated concurrent users."""
        num_users = 10
        requests_per_user = 5

        async def simulate_user(user_id: int) -> List[Dict[str, Any]]:
            """Simulate a single user's requests."""
            user_results = []

            for request_num in range(requests_per_user):
                context = {
                    "user_id": f"sim_user_{user_id}",
                    "session_id": f"sim_session_{user_id}_{request_num}",
                    "program_type": "PRIME" if user_id % 2 == 0 else "LONGEVITY",
                    "timestamp": datetime.now().isoformat(),
                }

                message = f"User {user_id} request {request_num}"

                try:
                    result = await wave_agent._run_async_impl(message, context)
                    user_results.append(result)

                    # Simulate think time between requests
                    await asyncio.sleep(0.1)

                except Exception as e:
                    user_results.append(
                        {
                            "success": False,
                            "error": str(e),
                            "user_id": user_id,
                            "request_num": request_num,
                        }
                    )

            return user_results

        # Mock skills manager
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "user_simulation",
                "response": "simulated_response",
            }
        )

        # Execute concurrent user simulation
        start_time = time.time()
        user_tasks = [simulate_user(user_id) for user_id in range(num_users)]
        all_user_results = await asyncio.gather(*user_tasks)
        end_time = time.time()

        # Flatten results
        all_results = []
        for user_results in all_user_results:
            all_results.extend(user_results)

        total_time = end_time - start_time
        total_requests = len(all_results)
        requests_per_second = total_requests / total_time

        # Verify performance
        success_count = sum(1 for result in all_results if result.get("success", False))
        success_rate = success_count / total_requests

        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} below 95%"

        # Verify concurrent user benchmark (reduced expectation)
        min_rps = performance_benchmarks["throughput"]["requests_per_second"] * 0.5
        assert (
            requests_per_second >= min_rps
        ), f"Concurrent throughput {requests_per_second:.1f} RPS too low"


class TestScalabilityPerformance:
    """Test scalability performance characteristics."""

    @pytest.mark.asyncio
    async def test_linear_scalability(self, wave_agent):
        """Test that response time scales linearly with request complexity."""
        # Test different complexity levels
        complexity_levels = [
            ("simple", "Quick status check"),
            ("medium", "Analyze my biometric data with trends"),
            (
                "complex",
                "Comprehensive fusion analysis with predictions and recommendations",
            ),
        ]

        response_times = {}

        for complexity, message in complexity_levels:
            context = {
                "user_id": "scalability_test",
                "session_id": f"scalability_{complexity}",
                "program_type": "PRIME",
                "timestamp": datetime.now().isoformat(),
            }

            # Mock responses with simulated complexity
            if complexity == "simple":
                mock_response = {"success": True, "skill": "simple", "data": "quick"}
                processing_delay = 0.001  # 1ms
            elif complexity == "medium":
                mock_response = {
                    "success": True,
                    "skill": "medium",
                    "analysis": ["item1", "item2"],
                }
                processing_delay = 0.01  # 10ms
            else:  # complex
                mock_response = {
                    "success": True,
                    "skill": "complex",
                    "fusion_analysis": {"detailed": "analysis"},
                    "predictions": {"risk": 0.15},
                    "recommendations": ["rec1", "rec2", "rec3"],
                }
                processing_delay = 0.05  # 50ms

            async def mock_with_delay(msg, ctx):
                await asyncio.sleep(processing_delay)
                return mock_response

            wave_agent.skills_manager.process_message = mock_with_delay

            # Measure response time
            start_time = time.time()
            result = await wave_agent._run_async_impl(message, context)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # ms
            response_times[complexity] = response_time

            assert result["success"] is True

        # Verify scalability characteristics
        assert response_times["simple"] < response_times["medium"]
        assert response_times["medium"] < response_times["complex"]

        # Response time should not increase exponentially
        ratio_medium_simple = response_times["medium"] / response_times["simple"]
        ratio_complex_medium = response_times["complex"] / response_times["medium"]

        # Allow up to 10x increase per complexity level
        assert (
            ratio_medium_simple < 10
        ), f"Medium/Simple ratio {ratio_medium_simple:.1f} too high"
        assert (
            ratio_complex_medium < 10
        ), f"Complex/Medium ratio {ratio_complex_medium:.1f} too high"

    @pytest.mark.asyncio
    async def test_degraded_performance_handling(self, wave_agent):
        """Test performance under degraded conditions."""

        # Simulate degraded AI service
        async def slow_ai_response(message, context):
            await asyncio.sleep(0.1)  # 100ms delay
            return {
                "success": True,
                "skill": "degraded_ai",
                "analysis": "slow_response",
                "performance_note": "ai_service_slow",
            }

        wave_agent.skills_manager.process_message = slow_ai_response

        context = {
            "user_id": "degraded_test",
            "session_id": "degraded_session",
            "program_type": "PRIME",
            "timestamp": datetime.now().isoformat(),
        }

        message = "Test under degraded conditions"

        start_time = time.time()
        result = await wave_agent._run_async_impl(message, context)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000

        # Should still complete successfully, but may be slower
        assert result["success"] is True

        # Should complete within reasonable degraded time (5x normal)
        max_degraded_time = 500  # ms
        assert (
            response_time < max_degraded_time
        ), f"Degraded response time {response_time}ms too slow"

    @pytest.mark.asyncio
    async def test_resource_limit_handling(self, wave_agent):
        """Test handling when approaching resource limits."""
        # Simulate high resource usage
        high_memory_context = {
            "user_id": "resource_test",
            "session_id": "resource_session",
            "program_type": "PRIME",
            "timestamp": datetime.now().isoformat(),
            "large_biometric_data": {
                "historical_data": ["data_point"] * 10000,  # Large dataset
                "detailed_metrics": {f"metric_{i}": i for i in range(1000)},
            },
        }

        message = "Process large dataset"

        # Mock response that handles large data
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "large_data_processing",
                "processed_count": 10000,
                "summary": "large_dataset_processed",
            }
        )

        start_time = time.time()
        result = await wave_agent._run_async_impl(message, high_memory_context)
        end_time = time.time()

        response_time = (end_time - start_time) * 1000

        # Should handle large data gracefully
        assert result["success"] is True

        # Should complete within extended time limit
        max_large_data_time = 2000  # ms
        assert (
            response_time < max_large_data_time
        ), f"Large data processing time {response_time}ms too slow"


class TestHealthCheckPerformance:
    """Test health check performance."""

    @pytest.mark.asyncio
    async def test_health_check_response_time(self, wave_agent, performance_benchmarks):
        """Test health check response time."""
        start_time = time.time()
        health_status = await wave_agent.get_health_status()
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # ms

        # Verify health check is fast
        benchmark = performance_benchmarks["response_times"]["health_check"] * 1000
        assert (
            response_time < benchmark
        ), f"Health check time {response_time}ms exceeds benchmark {benchmark}ms"

        # Verify health data structure
        assert "agent_id" in health_status
        assert "status" in health_status
        assert "health_score" in health_status
        assert isinstance(health_status["health_score"], (int, float))

    def test_capabilities_response_time(self, wave_agent, performance_benchmarks):
        """Test capabilities query response time."""
        start_time = time.time()
        capabilities = wave_agent.get_capabilities()
        end_time = time.time()

        response_time = (end_time - start_time) * 1000  # ms

        # Capabilities should be instant
        max_capabilities_time = 10  # ms
        assert (
            response_time < max_capabilities_time
        ), f"Capabilities query time {response_time}ms too slow"

        # Verify capabilities structure
        assert "agent_type" in capabilities
        assert "skills" in capabilities
        assert "features" in capabilities

    @pytest.mark.asyncio
    async def test_shutdown_performance(self, mock_dependencies, mock_config):
        """Test shutdown performance."""
        # Create new agent for shutdown test
        agent = WavePerformanceAnalyticsAgent(mock_dependencies, mock_config)

        start_time = time.time()
        await agent.shutdown()
        end_time = time.time()

        shutdown_time = (end_time - start_time) * 1000  # ms

        # Shutdown should be fast
        max_shutdown_time = 100  # ms
        assert (
            shutdown_time < max_shutdown_time
        ), f"Shutdown time {shutdown_time}ms too slow"

        # Verify shutdown state
        assert agent.is_initialized is False
        assert agent.fusion_capabilities_ready is False
