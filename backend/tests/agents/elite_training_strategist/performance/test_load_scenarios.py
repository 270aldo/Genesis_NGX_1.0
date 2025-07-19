"""
Performance tests for BLAZE Elite Training Strategist.
Tests system performance under various load scenarios.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.elite_training_strategist.skills_manager import BlazeSkillsManager
from agents.elite_training_strategist.schemas import GenerateTrainingPlanInput


@pytest.mark.asyncio
class TestPerformanceBenchmarks:
    """Test performance benchmarks for BLAZE agent."""

    async def test_training_plan_generation_performance(
        self, skills_manager, sample_training_plan_input, mock_ai_responses
    ):
        """Test training plan generation performance."""
        # Mock fast AI response
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        # Measure execution time
        start_time = time.time()
        result = await skills_manager._skill_generate_training_plan(
            sample_training_plan_input
        )
        execution_time = time.time() - start_time

        # Performance assertions
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert result is not None

        # Verify metrics tracking
        metrics = skills_manager.get_skill_metrics()
        assert (
            "test_skill" not in metrics or len(metrics) == 0
        )  # No actual skill name recorded yet

    async def test_performance_analysis_speed(
        self,
        skills_manager,
        sample_athlete_profile,
        sample_performance_data,
        mock_ai_responses,
    ):
        """Test performance analysis execution speed."""
        from agents.elite_training_strategist.schemas import AnalyzePerformanceDataInput

        analysis_input = AnalyzePerformanceDataInput(
            input_text="Analyze my performance quickly",
            user_profile=sample_athlete_profile,
            performance_metrics=sample_performance_data,
            time_period="last_7_days",
            analysis_focus=["strength"],
        )

        # Mock services for speed
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["performance_analysis"]
        )
        skills_manager.data_service.get_athlete_progress.return_value = {
            "total_sessions": 5
        }

        start_time = time.time()
        result = await skills_manager._skill_analyze_performance_data(analysis_input)
        execution_time = time.time() - start_time

        # Performance assertions
        assert execution_time < 3.0  # Should complete within 3 seconds
        assert result is not None

    async def test_exercise_prescription_performance(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test exercise prescription performance."""
        from agents.elite_training_strategist.schemas import (
            PrescribeExerciseRoutinesInput,
        )

        prescription_input = PrescribeExerciseRoutinesInput(
            input_text="Quick exercise routine",
            user_profile=sample_athlete_profile,
            target_muscle_groups=["chest"],
            experience_level="intermediate",
            session_duration=45,
            training_focus="strength",
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["exercise_prescription"]
        )

        start_time = time.time()
        result = await skills_manager._skill_prescribe_exercise_routines(
            prescription_input
        )
        execution_time = time.time() - start_time

        # Performance assertions
        assert execution_time < 2.0  # Should complete within 2 seconds
        assert result is not None

    async def test_message_processing_performance(
        self, skills_manager, sample_context, mock_ai_responses
    ):
        """Test overall message processing performance."""
        # Mock AI responses
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        start_time = time.time()
        result = await skills_manager.process_message(
            "Create a training plan", sample_context
        )
        execution_time = time.time() - start_time

        # Performance assertions
        assert execution_time < 6.0  # Full pipeline within 6 seconds
        assert result["success"] is True


@pytest.mark.asyncio
class TestConcurrentLoad:
    """Test system behavior under concurrent load."""

    async def test_concurrent_training_plan_requests(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test handling multiple concurrent training plan requests."""
        # Mock AI client for concurrent calls
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        # Create multiple training plan inputs
        inputs = []
        for i in range(5):
            athlete_profile = {**sample_athlete_profile, "id": f"athlete_{i}"}
            training_input = GenerateTrainingPlanInput(
                input_text=f"Training plan {i}",
                user_profile=athlete_profile,
                training_goals=["strength"],
                fitness_level="intermediate",
                duration_weeks=12,
                sessions_per_week=4,
            )
            inputs.append(training_input)

        # Execute concurrent requests
        start_time = time.time()
        tasks = [
            skills_manager._skill_generate_training_plan(input_data)
            for input_data in inputs
        ]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Performance assertions
        assert len(results) == 5
        assert all(result is not None for result in results)
        assert total_time < 10.0  # All 5 should complete within 10 seconds

        # Verify all results are valid
        for result in results:
            assert result.training_plan is not None
            assert result.plan_id is not None

    async def test_mixed_skill_concurrent_requests(
        self,
        skills_manager,
        sample_athlete_profile,
        sample_performance_data,
        mock_ai_responses,
    ):
        """Test concurrent requests for different skills."""
        # Mock AI responses
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )
        skills_manager.data_service.get_athlete_progress.return_value = {
            "total_sessions": 10
        }

        # Create different types of requests
        contexts = [
            {"user_profile": sample_athlete_profile, "type": "training_plan"},
            {"user_profile": sample_athlete_profile, "type": "performance_analysis"},
            {"user_profile": sample_athlete_profile, "type": "exercise_prescription"},
        ]

        messages = [
            "Create a training plan",
            "Analyze my performance",
            "Suggest exercises for chest",
        ]

        # Execute concurrent mixed requests
        start_time = time.time()
        tasks = [
            skills_manager.process_message(message, context)
            for message, context in zip(messages, contexts)
        ]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Performance assertions
        assert len(results) == 3
        assert all(result["success"] is True for result in results)
        assert total_time < 8.0  # Mixed requests within 8 seconds

    async def test_high_frequency_requests(
        self, skills_manager, sample_context, mock_ai_responses
    ):
        """Test system behavior with high frequency requests."""
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["exercise_prescription"]
        )

        # Simulate rapid-fire requests
        start_time = time.time()
        tasks = []

        for i in range(10):
            task = skills_manager.process_message(f"Quick exercise {i}", sample_context)
            tasks.append(task)
            # Small delay between requests
            await asyncio.sleep(0.1)

        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Performance assertions
        assert len(results) == 10
        assert all(result["success"] is True for result in results)
        assert total_time < 15.0  # High frequency requests within 15 seconds


@pytest.mark.asyncio
class TestMemoryAndResourceUsage:
    """Test memory usage and resource optimization."""

    async def test_cache_performance_impact(
        self, skills_manager, sample_context, mock_ai_responses
    ):
        """Test impact of caching on performance."""
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        # First request (cold cache)
        start_time = time.time()
        result1 = await skills_manager.process_message("Create plan", sample_context)
        cold_time = time.time() - start_time

        # Second similar request (potentially cached)
        start_time = time.time()
        result2 = await skills_manager.process_message("Create plan", sample_context)
        warm_time = time.time() - start_time

        # Verify both succeeded
        assert result1["success"] is True
        assert result2["success"] is True

        # Note: In real implementation, warm_time might be faster due to caching
        # For now, just verify both complete within reasonable time
        assert cold_time < 10.0
        assert warm_time < 10.0

    async def test_large_data_processing(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test processing of large performance datasets."""
        from agents.elite_training_strategist.schemas import AnalyzePerformanceDataInput

        # Create large performance dataset
        large_performance_data = {
            "sessions": [
                {
                    "date": f"2024-01-{day:02d}",
                    "exercises": [
                        {
                            "name": "squat",
                            "sets": [{"weight": 100 + i, "reps": 8} for i in range(5)],
                        },
                        {
                            "name": "bench",
                            "sets": [{"weight": 80 + i, "reps": 8} for i in range(5)],
                        },
                    ],
                }
                for day in range(1, 31)  # 30 days of data
            ]
        }

        analysis_input = AnalyzePerformanceDataInput(
            input_text="Analyze my complete training history",
            user_profile=sample_athlete_profile,
            performance_metrics=large_performance_data,
            time_period="last_30_days",
            analysis_focus=["strength", "volume", "frequency"],
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["performance_analysis"]
        )
        skills_manager.data_service.get_athlete_progress.return_value = {
            "total_sessions": 30
        }

        start_time = time.time()
        result = await skills_manager._skill_analyze_performance_data(analysis_input)
        execution_time = time.time() - start_time

        # Performance assertions for large data
        assert execution_time < 10.0  # Even large datasets within 10 seconds
        assert result is not None

    async def test_skill_metrics_overhead(
        self, skills_manager, sample_context, mock_ai_responses
    ):
        """Test overhead of skill metrics tracking."""
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        # Execute multiple requests to build metrics
        for i in range(20):
            await skills_manager.process_message(f"Request {i}", sample_context)

        # Measure metrics retrieval performance
        start_time = time.time()
        metrics = skills_manager.get_skill_metrics()
        metrics_time = time.time() - start_time

        # Metrics retrieval should be very fast
        assert metrics_time < 0.1  # Less than 100ms
        assert isinstance(metrics, dict)


@pytest.mark.asyncio
class TestScalabilityLimits:
    """Test system scalability and limits."""

    async def test_maximum_concurrent_requests(
        self, skills_manager, sample_context, mock_ai_responses
    ):
        """Test system behavior at maximum concurrent requests."""
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["exercise_prescription"]
        )

        # Test with high concurrency
        concurrent_requests = 20

        start_time = time.time()
        tasks = [
            skills_manager.process_message(f"Request {i}", sample_context)
            for i in range(concurrent_requests)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time

        # Analyze results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]

        # Performance assertions
        assert (
            len(successful_results) >= concurrent_requests * 0.8
        )  # At least 80% success
        assert total_time < 30.0  # Complete within reasonable time

        # Log performance info
        success_rate = len(successful_results) / concurrent_requests
        avg_time_per_request = total_time / concurrent_requests

        print(f"Concurrent requests: {concurrent_requests}")
        print(f"Success rate: {success_rate:.2%}")
        print(f"Average time per request: {avg_time_per_request:.2f}s")
        print(f"Total time: {total_time:.2f}s")

    async def test_extended_session_performance(
        self, skills_manager, sample_context, mock_ai_responses
    ):
        """Test performance during extended usage session."""
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        # Simulate extended session with various requests
        session_duration = 100  # Number of requests
        execution_times = []

        for i in range(session_duration):
            start_time = time.time()
            result = await skills_manager.process_message(
                f"Session request {i}", sample_context
            )
            execution_time = time.time() - start_time
            execution_times.append(execution_time)

            assert result["success"] is True

            # Small delay between requests
            await asyncio.sleep(0.05)

        # Analyze performance degradation
        early_avg = sum(execution_times[:20]) / 20
        late_avg = sum(execution_times[-20:]) / 20

        # Performance should not degrade significantly
        performance_degradation = (late_avg - early_avg) / early_avg

        print(f"Early session avg time: {early_avg:.3f}s")
        print(f"Late session avg time: {late_avg:.3f}s")
        print(f"Performance degradation: {performance_degradation:.2%}")

        # Allow for some degradation but not excessive
        assert performance_degradation < 0.5  # Less than 50% degradation
        assert late_avg < 10.0  # Still reasonable response times

    async def test_error_rate_under_load(
        self, skills_manager, sample_context, mock_ai_responses
    ):
        """Test error rates under various load conditions."""
        # Mix of successful and failing responses
        call_count = 0

        def mock_response(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 10 == 0:  # Fail every 10th request
                raise Exception("Simulated service error")
            return mock_ai_responses["training_plan"]

        skills_manager.dependencies.vertex_ai_client.generate_response.side_effect = (
            mock_response
        )

        # Execute load test
        total_requests = 50
        results = []

        for i in range(total_requests):
            try:
                result = await skills_manager.process_message(
                    f"Load test {i}", sample_context
                )
                results.append(
                    {"success": result.get("success", False), "error": False}
                )
            except Exception as e:
                results.append({"success": False, "error": True})

        # Analyze error rates
        successful_requests = sum(1 for r in results if r["success"])
        error_rate = 1 - (successful_requests / total_requests)

        print(f"Total requests: {total_requests}")
        print(f"Successful requests: {successful_requests}")
        print(f"Error rate: {error_rate:.2%}")

        # Error rate should match expected failure rate (10%)
        assert 0.08 <= error_rate <= 0.12  # Around 10% with some tolerance
