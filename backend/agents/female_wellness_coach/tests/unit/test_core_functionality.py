"""
Unit tests for LUNA Female Wellness Specialist core functionality.
Tests all 11 skills and core services for A+ level quality assurance.
"""

import pytest
import asyncio
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, Mock, patch

from agents.female_wellness_coach.core import (
    LunaConfig,
    LunaWellnessError,
    LunaValidationError,
    MenstrualCycleAnalysisError,
    CycleBasedTrainingError,
    HormonalNutritionError,
    MenopauseManagementError,
    BoneHealthAssessmentError,
    EmotionalWellnessError,
    VoiceSynthesisError,
)
from agents.female_wellness_coach.agent_optimized import LunaAgent
from agents.female_wellness_coach.skills_manager import LunaSkillsManager
from agents.female_wellness_coach.services import (
    FemaleWellnessSecurityService,
    FemaleWellnessDataService,
    FemaleWellnessIntegrationService,
    CycleData,
)
from agents.female_wellness_coach.schemas import (
    AnalyzeMenstrualCycleInput,
    CreateCycleBasedWorkoutInput,
    HormonalNutritionPlanInput,
    ManageMenopauseInput,
    AssessBoneHealthInput,
    EmotionalWellnessInput,
)


class TestLunaAgentCore:
    """Test LUNA agent core functionality."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, test_config, mock_dependencies):
        """Test agent initialization process."""
        agent = LunaAgent(config=test_config, dependencies=mock_dependencies)

        # Test initialization
        await agent.initialize()

        assert agent._initialized is True
        assert agent.config is not None
        assert agent.deps is not None
        assert len(agent._skills) == 11  # 6 functional + 5 conversational
        assert agent._health_status["initialized"] is True

    @pytest.mark.asyncio
    async def test_agent_configuration_validation(self, mock_dependencies):
        """Test configuration validation."""
        # Test invalid configuration
        invalid_config = LunaConfig(
            enable_gdpr_compliance=False,  # Required for health data
            enable_hipaa_compliance=False,  # Required for health data
        )

        with pytest.raises(ValueError, match="GDPR compliance must be enabled"):
            invalid_config.validate()

    @pytest.mark.asyncio
    async def test_agent_health_status(self, luna_agent):
        """Test agent health status reporting."""
        health_status = await luna_agent.get_health_status()

        assert "agent_metadata" in health_status
        assert "agent_health" in health_status
        assert "services_health" in health_status
        assert "compliance_status" in health_status

        # Check compliance status
        compliance = health_status["compliance_status"]
        assert compliance["gdpr_compliant"] is True
        assert compliance["hipaa_compliant"] is True
        assert compliance["data_encryption"] is True

    @pytest.mark.asyncio
    async def test_visibility_context_determination(self, luna_agent):
        """Test visibility context determination."""
        # Primary specialist context
        context = await luna_agent.determine_visibility_context(
            "I'm having irregular menstrual cycles", {}
        )
        assert context == "primary_specialist"

        # Activated specialist context
        context = await luna_agent.determine_visibility_context(
            "My hormones seem off lately", {}
        )
        assert context == "activated_specialist"

        # Recommended specialist context
        context = await luna_agent.determine_visibility_context(
            "I need nutrition advice for women", {}
        )
        assert context == "recommended_specialist"

    @pytest.mark.asyncio
    async def test_request_processing(self, luna_agent, sample_user_request):
        """Test request processing pipeline."""
        response = await luna_agent.process_request(sample_user_request)

        assert "request_id" in response
        assert response["agent_id"] == "luna_female_wellness_specialist"
        assert "result" in response
        assert "processing_time_ms" in response
        assert response["processing_time_ms"] < 10000  # Should be under 10 seconds


class TestMenstrualCycleAnalysis:
    """Test menstrual cycle analysis functionality."""

    @pytest.mark.asyncio
    async def test_analyze_menstrual_cycle_success(
        self, skills_manager, sample_menstrual_analysis_input
    ):
        """Test successful menstrual cycle analysis."""
        input_data = AnalyzeMenstrualCycleInput(**sample_menstrual_analysis_input)

        result = await skills_manager.analyze_menstrual_cycle(input_data)

        assert result.cycle_regularity is not None
        assert result.current_phase is not None
        assert result.next_cycle_prediction is not None
        assert result.ai_insights is not None
        assert len(result.recommendations) > 0

    @pytest.mark.asyncio
    async def test_analyze_menstrual_cycle_insufficient_data(self, skills_manager):
        """Test analysis with insufficient data."""
        input_data = AnalyzeMenstrualCycleInput(
            user_id="test_user",
            cycle_data=[],  # Empty data
        )

        with pytest.raises(MenstrualCycleAnalysisError):
            await skills_manager.analyze_menstrual_cycle(input_data)

    @pytest.mark.asyncio
    async def test_cycle_pattern_recognition(self, data_service, sample_cycle_data):
        """Test cycle pattern recognition algorithms."""
        user_id = "test_user_patterns"

        # Store multiple cycles
        for cycle in sample_cycle_data:
            await data_service.store_cycle_data(user_id, cycle)

        # Analyze patterns
        analysis = await data_service.analyze_cycle_patterns(user_id)

        assert "cycle_regularity" in analysis
        assert "symptom_analysis" in analysis
        assert "mood_analysis" in analysis
        assert analysis["cycles_analyzed"] == len(sample_cycle_data)

    @pytest.mark.asyncio
    async def test_cycle_prediction_accuracy(self, data_service, sample_cycle_data):
        """Test cycle prediction accuracy."""
        user_id = "test_user_prediction"

        # Store historical cycles
        for cycle in sample_cycle_data:
            await data_service.store_cycle_data(user_id, cycle)

        # Get prediction
        prediction = await data_service.predict_next_cycle(user_id)

        assert "predicted_start_date" in prediction
        assert "confidence_score" in prediction
        assert 0.5 <= prediction["confidence_score"] <= 1.0


class TestCycleBasedTraining:
    """Test cycle-based training functionality."""

    @pytest.mark.asyncio
    async def test_create_cycle_based_workout(
        self, skills_manager, sample_workout_input
    ):
        """Test cycle-based workout creation."""
        input_data = CreateCycleBasedWorkoutInput(**sample_workout_input)

        result = await skills_manager.create_cycle_based_workout(input_data)

        assert result.workout_plan is not None
        assert result.cycle_phase is not None
        assert result.intensity_level in ["low", "moderate", "high"]
        assert result.duration_minutes == sample_workout_input["time_available"]

    @pytest.mark.asyncio
    async def test_intensity_optimization_by_phase(self, skills_manager):
        """Test workout intensity optimization by cycle phase."""
        # Mock different cycle phases
        phase_contexts = [
            {"current_phase": "menstrual"},
            {"current_phase": "follicular"},
            {"current_phase": "ovulatory"},
            {"current_phase": "luteal"},
        ]

        expected_intensities = ["low", "moderate", "high", "moderate"]

        for i, phase_context in enumerate(phase_contexts):
            intensity = skills_manager._calculate_optimal_intensity(phase_context)
            assert intensity == expected_intensities[i]


class TestHormonalNutrition:
    """Test hormonal nutrition functionality."""

    @pytest.mark.asyncio
    async def test_hormonal_nutrition_plan(
        self, skills_manager, sample_nutrition_input
    ):
        """Test hormonal nutrition plan generation."""
        input_data = HormonalNutritionPlanInput(**sample_nutrition_input)

        result = await skills_manager.hormonal_nutrition_plan(input_data)

        assert result.nutrition_plan is not None
        assert result.cycle_phase is not None
        assert len(result.key_nutrients) > 0
        assert len(result.foods_to_emphasize) > 0
        assert result.plan_duration_days == 7

    @pytest.mark.asyncio
    async def test_phase_specific_nutrients(self, skills_manager):
        """Test phase-specific nutrient recommendations."""
        phases = ["menstrual", "follicular", "ovulatory", "luteal"]

        for phase in phases:
            nutrients = skills_manager._get_phase_nutrients(phase)
            assert len(nutrients) > 0
            assert isinstance(nutrients, list)

    @pytest.mark.asyncio
    async def test_dietary_restriction_handling(self, skills_manager):
        """Test handling of dietary restrictions."""
        input_data = HormonalNutritionPlanInput(
            user_id="test_user",
            dietary_preferences=["vegan", "gluten_free"],
            allergies=["nuts", "soy"],
            health_goals=["hormone_balance"],
            current_symptoms=["fatigue"],
        )

        result = await skills_manager.hormonal_nutrition_plan(input_data)

        # Plan should accommodate restrictions
        assert result.nutrition_plan is not None
        assert len(result.supplement_suggestions) > 0


class TestMenopauseManagement:
    """Test menopause management functionality."""

    @pytest.mark.asyncio
    async def test_manage_menopause(self, skills_manager, sample_menopause_input):
        """Test menopause management plan creation."""
        input_data = ManageMenopauseInput(**sample_menopause_input)

        result = await skills_manager.manage_menopause(input_data)

        assert result.management_plan is not None
        assert result.menopause_stage == "perimenopause"
        assert len(result.symptom_relief_strategies) > 0
        assert len(result.lifestyle_modifications) > 0
        assert len(result.red_flags) > 0

    @pytest.mark.asyncio
    async def test_menopause_stage_specific_guidance(self, skills_manager):
        """Test stage-specific menopause guidance."""
        stages = ["perimenopause", "menopause", "postmenopause"]

        for stage in stages:
            input_data = ManageMenopauseInput(
                user_id="test_user",
                age=50,
                menopause_stage=stage,
                symptoms=["hot_flashes"],
                last_menstrual_period="2023-12-01",
                current_treatments=[],
                health_concerns=[],
            )

            result = await skills_manager.manage_menopause(input_data)
            assert result.menopause_stage == stage


class TestBoneHealthAssessment:
    """Test bone health assessment functionality."""

    @pytest.mark.asyncio
    async def test_assess_bone_health(self, skills_manager, sample_bone_health_input):
        """Test bone health assessment."""
        input_data = AssessBoneHealthInput(**sample_bone_health_input)

        result = await skills_manager.assess_bone_health(input_data)

        assert result.bone_health_assessment is not None
        assert result.risk_level in ["low", "moderate", "high"]
        assert len(result.risk_factors) >= 0
        assert len(result.exercise_recommendations) > 0
        assert len(result.supplement_recommendations) > 0

    @pytest.mark.asyncio
    async def test_risk_factor_calculation(self, skills_manager):
        """Test bone health risk factor calculation."""
        # High risk scenario
        high_risk_input = AssessBoneHealthInput(
            user_id="test_user",
            age=65,
            menopause_status="postmenopause",
            family_history_osteoporosis=True,
            current_exercise_routine="sedentary",
            calcium_vitamin_d_intake="insufficient",
            medical_history=["corticosteroid_use"],
            fracture_history=True,
        )

        risk_score = skills_manager._calculate_bone_health_risk(high_risk_input)
        assert risk_score > 0.5  # Should indicate higher risk


class TestEmotionalWellness:
    """Test emotional wellness functionality."""

    @pytest.mark.asyncio
    async def test_emotional_wellness_support(
        self, skills_manager, sample_emotional_wellness_input
    ):
        """Test emotional wellness support."""
        input_data = EmotionalWellnessInput(**sample_emotional_wellness_input)

        result = await skills_manager.emotional_wellness_support(input_data)

        assert result.emotional_support is not None
        assert result.cycle_mood_connection is not None
        assert len(result.immediate_coping_strategies) > 0
        assert len(result.professional_help_indicators) > 0

    @pytest.mark.asyncio
    async def test_stress_management_plan_creation(self, skills_manager):
        """Test stress management plan creation."""
        input_data = EmotionalWellnessInput(
            user_id="test_user",
            current_mood="stressed",
            stress_level=8,
            sleep_quality=3,
            energy_level=2,
            recent_stressors=["work", "relationships"],
            support_system_strength="weak",
        )

        result = await skills_manager.emotional_wellness_support(input_data)
        stress_plan = result.stress_management_plan

        assert stress_plan is not None
        # Should provide appropriate strategies for high stress


class TestVoiceConversationalSkills:
    """Test voice-enabled conversational skills."""

    @pytest.mark.asyncio
    async def test_menstrual_conversation(self, skills_manager):
        """Test menstrual health conversation."""
        from agents.female_wellness_coach.schemas import StartMenstrualConversationInput

        input_data = StartMenstrualConversationInput(
            conversation_topic="cycle_irregularities",
            user_concern="periods are coming every 35 days instead of 28",
        )

        result = await skills_manager.start_menstrual_conversation(input_data)

        assert result.conversation_response is not None
        assert len(result.follow_up_questions) > 0

    @pytest.mark.asyncio
    async def test_hormonal_guidance_conversation(self, skills_manager):
        """Test hormonal guidance conversation."""
        from agents.female_wellness_coach.schemas import (
            HormonalGuidanceConversationInput,
        )

        input_data = HormonalGuidanceConversationInput(
            life_stage="reproductive_years",
            hormonal_question="Why do I feel so tired during my luteal phase?",
        )

        result = await skills_manager.hormonal_guidance_conversation(input_data)

        assert result.guidance_response is not None
        assert len(result.educational_resources) > 0

    @pytest.mark.asyncio
    async def test_voice_synthesis_integration(self, integration_service):
        """Test voice synthesis integration."""
        text = "Hello, I'm here to support your wellness journey."

        # Note: In tests, voice synthesis is disabled, so this returns None
        audio_data = await integration_service.synthesize_voice_response(text)

        # In test environment, should return None (voice disabled)
        assert audio_data is None


class TestSecurityAndCompliance:
    """Test security and compliance features."""

    @pytest.mark.asyncio
    async def test_data_encryption(self, security_service):
        """Test health data encryption."""
        test_data = {
            "user_id": "test_user",
            "cycle_start": "2024-01-15",
            "symptoms": ["cramping", "fatigue"],
        }

        # Encrypt data
        encrypted = await security_service.encrypt_health_data(test_data)
        assert encrypted is not None
        assert encrypted != str(test_data)

        # Decrypt data
        decrypted = await security_service.decrypt_health_data(encrypted)
        assert decrypted == test_data

    @pytest.mark.asyncio
    async def test_consent_validation(self, security_service):
        """Test health data consent validation."""
        # Valid consent
        consent_valid = await security_service.validate_health_data_consent(
            "test_user", "menstrual_cycle", "analyze"
        )
        assert consent_valid is True

    @pytest.mark.asyncio
    async def test_audit_logging(self, security_service):
        """Test audit logging functionality."""
        # Perform an operation that should be logged
        await security_service._log_data_access(
            "test_operation",
            {
                "user_id": "test_user",
                "operation": "data_access",
            },
        )

        # Check audit logs
        logs = await security_service.get_audit_logs()
        assert len(logs) > 0
        assert any(log["action"] == "test_operation" for log in logs)

    @pytest.mark.asyncio
    async def test_menstrual_data_protection(self, security_service):
        """Test special menstrual data protection."""
        cycle_data = {
            "flow_intensity": "heavy",
            "pain_levels": [8, 7, 6],
            "mood_patterns": ["anxious", "sad"],
        }

        access_valid = await security_service.validate_menstrual_data_access(
            "test_user", cycle_data
        )
        assert access_valid is True


class TestDataService:
    """Test data service functionality."""

    @pytest.mark.asyncio
    async def test_cycle_data_validation(self, data_service):
        """Test cycle data validation."""
        # Valid cycle data
        valid_cycle = CycleData(
            cycle_start=date(2024, 1, 15),
            cycle_length=28,
            flow_duration=5,
            flow_intensity="medium",
            symptoms=[],
            mood_patterns=[],
            energy_levels=[5, 6, 7],
            pain_levels=[2, 3, 2],
        )

        # Should not raise exception
        await data_service._validate_cycle_data(valid_cycle)

        # Invalid cycle data (cycle too short)
        invalid_cycle = CycleData(
            cycle_start=date(2024, 1, 15),
            cycle_length=15,  # Too short
            flow_duration=5,
            flow_intensity="medium",
            symptoms=[],
            mood_patterns=[],
            energy_levels=[5],
            pain_levels=[2],
        )

        with pytest.raises(LunaValidationError):
            await data_service._validate_cycle_data(invalid_cycle)

    @pytest.mark.asyncio
    async def test_data_storage_and_retrieval(self, data_service, sample_cycle_data):
        """Test data storage and retrieval."""
        user_id = "test_user_storage"

        # Store cycle data
        for cycle in sample_cycle_data:
            await data_service.store_cycle_data(user_id, cycle)

        # Retrieve cycle history
        history = await data_service.get_cycle_history(user_id, months=6)

        assert len(history) == len(sample_cycle_data)
        assert all(isinstance(cycle, CycleData) for cycle in history)

    @pytest.mark.asyncio
    async def test_current_phase_determination(self, data_service, sample_cycle_data):
        """Test current cycle phase determination."""
        user_id = "test_user_phase"

        # Store recent cycle
        recent_cycle = CycleData(
            cycle_start=date.today() - timedelta(days=10),  # 10 days ago
            cycle_length=28,
            flow_duration=5,
            flow_intensity="medium",
            symptoms=[],
            mood_patterns=[],
            energy_levels=[5],
            pain_levels=[2],
        )

        await data_service.store_cycle_data(user_id, recent_cycle)

        # Determine current phase
        current_phase = await data_service.determine_current_phase(user_id)

        assert "current_phase" in current_phase
        assert current_phase["current_phase"] in [
            "menstrual",
            "follicular",
            "ovulatory",
            "luteal",
        ]


class TestIntegrationService:
    """Test integration service functionality."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, integration_service):
        """Test circuit breaker pattern."""
        service_name = "test_service"

        # Initialize circuit breaker
        integration_service._circuit_breakers[service_name] = {
            "state": "closed",
            "failure_count": 0,
            "last_failure": None,
            "timeout": 60,
        }

        # Should allow requests when closed
        allowed = await integration_service._check_circuit_breaker(service_name)
        assert allowed is True

        # Simulate failures to open circuit
        for _ in range(3):
            await integration_service._record_failure(service_name)

        # Should block requests when open
        allowed = await integration_service._check_circuit_breaker(service_name)
        assert allowed is False

    @pytest.mark.asyncio
    async def test_data_normalization(self, integration_service):
        """Test external data normalization."""
        # Mock Fitbit data
        mock_fitbit_data = {
            "heart_rate": {"activities-heart": [{"value": {"restingHeartRate": 65}}]},
            "sleep": {"sleep": [{"minutesAsleep": 450}]},  # 7.5 hours
            "activity": {"summary": {"steps": 8500, "caloriesOut": 2000}},
        }

        normalized = await integration_service._normalize_fitbit_data(mock_fitbit_data)

        assert normalized["heart_rate"] == 65
        assert normalized["sleep_hours"] == 7.5
        assert normalized["steps"] == 8500


class TestPerformanceAndReliability:
    """Test performance and reliability requirements."""

    @pytest.mark.asyncio
    async def test_response_time_benchmark(
        self, luna_agent, sample_user_request, performance_benchmarks
    ):
        """Test response time meets benchmark."""
        start_time = datetime.utcnow()

        response = await luna_agent.process_request(sample_user_request)

        end_time = datetime.utcnow()
        response_time_ms = (end_time - start_time).total_seconds() * 1000

        assert response_time_ms <= performance_benchmarks["max_response_time_ms"]
        assert (
            response["processing_time_ms"]
            <= performance_benchmarks["max_response_time_ms"]
        )

    @pytest.mark.asyncio
    async def test_error_handling_resilience(self, skills_manager):
        """Test error handling and resilience."""
        # Test with invalid input
        with pytest.raises(LunaValidationError):
            await skills_manager.analyze_menstrual_cycle(
                AnalyzeMenstrualCycleInput(user_id="", cycle_data=[])
            )

        # Skills manager should still be functional after error
        assert skills_manager._initialized is True

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, luna_agent, sample_user_request):
        """Test handling multiple concurrent requests."""
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            request = sample_user_request.copy()
            request["user_id"] = f"test_user_{i}"
            tasks.append(luna_agent.process_request(request))

        # Execute concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        assert len(responses) == 5
        assert all(not isinstance(r, Exception) for r in responses)

    @pytest.mark.asyncio
    async def test_memory_usage_efficiency(self, luna_agent):
        """Test memory usage efficiency."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Perform multiple operations
        for i in range(10):
            request = {
                "user_id": f"test_user_{i}",
                "query": f"Test query {i}",
                "context": {},
            }
            await luna_agent.process_request(request)

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
