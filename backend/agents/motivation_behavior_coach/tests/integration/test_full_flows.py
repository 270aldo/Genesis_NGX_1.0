"""
Integration tests for SPARK Motivation Behavior Coach.
Tests end-to-end workflows and agent interactions.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from agents.motivation_behavior_coach.skills_manager import SparkSkillsManager
from agents.motivation_behavior_coach.core import SparkConfig, SparkDependencies
from agents.motivation_behavior_coach.services import (
    MotivationSecurityService,
    MotivationDataService,
    MotivationIntegrationService,
)


class TestCoachingWorkflows:
    """Test complete coaching workflow integrations."""

    @pytest.mark.asyncio
    async def test_complete_habit_formation_workflow(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test complete habit formation coaching workflow."""
        # Setup comprehensive AI response
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": """
            Habit Analysis: User wants to establish a daily exercise routine.
            Current Stage: Preparation - motivated but needs structure.
            Personalized Plan: 
            1. Start with 15-minute daily walks
            2. Same time each day (7 AM)
            3. Track completion with simple checkmarks
            4. Weekly progress reviews
            
            Success Factors:
            - Consistent timing
            - Low initial barrier
            - Clear tracking system
            - Positive reinforcement
            
            Potential Obstacles:
            - Weather dependency
            - Schedule conflicts
            - Motivation fluctuations
            - Perfectionism
            
            Tracking System:
            - Daily checkbox completion
            - Weekly streak counting
            - Monthly progress review
            
            Reinforcement Strategies:
            - Link to morning coffee routine
            - Celebrate weekly milestones
            - Share progress with accountability partner
            """,
        }

        # Test habit formation request
        message = "I want to start exercising every day but I'm not sure how to build this habit"
        result = await spark_skills_manager.process_message(
            message, sample_user_context
        )

        # Verify comprehensive response
        assert result["success"] is True
        assert result["skill"] == "habit_formation"
        assert "analysis" in result
        assert "recommendations" in result
        assert "next_steps" in result
        assert "tracking_suggestions" in result
        assert len(result["next_steps"]) >= 3

        # Verify data storage occurred
        data_service = spark_skills_manager.data_service
        stored_data = data_service.retrieve_behavioral_data(
            user_id=sample_user_context["user_id"],
            data_type="habit_formation_session",
            limit=1,
        )
        assert len(stored_data) == 1
        assert stored_data[0].content["session_type"] == "habit_formation"

    @pytest.mark.asyncio
    async def test_goal_setting_to_habit_formation_flow(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test workflow from goal setting to habit formation."""
        user_id = sample_user_context["user_id"]

        # Step 1: Goal Setting
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": """
            Goal Clarification: Lose 20 pounds in 6 months through sustainable lifestyle changes.
            SMART Analysis:
            - Specific: Lose 20 pounds
            - Measurable: Track weight weekly
            - Achievable: 3-4 pounds per month is realistic
            - Relevant: Health and confidence improvement
            - Time-bound: 6 months (by June 2024)
            
            Milestone Breakdown:
            - Month 1: Lose 4 pounds, establish exercise routine
            - Month 2: Lose 3 pounds, refine nutrition habits
            - Month 3: Lose 3 pounds, build consistency
            - Month 4-6: Lose 10 pounds, maintain momentum
            """,
        }

        goal_message = "I want to lose 20 pounds in the next 6 months"
        goal_result = await spark_skills_manager.process_message(
            goal_message, sample_user_context
        )

        assert goal_result["success"] is True
        assert goal_result["skill"] == "goal_setting"

        # Step 2: Follow-up with habit formation
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Habit formation plan to support weight loss goal...",
        }

        habit_message = (
            "Now help me build the daily habits I need to reach this weight loss goal"
        )
        habit_result = await spark_skills_manager.process_message(
            habit_message, sample_user_context
        )

        assert habit_result["success"] is True
        assert habit_result["skill"] == "habit_formation"

        # Verify both interactions were stored
        all_data = spark_skills_manager.data_service.retrieve_behavioral_data(user_id)
        assert len(all_data) >= 2

        session_types = [entry.content.get("session_type") for entry in all_data]
        assert "goal_setting" in session_types
        assert "habit_formation" in session_types

    @pytest.mark.asyncio
    async def test_motivation_crisis_intervention_flow(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test intervention workflow for motivation crisis."""
        user_id = sample_user_context["user_id"]

        # Simulate user having previous data showing declining motivation
        data_service = spark_skills_manager.data_service

        # Add historical motivation data showing decline
        for i, score in enumerate([8.0, 7.0, 5.0, 3.0, 2.0]):
            data_service.store_behavioral_data(
                user_id=user_id,
                data_type="motivation_assessment",
                content={"motivation_score": score, "date": f"day_{i+1}"},
            )

        # Setup AI response for motivation crisis
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": """
            Motivation Assessment: Significant decline detected (8.0 → 2.0 over 5 days).
            Root Cause Analysis: 
            - Overwhelming goals
            - Lack of recent wins
            - Possible burnout
            - External stressors
            
            Immediate Strategies:
            1. Simplify current goals to bare minimum
            2. Focus on one small daily win
            3. Reconnect with core values
            4. Seek social support
            
            Recovery Plan:
            - Week 1: Micro-goals only (5-minute actions)
            - Week 2: Gradually increase complexity
            - Week 3: Restore regular routine
            - Week 4: Set new challenging goals
            """,
        }

        crisis_message = (
            "I've completely lost motivation and feel like giving up on everything"
        )
        result = await spark_skills_manager.process_message(
            crisis_message, sample_user_context
        )

        assert result["success"] is True
        assert result["skill"] == "motivation_strategies"
        assert "guidance" in result
        assert "quick_boosters" in result
        assert "motivation_toolkit" in result

        # Verify the system recognized the crisis pattern
        motivation_analysis = data_service.analyze_behavior_patterns(
            user_id, "motivation_trends"
        )
        assert motivation_analysis["trend"] == "declining"

    @pytest.mark.asyncio
    async def test_obstacle_to_solution_workflow(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test workflow from obstacle identification to solution implementation."""
        # Step 1: Obstacle identification
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": """
            Obstacle Identification: Time constraints due to work schedule.
            Root Cause Analysis: 
            - Poor time management
            - Unrealistic expectations
            - Lack of prioritization
            
            Solution Strategies:
            1. Time-blocking for workouts
            2. Micro-workouts during breaks
            3. Weekend preparation sessions
            4. Flexible backup plans
            
            Implementation Plan:
            - Week 1: Track current time usage
            - Week 2: Implement time-blocking
            - Week 3: Add micro-workouts
            - Week 4: Evaluate and adjust
            """,
        }

        obstacle_message = "I keep missing my workouts because I don't have enough time"
        obstacle_result = await spark_skills_manager.process_message(
            obstacle_message, sample_user_context
        )

        assert obstacle_result["success"] is True
        assert obstacle_result["skill"] == "obstacle_management"
        assert "guidance" in obstacle_result
        assert "immediate_actions" in obstacle_result

        # Step 2: Follow-up behavior change support
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Behavior change plan for time management improvement...",
        }

        behavior_message = "Help me change my time management behaviors"
        behavior_result = await spark_skills_manager.process_message(
            behavior_message, sample_user_context
        )

        assert behavior_result["success"] is True
        assert behavior_result["skill"] == "behavior_change"

        # Verify obstacle was logged
        user_id = sample_user_context["user_id"]
        stored_data = spark_skills_manager.data_service.retrieve_behavioral_data(
            user_id
        )
        obstacle_sessions = [
            entry
            for entry in stored_data
            if entry.content.get("session_type") == "obstacle_management"
        ]
        assert len(obstacle_sessions) >= 1


class TestPersonalityAdaptationIntegration:
    """Test personality adaptation integration across workflows."""

    @pytest.mark.asyncio
    async def test_prime_vs_longevity_adaptation(
        self,
        spark_dependencies,
        spark_config,
        mock_gemini_client,
        mock_personality_adapter,
    ):
        """Test different responses for PRIME vs LONGEVITY programs."""
        skills_manager = SparkSkillsManager(spark_dependencies, spark_config)

        # Setup AI response
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Standard goal setting guidance and recommendations...",
        }

        # Test PRIME adaptation
        mock_personality_adapter.adapt_response.return_value = {
            "success": True,
            "adapted_message": "Strategic goal optimization for executive performance...",
            "confidence_score": 0.9,
        }

        prime_context = {
            "user_id": "prime_user",
            "program_type": "PRIME",
            "session_id": "prime_session",
        }

        prime_result = await skills_manager.process_message(
            "Help me set ambitious fitness goals", prime_context
        )

        # Test LONGEVITY adaptation
        mock_personality_adapter.adapt_response.return_value = {
            "success": True,
            "adapted_message": "Sustainable wellness goals for long-term health...",
            "confidence_score": 0.85,
        }

        longevity_context = {
            "user_id": "longevity_user",
            "program_type": "LONGEVITY",
            "session_id": "longevity_session",
        }

        longevity_result = await skills_manager.process_message(
            "Help me set sustainable fitness goals", longevity_context
        )

        # Verify different adaptations
        assert prime_result["guidance"] != longevity_result["guidance"]
        assert "strategic" in prime_result["guidance"].lower()
        assert "sustainable" in longevity_result["guidance"].lower()

        # Verify personality adaptation was applied
        assert prime_result["personality_adaptation"]["program_type"] == "PRIME"
        assert longevity_result["personality_adaptation"]["program_type"] == "LONGEVITY"

    @pytest.mark.asyncio
    async def test_adaptation_failure_fallback(
        self,
        spark_skills_manager,
        sample_user_context,
        mock_gemini_client,
        mock_personality_adapter,
    ):
        """Test fallback when personality adaptation fails."""
        # Setup AI response
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Original motivation guidance...",
        }

        # Setup personality adapter failure
        mock_personality_adapter.adapt_response.return_value = {
            "success": False,
            "error": "Adaptation service unavailable",
        }

        message = "I need motivation to keep going"
        result = await spark_skills_manager.process_message(
            message, sample_user_context
        )

        # Should still succeed with original content
        assert result["success"] is True
        assert result["guidance"] == "Original motivation guidance..."
        # Personality adaptation should not be present or marked as failed
        assert (
            "personality_adaptation" not in result
            or not result["personality_adaptation"]["applied"]
        )


class TestDataPersistenceIntegration:
    """Test data persistence across coaching sessions."""

    @pytest.mark.asyncio
    async def test_multi_session_data_continuity(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test data continuity across multiple coaching sessions."""
        user_id = sample_user_context["user_id"]

        # Session 1: Initial habit formation
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Initial habit formation plan...",
        }

        session1_result = await spark_skills_manager.process_message(
            "Help me start a meditation habit", sample_user_context
        )
        assert session1_result["success"] is True

        # Session 2: Progress check (should reference previous session)
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Progress review and adjustments...",
        }

        session2_result = await spark_skills_manager.process_message(
            "How am I doing with my meditation habit?", sample_user_context
        )
        assert session2_result["success"] is True

        # Session 3: Obstacle management
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Obstacle analysis and solutions...",
        }

        session3_result = await spark_skills_manager.process_message(
            "I'm struggling to maintain my meditation habit", sample_user_context
        )
        assert session3_result["success"] is True

        # Verify all sessions were stored and linked
        all_sessions = spark_skills_manager.data_service.retrieve_behavioral_data(
            user_id
        )
        assert len(all_sessions) >= 3

        # Verify different session types
        session_types = {entry.content.get("session_type") for entry in all_sessions}
        expected_types = {
            "habit_formation",
            "motivation_strategies",
            "obstacle_management",
        }
        assert expected_types.issubset(session_types)

    def test_behavioral_pattern_analysis_integration(self, spark_skills_manager):
        """Test behavioral pattern analysis with integrated data."""
        user_id = "pattern_test_user"
        data_service = spark_skills_manager.data_service

        # Add diverse behavioral data
        behavior_data = [
            ("motivation_assessment", {"motivation_score": 8.0}),
            ("habit_tracking", {"habit_name": "exercise", "completed": True}),
            ("goal_progress", {"goal_id": "fitness_1", "progress_percentage": 75.0}),
            ("obstacle_report", {"obstacle_type": "time_constraints"}),
            ("motivation_assessment", {"motivation_score": 6.5}),
            ("habit_tracking", {"habit_name": "exercise", "completed": False}),
            ("motivation_assessment", {"motivation_score": 7.0}),
        ]

        for data_type, content in behavior_data:
            data_service.store_behavioral_data(user_id, data_type, content)

        # Test different analysis types
        motivation_analysis = data_service.analyze_behavior_patterns(
            user_id, "motivation_trends"
        )
        habit_analysis = data_service.analyze_behavior_patterns(
            user_id, "habit_consistency"
        )
        obstacle_analysis = data_service.analyze_behavior_patterns(
            user_id, "obstacle_patterns"
        )

        # Verify analyses
        assert motivation_analysis["analysis_type"] == "motivation_trends"
        assert "average_score" in motivation_analysis

        assert habit_analysis["analysis_type"] == "habit_consistency"
        assert "habits" in habit_analysis

        assert obstacle_analysis["analysis_type"] == "obstacle_patterns"
        assert "patterns" in obstacle_analysis


class TestSecurityIntegration:
    """Test security integration across the system."""

    def test_end_to_end_data_encryption(self, spark_skills_manager):
        """Test data encryption throughout the system."""
        security_service = spark_skills_manager.security_service

        # Test data that should be encrypted
        sensitive_data = {
            "user_id": "security_test_user",
            "personal_insights": "User struggles with confidence and motivation",
            "behavioral_patterns": "Tends to abandon goals after 2-3 weeks",
            "private_notes": "Mentioned family stress affecting wellness goals",
        }

        # Encrypt the data
        encrypted = security_service.encrypt_behavioral_data(sensitive_data)
        assert isinstance(encrypted, str)
        assert str(sensitive_data) not in encrypted

        # Decrypt and verify
        decrypted = security_service.decrypt_behavioral_data(encrypted)
        assert decrypted == sensitive_data

        # Verify audit trail was created
        audit_logs = security_service.get_audit_logs()
        encryption_logs = [
            log for log in audit_logs if log["event_type"] == "data_encryption"
        ]
        assert len(encryption_logs) >= 1

    @pytest.mark.asyncio
    async def test_input_sanitization_integration(
        self, spark_skills_manager, sample_user_context
    ):
        """Test input sanitization across coaching workflows."""
        # Test with potentially malicious input
        malicious_message = (
            "<script>alert('xss')</script>Help me with habits; DROP TABLE users; --"
        )

        # Process the message
        result = await spark_skills_manager.process_message(
            malicious_message, sample_user_context
        )

        # Should still succeed but with sanitized input
        assert result["success"] is True

        # Verify input was sanitized (check stored data)
        user_id = sample_user_context["user_id"]
        stored_data = spark_skills_manager.data_service.retrieve_behavioral_data(
            user_id, limit=1
        )

        if stored_data:
            stored_request = stored_data[0].content.get("user_request", "")
            assert "<script>" not in stored_request
            assert "DROP TABLE" not in stored_request
            assert "Help me with habits" in stored_request

    def test_access_control_integration(self, spark_skills_manager):
        """Test access control throughout the system."""
        security_service = spark_skills_manager.security_service
        data_service = spark_skills_manager.data_service

        # Create data for two different users
        user1_id = "user_1_security_test"
        user2_id = "user_2_security_test"

        # Store data for both users
        data_service.store_behavioral_data(
            user1_id, "motivation_assessment", {"score": 8.0}
        )
        data_service.store_behavioral_data(
            user2_id, "motivation_assessment", {"score": 7.0}
        )

        # Test that users can only access their own data
        user1_data = data_service.retrieve_behavioral_data(user1_id)
        user2_data = data_service.retrieve_behavioral_data(user2_id)

        assert len(user1_data) == 1
        assert len(user2_data) == 1
        assert user1_data[0].user_id == user1_id
        assert user2_data[0].user_id == user2_id

        # Test access permission checking
        assert (
            security_service.check_access_permissions(
                user1_id, "read", f"user_{user1_id}_data"
            )
            is True
        )

        assert (
            security_service.check_access_permissions(
                user1_id, "read", f"user_{user2_id}_data"
            )
            is False
        )


class TestErrorRecoveryIntegration:
    """Test error recovery and fallback mechanisms."""

    @pytest.mark.asyncio
    async def test_ai_service_failure_recovery(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test recovery when AI service fails."""
        # Setup AI failure
        mock_gemini_client.generate_content.return_value = {
            "success": False,
            "error": "AI service temporarily unavailable",
        }

        message = "Help me build a habit"

        # Should raise appropriate exception
        with pytest.raises(
            Exception
        ):  # Specific exception type would depend on implementation
            await spark_skills_manager.process_message(message, sample_user_context)

        # Verify system logged the failure
        security_service = spark_skills_manager.security_service
        audit_logs = security_service.get_audit_logs()

        # Should have audit entries for the attempted operation
        assert len(audit_logs) > 0

    @pytest.mark.asyncio
    async def test_external_service_circuit_breaker(
        self, motivation_integration_service
    ):
        """Test circuit breaker behavior with external services."""
        service_name = "fitness_tracker"
        circuit_breaker = motivation_integration_service.circuit_breakers[service_name]

        # Simulate multiple failures to trip circuit breaker
        for _ in range(circuit_breaker.failure_threshold):
            circuit_breaker.record_failure()

        # Should now be in open state
        assert circuit_breaker.state == "open"

        # Attempt to use service should return fallback
        result = await motivation_integration_service.get_user_fitness_data(
            user_id="test_user", date_range=7
        )

        assert result["success"] is False
        assert "temporarily unavailable" in result["message"]
        assert result.get("fallback_applied") is True

    def test_data_corruption_handling(self, motivation_data_service):
        """Test handling of data corruption scenarios."""
        # Test with invalid data types
        with pytest.raises(ValueError):
            motivation_data_service.store_behavioral_data(
                user_id="",  # Invalid empty user_id
                data_type="test",
                content={"valid": "data"},
            )

        with pytest.raises(ValueError):
            motivation_data_service.store_behavioral_data(
                user_id="valid_user",
                data_type="",  # Invalid empty data_type
                content={"valid": "data"},
            )

        with pytest.raises(ValueError):
            motivation_data_service.store_behavioral_data(
                user_id="valid_user",
                data_type="test",
                content=None,  # Invalid None content
            )


class TestPerformanceIntegration:
    """Test performance aspects of integrated system."""

    @pytest.mark.asyncio
    async def test_concurrent_user_handling(
        self, spark_dependencies, spark_config, mock_gemini_client
    ):
        """Test system performance with multiple concurrent users."""
        # Setup fast AI responses
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Quick coaching response for performance test",
        }

        # Create multiple skills managers (simulating different user sessions)
        skills_managers = [
            SparkSkillsManager(spark_dependencies, spark_config) for _ in range(5)
        ]

        # Create concurrent requests
        async def process_user_request(manager, user_num):
            context = {
                "user_id": f"perf_test_user_{user_num}",
                "program_type": "PRIME" if user_num % 2 == 0 else "LONGEVITY",
                "session_id": f"perf_session_{user_num}",
            }

            message = f"Help me with motivation - user {user_num}"
            start_time = datetime.utcnow()

            result = await manager.process_message(message, context)

            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()

            return {
                "user_num": user_num,
                "success": result["success"],
                "response_time": response_time,
                "result": result,
            }

        # Execute concurrent requests
        tasks = [
            process_user_request(manager, i)
            for i, manager in enumerate(skills_managers)
        ]

        results = await asyncio.gather(*tasks)

        # Verify all requests succeeded
        for result in results:
            assert result["success"] is True
            assert result["response_time"] < 5.0  # Should be fast with mocks

        # Verify unique user data was stored
        user_ids = [f"perf_test_user_{i}" for i in range(5)]
        for i, manager in enumerate(skills_managers):
            user_data = manager.data_service.retrieve_behavioral_data(user_ids[i])
            assert len(user_data) >= 1

    def test_large_data_handling(self, motivation_data_service):
        """Test handling of large amounts of behavioral data."""
        user_id = "large_data_test_user"

        # Store large amount of data
        for i in range(100):
            motivation_data_service.store_behavioral_data(
                user_id=user_id,
                data_type="motivation_assessment",
                content={
                    "motivation_score": 5.0 + (i % 6),
                    "session_number": i,
                    "notes": f"Session {i} notes with some additional content",
                },
            )

        # Test retrieval with different limits
        all_data = motivation_data_service.retrieve_behavioral_data(user_id)
        limited_data = motivation_data_service.retrieve_behavioral_data(
            user_id, limit=10
        )

        assert len(all_data) == 100
        assert len(limited_data) == 10

        # Test analysis performance with large dataset
        start_time = datetime.utcnow()
        analysis = motivation_data_service.analyze_behavior_patterns(
            user_id, "motivation_trends"
        )
        end_time = datetime.utcnow()

        analysis_time = (end_time - start_time).total_seconds()
        assert analysis_time < 1.0  # Should complete within 1 second
        assert analysis["total_assessments"] == 100

    def test_cache_performance(self, motivation_data_service):
        """Test caching performance and efficiency."""
        user_id = "cache_test_user"

        # Store some data
        motivation_data_service.store_behavioral_data(
            user_id, "test_data", {"value": 1}
        )

        # First retrieval (should populate cache)
        start_time = datetime.utcnow()
        data1 = motivation_data_service.retrieve_behavioral_data(user_id)
        first_time = (datetime.utcnow() - start_time).total_seconds()

        # Second retrieval (should use cache)
        start_time = datetime.utcnow()
        data2 = motivation_data_service.retrieve_behavioral_data(user_id)
        second_time = (datetime.utcnow() - start_time).total_seconds()

        # Cache should make second retrieval faster or equal
        assert second_time <= first_time
        assert len(data1) == len(data2)
        assert data1[0].content == data2[0].content
