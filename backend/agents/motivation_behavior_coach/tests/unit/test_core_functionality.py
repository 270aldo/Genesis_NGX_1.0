"""
Unit tests for SPARK Motivation Behavior Coach core functionality.
Tests core components, services, and skills manager with 90%+ coverage target.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from agents.motivation_behavior_coach.core import (
    SparkDependencies,
    SparkConfig,
    create_production_dependencies,
    create_test_dependencies,
    MotivationType,
    StageOfChange,
    BehaviorChangeModel,
    CoachingStyle,
    get_personality_style,
    SparkBaseError,
    MotivationAnalysisError,
    HabitFormationError,
)
from agents.motivation_behavior_coach.services import (
    MotivationSecurityService,
    MotivationDataService,
    MotivationIntegrationService,
    BehavioralDataEntry,
)
from agents.motivation_behavior_coach.skills_manager import SparkSkillsManager


class TestSparkConfig:
    """Test SPARK configuration functionality."""

    def test_default_config_creation(self):
        """Test creating config with default values."""
        config = SparkConfig()

        assert config.agent_id == "spark_motivation_coach"
        assert config.max_response_time == 30.0
        assert config.min_habit_duration_days == 21
        assert config.max_concurrent_goals == 5
        assert config.enable_ai_insights is True

    def test_config_validation(self):
        """Test configuration validation."""
        # Test valid config
        config = SparkConfig(
            max_response_time=10.0,
            default_timeout=8.0,
            low_motivation_threshold=0.3,
            high_motivation_threshold=0.8,
        )
        # Should not raise any exceptions

        # Test invalid timeouts
        with pytest.raises(ValueError, match="max_response_time must be positive"):
            SparkConfig(max_response_time=-1.0)

        # Test invalid thresholds
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            SparkConfig(low_motivation_threshold=1.5)

        # Test invalid threshold relationship
        with pytest.raises(
            ValueError,
            match="low_motivation_threshold must be < high_motivation_threshold",
        ):
            SparkConfig(low_motivation_threshold=0.8, high_motivation_threshold=0.3)

    def test_config_from_environment(self):
        """Test creating config from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "SPARK_AGENT_ID": "test_spark",
                "SPARK_MAX_RESPONSE_TIME": "15.0",
                "SPARK_MAX_CONCURRENT_GOALS": "3",
            },
        ):
            config = SparkConfig.from_environment()

            assert config.agent_id == "test_spark"
            assert config.max_response_time == 15.0
            assert config.max_concurrent_goals == 3

    def test_coaching_style_for_program(self):
        """Test coaching style selection based on program type."""
        config = SparkConfig()

        prime_style = config.get_coaching_style_for_program("PRIME")
        assert prime_style == CoachingStyle.DIRECTIVE

        longevity_style = config.get_coaching_style_for_program("LONGEVITY")
        assert longevity_style == CoachingStyle.COLLABORATIVE

        default_style = config.get_coaching_style_for_program("UNKNOWN")
        assert default_style == config.default_coaching_style


class TestSparkDependencies:
    """Test SPARK dependencies management."""

    def test_dependencies_creation(self, spark_dependencies):
        """Test dependencies container creation."""
        assert spark_dependencies.vertex_ai_client is not None
        assert spark_dependencies.personality_adapter is not None
        assert spark_dependencies.supabase_client is not None
        assert spark_dependencies.program_classification_service is not None

    def test_dependencies_validation(self):
        """Test dependencies validation."""
        # Test with None dependency
        with pytest.raises(ValueError, match="Required dependency.*cannot be None"):
            SparkDependencies(
                vertex_ai_client=None,
                personality_adapter=MagicMock(),
                supabase_client=MagicMock(),
                program_classification_service=MagicMock(),
                mcp_toolkit=MagicMock(),
                state_manager_adapter=MagicMock(),
                intent_analyzer_adapter=MagicMock(),
                a2a_adapter=MagicMock(),
            )

    def test_dependency_health_check(self, spark_dependencies):
        """Test dependency health status check."""
        health_status = spark_dependencies.get_dependency_health()

        assert isinstance(health_status, dict)
        assert "vertex_ai_client" in health_status
        assert "personality_adapter" in health_status
        assert "supabase_client" in health_status

        # All should be healthy with mocks
        for service, status in health_status.items():
            assert status == "healthy"

    def test_create_production_dependencies(self):
        """Test production dependencies creation."""
        with (
            patch("agents.motivation_behavior_coach.core.dependencies.VertexAIClient"),
            patch(
                "agents.motivation_behavior_coach.core.dependencies.PersonalityAdapter"
            ),
            patch("agents.motivation_behavior_coach.core.dependencies.SupabaseClient"),
        ):

            deps = create_production_dependencies()
            assert isinstance(deps, SparkDependencies)

    def test_create_test_dependencies(self):
        """Test test dependencies creation."""
        deps = create_test_dependencies()

        assert isinstance(deps, SparkDependencies)
        # All dependencies should be mocks
        assert isinstance(deps.vertex_ai_client, MagicMock)
        assert isinstance(deps.personality_adapter, MagicMock)


class TestMotivationSecurityService:
    """Test motivation security service functionality."""

    def test_encryption_decryption(self, motivation_security_service):
        """Test data encryption and decryption."""
        test_data = {
            "user_id": "test_user",
            "motivation_score": 7.5,
            "behavioral_data": "sensitive information",
        }

        # Encrypt data
        encrypted = motivation_security_service.encrypt_behavioral_data(test_data)
        assert isinstance(encrypted, str)
        assert encrypted != str(test_data)

        # Decrypt data
        decrypted = motivation_security_service.decrypt_behavioral_data(encrypted)
        assert decrypted == test_data

    def test_input_sanitization(self, motivation_security_service):
        """Test user input sanitization."""
        malicious_input = "<script>alert('xss')</script>Hello World"
        sanitized = motivation_security_service.sanitize_user_input(malicious_input)

        assert "<script>" not in sanitized
        assert "Hello World" in sanitized
        assert len(sanitized) <= len(malicious_input)

    def test_data_validation(self, motivation_security_service):
        """Test behavioral data validation."""
        # Valid data
        valid_data = {
            "user_id": "test_user_123",
            "timestamp": datetime.utcnow().isoformat(),
            "data_type": "motivation_assessment",
            "content": {"score": 7.5},
        }

        assert motivation_security_service.validate_behavioral_data(valid_data) is True

        # Invalid data - missing required field
        invalid_data = {
            "user_id": "test_user_123",
            "data_type": "motivation_assessment",
            # Missing timestamp
        }

        with pytest.raises(ValueError, match="Missing required field: timestamp"):
            motivation_security_service.validate_behavioral_data(invalid_data)

    def test_access_permissions(self, motivation_security_service):
        """Test access permission checking."""
        user_id = "test_user_123"

        # User can access their own data
        assert (
            motivation_security_service.check_access_permissions(
                user_id, "read", f"user_{user_id}_motivation_data"
            )
            is True
        )

        # User cannot access other user's data
        assert (
            motivation_security_service.check_access_permissions(
                user_id, "read", "user_other_user_motivation_data"
            )
            is False
        )

    def test_audit_logging(self, motivation_security_service):
        """Test security audit logging."""
        initial_log_count = len(motivation_security_service.audit_logs)

        # Perform some operations that should generate logs
        motivation_security_service.sanitize_user_input("test input")
        motivation_security_service.encrypt_behavioral_data({"test": "data"})

        # Check that audit logs were created
        assert len(motivation_security_service.audit_logs) > initial_log_count

        # Verify audit log structure
        latest_log = motivation_security_service.audit_logs[-1]
        assert "timestamp" in latest_log
        assert "event_type" in latest_log
        assert "details" in latest_log
        assert "hash" in latest_log

    def test_audit_integrity(self, motivation_security_service):
        """Test audit log integrity verification."""
        # Generate some audit logs
        motivation_security_service.sanitize_user_input("test")

        # Verify integrity
        assert motivation_security_service.verify_audit_integrity() is True

        # Tamper with a log entry
        if motivation_security_service.audit_logs:
            motivation_security_service.audit_logs[0]["details"] = "tampered"
            assert motivation_security_service.verify_audit_integrity() is False


class TestMotivationDataService:
    """Test motivation data service functionality."""

    def test_store_behavioral_data(self, motivation_data_service):
        """Test storing behavioral data."""
        user_id = "test_user_123"
        data_type = "motivation_assessment"
        content = {"motivation_score": 8.0, "mood": "positive"}

        entry_id = motivation_data_service.store_behavioral_data(
            user_id=user_id, data_type=data_type, content=content
        )

        assert isinstance(entry_id, str)
        assert user_id in entry_id
        assert data_type in entry_id

        # Verify data was stored
        stored_data = motivation_data_service.retrieve_behavioral_data(user_id)
        assert len(stored_data) == 1
        assert stored_data[0].user_id == user_id
        assert stored_data[0].data_type == data_type
        assert stored_data[0].content == content

    def test_retrieve_behavioral_data_with_filters(self, motivation_data_service):
        """Test retrieving behavioral data with filters."""
        user_id = "test_user_123"

        # Store multiple entries
        motivation_data_service.store_behavioral_data(
            user_id, "motivation_assessment", {"score": 7.0}
        )
        motivation_data_service.store_behavioral_data(
            user_id, "habit_tracking", {"habit": "exercise", "completed": True}
        )
        motivation_data_service.store_behavioral_data(
            user_id, "motivation_assessment", {"score": 8.0}
        )

        # Filter by data type
        motivation_data = motivation_data_service.retrieve_behavioral_data(
            user_id, data_type="motivation_assessment"
        )
        assert len(motivation_data) == 2
        assert all(
            entry.data_type == "motivation_assessment" for entry in motivation_data
        )

        # Filter with limit
        limited_data = motivation_data_service.retrieve_behavioral_data(
            user_id, limit=1
        )
        assert len(limited_data) == 1

    def test_behavior_pattern_analysis(
        self, motivation_data_service, sample_behavioral_data
    ):
        """Test behavioral pattern analysis."""
        user_id = "test_user_123"

        # Add sample data to service
        for entry in sample_behavioral_data:
            motivation_data_service.behavioral_data[user_id].append(entry)

        # Test motivation trends analysis
        analysis = motivation_data_service.analyze_behavior_patterns(
            user_id, "motivation_trends"
        )

        assert analysis["analysis_type"] == "motivation_trends"
        assert "trend" in analysis
        assert "average_score" in analysis

    def test_user_profile_management(self, motivation_data_service):
        """Test user profile management."""
        user_id = "test_user_123"
        profile_data = {
            "age": 35,
            "goals": ["fitness", "wellness"],
            "preferences": {"coaching_style": "collaborative"},
        }

        # Update profile
        motivation_data_service.update_user_profile(user_id, profile_data)

        # Retrieve profile
        retrieved_profile = motivation_data_service.get_user_profile(user_id)

        assert retrieved_profile["age"] == 35
        assert retrieved_profile["goals"] == ["fitness", "wellness"]
        assert "last_updated" in retrieved_profile

    def test_caching_functionality(self, motivation_data_service):
        """Test data caching functionality."""
        user_id = "test_user_123"

        # Store some data
        motivation_data_service.store_behavioral_data(
            user_id, "test_data", {"value": 1}
        )

        # First retrieval should populate cache
        data1 = motivation_data_service.retrieve_behavioral_data(user_id)

        # Second retrieval should use cache
        data2 = motivation_data_service.retrieve_behavioral_data(user_id)

        # Data should be identical
        assert len(data1) == len(data2)
        assert data1[0].content == data2[0].content


class TestMotivationIntegrationService:
    """Test motivation integration service functionality."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, motivation_integration_service):
        """Test circuit breaker protection."""
        service_name = "fitness_tracker"
        circuit_breaker = motivation_integration_service.circuit_breakers[service_name]

        # Initially closed
        assert circuit_breaker.state == "closed"
        assert circuit_breaker.can_execute() is True

        # Simulate failures to open circuit breaker
        for _ in range(circuit_breaker.failure_threshold):
            circuit_breaker.record_failure()

        # Should now be open
        assert circuit_breaker.state == "open"
        assert circuit_breaker.can_execute() is False

    @pytest.mark.asyncio
    async def test_service_health_check(self, motivation_integration_service):
        """Test service health checking."""
        with patch.object(
            motivation_integration_service, "_make_api_call"
        ) as mock_api_call:
            mock_api_call.return_value = {"healthy": True}

            health_status = await motivation_integration_service.check_service_health()

            assert "overall_status" in health_status
            assert "services" in health_status
            assert "timestamp" in health_status

    @pytest.mark.asyncio
    async def test_fallback_responses(self, motivation_integration_service):
        """Test fallback response generation."""
        # Test when service is unavailable
        service_name = "coaching_service"
        circuit_breaker = motivation_integration_service.circuit_breakers[service_name]

        # Force circuit breaker open
        for _ in range(circuit_breaker.failure_threshold):
            circuit_breaker.record_failure()

        # Request should return fallback
        result = await motivation_integration_service.request_coaching_intervention(
            user_id="test_user", intervention_type="motivation_boost", context={}
        )

        assert result["success"] is True
        assert result["fallback_applied"] is True
        assert "intervention_type" in result


class TestSparkSkillsManager:
    """Test SPARK skills manager functionality."""

    @pytest.mark.asyncio
    async def test_message_processing(self, spark_skills_manager, sample_user_context):
        """Test message processing and skill determination."""
        message = "I want to build a habit of exercising daily"

        result = await spark_skills_manager.process_message(
            message, sample_user_context
        )

        assert result["success"] is True
        assert "skill" in result
        assert result["skill"] == "habit_formation"

    @pytest.mark.asyncio
    async def test_skill_determination(
        self, spark_skills_manager, sample_coaching_scenarios
    ):
        """Test skill determination based on message content."""
        for scenario_name, scenario in sample_coaching_scenarios.items():
            skill = await spark_skills_manager._determine_skill(
                scenario["message"], scenario["context"]
            )
            assert skill == scenario["expected_skill"]

    @pytest.mark.asyncio
    async def test_habit_formation_skill(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test habit formation skill execution."""
        # Set up AI response
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Detailed habit formation analysis and plan...",
        }

        message = "I want to start a morning meditation habit"
        result = await spark_skills_manager._skill_habit_formation(
            message, sample_user_context
        )

        assert result["success"] is True
        assert result["skill"] == "habit_formation"
        assert "analysis" in result
        assert "recommendations" in result
        assert "next_steps" in result

    @pytest.mark.asyncio
    async def test_goal_setting_skill(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test goal setting skill execution."""
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "SMART goal analysis and implementation plan...",
        }

        message = "Help me set a goal to improve my fitness"
        result = await spark_skills_manager._skill_goal_setting(
            message, sample_user_context
        )

        assert result["success"] is True
        assert result["skill"] == "goal_setting"
        assert "analysis" in result
        assert "smart_framework" in result
        assert "action_plan" in result

    @pytest.mark.asyncio
    async def test_motivation_strategies_skill(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test motivation strategies skill execution."""
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Personalized motivation strategies and techniques...",
        }

        message = "I'm feeling unmotivated and need help"
        result = await spark_skills_manager._skill_motivation_strategies(
            message, sample_user_context
        )

        assert result["success"] is True
        assert result["skill"] == "motivation_strategies"
        assert "guidance" in result
        assert "quick_boosters" in result
        assert "motivation_toolkit" in result

    @pytest.mark.asyncio
    async def test_personality_adaptation(
        self, spark_skills_manager, sample_user_context, mock_personality_adapter
    ):
        """Test personality adaptation in skill responses."""
        mock_personality_adapter.adapt_response.return_value = {
            "success": True,
            "adapted_message": "Adapted response for PRIME program",
            "confidence_score": 0.9,
        }

        base_result = {
            "success": True,
            "skill": "motivation_strategies",
            "guidance": "Original guidance message",
        }

        adapted_result = await spark_skills_manager._apply_personality_adaptation(
            base_result, sample_user_context
        )

        assert adapted_result["guidance"] == "Adapted response for PRIME program"
        assert "personality_adaptation" in adapted_result
        assert adapted_result["personality_adaptation"]["applied"] is True

    @pytest.mark.asyncio
    async def test_error_handling(
        self, spark_skills_manager, sample_user_context, mock_gemini_client
    ):
        """Test error handling in skills execution."""
        # Simulate AI failure
        mock_gemini_client.generate_content.return_value = {
            "success": False,
            "error": "AI service unavailable",
        }

        message = "Help with habit formation"

        with pytest.raises(HabitFormationError):
            await spark_skills_manager._skill_habit_formation(
                message, sample_user_context
            )

    def test_skills_status(self, spark_skills_manager):
        """Test skills manager status reporting."""
        status = spark_skills_manager.get_skills_status()

        assert "available_skills" in status
        assert "ai_integration" in status
        assert "personality_adaptation" in status
        assert "service_status" in status

        expected_skills = [
            "habit_formation",
            "goal_setting",
            "motivation_strategies",
            "behavior_change",
            "obstacle_management",
        ]

        for skill in expected_skills:
            assert skill in status["available_skills"]


class TestExceptionHandling:
    """Test exception handling and error responses."""

    def test_spark_base_error(self):
        """Test base SPARK error functionality."""
        error = SparkBaseError(
            message="Test error", error_code="TEST_ERROR", details={"context": "test"}
        )

        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details["context"] == "test"

        error_dict = error.to_dict()
        assert error_dict["error_type"] == "SparkBaseError"
        assert error_dict["message"] == "Test error"

    def test_specific_errors(self):
        """Test specific SPARK error types."""
        # Test different error types
        motivation_error = MotivationAnalysisError("Motivation analysis failed")
        habit_error = HabitFormationError("Habit formation failed")

        assert isinstance(motivation_error, SparkBaseError)
        assert isinstance(habit_error, SparkBaseError)

        assert motivation_error.error_code == "MotivationAnalysisError"
        assert habit_error.error_code == "HabitFormationError"


# Integration tests for core functionality
class TestCoreIntegration:
    """Test integration between core components."""

    @pytest.mark.asyncio
    async def test_full_coaching_flow(
        self,
        spark_skills_manager,
        sample_user_context,
        mock_gemini_client,
        mock_personality_adapter,
    ):
        """Test complete coaching interaction flow."""
        # Setup AI responses
        mock_gemini_client.generate_content.return_value = {
            "success": True,
            "content": "Comprehensive coaching analysis and recommendations...",
        }

        mock_personality_adapter.adapt_response.return_value = {
            "success": True,
            "adapted_message": "Personality-adapted coaching response",
            "confidence_score": 0.85,
        }

        # Test coaching flow
        message = "I want to build better habits and achieve my fitness goals"
        result = await spark_skills_manager.process_message(
            message, sample_user_context
        )

        # Verify complete flow
        assert result["success"] is True
        assert "skill" in result
        assert "guidance" in result
        assert "personality_adaptation" in result

    def test_service_coordination(self, spark_skills_manager):
        """Test coordination between different services."""
        # Test that all services are properly initialized
        assert spark_skills_manager.security_service is not None
        assert spark_skills_manager.data_service is not None
        assert spark_skills_manager.integration_service is not None

        # Test service status coordination
        status = spark_skills_manager.get_skills_status()
        assert status["service_status"] == "operational"
