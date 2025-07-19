"""
Test configuration and fixtures for LUNA Female Wellness Specialist.
Provides comprehensive test setup for A+ level testing framework.
"""

import pytest
import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

from agents.female_wellness_coach.core import (
    LunaConfig,
    LunaDependencies,
    create_luna_dependencies,
)
from agents.female_wellness_coach.agent_optimized import LunaAgent
from agents.female_wellness_coach.skills_manager import LunaSkillsManager
from agents.female_wellness_coach.services import (
    FemaleWellnessSecurityService,
    FemaleWellnessDataService,
    FemaleWellnessIntegrationService,
    CycleData,
    HormonalProfile,
    WellnessMetrics,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> LunaConfig:
    """Create test configuration with safe defaults."""
    return LunaConfig(
        # Performance settings
        max_response_time=10.0,  # Shorter for tests
        retry_attempts=1,  # Fewer retries for tests
        cache_ttl=60,  # Shorter cache for tests
        # Security (required for health data)
        enable_audit_logging=True,
        enable_data_encryption=True,
        enable_gdpr_compliance=True,
        enable_hipaa_compliance=True,
        enable_menstrual_data_protection=True,
        # Feature flags
        enable_real_wellness_analysis=False,  # Use mocks in tests
        enable_voice_synthesis=False,  # Disable for tests
        # Debug settings
        debug_mode=True,
        log_level="DEBUG",
    )


@pytest.fixture
def mock_dependencies() -> LunaDependencies:
    """Create mock dependencies for testing."""
    deps = Mock(spec=LunaDependencies)

    # Mock Gemini client
    deps.vertex_ai_client = AsyncMock()
    deps.vertex_ai_client.generate_content = AsyncMock(return_value="Mock AI response")

    # Mock Supabase client
    deps.supabase_client = Mock()

    # Mock personality adapter
    deps.personality_adapter = AsyncMock()
    deps.personality_adapter.initialize_profile = AsyncMock()
    deps.personality_adapter.adapt_response = AsyncMock(return_value="Adapted response")

    # Mock other adapters
    deps.state_manager_adapter = Mock()
    deps.intent_analyzer_adapter = Mock()
    deps.a2a_adapter = Mock()

    # Mock program classification service
    deps.program_classification_service = Mock()

    # Mock MCP toolkit
    deps.mcp_toolkit = Mock()

    return deps


@pytest.fixture
async def luna_agent(
    test_config: LunaConfig, mock_dependencies: LunaDependencies
) -> LunaAgent:
    """Create LUNA agent instance for testing."""
    agent = LunaAgent(config=test_config, dependencies=mock_dependencies)
    await agent.initialize()
    yield agent
    await agent.cleanup()


@pytest.fixture
async def skills_manager(
    test_config: LunaConfig, mock_dependencies: LunaDependencies
) -> LunaSkillsManager:
    """Create skills manager for testing."""
    manager = LunaSkillsManager(mock_dependencies, test_config)
    await manager.initialize()
    return manager


@pytest.fixture
async def security_service(test_config: LunaConfig) -> FemaleWellnessSecurityService:
    """Create security service for testing."""
    service = FemaleWellnessSecurityService(test_config)
    await service.initialize()
    return service


@pytest.fixture
async def data_service(test_config: LunaConfig) -> FemaleWellnessDataService:
    """Create data service for testing."""
    service = FemaleWellnessDataService(test_config)
    await service.initialize()
    return service


@pytest.fixture
async def integration_service(
    test_config: LunaConfig,
) -> FemaleWellnessIntegrationService:
    """Create integration service for testing."""
    service = FemaleWellnessIntegrationService(test_config)
    await service.initialize()
    yield service
    await service.cleanup()


# ======= TEST DATA FIXTURES =======


@pytest.fixture
def sample_cycle_data() -> List[CycleData]:
    """Create sample menstrual cycle data for testing."""
    return [
        CycleData(
            cycle_start=date(2024, 1, 15),
            cycle_length=28,
            flow_duration=5,
            flow_intensity="medium",
            symptoms=["cramping", "fatigue"],
            mood_patterns=["irritable", "sensitive"],
            energy_levels=[6, 5, 4, 3, 4],
            pain_levels=[2, 3, 5, 4, 2],
        ),
        CycleData(
            cycle_start=date(2024, 2, 12),
            cycle_length=29,
            flow_duration=4,
            flow_intensity="light",
            symptoms=["mild_cramping"],
            mood_patterns=["calm", "focused"],
            energy_levels=[7, 6, 5, 6, 7],
            pain_levels=[1, 2, 2, 1, 1],
        ),
        CycleData(
            cycle_start=date(2024, 3, 13),
            cycle_length=27,
            flow_duration=6,
            flow_intensity="heavy",
            symptoms=["severe_cramping", "headache", "fatigue"],
            mood_patterns=["anxious", "sad"],
            energy_levels=[4, 3, 2, 3, 4],
            pain_levels=[6, 7, 8, 6, 4],
        ),
    ]


@pytest.fixture
def sample_hormonal_profile() -> HormonalProfile:
    """Create sample hormonal profile for testing."""
    return HormonalProfile(
        estrogen_levels=45.2,
        progesterone_levels=12.8,
        fsh_levels=5.1,
        lh_levels=8.3,
        testosterone_levels=0.8,
        cycle_phase="follicular",
    )


@pytest.fixture
def sample_wellness_metrics() -> WellnessMetrics:
    """Create sample wellness metrics for testing."""
    return WellnessMetrics(
        sleep_quality=7.5,
        stress_levels=4.2,
        exercise_frequency=4,
        nutrition_quality=8.0,
        hydration_levels=2.8,
    )


@pytest.fixture
def sample_user_request() -> Dict[str, Any]:
    """Create sample user request for testing."""
    return {
        "user_id": "test_user_123",
        "query": "I've been having irregular periods lately. Can you help me understand what might be happening?",
        "context": {
            "age": 28,
            "last_period": "2024-01-15",
            "concerns": ["irregular_cycles", "mood_changes"],
            "preferred_language": "en",
        },
    }


@pytest.fixture
def sample_menstrual_analysis_input() -> Dict[str, Any]:
    """Create sample menstrual cycle analysis input."""
    return {
        "user_id": "test_user_123",
        "cycle_data": [
            {
                "start_date": "2024-01-15",
                "length": 28,
                "flow_duration": 5,
                "flow_intensity": "medium",
                "symptoms": ["cramping", "fatigue"],
                "moods": ["irritable", "sensitive"],
                "energy_levels": [6, 5, 4, 3, 4],
                "pain_levels": [2, 3, 5, 4, 2],
            },
            {
                "start_date": "2024-02-12",
                "length": 29,
                "flow_duration": 4,
                "flow_intensity": "light",
                "symptoms": ["mild_cramping"],
                "moods": ["calm", "focused"],
                "energy_levels": [7, 6, 5, 6, 7],
                "pain_levels": [1, 2, 2, 1, 1],
            },
        ],
        "analysis_preferences": {
            "include_predictions": True,
            "symptom_correlation": True,
            "mood_analysis": True,
        },
    }


@pytest.fixture
def sample_workout_input() -> Dict[str, Any]:
    """Create sample cycle-based workout input."""
    return {
        "user_id": "test_user_123",
        "fitness_level": "intermediate",
        "preferred_activities": ["strength_training", "yoga", "cardio"],
        "time_available": 45,
        "goals": ["strength", "flexibility", "energy"],
        "current_symptoms": ["mild_fatigue"],
        "equipment_available": ["dumbbells", "yoga_mat", "resistance_bands"],
    }


@pytest.fixture
def sample_nutrition_input() -> Dict[str, Any]:
    """Create sample hormonal nutrition input."""
    return {
        "user_id": "test_user_123",
        "dietary_preferences": ["vegetarian"],
        "allergies": ["nuts"],
        "health_goals": ["hormone_balance", "energy_boost"],
        "current_symptoms": ["fatigue", "mood_swings"],
        "meal_prep_preference": "batch_cooking",
        "budget_range": "moderate",
    }


@pytest.fixture
def sample_menopause_input() -> Dict[str, Any]:
    """Create sample menopause management input."""
    return {
        "user_id": "test_user_123",
        "age": 48,
        "menopause_stage": "perimenopause",
        "symptoms": ["hot_flashes", "sleep_disturbances", "mood_changes"],
        "last_menstrual_period": "2024-01-10",
        "current_treatments": ["none"],
        "health_concerns": ["bone_health", "heart_health"],
        "family_history": ["osteoporosis"],
    }


@pytest.fixture
def sample_bone_health_input() -> Dict[str, Any]:
    """Create sample bone health assessment input."""
    return {
        "user_id": "test_user_123",
        "age": 52,
        "menopause_status": "postmenopause",
        "family_history_osteoporosis": True,
        "current_exercise_routine": "walking 3x/week",
        "calcium_vitamin_d_intake": "supplements_daily",
        "medical_history": ["none"],
        "dexa_scan_results": None,
        "fracture_history": False,
    }


@pytest.fixture
def sample_emotional_wellness_input() -> Dict[str, Any]:
    """Create sample emotional wellness input."""
    return {
        "user_id": "test_user_123",
        "current_mood": "anxious",
        "stress_level": 7,
        "sleep_quality": 4,
        "energy_level": 3,
        "recent_stressors": ["work_pressure", "family_issues"],
        "support_system_strength": "moderate",
        "coping_strategies_used": ["meditation", "journaling"],
    }


# ======= MOCK FIXTURES =======


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini AI response."""
    return """
    Based on your menstrual cycle data, I can see some patterns that suggest you're experiencing normal variations within a healthy range. Here are my observations:

    **Cycle Analysis:**
    - Your cycles range from 27-29 days, which is well within normal
    - Flow intensity varies naturally, which is common
    - Symptoms are manageable and typical

    **Recommendations:**
    - Continue tracking your cycles for better pattern recognition
    - Focus on stress management during luteal phase
    - Ensure adequate iron intake during menstruation
    - Consider gentle exercise for symptom relief

    Remember, every woman's cycle is unique, and small variations are completely normal. If you have concerns, always consult with your healthcare provider.
    """


@pytest.fixture
def mock_voice_audio():
    """Mock voice audio data."""
    return b"mock_audio_data_for_testing"


@pytest.fixture
def mock_integration_data():
    """Mock external integration data."""
    return {
        "apple_health": {
            "steps_today": 8543,
            "active_minutes": 45,
            "heart_rate_avg": 72,
        },
        "fitbit": {
            "sleep_hours": 7.5,
            "resting_heart_rate": 65,
            "calories_burned": 1850,
        },
        "clue_app": {
            "cycle_length_avg": 28,
            "last_period": "2024-01-15",
            "predicted_next": "2024-02-12",
        },
    }


# ======= PERFORMANCE FIXTURES =======


@pytest.fixture
def performance_benchmarks():
    """Performance benchmarks for testing."""
    return {
        "max_response_time_ms": 500,
        "target_accuracy": 0.95,
        "max_error_rate": 0.001,
        "target_test_coverage": 0.90,
        "max_memory_usage_mb": 512,
    }


# ======= SECURITY FIXTURES =======


@pytest.fixture
def security_test_data():
    """Security test data and scenarios."""
    return {
        "valid_consent": {
            "user_id": "test_user_123",
            "data_type": "menstrual_cycle",
            "operation": "analyze",
            "consent_granted": True,
            "consent_date": datetime.utcnow().isoformat(),
        },
        "expired_consent": {
            "user_id": "test_user_456",
            "data_type": "menstrual_cycle",
            "operation": "analyze",
            "consent_granted": True,
            "consent_date": (datetime.utcnow() - timedelta(days=200)).isoformat(),
        },
        "no_consent": {
            "user_id": "test_user_789",
            "data_type": "menstrual_cycle",
            "operation": "analyze",
            "consent_granted": False,
        },
    }


# ======= TEST UTILITIES =======


@pytest.fixture
def test_utilities():
    """Test utility functions."""

    class TestUtils:
        @staticmethod
        def assert_response_structure(response: Dict[str, Any]):
            """Assert standard response structure."""
            required_fields = [
                "request_id",
                "agent_id",
                "agent_name",
                "timestamp",
                "result",
            ]
            for field in required_fields:
                assert field in response, f"Missing required field: {field}"

        @staticmethod
        def assert_health_data_compliance(data: Dict[str, Any]):
            """Assert health data compliance requirements."""
            assert "gdpr_compliant" in str(data).lower()
            assert "hipaa_compliant" in str(data).lower()
            assert "encryption" in str(data).lower()

        @staticmethod
        def assert_performance_benchmark(time_ms: float, benchmark_ms: float):
            """Assert performance meets benchmark."""
            assert (
                time_ms <= benchmark_ms
            ), f"Performance: {time_ms}ms > {benchmark_ms}ms"

    return TestUtils()


# ======= CLEANUP FIXTURES =======


@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Automatic cleanup after each test."""
    yield
    # Perform any necessary cleanup
    # This runs after each test automatically
