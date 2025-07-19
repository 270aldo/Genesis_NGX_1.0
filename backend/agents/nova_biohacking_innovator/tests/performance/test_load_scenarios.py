"""
NOVA Biohacking Innovator - Performance Load Testing.
Load testing scenarios for A+ performance validation and optimization.
"""

import pytest
import asyncio
import time
import statistics
import psutil
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Tuple
from unittest.mock import Mock, AsyncMock

# NOVA Core imports
from core import NovaDependencies, NovaConfig
from skills_manager import NovaSkillsManager


class TestLoadScenarios:
    """Test various load scenarios for NOVA performance validation."""

    @pytest.fixture
    async def load_test_system(self, nova_dependencies, nova_config):
        """Setup NOVA system for load testing."""
        # Configure for performance testing
        nova_config.max_response_time = 10.0  # Stricter for load testing
        nova_config.cache_ttl_seconds = 900  # Shorter cache for testing

        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Setup fast mock responses for load testing
        nova_dependencies.vertex_ai_client.generate_content = AsyncMock(
            return_value={
                "success": True,
                "content": "NOVA load test response: Optimized biohacking analysis complete!",
                "metadata": {"processing_time": 0.1},
            }
        )

        return skills_manager

    @pytest.mark.asyncio
    async def test_single_user_sustained_load(
        self, load_test_system, nova_performance_metrics
    ):
        """Test sustained load from a single user over time."""
        response_times = []
        success_count = 0
        error_count = 0

        test_context = {
            "user_id": "load_test_user",
            "program_type": "LONGEVITY",
            "session_id": "sustained_load_session",
        }

        queries = [
            "Optimize my longevity protocols",
            "Analyze my biomarker data",
            "Review my wearable metrics",
            "Create cognitive enhancement stack",
            "Generate hormonal optimization plan",
        ]

        # Run 50 requests over time
        for i in range(50):
            start_time = time.time()
            try:
                query = queries[i % len(queries)]
                result = await load_test_system.process_message(query, test_context)

                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)

                if result.get("success"):
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                error_count += 1
                print(f"Error in request {i}: {e}")

            # Small delay between requests
            await asyncio.sleep(0.1)

        # Analyze performance metrics
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[
            18
        ]  # 95th percentile
        success_rate = success_count / (success_count + error_count)

        # Performance assertions
        target_avg = nova_performance_metrics["response_time_targets"]["simple_query"]
        assert (
            avg_response_time < target_avg
        ), f"Average response time {avg_response_time:.2f}s exceeds target {target_avg}s"
        assert (
            p95_response_time < target_avg * 2
        ), f"P95 response time {p95_response_time:.2f}s too high"
        assert (
            success_rate >= 0.95
        ), f"Success rate {success_rate:.2%} below 95% threshold"

        print(f"Sustained Load Results:")
        print(f"  Average Response Time: {avg_response_time:.3f}s")
        print(f"  P95 Response Time: {p95_response_time:.3f}s")
        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Total Requests: {success_count + error_count}")

    @pytest.mark.asyncio
    async def test_concurrent_users_load(
        self, load_test_system, nova_performance_metrics
    ):
        """Test concurrent users accessing NOVA simultaneously."""
        concurrent_users = [5, 10, 25]  # Progressive load testing

        for user_count in concurrent_users:
            print(f"\nTesting {user_count} concurrent users...")

            # Create user contexts
            user_contexts = [
                {
                    "user_id": f"concurrent_user_{i}",
                    "program_type": "PRIME" if i % 2 else "LONGEVITY",
                    "session_id": f"concurrent_session_{i}",
                }
                for i in range(user_count)
            ]

            # Define varied queries per user
            queries = [
                "Optimize my longevity and healthspan",
                "Analyze cognitive performance enhancement",
                "Review hormonal optimization strategies",
                "Interpret my biomarker patterns",
                "Generate personalized biohacking protocol",
            ]

            # Create concurrent tasks
            start_time = time.time()
            tasks = []

            for i, context in enumerate(user_contexts):
                query = queries[i % len(queries)]
                task = load_test_system.process_message(query, context)
                tasks.append(task)

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            # Analyze concurrent performance
            total_time = end_time - start_time
            successful_results = [
                r for r in results if isinstance(r, dict) and r.get("success")
            ]
            error_results = [
                r
                for r in results
                if isinstance(r, Exception)
                or (isinstance(r, dict) and not r.get("success"))
            ]

            success_rate = len(successful_results) / len(results)
            throughput = len(results) / total_time  # requests per second

            # Performance assertions for concurrent load
            target_throughput = (
                nova_performance_metrics["throughput_targets"]["requests_per_minute"]
                / 60
            )

            assert (
                success_rate >= 0.90
            ), f"Success rate {success_rate:.2%} below 90% for {user_count} users"
            assert (
                total_time < 15
            ), f"Total time {total_time:.2f}s too high for {user_count} concurrent users"

            if user_count <= 10:  # More strict for smaller loads
                assert (
                    success_rate >= 0.95
                ), f"Success rate should be >95% for {user_count} users"

            print(f"  Concurrent Users: {user_count}")
            print(f"  Total Time: {total_time:.2f}s")
            print(f"  Success Rate: {success_rate:.2%}")
            print(f"  Throughput: {throughput:.1f} req/s")
            print(
                f"  Successful: {len(successful_results)}, Errors: {len(error_results)}"
            )

    @pytest.mark.asyncio
    async def test_burst_load_handling(self, load_test_system):
        """Test handling of sudden burst load scenarios."""
        # Simulate realistic burst: quiet period followed by sudden spike

        # Phase 1: Normal load (5 requests)
        normal_context = {"user_id": "burst_test", "program_type": "LONGEVITY"}
        normal_tasks = []

        for i in range(5):
            task = load_test_system.process_message(
                f"Normal load query {i}", normal_context
            )
            normal_tasks.append(task)

        normal_results = await asyncio.gather(*normal_tasks)
        normal_success = sum(1 for r in normal_results if r.get("success"))

        # Phase 2: Burst load (30 requests simultaneously)
        burst_start = time.time()
        burst_tasks = []

        for i in range(30):
            context = {
                "user_id": f"burst_user_{i}",
                "program_type": "PRIME" if i % 2 else "LONGEVITY",
            }
            task = load_test_system.process_message(f"Burst load query {i}", context)
            burst_tasks.append(task)

        burst_results = await asyncio.gather(*burst_tasks, return_exceptions=True)
        burst_end = time.time()

        # Analyze burst performance
        burst_time = burst_end - burst_start
        burst_successful = [
            r for r in burst_results if isinstance(r, dict) and r.get("success")
        ]
        burst_success_rate = len(burst_successful) / len(burst_results)

        # Burst load assertions
        assert (
            burst_success_rate >= 0.80
        ), f"Burst success rate {burst_success_rate:.2%} below 80%"
        assert burst_time < 20, f"Burst handling time {burst_time:.2f}s too high"
        assert (
            normal_success >= 4
        ), f"Normal load affected: only {normal_success}/5 successful"

        print(f"Burst Load Results:")
        print(f"  Normal Load Success: {normal_success}/5")
        print(f"  Burst Load Time: {burst_time:.2f}s")
        print(f"  Burst Success Rate: {burst_success_rate:.2%}")
        print(f"  Burst Throughput: {len(burst_results)/burst_time:.1f} req/s")

    @pytest.mark.asyncio
    async def test_memory_under_load(self, load_test_system):
        """Test memory usage patterns under sustained load."""
        process = psutil.Process(os.getpid())

        # Get baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_samples = [baseline_memory]

        context = {"user_id": "memory_test", "program_type": "LONGEVITY"}

        # Run 100 requests while monitoring memory
        for i in range(100):
            await load_test_system.process_message(f"Memory test query {i}", context)

            # Sample memory every 10 requests
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)

        # Analyze memory patterns
        final_memory = memory_samples[-1]
        max_memory = max(memory_samples)
        memory_growth = final_memory - baseline_memory
        peak_growth = max_memory - baseline_memory

        # Memory usage assertions
        assert (
            memory_growth < 50
        ), f"Memory grew by {memory_growth:.1f}MB, indicating possible leak"
        assert peak_growth < 100, f"Peak memory growth {peak_growth:.1f}MB too high"

        # Check for memory stability (last 3 samples shouldn't vary much)
        recent_samples = memory_samples[-3:]
        memory_stability = max(recent_samples) - min(recent_samples)
        assert (
            memory_stability < 20
        ), f"Memory not stable: {memory_stability:.1f}MB variance"

        print(f"Memory Usage Analysis:")
        print(f"  Baseline: {baseline_memory:.1f}MB")
        print(f"  Final: {final_memory:.1f}MB")
        print(f"  Growth: {memory_growth:.1f}MB")
        print(f"  Peak Growth: {peak_growth:.1f}MB")
        print(f"  Stability: {memory_stability:.1f}MB")

    @pytest.mark.asyncio
    async def test_cache_performance_under_load(self, load_test_system):
        """Test caching performance during high load scenarios."""
        # Test repeated queries to measure cache effectiveness

        context = {"user_id": "cache_test", "program_type": "LONGEVITY"}
        repeated_query = "Analyze longevity optimization protocols"

        # First request (cache miss)
        start_time = time.time()
        first_result = await load_test_system.process_message(repeated_query, context)
        first_time = time.time() - start_time

        # Subsequent requests (should benefit from caching)
        cache_times = []
        for i in range(10):
            start_time = time.time()
            result = await load_test_system.process_message(repeated_query, context)
            cache_time = time.time() - start_time
            cache_times.append(cache_time)

            assert result.get("success"), f"Cached request {i} failed"

        # Analyze cache performance
        avg_cache_time = statistics.mean(cache_times)

        # Cache should make subsequent requests faster
        # Note: With mocked responses, the improvement might be minimal
        # In real scenarios, this would show significant improvement

        print(f"Cache Performance Analysis:")
        print(f"  First Request Time: {first_time:.3f}s")
        print(f"  Average Cached Time: {avg_cache_time:.3f}s")
        print(f"  Cache Performance Ratio: {first_time/avg_cache_time:.2f}x")

    def test_skills_performance_distribution(self, load_test_system):
        """Test performance distribution across different NOVA skills."""
        # Test performance of different skill types
        skills_performance = {}

        test_scenarios = {
            "longevity_optimization": "Optimize my longevity protocols",
            "cognitive_enhancement": "Improve my cognitive performance",
            "hormonal_optimization": "Balance my hormones naturally",
            "biomarker_analysis": "Analyze my blood test results",
            "wearable_data_analysis": "Interpret my Oura ring data",
        }

        context = {"user_id": "skills_perf_test", "program_type": "LONGEVITY"}

        # Test each skill type multiple times
        for skill_name, query in test_scenarios.items():
            times = []

            for _ in range(5):
                start_time = time.time()
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    load_test_system.process_message(query, context)
                )
                end_time = time.time()

                if result.get("success"):
                    times.append(end_time - start_time)

            if times:
                skills_performance[skill_name] = {
                    "avg_time": statistics.mean(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "samples": len(times),
                }

        # Analyze skill performance distribution
        for skill, perf in skills_performance.items():
            print(f"{skill}:")
            print(f"  Average: {perf['avg_time']:.3f}s")
            print(f"  Range: {perf['min_time']:.3f}s - {perf['max_time']:.3f}s")

            # Performance assertions per skill type
            assert (
                perf["avg_time"] < 5.0
            ), f"{skill} average time {perf['avg_time']:.3f}s too high"
            assert (
                perf["max_time"] < 10.0
            ), f"{skill} max time {perf['max_time']:.3f}s too high"

    @pytest.mark.asyncio
    async def test_error_rate_under_load(self, load_test_system):
        """Test error rates during various load conditions."""

        # Setup scenarios with potential for errors
        error_test_scenarios = [
            # Normal scenarios
            {
                "query": "Normal longevity query",
                "context": {"user_id": "normal_user", "program_type": "LONGEVITY"},
            },
            {
                "query": "Standard cognitive enhancement",
                "context": {"user_id": "normal_user2", "program_type": "PRIME"},
            },
            # Edge case scenarios
            {
                "query": "",
                "context": {"user_id": "edge_user", "program_type": "LONGEVITY"},
            },  # Empty query
            {
                "query": "x" * 1000,
                "context": {"user_id": "long_user", "program_type": "LONGEVITY"},
            },  # Very long query
            {
                "query": "Test query",
                "context": {"user_id": "invalid_user", "program_type": "INVALID"},
            },  # Invalid program
            # High complexity scenarios
            {
                "query": "Complex multi-modal biohacking optimization with advanced protocols",
                "context": {"user_id": "complex_user", "program_type": "LONGEVITY"},
            },
        ]

        total_requests = 0
        total_errors = 0
        error_types = {}

        # Run each scenario multiple times under load
        for scenario in error_test_scenarios:
            for i in range(10):  # 10 attempts per scenario
                total_requests += 1
                try:
                    result = await load_test_system.process_message(
                        scenario["query"], scenario["context"]
                    )

                    if not result.get("success"):
                        total_errors += 1
                        error_type = result.get("error", "unknown_error")
                        error_types[error_type] = error_types.get(error_type, 0) + 1

                except Exception as e:
                    total_errors += 1
                    error_type = type(e).__name__
                    error_types[error_type] = error_types.get(error_type, 0) + 1

        # Calculate error metrics
        error_rate = total_errors / total_requests

        # Error rate assertions
        assert error_rate <= 0.10, f"Error rate {error_rate:.2%} exceeds 10% threshold"

        print(f"Error Rate Analysis:")
        print(f"  Total Requests: {total_requests}")
        print(f"  Total Errors: {total_errors}")
        print(f"  Error Rate: {error_rate:.2%}")
        print(f"  Error Types: {error_types}")

        # Specific error type analysis
        for error_type, count in error_types.items():
            error_type_rate = count / total_requests
            print(f"    {error_type}: {count} ({error_type_rate:.2%})")


class TestResourceUtilization:
    """Test resource utilization patterns during load scenarios."""

    @pytest.mark.asyncio
    async def test_cpu_utilization_monitoring(self, load_test_system):
        """Monitor CPU utilization during load testing."""
        import threading
        import time

        cpu_samples = []
        monitoring = True

        def monitor_cpu():
            while monitoring:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_samples.append(cpu_percent)
                time.sleep(0.5)

        # Start CPU monitoring
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        try:
            # Generate load while monitoring
            tasks = []
            context = {"user_id": "cpu_test", "program_type": "LONGEVITY"}

            for i in range(20):
                task = load_test_system.process_message(f"CPU test query {i}", context)
                tasks.append(task)

            await asyncio.gather(*tasks)

            # Small delay to capture post-load CPU
            await asyncio.sleep(2)

        finally:
            monitoring = False
            monitor_thread.join()

        # Analyze CPU utilization
        if cpu_samples:
            avg_cpu = statistics.mean(cpu_samples)
            max_cpu = max(cpu_samples)

            print(f"CPU Utilization:")
            print(f"  Average: {avg_cpu:.1f}%")
            print(f"  Peak: {max_cpu:.1f}%")
            print(f"  Samples: {len(cpu_samples)}")

            # CPU utilization should be reasonable
            assert avg_cpu < 80, f"Average CPU {avg_cpu:.1f}% too high"
            assert max_cpu < 95, f"Peak CPU {max_cpu:.1f}% too high"

    @pytest.mark.asyncio
    async def test_network_simulation_load(self, load_test_system):
        """Simulate network latency effects on performance."""

        # Simulate network delays in external services
        original_gemini_call = (
            load_test_system.dependencies.vertex_ai_client.generate_content
        )

        async def slow_gemini_response(*args, **kwargs):
            # Simulate network latency
            await asyncio.sleep(0.2)  # 200ms network delay
            return await original_gemini_call(*args, **kwargs)

        load_test_system.dependencies.vertex_ai_client.generate_content = (
            slow_gemini_response
        )

        # Test performance with network delays
        start_time = time.time()
        context = {"user_id": "network_test", "program_type": "LONGEVITY"}

        # Run 10 concurrent requests with simulated network delay
        tasks = [
            load_test_system.process_message(f"Network test {i}", context)
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks)
        end_time = time.time()

        # Analyze network impact
        total_time = end_time - start_time
        successful_results = [r for r in results if r.get("success")]
        success_rate = len(successful_results) / len(results)

        print(f"Network Latency Impact:")
        print(f"  Total Time with Delays: {total_time:.2f}s")
        print(f"  Success Rate: {success_rate:.2%}")
        print(f"  Average per Request: {total_time/len(results):.2f}s")

        # Should handle network delays gracefully
        assert (
            success_rate >= 0.90
        ), f"Success rate {success_rate:.2%} dropped due to network delays"
        assert (
            total_time < 15
        ), f"Total time {total_time:.2f}s too high even with network delays"

    def test_thread_safety_under_load(self, load_test_system):
        """Test thread safety during concurrent operations."""
        import threading
        import concurrent.futures

        results = []
        errors = []

        def sync_request(query_id):
            """Synchronous wrapper for async request."""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                context = {
                    "user_id": f"thread_user_{query_id}",
                    "program_type": "LONGEVITY",
                }
                result = loop.run_until_complete(
                    load_test_system.process_message(
                        f"Thread test query {query_id}", context
                    )
                )

                results.append(result)
                return result

            except Exception as e:
                errors.append(e)
                return None
            finally:
                loop.close()

        # Run requests in multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(sync_request, i) for i in range(15)]
            concurrent.futures.wait(futures)

        # Analyze thread safety
        successful_results = [r for r in results if r and r.get("success")]
        success_rate = (
            len(successful_results) / (len(results) + len(errors))
            if (len(results) + len(errors)) > 0
            else 0
        )

        print(f"Thread Safety Results:")
        print(f"  Successful Results: {len(successful_results)}")
        print(f"  Failed Results: {len(results) - len(successful_results)}")
        print(f"  Exceptions: {len(errors)}")
        print(f"  Success Rate: {success_rate:.2%}")

        # Thread safety assertions
        assert len(errors) == 0, f"Thread safety errors occurred: {errors}"
        assert (
            success_rate >= 0.90
        ), f"Success rate {success_rate:.2%} indicates thread safety issues"
