"""
Unit tests for WAVE Performance Analytics Agent core functionality.
A+ testing framework targeting 90%+ coverage.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from agents.wave_performance_analytics.core.config import WaveAnalyticsConfig
from agents.wave_performance_analytics.core.dependencies import (
    WaveAnalyticsAgentDependencies,
)
from agents.wave_performance_analytics.core.exceptions import (
    WaveAnalyticsError,
    RecoveryError,
    AnalyticsError,
    FusionError,
    RecoveryValidationError,
    InjuryPreventionError,
    RehabilitationError,
    SleepOptimizationError,
    MobilityAssessmentError,
    BiometricAnalysisError,
)
from agents.wave_performance_analytics.agent_optimized import (
    WavePerformanceAnalyticsAgent,
)
from agents.wave_performance_analytics.skills_manager import WaveAnalyticsSkillsManager
from agents.wave_performance_analytics.services.recovery_service import RecoveryService


class TestWaveAnalyticsConfig:
    """Test configuration management."""

    def test_default_config_creation(self):
        """Test creating default configuration."""
        config = WaveAnalyticsConfig()

        # Performance settings
        assert config.max_response_time == 25.0
        assert config.max_retry_attempts == 3
        assert config.request_timeout == 20.0

        # AI settings
        assert config.gemini_model == "gemini-1.5-flash-002"
        assert config.temperature == 0.6
        assert config.max_output_tokens == 6144
        assert config.enable_vision_analysis is True

        # Feature flags
        assert config.enable_injury_prediction is True
        assert config.enable_sleep_coaching is True
        assert config.enable_recovery_analytics_fusion is True

        # Compliance
        assert config.gdpr_compliant is True
        assert config.hipaa_compliant is True
        assert config.data_residency == "eu"

    def test_config_from_environment(self):
        """Test configuration from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "WAVE_MAX_RESPONSE_TIME": "30.0",
                "WAVE_GEMINI_MODEL": "gemini-1.5-pro",
                "WAVE_TEMPERATURE": "0.8",
                "WAVE_ENABLE_ENCRYPTION": "true",
                "WAVE_ENABLE_FUSION": "false",
            },
        ):
            config = WaveAnalyticsConfig.from_environment()

            assert config.max_response_time == 30.0
            assert config.gemini_model == "gemini-1.5-pro"
            assert config.temperature == 0.8
            assert config.enable_health_data_encryption is True
            assert config.enable_recovery_analytics_fusion is False

    def test_config_validation_success(self):
        """Test successful configuration validation."""
        config = WaveAnalyticsConfig()
        errors = config.validate()
        assert errors == []

    def test_config_validation_errors(self):
        """Test configuration validation with errors."""
        config = WaveAnalyticsConfig()

        # Invalid values
        config.max_response_time = -1.0
        config.temperature = 3.0
        config.recovery_protocols["injury_prevention"]["risk_threshold"] = 1.5

        errors = config.validate()
        assert len(errors) >= 3
        assert any("max_response_time must be positive" in error for error in errors)
        assert any("temperature must be between 0 and 2" in error for error in errors)
        assert any(
            "risk_threshold must be between 0 and 1" in error for error in errors
        )

    def test_get_recovery_protocol(self):
        """Test getting specific recovery protocol."""
        config = WaveAnalyticsConfig()

        protocol = config.get_recovery_protocol("injury_prevention")
        assert protocol is not None
        assert "assessment_frequency" in protocol
        assert "risk_threshold" in protocol

        invalid_protocol = config.get_recovery_protocol("nonexistent")
        assert invalid_protocol is None

    def test_get_fusion_config(self):
        """Test getting fusion configuration."""
        config = WaveAnalyticsConfig()

        fusion_config = config.get_fusion_config("recovery_analytics_fusion")
        assert fusion_config is not None
        assert "integration_weight_recovery" in fusion_config
        assert "fusion_confidence_threshold" in fusion_config

    def test_is_feature_enabled(self):
        """Test feature flag checking."""
        config = WaveAnalyticsConfig()

        assert config.is_feature_enabled("injury_prediction") is True
        assert config.is_feature_enabled("sleep_coaching") is True
        assert config.is_feature_enabled("nonexistent_feature") is False

    def test_get_device_config(self):
        """Test device-specific configuration."""
        config = WaveAnalyticsConfig()

        whoop_config = config.get_device_config("whoop")
        assert whoop_config is not None
        assert whoop_config["device_type"] == "whoop"
        assert "primary_metrics" in whoop_config

        invalid_device = config.get_device_config("invalid_device")
        assert invalid_device is None

    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = WaveAnalyticsConfig()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "performance" in config_dict
        assert "ai_ml" in config_dict
        assert "recovery" in config_dict
        assert "analytics" in config_dict
        assert "fusion" in config_dict
        assert "security" in config_dict
        assert "features" in config_dict


class TestWaveAnalyticsAgentDependencies:
    """Test dependency injection container."""

    def test_dependencies_creation(
        self, mock_cache, mock_gemini_client, mock_personality_adapter
    ):
        """Test creating dependencies container."""
        deps = WaveAnalyticsAgentDependencies(
            cache=mock_cache,
            vertex_ai_client=mock_gemini_client,
            personality_adapter=mock_personality_adapter,
        )

        assert deps.cache == mock_cache
        assert deps.vertex_ai_client == mock_gemini_client
        assert deps.personality_adapter == mock_personality_adapter

    def test_create_default_dependencies(self):
        """Test creating default dependencies."""
        with (
            patch(
                "agents.wave_performance_analytics.core.dependencies.CacheManager"
            ) as mock_cache_class,
            patch(
                "agents.wave_performance_analytics.core.dependencies.VertexAIClient"
            ) as mock_gemini_class,
        ):

            deps = WaveAnalyticsAgentDependencies.create_default()
            assert deps is not None


class TestWaveAnalyticsExceptions:
    """Test domain-specific exceptions."""

    def test_wave_analytics_error(self):
        """Test base WaveAnalyticsError."""
        details = {"component": "test", "value": 123}
        error = WaveAnalyticsError("Test error", details)

        assert str(error) == "Test error"
        assert error.details == details

    def test_recovery_validation_error(self):
        """Test RecoveryValidationError."""
        error = RecoveryValidationError(
            "Invalid field",
            field_name="test_field",
            invalid_value="invalid",
            validation_rule="must be positive",
        )

        assert error.details["field_name"] == "test_field"
        assert error.details["invalid_value"] == "invalid"
        assert error.details["validation_rule"] == "must be positive"

    def test_injury_prevention_error(self):
        """Test InjuryPreventionError."""
        error = InjuryPreventionError(
            "Prevention failed", injury_type="lower_back", risk_level=0.8
        )

        assert error.details["injury_type"] == "lower_back"
        assert error.details["risk_level"] == 0.8

    def test_rehabilitation_error(self):
        """Test RehabilitationError."""
        error = RehabilitationError(
            "Rehab failed",
            exercise_type="stretching",
            pain_level=7,
            session_id="session_123",
        )

        assert error.details["exercise_type"] == "stretching"
        assert error.details["pain_level"] == 7
        assert error.details["session_id"] == "session_123"

    def test_biometric_analysis_error(self):
        """Test BiometricAnalysisError."""
        error = BiometricAnalysisError(
            "Analysis failed",
            metric_name="hrv",
            value=25.5,
            expected_range={"min": 30, "max": 80},
        )

        assert error.details["metric"] == "hrv"
        assert error.details["value"] == 25.5
        assert error.details["expected_range"]["min"] == 30


class TestWavePerformanceAnalyticsAgent:
    """Test main agent functionality."""

    def test_agent_initialization(self, mock_dependencies, mock_config):
        """Test agent initialization."""
        agent = WavePerformanceAnalyticsAgent(mock_dependencies, mock_config)

        assert agent.agent_id == "wave_performance_analytics"
        assert agent.name == "Recovery & Performance Analytics Specialist"
        assert agent.is_initialized is True
        assert agent.request_count == 0
        assert hasattr(agent, "config")
        assert hasattr(agent, "deps")
        assert hasattr(agent, "skills_manager")

    def test_agent_initialization_with_defaults(self):
        """Test agent initialization with default parameters."""
        with (
            patch(
                "agents.wave_performance_analytics.agent_optimized.WaveAnalyticsConfig"
            ) as mock_config_class,
            patch(
                "agents.wave_performance_analytics.agent_optimized.WaveAnalyticsAgentDependencies"
            ) as mock_deps_class,
        ):

            mock_config_class.from_environment.return_value = Mock()
            mock_deps_class.create_default.return_value = Mock()

            agent = WavePerformanceAnalyticsAgent()
            assert agent is not None

    def test_configuration_validation(self, mock_dependencies):
        """Test configuration validation during initialization."""
        # Test with invalid configuration
        invalid_config = WaveAnalyticsConfig()
        invalid_config.max_response_time = -1.0

        with pytest.raises(RecoveryValidationError) as exc_info:
            WavePerformanceAnalyticsAgent(mock_dependencies, invalid_config)

        assert "Configuration validation failed" in str(exc_info.value)

    def test_dependencies_validation(self, mock_config):
        """Test dependencies validation during initialization."""
        # Test with invalid dependencies
        invalid_deps = Mock()
        invalid_deps.validate_dependencies.return_value = False

        with pytest.raises(RecoveryValidationError) as exc_info:
            WavePerformanceAnalyticsAgent(invalid_deps, mock_config)

        assert "Critical dependencies validation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_process_message_success(self, wave_agent, sample_context):
        """Test successful message processing."""
        message = "How is my recovery looking this week?"

        # Mock skills manager response
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "recovery_analytics_fusion",
                "analysis": {
                    "recovery_status": "good",
                    "readiness_score": 85,
                    "recommendations": ["Continue current protocols"],
                },
            }
        )

        result = await wave_agent._run_async_impl(message, sample_context)

        assert result["success"] is True
        assert result["agent"] == "wave_performance_analytics"
        assert result["agent_type"] == "recovery_analytics_fusion"
        assert "fusion_capabilities" in result
        assert "personality_fusion" in result
        assert "usage_stats" in result

    @pytest.mark.asyncio
    async def test_process_message_error(self, wave_agent, sample_context):
        """Test message processing with error."""
        message = "Analyze my recovery"

        # Mock skills manager to raise error
        wave_agent.skills_manager.process_message = AsyncMock(
            side_effect=RecoveryError("Processing failed")
        )

        result = await wave_agent._run_async_impl(message, sample_context)

        assert result["success"] is False
        assert result["error"] == "Processing failed"
        assert result["error_type"] == "RecoveryError"
        assert result["agent"] == "wave_performance_analytics"

    @pytest.mark.asyncio
    async def test_preprocess_request(self, wave_agent):
        """Test request preprocessing."""
        message = "Test message"
        context = {"user_id": "test_user", "program_type": "PRIME"}

        processed = await wave_agent._preprocess_request(message, context)

        assert processed["user_id"] == "test_user"
        assert processed["program_type"] == "PRIME"
        assert processed["fusion_mode"] is True
        assert "timestamp" in processed
        assert "session_id" in processed

    @pytest.mark.asyncio
    async def test_preprocess_request_empty_message(self, wave_agent):
        """Test preprocessing with empty message."""
        message = ""
        context = {}

        with pytest.raises(RecoveryValidationError) as exc_info:
            await wave_agent._preprocess_request(message, context)

        assert "Empty message provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_data_consent_check(self, wave_agent):
        """Test health data consent checking."""
        context = {"user_id": "test_user", "biometric_data": {"hrv": 45, "rhr": 60}}

        # Should not raise exception (just logs in current implementation)
        await wave_agent._check_health_data_consent(context)

    @pytest.mark.asyncio
    async def test_postprocess_fusion_response(self, wave_agent):
        """Test response post-processing."""
        original_result = {
            "success": True,
            "skill": "recovery_analytics_fusion",
            "data": "test_data",
        }
        context = {"session_id": "session_123", "program_type": "LONGEVITY"}

        processed = await wave_agent._postprocess_fusion_response(
            original_result, context
        )

        assert processed["agent"] == "wave_performance_analytics"
        assert processed["agent_type"] == "recovery_analytics_fusion"
        assert processed["version"] == "1.0.0"
        assert processed["request_id"] == "session_123"
        assert "fusion_capabilities" in processed
        assert "personality_fusion" in processed
        assert processed["personality_fusion"]["program_adaptation"] == "LONGEVITY"

    def test_create_error_response(self, wave_agent):
        """Test error response creation."""
        error = RecoveryError("Test error", {"detail": "test"})

        response = wave_agent._create_error_response(error)

        assert response["success"] is False
        assert response["error"] == "Test error"
        assert response["error_type"] == "RecoveryError"
        assert response["error_details"] == {"detail": "test"}
        assert response["agent"] == "wave_performance_analytics"

    def test_update_performance_metrics(self, wave_agent):
        """Test performance metrics updating."""
        start_time = datetime.now() - timedelta(milliseconds=500)

        wave_agent._update_performance_metrics(start_time, True)

        # Check if metrics were recorded (if telemetry available)
        if wave_agent.telemetry:
            wave_agent.telemetry.record_metric.assert_called()

    @pytest.mark.asyncio
    async def test_get_health_status(self, wave_agent):
        """Test health status reporting."""
        health_status = await wave_agent.get_health_status()

        assert "agent_id" in health_status
        assert "agent_type" in health_status
        assert "status" in health_status
        assert "health_score" in health_status
        assert "components" in health_status
        assert "dependencies" in health_status
        assert "fusion_capabilities" in health_status
        assert "performance" in health_status
        assert "configuration" in health_status

        # Check agent type
        assert health_status["agent_type"] == "recovery_analytics_fusion"

        # Check components
        components = health_status["components"]
        assert "skills_manager" in components
        assert "recovery_service" in components
        assert "fusion_capabilities" in components

    def test_get_capabilities(self, wave_agent):
        """Test capabilities reporting."""
        capabilities = wave_agent.get_capabilities()

        assert capabilities["agent_type"] == "recovery_analytics_fusion"
        assert (
            capabilities["specialization"]
            == "holistic_recovery_with_analytical_precision"
        )
        assert "fusion_components" in capabilities
        assert "personality_fusion" in capabilities
        assert "skills" in capabilities
        assert "features" in capabilities
        assert "integrations" in capabilities
        assert "ai_capabilities" in capabilities

        # Check skills categorization
        skills = capabilities["skills"]
        assert "recovery" in skills
        assert "analytics" in skills
        assert "fusion" in skills

    @pytest.mark.asyncio
    async def test_shutdown(self, wave_agent):
        """Test graceful shutdown."""
        await wave_agent.shutdown()

        assert wave_agent.is_initialized is False
        assert wave_agent.fusion_capabilities_ready is False

    def test_repr(self, wave_agent):
        """Test string representation."""
        repr_str = repr(wave_agent)

        assert "WavePerformanceAnalyticsAgent" in repr_str
        assert "agent_id='wave_performance_analytics'" in repr_str
        assert "initialized=True" in repr_str


class TestRecoveryService:
    """Test recovery service functionality."""

    @pytest.mark.asyncio
    async def test_assess_injury_risk(
        self, mock_recovery_service, sample_user_data, sample_biometric_data
    ):
        """Test injury risk assessment."""
        result = await mock_recovery_service.assess_injury_risk(
            sample_user_data, sample_biometric_data
        )

        assert "risk_score" in result
        assert "risk_level" in result
        assert "primary_risk_factors" in result
        assert "prevention_recommendations" in result
        assert "assessment_date" in result
        assert "reassessment_due" in result

    @pytest.mark.asyncio
    async def test_create_rehabilitation_plan(self, mock_recovery_service):
        """Test rehabilitation plan creation."""
        result = await mock_recovery_service.create_rehabilitation_plan(
            injury_type="lower_back",
            severity="mild",
            user_profile={"age": 30, "fitness_level": "moderate"},
        )

        assert result["injury_type"] == "lower_back"
        assert result["severity"] == "mild"
        assert "plan_id" in result
        assert "phases" in result
        assert "duration_weeks" in result
        assert "session_frequency" in result

    @pytest.mark.asyncio
    async def test_optimize_sleep_protocol(self, mock_recovery_service):
        """Test sleep protocol optimization."""
        sleep_data = {
            "avg_total_sleep": 7.5,
            "avg_deep_sleep": 1.2,
            "sleep_efficiency": 82,
        }
        recovery_goals = ["improve_deep_sleep", "increase_efficiency"]

        result = await mock_recovery_service.optimize_sleep_protocol(
            sleep_data, recovery_goals
        )

        assert "current_metrics" in result
        assert "optimization_opportunities" in result
        assert "recommendations" in result
        assert "target_metrics" in result

    @pytest.mark.asyncio
    async def test_assess_mobility(self, mock_recovery_service):
        """Test mobility assessment."""
        result = await mock_recovery_service.assess_mobility(
            assessment_type="full", user_profile={"age": 30, "activity_level": "high"}
        )

        assert result["assessment_type"] == "full"
        assert "overall_score" in result
        assert "limitations_identified" in result
        assert "improvement_recommendations" in result


class TestWaveAnalyticsSkillsManager:
    """Test skills manager functionality."""

    def test_skills_manager_initialization(self, mock_dependencies):
        """Test skills manager initialization."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        assert len(skills_manager.skills) == 13  # Total skills expected

        # Check skill categories
        recovery_skills = [
            s
            for s in skills_manager.skills.keys()
            if any(
                word in s
                for word in ["injury", "rehab", "sleep", "mobility", "recovery"]
            )
        ]
        analytics_skills = [
            s
            for s in skills_manager.skills.keys()
            if any(word in s for word in ["biometric", "pattern", "trend", "data"])
        ]
        fusion_skills = [
            s
            for s in skills_manager.skills.keys()
            if any(word in s for word in ["fusion", "prediction", "optimization"])
        ]

        assert len(recovery_skills) >= 5
        assert len(analytics_skills) >= 3
        assert len(fusion_skills) >= 3

    @pytest.mark.asyncio
    async def test_process_message(self, mock_dependencies):
        """Test message processing through skills manager."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        message = "How is my recovery looking?"
        context = {"user_id": "test_user", "program_type": "PRIME"}

        # Mock skill determination and execution
        with (
            patch.object(
                skills_manager, "_determine_skill", return_value="general_recovery"
            ),
            patch.object(
                skills_manager, "_execute_skill", new_callable=AsyncMock
            ) as mock_execute,
        ):

            mock_execute.return_value = {
                "skill": "general_recovery",
                "success": True,
                "status": "fallback_active",
            }

            result = await skills_manager.process_message(message, context)

            assert result["skill"] == "general_recovery"
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_determine_skill_with_ai(self, mock_dependencies):
        """Test skill determination using AI."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        # Mock Gemini response
        mock_dependencies.vertex_ai_client.generate_content_async.return_value = (
            "injury_prevention"
        )

        message = "I'm worried about getting injured"
        context = {"user_id": "test_user"}

        skill_name = await skills_manager._determine_skill(message, context)

        assert skill_name == "injury_prevention"

    @pytest.mark.asyncio
    async def test_determine_skill_fallback(self, mock_dependencies):
        """Test skill determination fallback without AI."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        # Mock Gemini client as None
        skills_manager.vertex_ai_client = None

        message = "I need help with sleep"
        context = {"user_id": "test_user"}

        skill_name = await skills_manager._determine_skill(message, context)

        assert skill_name == "sleep_optimization"

    def test_fallback_skill_determination(self, mock_dependencies):
        """Test fallback skill determination logic."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        # Test various keywords
        test_cases = [
            ("I have an injury", "injury_prevention"),
            ("Need help with sleep", "sleep_optimization"),
            ("Check my mobility", "mobility_assessment"),
            ("Analyze my data", "biometric_analysis"),
            ("Show me charts", "data_visualization"),
            ("Optimize my performance", "recovery_analytics_fusion"),
            ("Random message", "general_recovery"),
        ]

        for message, expected_skill in test_cases:
            skill = skills_manager._fallback_skill_determination(message)
            assert skill == expected_skill

    @pytest.mark.asyncio
    async def test_injury_prevention_skill(
        self, mock_dependencies, sample_user_data, sample_biometric_data
    ):
        """Test injury prevention skill execution."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        message = "Assess my injury risk"
        context = {
            "user_id": "test_user",
            **sample_user_data,
            "biometric_trends": sample_biometric_data,
        }

        # Mock recovery service
        skills_manager.recovery_service.assess_injury_risk = AsyncMock(
            return_value={
                "risk_level": "low",
                "risk_score": 0.25,
                "prevention_recommendations": ["Continue current protocols"],
            }
        )

        result = await skills_manager._skill_injury_prevention(message, context)

        assert result["skill"] == "injury_prevention"
        assert result["success"] is True
        assert "assessment" in result
        assert "risk_level" in result

    @pytest.mark.asyncio
    async def test_biometric_analysis_skill(
        self, mock_dependencies, sample_biometric_data
    ):
        """Test biometric analysis skill execution."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        message = "Analyze my biometric data"
        context = {"user_id": "test_user", "biometric_data": sample_biometric_data}

        result = await skills_manager._skill_biometric_analysis(message, context)

        assert result["skill"] == "biometric_analysis"
        assert result["success"] is True
        assert "analysis" in result
        assert "recovery_status" in result
        assert "readiness_score" in result

    @pytest.mark.asyncio
    async def test_fusion_skill(
        self, mock_dependencies, sample_recovery_data, sample_analytics_data
    ):
        """Test recovery-analytics fusion skill execution."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        message = "Give me a comprehensive analysis"
        context = {
            "user_id": "test_user",
            "recovery_data": sample_recovery_data,
            "biometric_data": sample_analytics_data,
        }

        result = await skills_manager._skill_recovery_analytics_fusion(message, context)

        assert result["skill"] == "recovery_analytics_fusion"
        assert result["success"] is True
        assert "fusion_analysis" in result
        assert "fusion_confidence" in result
        assert "holistic_insights" in result
        assert "analytical_insights" in result

    @pytest.mark.asyncio
    async def test_injury_prediction_analytics_skill(
        self, mock_dependencies, sample_user_data
    ):
        """Test injury prediction analytics skill."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        message = "Predict my injury risk for the next two weeks"
        context = {
            "user_id": "test_user",
            **sample_user_data,
            "historical_biometrics": {
                "hrv_trend": "declining",
                "training_load": "high",
            },
        }

        result = await skills_manager._skill_injury_prediction_analytics(
            message, context
        )

        assert result["skill"] == "injury_prediction_analytics"
        assert result["success"] is True
        assert "prediction" in result
        assert result["prediction_horizon_days"] == 14
        assert "risk_probabilities" in result

    def test_extract_user_data(self, mock_dependencies):
        """Test user data extraction utility."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        context = {
            "user_id": "test_user",
            "age": 30,
            "activity_level": "high",
            "goals": ["performance", "recovery"],
            "injury_history": [{"type": "ankle", "date": "2023-01-01"}],
            "program_type": "PRIME",
        }

        user_data = skills_manager._extract_user_data(context)

        assert user_data["user_id"] == "test_user"
        assert user_data["age"] == 30
        assert user_data["activity_level"] == "high"
        assert user_data["fitness_goals"] == ["performance", "recovery"]
        assert user_data["program_type"] == "PRIME"

    @pytest.mark.asyncio
    async def test_personality_adaptation(self, mock_dependencies):
        """Test personality adaptation application."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        result = {"skill": "test_skill", "success": True, "data": "test_data"}
        context = {"program_type": "LONGEVITY"}

        adapted_result = await skills_manager._apply_personality_adaptation(
            result, context
        )

        assert "personality_adaptation" in adapted_result
        assert "personality_context" in adapted_result
        assert adapted_result["personality_context"]["program_type"] == "LONGEVITY"

    def test_create_error_response(self, mock_dependencies):
        """Test error response creation in skills manager."""
        skills_manager = WaveAnalyticsSkillsManager(mock_dependencies)

        error_response = skills_manager._create_error_response(
            "Test error", skill_name="test_skill", context="test_context"
        )

        assert error_response["success"] is False
        assert error_response["error"] == "Test error"
        assert error_response["error_details"]["skill_name"] == "test_skill"
        assert "timestamp" in error_response


class TestIntegrationPoints:
    """Test integration between components."""

    @pytest.mark.asyncio
    async def test_agent_skills_manager_integration(self, wave_agent, sample_context):
        """Test integration between agent and skills manager."""
        message = "Analyze my recovery status"

        # Verify skills manager is properly initialized
        assert wave_agent.skills_manager is not None
        assert hasattr(wave_agent.skills_manager, "process_message")

        # Mock the skills manager response
        wave_agent.skills_manager.process_message = AsyncMock(
            return_value={
                "success": True,
                "skill": "recovery_analytics_fusion",
                "analysis": "test_analysis",
            }
        )

        result = await wave_agent._run_async_impl(message, sample_context)

        # Verify skills manager was called
        wave_agent.skills_manager.process_message.assert_called_once_with(
            message, sample_context
        )
        assert result["success"] is True

    def test_config_dependencies_integration(self, mock_config):
        """Test integration between config and dependencies."""
        # Test that config values are properly used in dependencies
        deps = WaveAnalyticsAgentDependencies.create_default()

        # Verify dependencies can be created with config
        agent = WavePerformanceAnalyticsAgent(deps, mock_config)

        assert agent.config == mock_config
        assert agent.deps == deps
