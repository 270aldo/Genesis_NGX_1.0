"""
Comprehensive test fixtures for WAVE Performance Analytics Agent.
A+ testing framework with 90%+ coverage targeting.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, MagicMock

# Core framework imports
from core.telemetry import TelemetryService
from core.cache import CacheManager
from clients.vertex_ai.vertex_ai_client import VertexAIClient
from core.personality.personality_adapter import PersonalityAdapter

# Agent-specific imports
from ..core.dependencies import WaveAnalyticsAgentDependencies
from ..core.config import WaveAnalyticsConfig
from ..core.exceptions import (
    WaveAnalyticsError,
    RecoveryError,
    AnalyticsError,
    FusionError,
    RecoveryValidationError,
    InjuryPreventionError,
    RehabilitationError,
)
from ..services.recovery_service import RecoveryService
from ..skills_manager import WaveAnalyticsSkillsManager
from ..agent_optimized import WavePerformanceAnalyticsAgent


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async testing."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = WaveAnalyticsConfig()

    # Override with test values
    config.max_response_time = 10.0
    config.gemini_model = "gemini-1.5-flash-002"
    config.temperature = 0.7
    config.enable_vision_analysis = True
    config.enable_injury_prediction = True
    config.enable_recovery_analytics_fusion = True
    config.enable_real_time_monitoring = True
    config.gdpr_compliant = True
    config.hipaa_compliant = True
    config.data_residency = "eu"

    return config


@pytest.fixture
def mock_cache():
    """Mock cache manager for testing."""
    cache = Mock(spec=CacheManager)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=True)
    cache.exists = AsyncMock(return_value=False)
    cache.ttl = AsyncMock(return_value=3600)
    cache.keys = AsyncMock(return_value=[])

    return cache


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    client = Mock(spec=VertexAIClient)

    # Mock successful AI responses
    client.generate_content_async = AsyncMock(
        return_value="""
    Based on the user's recovery and analytics data, here's my analysis:
    
    Recovery Status: Good (85/100)
    Risk Assessment: Low (0.15)
    
    Recommendations:
    1. Continue current recovery protocol
    2. Monitor HRV trends daily
    3. Maintain sleep quality above 80%
    
    Fusion Analysis:
    - Holistic insight: Body is responding well to current program
    - Analytical insight: Biometric trends show consistent improvement
    - Integrated recommendation: Gradual increase in training intensity
    """
    )

    # Mock configuration
    client.model_config = {
        "max_output_tokens": 6144,
        "temperature": 0.6,
        "safety_settings": [],
    }

    return client


@pytest.fixture
def mock_personality_adapter():
    """Mock personality adapter for testing."""
    adapter = Mock(spec=PersonalityAdapter)

    # Mock adaptation responses
    adapter.adapt_response = AsyncMock(
        side_effect=lambda response, program_type, agent_id: {
            "adapted_content": f"[{program_type}] {response}",
            "program_type": program_type,
            "agent_id": agent_id,
            "adaptation_confidence": 0.85,
            "adaptation_metrics": {
                "tone_adjustment": 0.7,
                "vocabulary_adaptation": 0.8,
                "complexity_level": 0.9,
            },
        }
    )

    return adapter


@pytest.fixture
def mock_telemetry():
    """Mock telemetry service for testing."""
    telemetry = Mock(spec=TelemetryService)
    telemetry.set_context = Mock()
    telemetry.set_custom_attributes = Mock()
    telemetry.record_metric = Mock()
    telemetry.shutdown = AsyncMock()

    return telemetry


@pytest.fixture
def mock_dependencies(
    mock_cache, mock_gemini_client, mock_personality_adapter, mock_telemetry
):
    """Mock dependencies container for testing."""
    deps = Mock(spec=WaveAnalyticsAgentDependencies)

    # Core dependencies
    deps.cache = mock_cache
    deps.vertex_ai_client = mock_gemini_client
    deps.personality_adapter = mock_personality_adapter
    deps.telemetry = mock_telemetry

    # Recovery services (mocked)
    deps.injury_prevention_service = Mock()
    deps.rehabilitation_service = Mock()
    deps.sleep_optimization_service = Mock()
    deps.mobility_assessment_service = Mock()

    # Analytics services (mocked)
    deps.biometric_analyzer = Mock()
    deps.pattern_recognition_service = Mock()
    deps.trend_analyzer = Mock()
    deps.data_visualizer = Mock()

    # Fusion services (mocked)
    deps.recovery_analytics_fusion_service = Mock()
    deps.performance_optimizer = Mock()

    # Validation methods
    deps.validate_dependencies = Mock(return_value=True)
    deps.get_health_status = Mock(
        return_value={
            "cache": True,
            "vertex_ai_client": True,
            "personality_adapter": True,
            "recovery_services": True,
            "analytics_services": True,
            "fusion_services": True,
        }
    )

    # Fusion capabilities
    deps.get_fusion_capabilities = Mock(
        return_value={
            "recovery_analytics_fusion": True,
            "injury_prediction": True,
            "performance_optimization": True,
            "holistic_dashboard": True,
            "adaptive_protocol": True,
        }
    )

    # Service injection
    deps.inject_recovery_services = Mock()
    deps.inject_analytics_services = Mock()
    deps.inject_fusion_services = Mock()

    return deps


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "user_id": "test_user_123",
        "age": 32,
        "biological_sex": "male",
        "activity_level": "high",
        "fitness_goals": ["performance", "recovery", "injury_prevention"],
        "program_type": "PRIME",
        "current_training_program": "strength_endurance",
        "injury_history": [
            {
                "type": "lower_back",
                "date": "2023-06-15",
                "severity": "mild",
                "status": "recovered",
            }
        ],
        "health_conditions": [],
        "medications": [],
    }


@pytest.fixture
def sample_biometric_data():
    """Sample biometric data for testing."""
    return {
        "date_range": {"start": "2024-06-01", "end": "2024-06-07"},
        "hrv": {
            "avg": 45.2,
            "trend": "stable",
            "daily_values": [44.1, 45.8, 44.9, 46.2, 45.0, 44.7, 45.5],
        },
        "resting_heart_rate": {
            "avg": 58.5,
            "trend": "decreasing",
            "daily_values": [60, 59, 58, 57, 58, 59, 57],
        },
        "sleep_quality": {
            "avg_score": 82.3,
            "avg_duration": 7.8,
            "deep_sleep_percentage": 18.5,
            "rem_sleep_percentage": 24.2,
            "sleep_efficiency": 89.1,
        },
        "recovery_score": {
            "avg": 76.8,
            "trend": "improving",
            "daily_values": [72, 75, 78, 79, 77, 76, 80],
        },
        "training_load": {
            "weekly_total": 485,
            "trend": "increasing",
            "acute_chronic_ratio": 1.15,
        },
        "stress_score": {
            "avg": 23.4,
            "trend": "stable",
            "daily_values": [25, 22, 24, 23, 22, 24, 23],
        },
    }


@pytest.fixture
def sample_recovery_data():
    """Sample recovery data for testing."""
    return {
        "current_protocols": [
            {
                "type": "sleep_optimization",
                "status": "active",
                "adherence": 0.85,
                "effectiveness": "good",
            },
            {
                "type": "mobility_routine",
                "status": "active",
                "adherence": 0.92,
                "effectiveness": "excellent",
            },
        ],
        "recent_assessments": [
            {
                "date": "2024-06-05",
                "type": "mobility_assessment",
                "overall_score": 78,
                "areas_of_concern": ["hip_flexors", "thoracic_spine"],
            }
        ],
        "injury_risk_factors": [
            {
                "factor": "training_load_increase",
                "risk_level": "moderate",
                "mitigation": "gradual_progression",
            }
        ],
    }


@pytest.fixture
def sample_context():
    """Sample conversation context for testing."""
    return {
        "user_id": "test_user_123",
        "session_id": "session_456",
        "timestamp": datetime.now().isoformat(),
        "program_type": "PRIME",
        "conversation_history": [
            {
                "role": "user",
                "content": "How is my recovery looking this week?",
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
            }
        ],
        "user_preferences": {
            "communication_style": "direct",
            "detail_level": "detailed",
            "motivational_tone": "encouraging",
        },
        "device_data": {
            "primary_device": "whoop",
            "last_sync": datetime.now().isoformat(),
            "sync_quality": "good",
        },
    }


@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing."""
    return {
        "data_quality": {"completeness": 0.95, "accuracy": 0.98, "consistency": 0.94},
        "patterns_detected": [
            {
                "pattern_type": "circadian_rhythm",
                "confidence": 0.89,
                "description": "Consistent sleep-wake cycle",
            },
            {
                "pattern_type": "training_response",
                "confidence": 0.82,
                "description": "Positive adaptation to current load",
            },
        ],
        "trends": [
            {
                "metric": "hrv",
                "direction": "improving",
                "strength": 0.76,
                "duration_days": 14,
            },
            {
                "metric": "recovery_score",
                "direction": "stable",
                "strength": 0.65,
                "duration_days": 21,
            },
        ],
        "anomalies": [],
        "correlations": [
            {
                "metric_1": "sleep_quality",
                "metric_2": "next_day_hrv",
                "correlation": 0.78,
                "significance": 0.001,
            }
        ],
    }


@pytest.fixture
def sample_fusion_request():
    """Sample fusion analysis request."""
    return {
        "message": "I want to optimize my recovery and performance together",
        "context": {
            "user_id": "test_user_123",
            "program_type": "PRIME",
            "fusion_mode": True,
            "recovery_data": {
                "current_status": "good",
                "protocols_active": ["sleep", "mobility"],
            },
            "analytics_data": {"hrv_trend": "improving", "training_load": "optimal"},
        },
        "requested_analysis": [
            "recovery_analytics_fusion",
            "performance_optimization",
            "injury_prediction",
        ],
    }


@pytest.fixture
def mock_recovery_service(mock_config, mock_cache):
    """Mock recovery service for testing."""
    service = Mock(spec=RecoveryService)

    # Mock assess_injury_risk
    service.assess_injury_risk = AsyncMock(
        return_value={
            "risk_score": 0.25,
            "risk_level": "low",
            "primary_risk_factors": ["training_load_increase"],
            "secondary_risk_factors": ["sleep_quality_variance"],
            "prevention_recommendations": [
                "Maintain current training progression",
                "Monitor sleep consistency",
                "Continue mobility routine",
            ],
            "assessment_date": datetime.now().isoformat(),
            "reassessment_due": (datetime.now() + timedelta(days=7)).isoformat(),
        }
    )

    # Mock create_rehabilitation_plan
    service.create_rehabilitation_plan = AsyncMock(
        return_value={
            "injury_type": "lower_back",
            "severity": "mild",
            "plan_id": "rehab_lower_back_20240607_120000",
            "phases": [
                {
                    "phase": 1,
                    "name": "Acute/Pain Management",
                    "duration_weeks": 1,
                    "goals": ["reduce_pain", "reduce_inflammation"],
                }
            ],
            "duration_weeks": 6,
            "session_frequency": "3x/week",
            "created_date": datetime.now().isoformat(),
        }
    )

    # Mock optimize_sleep_protocol
    service.optimize_sleep_protocol = AsyncMock(
        return_value={
            "current_metrics": {
                "total_sleep_hours": 7.8,
                "deep_sleep_percentage": 18.5,
                "sleep_efficiency": 89.1,
            },
            "optimization_opportunities": [
                "Increase deep sleep percentage",
                "Improve sleep onset time",
            ],
            "recommendations": [
                "Maintain consistent bedtime",
                "Reduce blue light exposure 2h before bed",
            ],
            "target_metrics": {
                "total_sleep_hours": 8.0,
                "deep_sleep_percentage": 20.0,
                "sleep_efficiency": 90.0,
            },
            "created_date": datetime.now().isoformat(),
        }
    )

    # Mock assess_mobility
    service.assess_mobility = AsyncMock(
        return_value={
            "assessment_type": "full",
            "assessment_date": datetime.now().isoformat(),
            "overall_score": 78,
            "limitations_identified": [
                "hip_flexor_tightness",
                "reduced_thoracic_rotation",
            ],
            "improvement_recommendations": [
                "Daily hip flexor stretching",
                "Thoracic spine mobility work",
            ],
            "next_assessment": (datetime.now() + timedelta(days=14)).isoformat(),
        }
    )

    return service


@pytest.fixture
def wave_agent(mock_dependencies, mock_config):
    """Create WAVE Performance Analytics agent instance for testing."""
    agent = WavePerformanceAnalyticsAgent(
        dependencies=mock_dependencies, config=mock_config
    )
    return agent


@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing."""
    return {
        "validation_error": {
            "type": RecoveryValidationError,
            "message": "Invalid input data",
            "field_name": "test_field",
            "invalid_value": "invalid_value",
        },
        "injury_prevention_error": {
            "type": InjuryPreventionError,
            "message": "Injury prevention protocol failed",
            "injury_type": "lower_back",
            "risk_level": 0.8,
        },
        "analytics_error": {
            "type": AnalyticsError,
            "message": "Analytics processing failed",
        },
        "fusion_error": {"type": FusionError, "message": "Fusion analysis failed"},
    }


@pytest.fixture
def performance_benchmarks():
    """Performance benchmarks for testing."""
    return {
        "response_times": {
            "simple_query": 0.5,  # seconds
            "complex_analysis": 2.0,
            "fusion_analysis": 3.0,
            "health_check": 0.1,
        },
        "memory_usage": {
            "agent_initialization": 50,  # MB
            "processing_peak": 100,
            "steady_state": 30,
        },
        "throughput": {"requests_per_second": 10, "concurrent_users": 50},
    }


@pytest.fixture
def security_test_data():
    """Security test data for compliance validation."""
    return {
        "pii_data": {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-01",
        },
        "health_data": {
            "medical_conditions": ["hypertension"],
            "medications": ["lisinopril"],
            "genetic_markers": ["APOE_e4"],
            "biometric_data": {
                "blood_pressure": "120/80",
                "cholesterol": 180,
                "glucose": 95,
            },
        },
        "sensitive_queries": [
            "I have been diagnosed with diabetes",
            "My doctor prescribed medication for depression",
            "I'm pregnant and want to exercise safely",
        ],
    }


@pytest.fixture
def integration_test_data():
    """Data for integration testing with external services."""
    return {
        "device_integrations": [
            {
                "device_type": "whoop",
                "data_types": ["hrv", "recovery", "strain", "sleep"],
                "sync_frequency": "real_time",
            },
            {
                "device_type": "oura",
                "data_types": ["sleep", "readiness", "activity", "temperature"],
                "sync_frequency": "hourly",
            },
        ],
        "ai_services": [
            {
                "service": "gemini",
                "endpoints": ["generate_content", "analyze_image"],
                "rate_limits": {"requests_per_minute": 60, "tokens_per_minute": 32000},
            }
        ],
        "database_operations": [
            "user_profile_read",
            "biometric_data_write",
            "recovery_plan_update",
            "analytics_cache_read",
        ],
    }


# Helper functions for test utilities
def create_test_message(content: str, user_id: str = "test_user") -> str:
    """Create standardized test message."""
    return content


def create_test_context(
    user_id: str = "test_user", program_type: str = "PRIME", **kwargs
) -> Dict[str, Any]:
    """Create standardized test context."""
    context = {
        "user_id": user_id,
        "program_type": program_type,
        "timestamp": datetime.now().isoformat(),
        "session_id": f"session_{user_id}",
        **kwargs,
    }
    return context


def assert_response_structure(response: Dict[str, Any]) -> None:
    """Assert standard response structure."""
    assert isinstance(response, dict)
    assert "success" in response
    assert "timestamp" in response
    assert "agent" in response
    assert response["agent"] == "wave_performance_analytics"


def assert_error_response(response: Dict[str, Any]) -> None:
    """Assert error response structure."""
    assert_response_structure(response)
    assert response["success"] is False
    assert "error" in response
    assert "error_type" in response


def assert_success_response(response: Dict[str, Any]) -> None:
    """Assert success response structure."""
    assert_response_structure(response)
    assert response["success"] is True
