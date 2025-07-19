"""
Test fixtures for BLAZE Elite Training Strategist tests.
Provides comprehensive fixtures for all testing scenarios.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any

from agents.elite_training_strategist.core.dependencies import BlazeAgentDependencies
from agents.elite_training_strategist.core.config import BlazeAgentConfig
from agents.elite_training_strategist.skills_manager import BlazeSkillsManager
from clients.vertex_ai.client import VertexAIClient
from clients.supabase_client import SupabaseClient
from tools.mcp_toolkit import MCPToolkit


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    client = Mock(spec=VertexAIClient)
    client.generate_response = AsyncMock(return_value="Mocked AI training response")
    return client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    client = Mock(spec=SupabaseClient)

    # Mock database operations
    client.insert = AsyncMock(return_value=[{"id": "test_plan_123"}])
    client.select = AsyncMock(
        return_value=[
            {
                "id": "test_plan_123",
                "plan_data": {"summary": "Test training plan"},
                "created_at": datetime.now().isoformat(),
            }
        ]
    )
    client.update = AsyncMock(return_value=[{"id": "test_athlete_456"}])

    return client


@pytest.fixture
def mock_mcp_toolkit():
    """Mock MCP toolkit for testing."""
    return Mock(spec=MCPToolkit)


@pytest.fixture
def test_config():
    """Test configuration for BLAZE agent."""
    config = BlazeAgentConfig(
        max_response_time=10.0,
        enable_advanced_ai_features=True,
        enable_voice_coaching=True,
        enable_data_encryption=True,
        cache_training_plans=False,  # Disable caching for tests
    )
    return config


@pytest.fixture
def mock_dependencies(mock_gemini_client, mock_supabase_client, mock_mcp_toolkit):
    """Mock dependencies for BLAZE agent."""
    dependencies = Mock(spec=BlazeAgentDependencies)

    # Core services
    dependencies.vertex_ai_client = mock_gemini_client
    dependencies.supabase_client = mock_supabase_client
    dependencies.mcp_toolkit = mock_mcp_toolkit

    # Mock other services
    dependencies.program_classification_service = Mock()
    dependencies.personality_adapter = Mock()

    # Mock skills
    dependencies.workout_voice_guide_skill = Mock()
    dependencies.voice_command_skill = Mock()
    dependencies.audio_feedback_skill = Mock()
    dependencies.advanced_training_plan_skill = Mock()
    dependencies.intelligent_nutrition_skill = Mock()
    dependencies.ai_progress_analysis_skill = Mock()
    dependencies.adaptive_training_skill = Mock()

    return dependencies


@pytest.fixture
def skills_manager(mock_dependencies, test_config):
    """BLAZE skills manager for testing."""
    return BlazeSkillsManager(mock_dependencies, test_config)


@pytest.fixture
def sample_athlete_profile():
    """Sample athlete profile for testing."""
    return {
        "id": "test_athlete_456",
        "age": 28,
        "fitness_level": "intermediate",
        "training_goals": ["strength", "hypertrophy"],
        "weight": 75.0,
        "height": 180.0,
        "injuries": [],
        "equipment_access": ["barbell", "dumbbells", "machines"],
        "program_type": "PRIME",
    }


@pytest.fixture
def sample_training_plan_input(sample_athlete_profile):
    """Sample training plan input for testing."""
    from agents.elite_training_strategist.schemas import GenerateTrainingPlanInput

    return GenerateTrainingPlanInput(
        input_text="Create a 12-week strength training plan",
        user_profile=sample_athlete_profile,
        training_goals=["strength", "hypertrophy"],
        fitness_level="intermediate",
        duration_weeks=12,
        sessions_per_week=4,
        equipment_available=["barbell", "dumbbells", "machines"],
        time_constraints={"max_session_minutes": 90},
        specific_requirements=["focus_on_compound_movements"],
    )


@pytest.fixture
def sample_performance_data():
    """Sample performance data for testing."""
    return {
        "timestamp": datetime.now().isoformat(),
        "heart_rate": 150,
        "power": 250,
        "speed": 12.5,
        "distance": 5000,
        "duration": 3600,
        "rpe": 7,
        "exercise": "squat",
        "weight": 100,
        "reps": 8,
        "sets": 3,
        "notes": "Felt strong today",
    }


@pytest.fixture
def sample_workout_session(sample_athlete_profile):
    """Sample workout session for testing."""
    return {
        "athlete_id": sample_athlete_profile["id"],
        "duration_minutes": 75,
        "exercises_completed": [
            {
                "name": "squat",
                "weight": 100,
                "reps": 8,
                "sets": 3,
                "rpe": 7,
            },
            {
                "name": "bench_press",
                "weight": 80,
                "reps": 10,
                "sets": 3,
                "rpe": 6,
            },
        ],
        "performance_metrics": {
            "average_heart_rate": 145,
            "max_heart_rate": 165,
            "total_volume": 2400,
        },
        "rpe": 7,
        "notes": "Good session, felt strong",
    }


@pytest.fixture
def sample_biometric_data():
    """Sample biometric data for testing."""
    return {
        "heart_rate": 65,
        "heart_rate_variability": 45,
        "sleep_score": 85,
        "recovery_score": 78,
        "strain": 12.5,
        "readiness": 82,
        "device_type": "whoop",
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def sample_context(sample_athlete_profile):
    """Sample request context for testing."""
    return {
        "user_profile": sample_athlete_profile,
        "duration_weeks": 12,
        "sessions_per_week": 4,
        "time_constraints": {"max_session_minutes": 90},
        "specific_requirements": ["focus_on_compound_movements"],
        "program_type": "PRIME",
    }


@pytest.fixture
def invalid_athlete_data():
    """Invalid athlete data for security testing."""
    return {
        "age": -5,  # Invalid age
        "fitness_level": "invalid_level",  # Invalid fitness level
        "training_goals": [],  # Empty goals
        "weight": 500,  # Invalid weight
        "height": 50,  # Invalid height
    }


@pytest.fixture
def sample_nutrition_data():
    """Sample nutrition data for integration testing."""
    return {
        "total_calories": 2200,
        "protein_g": 120,
        "carbs_g": 250,
        "fat_g": 75,
        "fiber_g": 35,
        "vitamin_d_mcg": 15,
        "omega_3_g": 2.5,
        "fluid_intake_ml": 2800,
        "meal_timing": [
            {"time": "07:00", "calories": 500},
            {"time": "12:00", "calories": 700},
            {"time": "15:00", "calories": 300},
            {"time": "19:00", "calories": 700},
        ],
    }


@pytest.fixture
def sample_device_params():
    """Sample device connection parameters."""
    return {
        "apple_watch": {"health_kit_enabled": True},
        "whoop": {"api_token": "test_whoop_token"},
        "oura_ring": {"access_token": "test_oura_token"},
        "garmin": {"connect_iq_key": "test_garmin_key"},
    }


@pytest.fixture
def mock_ai_responses():
    """Mock AI responses for different scenarios."""
    return {
        "training_plan": """
        Based on your profile and goals, here's a comprehensive 12-week strength training plan:
        
        Phase 1 (Weeks 1-4): Foundation Building
        - Focus on movement quality and base strength
        - 4 sessions per week, 60-75 minutes each
        - Compound movements: squat, deadlift, bench press, row
        
        Phase 2 (Weeks 5-8): Strength Development
        - Increase intensity to 80-85% 1RM
        - Progressive overload focus
        - Add accessory movements for weak points
        
        Phase 3 (Weeks 9-12): Peak Strength
        - High intensity training 85-95% 1RM
        - Competition prep focus
        - Deload in week 11, test maxes in week 12
        """,
        "performance_analysis": """
        Performance Analysis Summary:
        
        Strengths:
        - Excellent strength progression (+15% over 3 months)
        - Consistent training adherence (90%+ sessions completed)
        - Good recovery metrics (HRV stable)
        
        Areas for Improvement:
        - Endurance capacity below average for fitness level
        - Mobility limitations in hip flexors and shoulders
        - Sleep quality inconsistent (average 6.5 hours)
        
        Recommendations:
        1. Add 2 conditioning sessions per week
        2. Daily mobility routine (15 minutes)
        3. Sleep hygiene optimization
        """,
        "exercise_prescription": """
        Exercise Routine for Strength Focus:
        
        Primary Routine (4 exercises, 75 minutes):
        1. Back Squat: 4 sets x 6-8 reps @ 80-85% 1RM
        2. Bench Press: 4 sets x 6-8 reps @ 80-85% 1RM
        3. Bent-Over Row: 3 sets x 8-10 reps @ 75-80% 1RM
        4. Romanian Deadlift: 3 sets x 10-12 reps @ 70-75% 1RM
        
        Rest periods: 3-4 minutes between sets
        Progression: Increase weight by 2.5kg when all reps completed
        """,
    }


@pytest.fixture
def sample_training_plan_artifact():
    """Sample training plan artifact for testing."""
    from agents.elite_training_strategist.schemas import TrainingPlanArtifact

    return TrainingPlanArtifact(
        plan_id="test_plan_123",
        athlete_profile={"id": "test_athlete_456", "fitness_level": "intermediate"},
        plan_overview={
            "duration_weeks": 12,
            "sessions_per_week": 4,
            "primary_goals": ["strength", "hypertrophy"],
        },
        weekly_structure=[
            {"week": 1, "focus": "adaptation", "intensity": "moderate"},
            {"week": 2, "focus": "progression", "intensity": "moderate"},
        ],
        progression_strategy={
            "strength": "linear_progression",
            "volume": "weekly_increase_10_percent",
        },
        exercise_library=[
            {
                "name": "squat",
                "category": "compound",
                "muscle_groups": ["quads", "glutes"],
            },
            {
                "name": "bench_press",
                "category": "compound",
                "muscle_groups": ["chest", "triceps"],
            },
        ],
        periodization={
            "phase_1": {"weeks": "1-4", "focus": "foundation"},
            "phase_2": {"weeks": "5-8", "focus": "development"},
            "phase_3": {"weeks": "9-12", "focus": "peak"},
        },
        created_at=datetime.now().isoformat(),
    )


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Utility fixtures for common test patterns


@pytest.fixture
def assert_training_plan_valid():
    """Utility function to validate training plan structure."""

    def _validate(training_plan):
        assert "duration_weeks" in training_plan
        assert "sessions_per_week" in training_plan
        assert "weekly_structure" in training_plan
        assert "progression_strategy" in training_plan
        assert "exercise_library" in training_plan
        assert training_plan["duration_weeks"] > 0
        assert training_plan["sessions_per_week"] > 0

    return _validate


@pytest.fixture
def assert_performance_analysis_valid():
    """Utility function to validate performance analysis structure."""

    def _validate(analysis):
        assert "performance_summary" in analysis
        assert "strength_analysis" in analysis
        assert "improvement_areas" in analysis
        assert "recommendations" in analysis
        assert len(analysis["recommendations"]) > 0

    return _validate


@pytest.fixture
def mock_circuit_breaker():
    """Mock circuit breaker for service testing."""
    circuit_breaker = Mock()
    circuit_breaker.call = AsyncMock(
        side_effect=lambda func, *args, **kwargs: func(*args, **kwargs)
    )
    circuit_breaker.is_open = False
    circuit_breaker.failure_count = 0
    return circuit_breaker
