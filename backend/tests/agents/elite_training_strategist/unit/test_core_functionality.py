"""
Unit tests for BLAZE Elite Training Strategist core functionality.
Tests individual components and methods in isolation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from agents.elite_training_strategist.core.dependencies import BlazeAgentDependencies
from agents.elite_training_strategist.core.config import BlazeAgentConfig
from agents.elite_training_strategist.core.exceptions import (
    BlazeTrainingError,
    TrainingPlanGenerationError,
    InvalidTrainingParametersError,
    AthleteProfileError,
    create_training_error_response,
)
from agents.elite_training_strategist.core.constants import (
    TrainingPhase,
    TrainingGoal,
    AthleteLevel,
    TRAINING_FREQUENCIES,
    STRENGTH_STANDARDS,
)
from agents.elite_training_strategist.skills_manager import BlazeSkillsManager
from agents.elite_training_strategist.services import (
    TrainingSecurityService,
    TrainingDataService,
    TrainingIntegrationService,
)


class TestBlazeAgentConfig:
    """Test BLAZE agent configuration."""

    def test_default_config_creation(self):
        """Test creating config with default values."""
        config = BlazeAgentConfig()

        assert config.agent_id == "elite_training_strategist"
        assert config.agent_name == "Elite Training Strategist"
        assert config.default_model == "gemini-1.5-flash"
        assert config.max_response_time == 30.0
        assert config.enable_advanced_ai_features is True
        assert config.enable_voice_coaching is True

    def test_config_from_environment(self):
        """Test creating config from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "BLAZE_MODEL": "gemini-2.0-flash",
                "BLAZE_MAX_RESPONSE_TIME": "45.0",
                "BLAZE_ENABLE_AI": "false",
                "BLAZE_ENABLE_VOICE": "false",
            },
        ):
            config = BlazeAgentConfig.from_environment()

            assert config.default_model == "gemini-2.0-flash"
            assert config.max_response_time == 45.0
            assert config.enable_advanced_ai_features is False
            assert config.enable_voice_coaching is False

    def test_config_validation_success(self):
        """Test successful config validation."""
        config = BlazeAgentConfig(
            max_response_time=30.0,
            max_training_plan_duration_weeks=52,
            min_training_sessions_per_week=1,
            max_training_sessions_per_week=14,
            injury_risk_threshold=0.7,
        )

        errors = config.validate()
        assert len(errors) == 0

    def test_config_validation_failures(self):
        """Test config validation with invalid values."""
        config = BlazeAgentConfig(
            max_response_time=-1.0,
            max_training_plan_duration_weeks=0,
            min_training_sessions_per_week=0,
            max_training_sessions_per_week=0,
            injury_risk_threshold=1.5,
        )

        errors = config.validate()
        assert len(errors) > 0
        assert any("max_response_time must be positive" in error for error in errors)
        assert any(
            "max_training_plan_duration_weeks must be at least 1" in error
            for error in errors
        )

    def test_training_parameters_retrieval(self):
        """Test training parameters getter."""
        config = BlazeAgentConfig()
        params = config.get_training_parameters()

        assert "max_duration_weeks" in params
        assert "min_sessions_per_week" in params
        assert "max_sessions_per_week" in params
        assert "injury_risk_threshold" in params
        assert params["max_duration_weeks"] == 52

    def test_ai_features_retrieval(self):
        """Test AI features getter."""
        config = BlazeAgentConfig()
        features = config.get_ai_features()

        assert "advanced_ai" in features
        assert "posture_detection" in features
        assert "voice_coaching" in features
        assert features["advanced_ai"] is True


class TestBlazeAgentDependencies:
    """Test BLAZE agent dependencies container."""

    def test_create_default_dependencies(self):
        """Test creating dependencies with defaults."""
        deps = BlazeAgentDependencies.create_default()

        assert deps.vertex_ai_client is not None
        assert deps.supabase_client is not None
        assert deps.mcp_toolkit is not None
        assert deps.program_classification_service is not None
        assert deps.personality_adapter is not None

        # Test training-specific skills
        assert deps.advanced_training_plan_skill is not None
        assert deps.intelligent_nutrition_skill is not None
        assert deps.ai_progress_analysis_skill is not None
        assert deps.adaptive_training_skill is not None

    def test_create_dependencies_with_custom_toolkit(self):
        """Test creating dependencies with custom MCP toolkit."""
        custom_toolkit = Mock()
        deps = BlazeAgentDependencies.create_default(mcp_toolkit=custom_toolkit)

        assert deps.mcp_toolkit is custom_toolkit


class TestBlazeTrainingExceptions:
    """Test BLAZE training-specific exceptions."""

    def test_base_training_error(self):
        """Test base training error."""
        error = BlazeTrainingError(
            "Test error", error_code="TEST001", context={"test": "data"}
        )

        assert str(error) == "Test error"
        assert error.error_code == "TEST001"
        assert error.context["test"] == "data"

    def test_specific_training_errors(self):
        """Test specific training error types."""
        plan_error = TrainingPlanGenerationError("Plan generation failed")
        param_error = InvalidTrainingParametersError("Invalid parameters")
        profile_error = AthleteProfileError("Profile error")

        assert isinstance(plan_error, BlazeTrainingError)
        assert isinstance(param_error, BlazeTrainingError)
        assert isinstance(profile_error, BlazeTrainingError)

    def test_create_error_response(self):
        """Test error response creation."""
        error = TrainingPlanGenerationError("Test error", error_code="E001")
        response = create_training_error_response(error)

        assert response["error"] is True
        assert response["error_type"] == "TrainingPlanGenerationError"
        assert response["error_code"] == "E001"
        assert response["message"] == "Test error"
        assert isinstance(response["suggestions"], list)
        assert len(response["suggestions"]) > 0


class TestTrainingSecurityService:
    """Test training security service."""

    def test_sanitize_valid_athlete_data(self):
        """Test sanitizing valid athlete data."""
        config = BlazeAgentConfig()
        security_service = TrainingSecurityService(config)

        athlete_data = {
            "age": 28,
            "fitness_level": "intermediate",
            "training_goals": ["strength", "hypertrophy"],
            "weight": 75.0,
            "height": 180.0,
            "injuries": ["knee strain"],
            "equipment_access": ["barbell", "dumbbells"],
        }

        sanitized = security_service.sanitize_athlete_data(athlete_data)

        assert sanitized["age"] == 28
        assert sanitized["fitness_level"] == "intermediate"
        assert "strength" in sanitized["training_goals"]
        assert sanitized["weight"] == 75.0
        assert sanitized["height"] == 180.0
        assert len(sanitized["injuries"]) == 1
        assert len(sanitized["equipment_access"]) == 2

    def test_sanitize_invalid_athlete_data(self):
        """Test sanitizing invalid athlete data."""
        config = BlazeAgentConfig()
        security_service = TrainingSecurityService(config)

        invalid_data = {
            "age": -5,  # Invalid age
            "fitness_level": "invalid_level",  # Invalid level
            "training_goals": [],  # Empty goals
        }

        with pytest.raises(BlazeTrainingError):
            security_service.sanitize_athlete_data(invalid_data)

    def test_validate_training_parameters(self):
        """Test training parameters validation."""
        config = BlazeAgentConfig()
        security_service = TrainingSecurityService(config)

        training_params = {
            "duration_weeks": 12,
            "sessions_per_week": 4,
            "intensity_distribution": "polarized",
            "training_phase": "build",
        }

        validated = security_service.validate_training_parameters(training_params)

        assert validated["duration_weeks"] == 12
        assert validated["sessions_per_week"] == 4
        assert validated["intensity_distribution"] == "polarized"
        assert validated["training_phase"] == "build"

    def test_secure_performance_data(self):
        """Test performance data security."""
        config = BlazeAgentConfig()
        security_service = TrainingSecurityService(config)

        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "heart_rate": 150,
            "power": 250,
            "speed": 12.5,
            "exercise": "squat",
            "notes": "Good session",
        }

        secured = security_service.secure_performance_data(performance_data)

        assert "timestamp" in secured
        assert secured["heart_rate"] == 150.0
        assert secured["power"] == 250.0
        assert secured["exercise"] == "squat"
        assert secured["notes"] == "Good session"

    def test_generate_secure_session_id(self):
        """Test secure session ID generation."""
        config = BlazeAgentConfig()
        security_service = TrainingSecurityService(config)

        athlete_id = "test_athlete_123"
        timestamp = datetime.now().isoformat()

        session_id = security_service.generate_secure_session_id(athlete_id, timestamp)

        assert isinstance(session_id, str)
        assert len(session_id) == 16

        # Should generate different IDs for different inputs
        session_id2 = security_service.generate_secure_session_id(
            "different_athlete", timestamp
        )
        assert session_id != session_id2

    def test_validate_biometric_data(self):
        """Test biometric data validation."""
        config = BlazeAgentConfig()
        security_service = TrainingSecurityService(config)

        biometric_data = {
            "heart_rate": 65,
            "hrv": 45,
            "sleep_score": 85,
            "recovery_score": 78,
        }

        validated = security_service.validate_biometric_data(biometric_data)

        assert validated["heart_rate"] == 65.0
        assert validated["hrv"] == 45.0
        assert validated["sleep_score"] == 85.0
        assert validated["recovery_score"] == 78.0

    def test_audit_logging(self):
        """Test audit logging functionality."""
        config = BlazeAgentConfig(log_training_sessions=True)
        security_service = TrainingSecurityService(config)

        # Trigger an operation that logs
        athlete_data = {
            "age": 28,
            "fitness_level": "intermediate",
            "training_goals": ["strength"],
        }
        security_service.sanitize_athlete_data(athlete_data)

        audit_log = security_service.get_audit_log()
        assert len(audit_log) > 0
        assert audit_log[0]["event_type"] == "athlete_data_sanitized"

        # Test clearing audit log
        security_service.clear_audit_log()
        assert len(security_service.get_audit_log()) == 0


class TestTrainingConstants:
    """Test training constants and enumerations."""

    def test_training_phase_enum(self):
        """Test training phase enumeration."""
        assert TrainingPhase.PREPARATION.value == "preparation"
        assert TrainingPhase.BUILD.value == "build"
        assert TrainingPhase.PEAK.value == "peak"
        assert TrainingPhase.RECOVERY.value == "recovery"

    def test_training_goal_enum(self):
        """Test training goal enumeration."""
        assert TrainingGoal.STRENGTH.value == "strength"
        assert TrainingGoal.POWER.value == "power"
        assert TrainingGoal.ENDURANCE.value == "endurance"
        assert TrainingGoal.HYPERTROPHY.value == "hypertrophy"

    def test_athlete_level_enum(self):
        """Test athlete level enumeration."""
        assert AthleteLevel.BEGINNER.value == "beginner"
        assert AthleteLevel.INTERMEDIATE.value == "intermediate"
        assert AthleteLevel.ADVANCED.value == "advanced"
        assert AthleteLevel.ELITE.value == "elite"

    def test_training_frequencies(self):
        """Test training frequency constants."""
        assert "beginner" in TRAINING_FREQUENCIES
        assert "elite" in TRAINING_FREQUENCIES
        assert len(TRAINING_FREQUENCIES["beginner"]) >= 2
        assert max(TRAINING_FREQUENCIES["elite"]) > max(
            TRAINING_FREQUENCIES["beginner"]
        )

    def test_strength_standards(self):
        """Test strength standards constants."""
        assert "squat" in STRENGTH_STANDARDS
        assert "deadlift" in STRENGTH_STANDARDS
        assert "bench_press" in STRENGTH_STANDARDS

        # Check progression across levels
        squat_standards = STRENGTH_STANDARDS["squat"]
        assert squat_standards["elite"] > squat_standards["advanced"]
        assert squat_standards["advanced"] > squat_standards["intermediate"]


@pytest.mark.asyncio
class TestBlazeSkillsManagerCore:
    """Test core functionality of BLAZE skills manager."""

    async def test_skills_manager_initialization(self, mock_dependencies, test_config):
        """Test skills manager initialization."""
        skills_manager = BlazeSkillsManager(mock_dependencies, test_config)

        assert skills_manager.dependencies is mock_dependencies
        assert skills_manager.config is test_config
        assert skills_manager.security_service is not None
        assert skills_manager.data_service is not None
        assert skills_manager.integration_service is not None
        assert isinstance(skills_manager.skill_metrics, dict)

    async def test_determine_skill_training_plan(self, skills_manager):
        """Test skill determination for training plan requests."""
        message = "I need a comprehensive training plan for strength"
        context = {"user_profile": {"fitness_level": "intermediate"}}

        skill_name = await skills_manager._determine_skill(message, context)
        assert skill_name == "generate_training_plan"

    async def test_determine_skill_performance_analysis(self, skills_manager):
        """Test skill determination for performance analysis."""
        message = "Can you analyze my recent performance data?"
        context = {"user_profile": {"fitness_level": "advanced"}}

        skill_name = await skills_manager._determine_skill(message, context)
        assert skill_name == "analyze_performance_data"

    async def test_determine_skill_exercise_prescription(self, skills_manager):
        """Test skill determination for exercise prescription."""
        message = "What exercises should I do for my chest workout?"
        context = {"user_profile": {"fitness_level": "beginner"}}

        skill_name = await skills_manager._determine_skill(message, context)
        assert skill_name == "prescribe_exercise_routines"

    async def test_prepare_skill_input_training_plan(
        self, skills_manager, sample_athlete_profile
    ):
        """Test skill input preparation for training plan generation."""
        context = {
            "user_profile": sample_athlete_profile,
            "duration_weeks": 12,
            "sessions_per_week": 4,
        }

        skill_input = skills_manager._prepare_skill_input(
            "generate_training_plan", "Create a strength plan", context
        )

        assert skill_input.input_text == "Create a strength plan"
        assert skill_input.duration_weeks == 12
        assert skill_input.sessions_per_week == 4
        assert skill_input.fitness_level == "intermediate"
        assert "strength" in skill_input.training_goals

    async def test_skill_metrics_tracking(self, skills_manager):
        """Test skill execution metrics tracking."""
        # Track successful execution
        skills_manager._update_skill_metrics("test_skill", 1.5, True)
        skills_manager._update_skill_metrics("test_skill", 2.0, True)

        # Track failed execution
        skills_manager._update_skill_metrics("test_skill", 0.0, False)

        metrics = skills_manager.get_skill_metrics()
        test_metrics = metrics["test_skill"]

        assert test_metrics["total_executions"] == 3
        assert test_metrics["successful_executions"] == 2
        assert test_metrics["success_rate"] == 2 / 3
        assert test_metrics["average_time"] == 1.75  # (1.5 + 2.0) / 2

    async def test_error_handling_in_process_message(self, skills_manager):
        """Test error handling in message processing."""
        # Mock an error in skill execution
        with patch.object(
            skills_manager,
            "_execute_skill",
            side_effect=BlazeTrainingError("Test error"),
        ):
            result = await skills_manager.process_message("test message", {})

            assert result["error"] is True
            assert "Test error" in result["message"]

    async def test_unknown_skill_handling(self, skills_manager, sample_context):
        """Test handling of unknown skill execution."""
        with pytest.raises(BlazeTrainingError, match="Unknown skill"):
            await skills_manager._execute_skill(
                "unknown_skill", "test message", sample_context
            )
