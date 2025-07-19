"""
Unit tests for SAGE core functionality.
Tests all core modules with 90%+ coverage target.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

from agents.precision_nutrition_architect.core.dependencies import (
    NutritionAgentDependencies,
)
from agents.precision_nutrition_architect.core.config import NutritionConfig
from agents.precision_nutrition_architect.core.exceptions import *
from agents.precision_nutrition_architect.core.constants import *
from agents.precision_nutrition_architect.skills_manager import NutritionSkillsManager
from agents.precision_nutrition_architect.services.nutrition_security_service import (
    NutritionSecurityService,
)
from agents.precision_nutrition_architect.services.nutrition_data_service import (
    NutritionDataService,
)


class TestNutritionConfig:
    """Test nutrition configuration module."""

    def test_default_config_creation(self):
        """Test creating default configuration."""
        config = NutritionConfig()

        assert config.max_response_time == 30.0
        assert config.gemini_model == "gemini-1.5-flash-002"
        assert config.enable_health_data_encryption is True
        assert config.gdpr_compliant is True
        assert config.hipaa_compliant is True

    def test_config_from_environment(self):
        """Test configuration creation from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "SAGE_MAX_RESPONSE_TIME": "15.0",
                "SAGE_TEMPERATURE": "0.5",
                "SAGE_ENABLE_ENCRYPTION": "false",
            },
        ):
            config = NutritionConfig.from_environment()

            assert config.max_response_time == 15.0
            assert config.temperature == 0.5
            assert config.enable_health_data_encryption is False

    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = NutritionConfig()
        errors = config.validate()
        assert len(errors) == 0

        # Invalid config
        config.max_response_time = -5.0
        config.temperature = 3.0
        config.min_calories_per_meal = 2000
        config.max_calories_per_meal = 1000

        errors = config.validate()
        assert len(errors) == 4
        assert any("max_response_time must be positive" in error for error in errors)
        assert any("temperature must be between 0 and 2" in error for error in errors)

    def test_macro_ratios_retrieval(self):
        """Test macro ratio preset retrieval."""
        config = NutritionConfig()

        # Valid preset
        ratios = config.get_macro_ratios("ketogenic")
        assert ratios["protein"] == 0.25
        assert ratios["carbs"] == 0.05
        assert ratios["fat"] == 0.70

        # Invalid preset returns balanced
        ratios = config.get_macro_ratios("invalid_preset")
        assert ratios == config.macro_ratio_presets["balanced"]

    def test_biomarker_range_retrieval(self):
        """Test biomarker reference range retrieval."""
        config = NutritionConfig()

        # Valid biomarker
        range_data = config.get_biomarker_range("glucose_fasting")
        assert range_data["min"] == 70
        assert range_data["max"] == 100
        assert range_data["unit"] == "mg/dL"

        # Invalid biomarker
        assert config.get_biomarker_range("invalid_marker") is None


class TestNutritionAgentDependencies:
    """Test dependency injection system."""

    def test_create_for_testing(self):
        """Test creating test dependencies."""
        deps = NutritionAgentDependencies.create_for_testing()

        assert deps.personality_adapter is not None
        assert deps.vertex_ai_client is None  # Should be None for testing
        assert deps.cache is not None
        assert deps.cache.max_size == 100

    def test_dependency_validation(self):
        """Test dependency validation."""
        # Valid dependencies
        deps = NutritionAgentDependencies.create_for_testing(
            vertex_ai_client=Mock(), vertex_client=Mock()
        )
        assert deps.validate_dependencies() is True

        # Missing critical dependencies
        deps = NutritionAgentDependencies.create_for_testing()
        assert deps.validate_dependencies() is False

    def test_inject_nutrition_services(self):
        """Test nutrition service injection."""
        deps = NutritionAgentDependencies.create_for_testing()

        # Initial state
        assert deps.nutrition_analyzer is None

        # Inject services
        mock_analyzer = Mock()
        mock_biomarker = Mock()
        mock_planner = Mock()
        mock_advisor = Mock()

        deps.inject_nutrition_services(
            mock_analyzer, mock_biomarker, mock_planner, mock_advisor
        )

        assert deps.nutrition_analyzer is mock_analyzer
        assert deps.biomarker_analyzer is mock_biomarker
        assert deps.meal_planner is mock_planner
        assert deps.supplement_advisor is mock_advisor

    def test_health_status_report(self):
        """Test health status reporting."""
        deps = NutritionAgentDependencies.create_for_testing(
            vertex_ai_client=Mock(), vertex_client=Mock()
        )

        status = deps.get_health_status()

        assert "core_dependencies" in status
        assert "optional_dependencies" in status
        assert "nutrition_services" in status

        assert status["core_dependencies"]["vertex_ai_client"] is True
        assert status["nutrition_services"]["nutrition_analyzer"] is False


class TestNutritionConstants:
    """Test nutrition constants and enums."""

    def test_enum_values(self):
        """Test enum value definitions."""
        # Activity levels
        assert ActivityLevel.SEDENTARY == "sedentary"
        assert ActivityLevel.VERY_ACTIVE == "very_active"

        # Diet types
        assert DietType.KETOGENIC == "ketogenic"
        assert DietType.MEDITERRANEAN == "mediterranean"

        # Meal types
        assert MealType.BREAKFAST == "breakfast"
        assert MealType.POST_WORKOUT == "post_workout"

    def test_activity_multipliers(self):
        """Test activity level multiplier mappings."""
        assert ACTIVITY_MULTIPLIERS[ActivityLevel.SEDENTARY] == 1.2
        assert ACTIVITY_MULTIPLIERS[ActivityLevel.EXTREMELY_ACTIVE] == 1.9

        # Ensure all activity levels have multipliers
        for activity in ActivityLevel:
            assert activity in ACTIVITY_MULTIPLIERS

    def test_calories_per_gram(self):
        """Test macronutrient calorie values."""
        assert CALORIES_PER_GRAM["protein"] == 4.0
        assert CALORIES_PER_GRAM["fat"] == 9.0
        assert CALORIES_PER_GRAM["alcohol"] == 7.0

    def test_biomarker_ranges(self):
        """Test biomarker optimal ranges."""
        glucose = BIOMARKER_OPTIMAL_RANGES["glucose_fasting"]
        assert glucose["min"] == 75
        assert glucose["max"] == 95
        assert glucose["unit"] == "mg/dL"

        # Ensure key biomarkers are defined
        required_biomarkers = [
            "glucose_fasting",
            "hba1c",
            "cholesterol_total",
            "hdl",
            "ldl",
            "triglycerides",
            "vitamin_d",
        ]
        for biomarker in required_biomarkers:
            assert biomarker in BIOMARKER_OPTIMAL_RANGES


class TestNutritionSecurityService:
    """Test nutrition security service."""

    def test_initialization(self, nutrition_config):
        """Test security service initialization."""
        service = NutritionSecurityService(nutrition_config)

        assert service.encryption_enabled is True
        assert service.audit_enabled is True
        assert service.gdpr_compliant is True
        assert service.hipaa_compliant is True

    def test_health_data_encryption(self, nutrition_config):
        """Test health data encryption/decryption."""
        service = NutritionSecurityService(nutrition_config)

        # Test data
        health_data = {"glucose": 95, "cholesterol": 180, "blood_pressure": "120/80"}

        # Encrypt
        encrypted = service.encrypt_health_data(health_data)
        assert encrypted != json.dumps(health_data)
        assert isinstance(encrypted, str)

        # Decrypt
        decrypted = service.decrypt_health_data(encrypted)
        assert decrypted == health_data

    def test_biomarker_data_sanitization(self, nutrition_config):
        """Test biomarker data sanitization."""
        service = NutritionSecurityService(nutrition_config)

        # Data with PII
        raw_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "glucose": 95,
            "cholesterol": 180,
            "malicious_script": "<script>alert('xss')</script>",
            "extremely_large_value": 999999999,
            "nested_data": {"ssn": "123-45-6789", "vitamin_d": 32},
        }

        sanitized = service.sanitize_biomarker_data(raw_data)

        # PII should be removed
        assert "name" not in sanitized
        assert "email" not in sanitized

        # Valid biomarkers should remain
        assert sanitized["glucose"] == 95
        assert sanitized["cholesterol"] == 180

        # Malicious content should be sanitized
        assert "<script>" not in sanitized["malicious_script"]

        # Extreme values should be excluded
        assert "extremely_large_value" not in sanitized

        # Nested PII should be removed
        assert "ssn" not in sanitized["nested_data"]
        assert sanitized["nested_data"]["vitamin_d"] == 32

    def test_consent_management(self, nutrition_config):
        """Test consent checking."""
        service = NutritionSecurityService(nutrition_config)

        # With consent required
        assert service.check_consent("user123", "biomarker_analysis") is True

        # Check audit log
        assert len(service.audit_log) > 0
        last_log = service.audit_log[-1]
        assert last_log["action"] == "consent_checked"
        assert "user_id" in last_log["details"]

    def test_data_retention_check(self, nutrition_config):
        """Test data retention policy checking."""
        service = NutritionSecurityService(nutrition_config)

        # Recent data - should pass
        recent_date = datetime.now() - timedelta(days=30)
        assert service.check_data_retention(recent_date) is True

        # Old data - should fail
        old_date = datetime.now() - timedelta(days=400)
        with pytest.raises(DataRetentionError):
            service.check_data_retention(old_date)

    def test_compliance_report_generation(self, nutrition_config):
        """Test compliance report generation."""
        service = NutritionSecurityService(nutrition_config)

        # Generate some audit events
        service._audit_log("test_action_1", {"test": "data"})
        service._audit_log("test_action_2", {"test": "data"})

        report = service.generate_compliance_report()

        assert "generated_at" in report
        assert "compliance_status" in report
        assert "audit_summary" in report

        # Check GDPR compliance
        gdpr = report["compliance_status"]["gdpr"]
        assert gdpr["enabled"] is True
        assert gdpr["encryption"] is True
        assert gdpr["audit_logging"] is True

        # Check audit summary
        audit = report["audit_summary"]
        assert audit["total_events"] == 2
        assert "test_action_1" in audit["event_types"]

    def test_meal_plan_anonymization(self, nutrition_config):
        """Test meal plan anonymization."""
        service = NutritionSecurityService(nutrition_config)

        meal_plan = {
            "id": "plan-123",
            "user_id": "user-456",
            "user_name": "John Doe",
            "meals": {"breakfast": "oatmeal"},
            "created_by": "nutritionist-789",
        }

        anonymized = service.anonymize_meal_plan(meal_plan)

        # PII should be removed
        assert "user_id" not in anonymized
        assert "user_name" not in anonymized
        assert "created_by" not in anonymized

        # Meal data should remain
        assert anonymized["meals"] == {"breakfast": "oatmeal"}

        # ID should be hashed
        assert anonymized["id"] != "plan-123"
        assert len(anonymized["id"]) == 64  # SHA256 hex length


class TestNutritionSkillsManager:
    """Test nutrition skills manager."""

    @pytest.mark.asyncio
    async def test_initialization(self, test_dependencies):
        """Test skills manager initialization."""
        manager = NutritionSkillsManager(test_dependencies)

        assert manager.deps is test_dependencies
        assert manager.personality_adapter is not None
        assert len(manager.skills) == 8  # 8 skills defined

    @pytest.mark.asyncio
    async def test_skill_determination(self, nutrition_skills_manager):
        """Test skill determination from messages."""
        # Test meal planning
        skill = await nutrition_skills_manager._determine_skill(
            "I need a meal plan for weight loss", {"goals": ["weight_loss"]}
        )
        assert skill == "create_meal_plan"

        # Test image analysis
        skill = await nutrition_skills_manager._determine_skill(
            "Can you analyze this food photo?", {"image_data": "test"}
        )
        # Should fallback to keyword matching
        assert skill in nutrition_skills_manager.skills

    @pytest.mark.asyncio
    async def test_fallback_skill_determination(self, nutrition_skills_manager):
        """Test fallback skill determination."""
        # Meal planning keywords
        skill = nutrition_skills_manager._fallback_skill_determination(
            "create a meal plan"
        )
        assert skill == "create_meal_plan"

        # Supplement keywords
        skill = nutrition_skills_manager._fallback_skill_determination(
            "what vitamins should I take?"
        )
        assert skill == "recommend_supplements"

        # Default fallback
        skill = nutrition_skills_manager._fallback_skill_determination(
            "random question"
        )
        assert skill == "create_meal_plan"

    @pytest.mark.asyncio
    async def test_user_data_extraction(
        self, nutrition_skills_manager, sample_user_context
    ):
        """Test user data extraction from context."""
        user_data = nutrition_skills_manager._extract_user_data(sample_user_context)

        assert user_data["age"] == 35
        assert user_data["weight"] == 80
        assert user_data["activity_level"] == "moderately_active"
        assert user_data["program_type"] == "PRIME"
        assert "weight_loss" in user_data["goals"]

    @pytest.mark.asyncio
    async def test_nutrition_targets_calculation(self, nutrition_skills_manager):
        """Test nutrition targets calculation."""
        user_data = {
            "age": 30,
            "gender": "male",
            "weight": 75,
            "height": 175,
            "activity_level": "moderately_active",
            "goals": ["muscle_gain"],
        }

        targets = await nutrition_skills_manager._calculate_nutrition_targets(user_data)

        assert targets["calories"] > 0
        assert targets["protein_g"] > 0
        assert targets["carbs_g"] > 0
        assert targets["fat_g"] > 0

        # Check macro percentages sum to ~1.0
        total_pct = targets["protein_pct"] + targets["carbs_pct"] + targets["fat_pct"]
        assert 0.99 <= total_pct <= 1.01

        # Muscle gain should have higher calories (15% surplus)
        bmr_estimate = 10 * 75 + 6.25 * 175 - 5 * 30 + 5  # Male BMR
        expected_calories = bmr_estimate * 1.55 * 1.15  # Activity * surplus
        assert abs(targets["calories"] - expected_calories) < 100

    @pytest.mark.asyncio
    async def test_create_meal_plan_skill(
        self, nutrition_skills_manager, sample_user_context
    ):
        """Test meal plan creation skill."""
        result = await nutrition_skills_manager._skill_create_meal_plan(
            "Create a 7-day meal plan for weight loss", sample_user_context
        )

        assert result["skill"] == "create_meal_plan"
        assert result["success"] is True
        assert "meal_plan" in result
        assert "targets" in result
        assert "validation" in result
        assert "generated_at" in result

        # Check targets are calculated
        targets = result["targets"]
        assert targets["calories"] > 0
        assert targets["protein_g"] > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, nutrition_skills_manager):
        """Test error handling in skills."""
        # Test with invalid context that should cause error
        with patch.object(
            nutrition_skills_manager,
            "_calculate_nutrition_targets",
            side_effect=Exception("Test error"),
        ):

            with pytest.raises(MealPlanningError):
                await nutrition_skills_manager._skill_create_meal_plan(
                    "test message", {}
                )

    @pytest.mark.asyncio
    async def test_personality_adaptation(
        self, nutrition_skills_manager, sample_user_context
    ):
        """Test personality adaptation application."""
        result = {"skill": "test_skill", "meal_plan": {"day_1": "test"}}

        adapted = await nutrition_skills_manager._apply_personality_adaptation(
            result, sample_user_context
        )

        assert "personality_context" in adapted
        context = adapted["personality_context"]
        assert context["program_type"] == "PRIME"
        assert context["tone"] == "strategic"
        assert context["focus"] == "optimization"

    def test_error_response_creation(self, nutrition_skills_manager):
        """Test error response creation."""
        error_response = nutrition_skills_manager._create_error_response(
            "Test error message", skill_name="test_skill", error_code=500
        )

        assert error_response["success"] is False
        assert error_response["error"] == "Test error message"
        assert error_response["error_details"]["skill_name"] == "test_skill"
        assert error_response["error_details"]["error_code"] == 500
        assert "timestamp" in error_response


class TestNutritionExceptions:
    """Test nutrition-specific exceptions."""

    def test_base_nutrition_error(self):
        """Test base nutrition error."""
        details = {"context": "test"}
        error = NutritionError("Test error", details)

        assert str(error) == "Test error"
        assert error.details == details

    def test_meal_planning_error(self):
        """Test meal planning error hierarchy."""
        error = MealPlanningError("Meal planning failed")
        assert isinstance(error, NutritionError)

    def test_calorie_calculation_error(self):
        """Test calorie calculation error with details."""
        error = CalorieCalculationError(
            "Calorie mismatch", target_calories=2000, actual_calories=1500
        )

        assert error.details["target_calories"] == 2000
        assert error.details["actual_calories"] == 1500
        assert isinstance(error, MealPlanningError)

    def test_biomarker_analysis_error(self):
        """Test biomarker analysis error."""
        error = InvalidBiomarkerError(
            "Invalid glucose value",
            biomarker_name="glucose",
            value=300,
            expected_range={"min": 70, "max": 100},
        )

        assert error.details["biomarker"] == "glucose"
        assert error.details["value"] == 300
        assert error.details["expected_range"]["max"] == 100

    def test_supplement_interaction_error(self):
        """Test supplement interaction error."""
        error = SupplementInteractionError(
            "Supplement interactions detected",
            supplements=["iron", "calcium"],
            interactions=["reduced_absorption"],
        )

        assert "iron" in error.details["supplements"]
        assert "reduced_absorption" in error.details["interactions"]

    def test_security_error(self):
        """Test health data security error."""
        error = ConsentRequiredError(
            "Consent required for genetic analysis",
            consent_type="genetic_data",
            data_usage="nutrigenomics analysis",
        )

        assert error.details["consent_type"] == "genetic_data"
        assert error.details["data_usage"] == "nutrigenomics analysis"
        assert isinstance(error, HealthDataSecurityError)
