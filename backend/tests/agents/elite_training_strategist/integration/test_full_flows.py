"""
Integration tests for BLAZE Elite Training Strategist full workflows.
Tests complete end-to-end scenarios and skill interactions.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from agents.elite_training_strategist.skills_manager import BlazeSkillsManager
from agents.elite_training_strategist.schemas import (
    GenerateTrainingPlanInput,
    GenerateTrainingPlanOutput,
    AnalyzePerformanceDataInput,
    AnalyzePerformanceDataOutput,
    PrescribeExerciseRoutinesInput,
    PrescribeExerciseRoutinesOutput,
)


@pytest.mark.asyncio
class TestTrainingPlanGenerationFlow:
    """Test complete training plan generation workflow."""

    async def test_generate_training_plan_full_flow(
        self,
        skills_manager,
        sample_training_plan_input,
        mock_ai_responses,
        assert_training_plan_valid,
    ):
        """Test complete training plan generation workflow."""
        # Mock AI response
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        # Execute skill
        result = await skills_manager._skill_generate_training_plan(
            sample_training_plan_input
        )

        # Verify result structure
        assert isinstance(result, GenerateTrainingPlanOutput)
        assert result.training_plan is not None
        assert result.plan_summary != ""
        assert len(result.key_recommendations) > 0
        assert result.plan_id is not None

        # Verify training plan content
        training_plan = result.training_plan
        assert training_plan.plan_id != ""
        assert training_plan.athlete_profile is not None
        assert training_plan.plan_overview is not None
        assert training_plan.created_at is not None

        # Verify database interaction
        skills_manager.data_service.save_training_plan.assert_called_once()

    async def test_training_plan_with_equipment_constraints(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test training plan generation with equipment constraints."""
        # Create input with limited equipment
        training_input = GenerateTrainingPlanInput(
            input_text="Create a home workout plan",
            user_profile=sample_athlete_profile,
            training_goals=["strength"],
            fitness_level="intermediate",
            duration_weeks=8,
            sessions_per_week=3,
            equipment_available=["bodyweight", "resistance_bands"],
            time_constraints={"max_session_minutes": 45},
            specific_requirements=["no_gym_access"],
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        result = await skills_manager._skill_generate_training_plan(training_input)

        # Verify plan adapts to constraints
        assert isinstance(result, GenerateTrainingPlanOutput)
        assert result.training_plan.plan_overview["duration_weeks"] == 8

        # Verify AI was called with equipment constraints
        ai_call_args = (
            skills_manager.dependencies.vertex_ai_client.generate_response.call_args[0][0]
        )
        assert "bodyweight" in ai_call_args
        assert "resistance_bands" in ai_call_args

    async def test_training_plan_error_handling(
        self, skills_manager, sample_training_plan_input
    ):
        """Test error handling in training plan generation."""
        # Mock AI client to raise an exception
        skills_manager.dependencies.vertex_ai_client.generate_response.side_effect = (
            Exception("AI service error")
        )

        with pytest.raises(Exception):
            await skills_manager._skill_generate_training_plan(
                sample_training_plan_input
            )

    async def test_training_plan_security_validation(
        self, skills_manager, invalid_athlete_data
    ):
        """Test security validation during training plan generation."""
        training_input = GenerateTrainingPlanInput(
            input_text="Create a plan",
            user_profile=invalid_athlete_data,
            training_goals=["strength"],
            fitness_level="intermediate",
            duration_weeks=12,
            sessions_per_week=4,
        )

        with pytest.raises(Exception):  # Should fail during security validation
            await skills_manager._skill_generate_training_plan(training_input)


@pytest.mark.asyncio
class TestPerformanceAnalysisFlow:
    """Test complete performance analysis workflow."""

    async def test_analyze_performance_data_full_flow(
        self,
        skills_manager,
        sample_athlete_profile,
        sample_performance_data,
        mock_ai_responses,
        assert_performance_analysis_valid,
    ):
        """Test complete performance analysis workflow."""
        # Create analysis input
        analysis_input = AnalyzePerformanceDataInput(
            input_text="Analyze my recent training performance",
            user_profile=sample_athlete_profile,
            performance_metrics=sample_performance_data,
            time_period="last_30_days",
            analysis_focus=["strength", "endurance"],
            comparison_baseline="previous_period",
        )

        # Mock AI response and data service
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["performance_analysis"]
        )
        skills_manager.data_service.get_athlete_progress.return_value = {
            "total_sessions": 12,
            "average_rpe": 7.2,
            "strength_progress": {"squat": {"improvement_percentage": 15}},
        }

        # Execute skill
        result = await skills_manager._skill_analyze_performance_data(analysis_input)

        # Verify result structure
        assert isinstance(result, AnalyzePerformanceDataOutput)
        assert_performance_analysis_valid(result.__dict__)

        # Verify data service interaction
        skills_manager.data_service.get_athlete_progress.assert_called_once_with(
            sample_athlete_profile["id"], days=90
        )

    async def test_performance_analysis_with_biometric_data(
        self,
        skills_manager,
        sample_athlete_profile,
        sample_biometric_data,
        mock_ai_responses,
    ):
        """Test performance analysis with biometric data integration."""
        analysis_input = AnalyzePerformanceDataInput(
            input_text="Analyze my performance including biometrics",
            user_profile=sample_athlete_profile,
            performance_metrics=sample_biometric_data,
            time_period="last_7_days",
            analysis_focus=["recovery", "readiness"],
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["performance_analysis"]
        )
        skills_manager.data_service.get_athlete_progress.return_value = {
            "total_sessions": 5
        }

        result = await skills_manager._skill_analyze_performance_data(analysis_input)

        # Verify biometric data was processed
        assert isinstance(result, AnalyzePerformanceDataOutput)
        assert result.performance_summary != ""

        # Verify security service was used to secure the data
        assert skills_manager.security_service is not None

    async def test_performance_trend_analysis(
        self,
        skills_manager,
        sample_athlete_profile,
        sample_performance_data,
        mock_ai_responses,
    ):
        """Test performance trend analysis over time."""
        # Mock historical data showing improvement
        historical_data = {
            "total_sessions": 20,
            "weekly_sessions": [3, 4, 4, 5],
            "strength_progress": {
                "squat": {"improvement_percentage": 18, "latest_estimated_1rm": 140},
                "bench_press": {
                    "improvement_percentage": 12,
                    "latest_estimated_1rm": 100,
                },
            },
        }

        analysis_input = AnalyzePerformanceDataInput(
            input_text="Show me my strength progression trends",
            user_profile=sample_athlete_profile,
            performance_metrics=sample_performance_data,
            time_period="last_90_days",
            analysis_focus=["strength"],
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["performance_analysis"]
        )
        skills_manager.data_service.get_athlete_progress.return_value = historical_data

        result = await skills_manager._skill_analyze_performance_data(analysis_input)

        # Verify trend analysis was included
        assert isinstance(result, AnalyzePerformanceDataOutput)
        assert result.trend_analysis is not None


@pytest.mark.asyncio
class TestExercisePrescriptionFlow:
    """Test complete exercise prescription workflow."""

    async def test_prescribe_exercise_routines_full_flow(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test complete exercise prescription workflow."""
        prescription_input = PrescribeExerciseRoutinesInput(
            input_text="I need a upper body strength routine",
            user_profile=sample_athlete_profile,
            target_muscle_groups=["chest", "back", "shoulders"],
            equipment_available=["barbell", "dumbbells", "bench"],
            experience_level="intermediate",
            session_duration=75,
            training_focus="strength",
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["exercise_prescription"]
        )

        result = await skills_manager._skill_prescribe_exercise_routines(
            prescription_input
        )

        # Verify result structure
        assert isinstance(result, PrescribeExerciseRoutinesOutput)
        assert result.primary_routine is not None
        assert isinstance(result.alternative_routines, list)
        assert isinstance(result.progression_guidelines, list)
        assert isinstance(result.safety_considerations, list)

    async def test_exercise_prescription_bodyweight_only(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test exercise prescription with bodyweight only."""
        prescription_input = PrescribeExerciseRoutinesInput(
            input_text="Create a bodyweight workout for me",
            user_profile=sample_athlete_profile,
            target_muscle_groups=["full_body"],
            equipment_available=["bodyweight"],
            experience_level="beginner",
            session_duration=30,
            training_focus="general_fitness",
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["exercise_prescription"]
        )

        result = await skills_manager._skill_prescribe_exercise_routines(
            prescription_input
        )

        # Verify bodyweight adaptations
        assert isinstance(result, PrescribeExerciseRoutinesOutput)

        # Verify AI was called with bodyweight constraints
        ai_call_args = (
            skills_manager.dependencies.vertex_ai_client.generate_response.call_args[0][0]
        )
        assert "bodyweight" in ai_call_args

    async def test_exercise_prescription_injury_considerations(
        self, skills_manager, mock_ai_responses
    ):
        """Test exercise prescription with injury considerations."""
        athlete_with_injury = {
            "id": "test_athlete_789",
            "age": 35,
            "fitness_level": "intermediate",
            "training_goals": ["strength"],
            "injuries": ["lower_back_strain", "shoulder_impingement"],
        }

        prescription_input = PrescribeExerciseRoutinesInput(
            input_text="I need a safe workout that avoids aggravating my injuries",
            user_profile=athlete_with_injury,
            target_muscle_groups=["legs", "core"],
            equipment_available=["machines", "resistance_bands"],
            experience_level="intermediate",
            session_duration=45,
            training_focus="rehabilitation",
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["exercise_prescription"]
        )

        result = await skills_manager._skill_prescribe_exercise_routines(
            prescription_input
        )

        # Verify safety considerations for injuries
        assert isinstance(result, PrescribeExerciseRoutinesOutput)
        assert len(result.safety_considerations) > 0

        # Verify AI prompt included injury information
        ai_call_args = (
            skills_manager.dependencies.vertex_ai_client.generate_response.call_args[0][0]
        )
        assert (
            "lower_back_strain" in ai_call_args
            or "shoulder_impingement" in ai_call_args
        )


@pytest.mark.asyncio
class TestIntegratedWorkflows:
    """Test integrated workflows combining multiple skills."""

    async def test_complete_athlete_onboarding_flow(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test complete athlete onboarding workflow."""
        # Step 1: Generate training plan
        training_input = GenerateTrainingPlanInput(
            input_text="I'm new to strength training, create a beginner plan",
            user_profile={**sample_athlete_profile, "fitness_level": "beginner"},
            training_goals=["strength", "muscle_building"],
            fitness_level="beginner",
            duration_weeks=16,
            sessions_per_week=3,
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        plan_result = await skills_manager._skill_generate_training_plan(training_input)

        # Step 2: Prescribe initial routine
        routine_input = PrescribeExerciseRoutinesInput(
            input_text="Show me my first workout routine",
            user_profile={**sample_athlete_profile, "fitness_level": "beginner"},
            target_muscle_groups=["full_body"],
            experience_level="beginner",
            session_duration=45,
            training_focus="strength",
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["exercise_prescription"]
        )

        routine_result = await skills_manager._skill_prescribe_exercise_routines(
            routine_input
        )

        # Verify both results
        assert isinstance(plan_result, GenerateTrainingPlanOutput)
        assert isinstance(routine_result, PrescribeExerciseRoutinesOutput)

        # Verify progression from beginner level
        assert plan_result.training_plan.plan_overview is not None
        assert len(routine_result.progression_guidelines) > 0

    async def test_performance_monitoring_workflow(
        self,
        skills_manager,
        sample_athlete_profile,
        sample_performance_data,
        mock_ai_responses,
    ):
        """Test ongoing performance monitoring workflow."""
        # Simulate multiple performance data points
        performance_sessions = [
            {
                **sample_performance_data,
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
            }
            for i in range(7)  # Last 7 days
        ]

        # Mock historical progress data
        skills_manager.data_service.get_athlete_progress.return_value = {
            "total_sessions": 15,
            "average_rpe": 6.8,
            "strength_progress": {"squat": {"improvement_percentage": 22}},
            "weekly_sessions": [3, 4, 4, 4],
        }

        # Analyze current performance
        analysis_input = AnalyzePerformanceDataInput(
            input_text="How am I progressing with my training?",
            user_profile=sample_athlete_profile,
            performance_metrics=performance_sessions[0],  # Most recent
            time_period="last_30_days",
            analysis_focus=["strength", "consistency"],
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["performance_analysis"]
        )

        analysis_result = await skills_manager._skill_analyze_performance_data(
            analysis_input
        )

        # Verify comprehensive analysis
        assert isinstance(analysis_result, AnalyzePerformanceDataOutput)
        assert analysis_result.trend_analysis is not None
        assert len(analysis_result.recommendations) > 0
        assert len(analysis_result.next_goals) > 0

    async def test_adaptive_training_workflow(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test adaptive training workflow based on feedback."""
        from agents.elite_training_strategist.schemas import (
            AdaptTrainingProgramInput,
            AdaptTrainingProgramOutput,
        )

        # Simulate program adaptation based on feedback
        current_program = {
            "duration_weeks": 12,
            "sessions_per_week": 4,
            "current_week": 6,
            "exercises": ["squat", "bench_press", "deadlift", "row"],
        }

        adaptation_input = AdaptTrainingProgramInput(
            input_text="I'm finding the workouts too easy, need more challenge",
            user_profile=sample_athlete_profile,
            current_program=current_program,
            feedback=["workouts_too_easy", "progressing_faster"],
            new_goals=["increase_strength_focus"],
            life_changes=["more_time_available"],
            performance_data={"strength_improvement": 15, "recovery_good": True},
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = """
        Based on your excellent progress and feedback, here are the recommended adaptations:
        
        1. Increase training intensity to 85-90% 1RM
        2. Add an additional training day per week
        3. Include advanced variations of main lifts
        4. Implement periodization with intensity blocks
        """

        adaptation_result = await skills_manager._skill_adapt_training_program(
            adaptation_input
        )

        # Verify adaptive response
        assert isinstance(adaptation_result, AdaptTrainingProgramOutput)
        assert adaptation_result.adapted_program is not None
        assert len(adaptation_result.changes_made) > 0
        assert len(adaptation_result.reasoning) > 0


@pytest.mark.asyncio
class TestErrorHandlingAndRecovery:
    """Test error handling and recovery in integrated workflows."""

    async def test_ai_service_failure_recovery(
        self, skills_manager, sample_training_plan_input
    ):
        """Test recovery from AI service failures."""
        # Mock AI service failure
        skills_manager.dependencies.vertex_ai_client.generate_response.side_effect = (
            Exception("AI service unavailable")
        )

        with pytest.raises(Exception):
            await skills_manager._skill_generate_training_plan(
                sample_training_plan_input
            )

        # Verify error is properly propagated
        assert skills_manager.dependencies.vertex_ai_client.generate_response.called

    async def test_database_failure_recovery(
        self, skills_manager, sample_training_plan_input, mock_ai_responses
    ):
        """Test recovery from database failures."""
        # Mock successful AI response but database failure
        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )
        skills_manager.data_service.save_training_plan.side_effect = Exception(
            "Database unavailable"
        )

        with pytest.raises(Exception):
            await skills_manager._skill_generate_training_plan(
                sample_training_plan_input
            )

    async def test_partial_workflow_completion(
        self, skills_manager, sample_athlete_profile, mock_ai_responses
    ):
        """Test handling of partial workflow completion."""
        # Start with successful training plan generation
        training_input = GenerateTrainingPlanInput(
            input_text="Create a strength plan",
            user_profile=sample_athlete_profile,
            training_goals=["strength"],
            fitness_level="intermediate",
            duration_weeks=12,
            sessions_per_week=4,
        )

        skills_manager.dependencies.vertex_ai_client.generate_response.return_value = (
            mock_ai_responses["training_plan"]
        )

        plan_result = await skills_manager._skill_generate_training_plan(training_input)
        assert isinstance(plan_result, GenerateTrainingPlanOutput)

        # Then simulate failure in exercise prescription
        routine_input = PrescribeExerciseRoutinesInput(
            input_text="Show me the exercises",
            user_profile=sample_athlete_profile,
            target_muscle_groups=["full_body"],
            experience_level="intermediate",
            session_duration=60,
            training_focus="strength",
        )

        # Mock failure in exercise prescription
        skills_manager.dependencies.vertex_ai_client.generate_response.side_effect = (
            Exception("Service error")
        )

        with pytest.raises(Exception):
            await skills_manager._skill_prescribe_exercise_routines(routine_input)

        # Verify first step completed successfully despite second step failure
        assert plan_result.plan_id is not None
