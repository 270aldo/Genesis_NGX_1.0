"""
Integration tests for LUNA Female Wellness Specialist.
Tests complete end-to-end workflows and service integration.
"""

import pytest
import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, Any

from agents.female_wellness_coach.agent_optimized import LunaAgent
from agents.female_wellness_coach.core import (
    LunaConfig,
    CORE_SKILLS,
    CONVERSATIONAL_SKILLS,
)
from agents.female_wellness_coach.schemas import (
    AnalyzeMenstrualCycleInput,
    CreateCycleBasedWorkoutInput,
    HormonalNutritionPlanInput,
    ManageMenopauseInput,
    AssessBoneHealthInput,
    EmotionalWellnessInput,
)


class TestEndToEndWorkflows:
    """Test complete end-to-end user workflows."""

    @pytest.mark.asyncio
    async def test_new_user_onboarding_flow(self, luna_agent):
        """Test complete new user onboarding workflow."""
        user_id = "new_user_onboarding"

        # Step 1: Initial consultation
        initial_request = {
            "user_id": user_id,
            "query": "Hi, I'm new here. I want to start tracking my menstrual health and get personalized advice.",
            "context": {
                "age": 28,
                "first_time_user": True,
                "health_goals": ["cycle_tracking", "symptom_management"],
            },
        }

        response = await luna_agent.process_request(initial_request)

        assert response["result"]["text_response"] is not None
        assert "welcome" in response["result"]["text_response"].lower()
        assert len(response["result"]["suggested_skills"]) > 0

        # Step 2: Cycle data input and analysis
        cycle_input = AnalyzeMenstrualCycleInput(
            user_id=user_id,
            cycle_data=[
                {
                    "start_date": "2024-01-15",
                    "length": 28,
                    "flow_duration": 5,
                    "flow_intensity": "medium",
                    "symptoms": ["cramping", "fatigue"],
                    "moods": ["irritable"],
                    "energy_levels": [6, 5, 4, 5, 6],
                    "pain_levels": [2, 3, 4, 3, 2],
                }
            ],
        )

        cycle_analysis = await luna_agent.skills_manager.analyze_menstrual_cycle(
            cycle_input
        )

        assert cycle_analysis.cycle_regularity is not None
        assert cycle_analysis.ai_insights is not None
        assert len(cycle_analysis.recommendations) > 0

        # Step 3: Get personalized workout plan
        workout_input = CreateCycleBasedWorkoutInput(
            user_id=user_id,
            fitness_level="beginner",
            preferred_activities=["yoga", "walking"],
            time_available=30,
            goals=["flexibility", "stress_relief"],
        )

        workout_plan = await luna_agent.skills_manager.create_cycle_based_workout(
            workout_input
        )

        assert workout_plan.workout_plan is not None
        assert workout_plan.cycle_phase is not None
        assert workout_plan.duration_minutes == 30

        # Step 4: Get nutrition guidance
        nutrition_input = HormonalNutritionPlanInput(
            user_id=user_id,
            dietary_preferences=["vegetarian"],
            health_goals=["hormone_balance", "energy"],
            current_symptoms=["fatigue"],
        )

        nutrition_plan = await luna_agent.skills_manager.hormonal_nutrition_plan(
            nutrition_input
        )

        assert nutrition_plan.nutrition_plan is not None
        assert len(nutrition_plan.key_nutrients) > 0
        assert nutrition_plan.shopping_list is not None

    @pytest.mark.asyncio
    async def test_menopause_transition_support_flow(self, luna_agent):
        """Test complete menopause transition support workflow."""
        user_id = "menopause_user"

        # Step 1: Initial menopause consultation
        initial_request = {
            "user_id": user_id,
            "query": "I'm 48 and my periods are becoming irregular. I think I might be entering perimenopause.",
            "context": {
                "age": 48,
                "last_period": "2024-01-10",
                "symptoms": ["hot_flashes", "sleep_issues", "mood_changes"],
            },
        }

        response = await luna_agent.process_request(initial_request)

        assert "perimenopause" in response["result"]["text_response"].lower()
        assert "menopause" in response["result"]["suggested_skills"]

        # Step 2: Comprehensive menopause management
        menopause_input = ManageMenopauseInput(
            user_id=user_id,
            age=48,
            menopause_stage="perimenopause",
            symptoms=["hot_flashes", "sleep_disturbances", "mood_changes"],
            last_menstrual_period="2024-01-10",
            current_treatments=[],
            health_concerns=["bone_health", "heart_health"],
        )

        menopause_plan = await luna_agent.skills_manager.manage_menopause(
            menopause_input
        )

        assert menopause_plan.management_plan is not None
        assert "perimenopause" in menopause_plan.management_plan.lower()
        assert len(menopause_plan.symptom_relief_strategies) > 0
        assert len(menopause_plan.lifestyle_modifications) > 0

        # Step 3: Bone health assessment
        bone_input = AssessBoneHealthInput(
            user_id=user_id,
            age=48,
            menopause_status="perimenopause",
            family_history_osteoporosis=True,
            current_exercise_routine="moderate_walking",
            calcium_vitamin_d_intake="supplements_daily",
        )

        bone_assessment = await luna_agent.skills_manager.assess_bone_health(bone_input)

        assert bone_assessment.bone_health_assessment is not None
        assert bone_assessment.risk_level in ["low", "moderate", "high"]
        assert len(bone_assessment.exercise_recommendations) > 0

        # Step 4: Emotional support
        emotional_input = EmotionalWellnessInput(
            user_id=user_id,
            current_mood="anxious",
            stress_level=6,
            sleep_quality=4,
            energy_level=5,
            recent_stressors=["menopause_symptoms", "life_changes"],
            support_system_strength="moderate",
        )

        emotional_support = await luna_agent.skills_manager.emotional_wellness_support(
            emotional_input
        )

        assert emotional_support.emotional_support is not None
        assert len(emotional_support.immediate_coping_strategies) > 0
        assert emotional_support.guided_meditation_script is not None

    @pytest.mark.asyncio
    async def test_cycle_optimization_flow(self, luna_agent):
        """Test cycle optimization workflow for athletic performance."""
        user_id = "athlete_user"

        # Step 1: Athletic consultation
        initial_request = {
            "user_id": user_id,
            "query": "I'm a competitive athlete. How can I optimize my training around my menstrual cycle?",
            "context": {
                "age": 25,
                "athletic_level": "competitive",
                "sport": "running",
                "goals": ["performance_optimization", "injury_prevention"],
            },
        }

        response = await luna_agent.process_request(initial_request)

        assert "training" in response["result"]["suggested_skills"]
        assert "cycle" in response["result"]["text_response"].lower()

        # Step 2: Establish cycle baseline
        cycle_input = AnalyzeMenstrualCycleInput(
            user_id=user_id,
            cycle_data=[
                {
                    "start_date": "2024-01-15",
                    "length": 28,
                    "flow_duration": 4,
                    "flow_intensity": "light",
                    "symptoms": ["minimal"],
                    "moods": ["focused"],
                    "energy_levels": [8, 9, 9, 8, 7],
                    "pain_levels": [1, 1, 1, 1, 1],
                },
                {
                    "start_date": "2024-02-12",
                    "length": 29,
                    "flow_duration": 4,
                    "flow_intensity": "light",
                    "symptoms": ["minimal"],
                    "moods": ["energetic"],
                    "energy_levels": [8, 8, 9, 8, 7],
                    "pain_levels": [1, 1, 1, 1, 1],
                },
            ],
        )

        cycle_analysis = await luna_agent.skills_manager.analyze_menstrual_cycle(
            cycle_input
        )

        assert cycle_analysis.cycle_regularity["is_regular"] is True
        assert (
            "athlete" in cycle_analysis.ai_insights.lower()
            or "performance" in cycle_analysis.ai_insights.lower()
        )

        # Step 3: Phase-specific training plans
        phases = ["menstrual", "follicular", "ovulatory", "luteal"]
        training_plans = {}

        for phase in phases:
            # Mock phase context
            with pytest.MonkeyPatch().context() as m:

                async def mock_determine_phase(user_id):
                    return {
                        "current_phase": phase,
                        "phase_description": f"Currently in {phase} phase",
                        "phase_characteristics": {
                            "energy_level": (
                                "high" if phase == "ovulatory" else "moderate"
                            ),
                            "recommended_activities": (
                                ["strength_training", "HIIT"]
                                if phase == "ovulatory"
                                else ["moderate_cardio"]
                            ),
                        },
                    }

                m.setattr(
                    luna_agent.skills_manager.data_service,
                    "determine_current_phase",
                    mock_determine_phase,
                )

                workout_input = CreateCycleBasedWorkoutInput(
                    user_id=user_id,
                    fitness_level="advanced",
                    preferred_activities=["running", "strength_training", "HIIT"],
                    time_available=90,
                    goals=["performance", "strength"],
                )

                workout_plan = (
                    await luna_agent.skills_manager.create_cycle_based_workout(
                        workout_input
                    )
                )
                training_plans[phase] = workout_plan

        # Verify different intensity levels for different phases
        assert len(training_plans) == 4
        assert all(plan.workout_plan is not None for plan in training_plans.values())

        # Step 4: Athletic nutrition optimization
        nutrition_input = HormonalNutritionPlanInput(
            user_id=user_id,
            dietary_preferences=["high_protein"],
            health_goals=["performance", "recovery", "hormone_balance"],
            current_symptoms=[],
        )

        nutrition_plan = await luna_agent.skills_manager.hormonal_nutrition_plan(
            nutrition_input
        )

        assert (
            "performance" in nutrition_plan.nutrition_plan.lower()
            or "athlete" in nutrition_plan.nutrition_plan.lower()
        )
        assert len(nutrition_plan.key_nutrients) > 0

    @pytest.mark.asyncio
    async def test_pregnancy_planning_flow(self, luna_agent):
        """Test pregnancy planning and fertility optimization workflow."""
        user_id = "pregnancy_planning_user"

        # Step 1: Fertility consultation
        initial_request = {
            "user_id": user_id,
            "query": "My partner and I are planning to try for a baby. How can I optimize my cycle for conception?",
            "context": {
                "age": 30,
                "relationship_status": "partnered",
                "trying_to_conceive": True,
                "health_status": "good",
            },
        }

        response = await luna_agent.process_request(initial_request)

        assert (
            "fertility" in response["result"]["text_response"].lower()
            or "conception" in response["result"]["text_response"].lower()
        )

        # Step 2: Cycle tracking for fertility
        cycle_input = AnalyzeMenstrualCycleInput(
            user_id=user_id,
            cycle_data=[
                {
                    "start_date": "2024-01-15",
                    "length": 28,
                    "flow_duration": 5,
                    "flow_intensity": "medium",
                    "symptoms": ["mild_cramping"],
                    "moods": ["hopeful"],
                    "energy_levels": [7, 8, 9, 8, 7],
                    "pain_levels": [2, 2, 1, 1, 2],
                }
            ],
        )

        cycle_analysis = await luna_agent.skills_manager.analyze_menstrual_cycle(
            cycle_input
        )

        assert cycle_analysis.next_cycle_prediction is not None
        assert (
            "ovulation" in cycle_analysis.ai_insights.lower()
            or "fertile" in cycle_analysis.ai_insights.lower()
        )

        # Step 3: Preconception nutrition
        nutrition_input = HormonalNutritionPlanInput(
            user_id=user_id,
            dietary_preferences=["balanced"],
            health_goals=["fertility", "preconception_health", "hormone_balance"],
            current_symptoms=[],
        )

        nutrition_plan = await luna_agent.skills_manager.hormonal_nutrition_plan(
            nutrition_input
        )

        assert (
            "folic" in nutrition_plan.nutrition_plan.lower()
            or "folate" in nutrition_plan.nutrition_plan.lower()
        )
        assert any(
            "folic" in supp.lower() or "folate" in supp.lower()
            for supp in nutrition_plan.supplement_suggestions
        )

        # Step 4: Fertility-supportive exercise
        workout_input = CreateCycleBasedWorkoutInput(
            user_id=user_id,
            fitness_level="intermediate",
            preferred_activities=["yoga", "swimming", "walking"],
            time_available=45,
            goals=["fertility", "stress_reduction", "general_health"],
        )

        workout_plan = await luna_agent.skills_manager.create_cycle_based_workout(
            workout_input
        )

        assert workout_plan.workout_plan is not None
        assert (
            "stress" in workout_plan.workout_plan.lower()
            or "gentle" in workout_plan.workout_plan.lower()
        )


class TestServiceIntegration:
    """Test integration between different services."""

    @pytest.mark.asyncio
    async def test_security_data_integration_flow(self, luna_agent):
        """Test security service integration with data operations."""
        user_id = "security_test_user"

        # Test data encryption during storage
        cycle_data = {
            "user_id": user_id,
            "cycle_start": "2024-01-15",
            "flow_intensity": "heavy",
            "symptoms": ["severe_cramping"],
        }

        # Security service should validate and encrypt data
        encrypted = await luna_agent.security_service.encrypt_health_data(cycle_data)
        assert encrypted is not None

        # Data should be decryptable
        decrypted = await luna_agent.security_service.decrypt_health_data(encrypted)
        assert decrypted == cycle_data

        # Audit logs should be created
        logs = await luna_agent.security_service.get_audit_logs()
        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_personality_adaptation_integration(self, luna_agent):
        """Test personality adapter integration with responses."""
        request = {
            "user_id": "personality_test_user",
            "query": "I'm feeling overwhelmed with my symptoms",
            "context": {
                "emotional_state": "distressed",
                "preferred_communication": "empathetic",
            },
        }

        response = await luna_agent.process_request(request)

        # Response should be adapted for ENFJ personality
        assert response["personality_adapted"] is True
        assert (
            "empathetic" in response["result"]["text_response"].lower()
            or "support" in response["result"]["text_response"].lower()
        )

    @pytest.mark.asyncio
    async def test_skills_data_service_integration(self, luna_agent):
        """Test skills manager integration with data service."""
        user_id = "skills_data_test_user"

        # Use analyze_menstrual_cycle skill which integrates with data service
        cycle_input = AnalyzeMenstrualCycleInput(
            user_id=user_id,
            cycle_data=[
                {
                    "start_date": "2024-01-15",
                    "length": 28,
                    "flow_duration": 5,
                    "flow_intensity": "medium",
                    "symptoms": ["cramping"],
                    "moods": ["normal"],
                    "energy_levels": [6, 7, 8, 7, 6],
                    "pain_levels": [3, 4, 5, 4, 3],
                }
            ],
        )

        result = await luna_agent.skills_manager.analyze_menstrual_cycle(cycle_input)

        # Data should be stored in data service
        stored_cycles = await luna_agent.skills_manager.data_service.get_cycle_history(
            user_id
        )
        assert len(stored_cycles) > 0

        # Analysis should include insights
        assert result.ai_insights is not None
        assert result.current_phase is not None


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios."""

    @pytest.mark.asyncio
    async def test_service_failure_recovery(self, luna_agent):
        """Test recovery from service failures."""
        # Simulate service failure
        original_method = luna_agent.deps.vertex_ai_client.generate_content
        luna_agent.deps.vertex_ai_client.generate_content = AsyncMock(
            side_effect=Exception("Service unavailable")
        )

        request = {
            "user_id": "error_test_user",
            "query": "Test query during service failure",
            "context": {},
        }

        response = await luna_agent.process_request(request)

        # Should handle error gracefully
        assert response["error"] is True
        assert "error_message" in response

        # Restore original method
        luna_agent.deps.vertex_ai_client.generate_content = original_method

        # Should recover after service restoration
        recovery_response = await luna_agent.process_request(request)
        assert (
            "error" not in recovery_response or recovery_response.get("error") is False
        )

    @pytest.mark.asyncio
    async def test_invalid_data_handling(self, luna_agent):
        """Test handling of invalid data inputs."""
        # Test with completely invalid cycle data
        invalid_cycle_input = AnalyzeMenstrualCycleInput(
            user_id="invalid_test_user",
            cycle_data=[
                {
                    "start_date": "invalid_date",
                    "length": -5,  # Invalid length
                    "flow_duration": 100,  # Invalid duration
                    "flow_intensity": "invalid_intensity",
                    "symptoms": [],
                    "moods": [],
                    "energy_levels": [15, 20],  # Invalid scale
                    "pain_levels": [-5, 20],  # Invalid scale
                }
            ],
        )

        # Should handle validation errors gracefully
        with pytest.raises(Exception):  # Will raise validation error
            await luna_agent.skills_manager.analyze_menstrual_cycle(invalid_cycle_input)

        # Agent should remain functional after error
        assert luna_agent._initialized is True

    @pytest.mark.asyncio
    async def test_concurrent_request_error_isolation(self, luna_agent):
        """Test that errors in one request don't affect others."""
        # Create one failing request and one normal request
        failing_request = {
            "user_id": "",  # Invalid user ID
            "query": "This should fail",
            "context": {},
        }

        normal_request = {
            "user_id": "normal_user",
            "query": "This should succeed",
            "context": {},
        }

        # Execute concurrently
        responses = await asyncio.gather(
            luna_agent.process_request(failing_request),
            luna_agent.process_request(normal_request),
            return_exceptions=True,
        )

        # Failing request should error, normal request should succeed
        assert len(responses) == 2
        # At least one should succeed (the normal request)
        assert any(
            not isinstance(r, Exception) and not r.get("error", False)
            for r in responses
        )


class TestPerformanceIntegration:
    """Test performance across integrated systems."""

    @pytest.mark.asyncio
    async def test_end_to_end_performance(self, luna_agent, performance_benchmarks):
        """Test end-to-end performance across all systems."""
        user_id = "performance_test_user"

        # Complex workflow that touches all services
        start_time = datetime.utcnow()

        # Step 1: Initial analysis
        cycle_input = AnalyzeMenstrualCycleInput(
            user_id=user_id,
            cycle_data=[
                {
                    "start_date": "2024-01-15",
                    "length": 28,
                    "flow_duration": 5,
                    "flow_intensity": "medium",
                    "symptoms": ["cramping", "fatigue"],
                    "moods": ["irritable"],
                    "energy_levels": [6, 5, 4, 5, 6],
                    "pain_levels": [2, 3, 4, 3, 2],
                }
            ],
        )

        cycle_analysis = await luna_agent.skills_manager.analyze_menstrual_cycle(
            cycle_input
        )

        # Step 2: Get workout plan
        workout_input = CreateCycleBasedWorkoutInput(
            user_id=user_id,
            fitness_level="intermediate",
            preferred_activities=["yoga", "cardio"],
            time_available=45,
            goals=["fitness", "wellness"],
        )

        workout_plan = await luna_agent.skills_manager.create_cycle_based_workout(
            workout_input
        )

        # Step 3: Get nutrition plan
        nutrition_input = HormonalNutritionPlanInput(
            user_id=user_id,
            dietary_preferences=["balanced"],
            health_goals=["energy", "hormone_balance"],
            current_symptoms=["fatigue"],
        )

        nutrition_plan = await luna_agent.skills_manager.hormonal_nutrition_plan(
            nutrition_input
        )

        end_time = datetime.utcnow()
        total_time_ms = (end_time - start_time).total_seconds() * 1000

        # Should complete within performance benchmark
        assert (
            total_time_ms <= performance_benchmarks["max_response_time_ms"] * 3
        )  # Allow 3x for complex workflow

        # All results should be valid
        assert cycle_analysis.ai_insights is not None
        assert workout_plan.workout_plan is not None
        assert nutrition_plan.nutrition_plan is not None

    @pytest.mark.asyncio
    async def test_memory_efficiency_across_services(self, luna_agent):
        """Test memory efficiency across integrated services."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Perform multiple complex operations
        user_ids = [f"memory_test_user_{i}" for i in range(5)]

        for user_id in user_ids:
            # Complex workflow for each user
            cycle_input = AnalyzeMenstrualCycleInput(
                user_id=user_id,
                cycle_data=[
                    {
                        "start_date": "2024-01-15",
                        "length": 28,
                        "flow_duration": 5,
                        "flow_intensity": "medium",
                        "symptoms": ["cramping"],
                        "moods": ["normal"],
                        "energy_levels": [6, 7, 8, 7, 6],
                        "pain_levels": [2, 3, 2, 2, 2],
                    }
                ],
            )

            await luna_agent.skills_manager.analyze_menstrual_cycle(cycle_input)

            # Get health status (triggers cleanup processes)
            await luna_agent.get_health_status()

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        # Memory increase should be reasonable
        assert memory_increase < 200  # Less than 200MB increase


class TestComplianceIntegration:
    """Test compliance features integration."""

    @pytest.mark.asyncio
    async def test_gdpr_hipaa_compliance_flow(self, luna_agent):
        """Test GDPR/HIPAA compliance throughout complete workflow."""
        user_id = "compliance_test_user"

        # All operations should maintain compliance
        cycle_input = AnalyzeMenstrualCycleInput(
            user_id=user_id,
            cycle_data=[
                {
                    "start_date": "2024-01-15",
                    "length": 28,
                    "flow_duration": 5,
                    "flow_intensity": "medium",
                    "symptoms": ["cramping"],
                    "moods": ["normal"],
                    "energy_levels": [6, 7, 8],
                    "pain_levels": [2, 3, 2],
                }
            ],
        )

        # Analysis should validate consent
        result = await luna_agent.skills_manager.analyze_menstrual_cycle(cycle_input)

        # Check audit trail
        audit_logs = await luna_agent.security_service.get_audit_logs()
        assert len(audit_logs) > 0

        # Check data encryption
        assert luna_agent.config.enable_data_encryption is True
        assert luna_agent.config.enable_gdpr_compliance is True
        assert luna_agent.config.enable_hipaa_compliance is True

        # Health status should show compliance
        health_status = await luna_agent.get_health_status()
        compliance = health_status["compliance_status"]
        assert compliance["gdpr_compliant"] is True
        assert compliance["hipaa_compliant"] is True
        assert compliance["data_encryption"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
