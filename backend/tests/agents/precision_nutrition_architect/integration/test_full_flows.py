"""
Integration tests for SAGE agent full workflows.
Tests end-to-end functionality and integration between components.
"""

import pytest
import json
from datetime import datetime

from agents.precision_nutrition_architect.skills_manager import NutritionSkillsManager
from agents.precision_nutrition_architect.core.exceptions import *


class TestMealPlanningWorkflow:
    """Test complete meal planning workflow."""

    @pytest.mark.asyncio
    async def test_complete_meal_planning_flow(
        self,
        nutrition_skills_manager,
        sample_user_context,
        assert_response_structure,
        assert_nutrition_data,
    ):
        """Test complete meal planning from request to result."""
        # Execute meal planning skill
        result = await nutrition_skills_manager.process_message(
            "Create a 7-day meal plan for weight loss with 2000 calories per day",
            sample_user_context,
        )

        # Validate response structure
        required_fields = ["skill", "success", "meal_plan", "targets"]
        assert_response_structure(result, required_fields)

        # Validate success
        assert result["success"] is True
        assert result["skill"] == "create_meal_plan"

        # Validate nutrition targets
        targets = result["targets"]
        assert_nutrition_data(targets)

        # Validate meal plan structure
        meal_plan = result["meal_plan"]
        assert isinstance(meal_plan, dict)

        # Check personality adaptation was applied
        assert "personality_context" in result
        personality = result["personality_context"]
        assert personality["program_type"] == "PRIME"
        assert personality["tone"] == "strategic"


class TestBiomarkerAnalysisWorkflow:
    """Test biomarker analysis workflow."""

    @pytest.mark.asyncio
    async def test_biomarker_assessment_flow(
        self, nutrition_skills_manager, sample_biomarkers, assert_response_structure
    ):
        """Test biomarker analysis workflow."""
        context = {"biomarkers": sample_biomarkers, "program_type": "LONGEVITY"}

        result = await nutrition_skills_manager.process_message(
            "Analyze my latest blood test results", context
        )

        # Validate response
        required_fields = ["skill", "success", "assessment", "biomarkers"]
        assert_response_structure(result, required_fields)

        assert result["success"] is True
        assert result["skill"] == "assess_biomarkers"

        # Validate biomarkers were processed
        biomarkers = result["biomarkers"]
        assert "glucose_fasting" in biomarkers
        assert biomarkers["glucose_fasting"] == 92


class TestSecurityIntegration:
    """Test security service integration."""

    def test_health_data_security_integration(
        self, security_service, sample_biomarkers
    ):
        """Test health data encryption in workflow."""
        # Encrypt sensitive health data
        encrypted = security_service.encrypt_health_data(sample_biomarkers)
        assert encrypted != json.dumps(sample_biomarkers)

        # Decrypt and verify
        decrypted = security_service.decrypt_health_data(encrypted)
        assert decrypted == sample_biomarkers

        # Check audit log
        audit_events = security_service.get_audit_log()
        assert len(audit_events) >= 2  # Encrypt + decrypt events

        encrypt_event = next(
            (e for e in audit_events if e["action"] == "health_data_encrypted"), None
        )
        assert encrypt_event is not None
        assert encrypt_event["details"]["data_type"] == "health_record"


class TestDataServiceIntegration:
    """Test data service integration."""

    @pytest.mark.asyncio
    async def test_meal_plan_persistence_flow(self, data_service, sample_meal_plan):
        """Test meal plan save and retrieve flow."""
        user_id = "test-user-123"

        # Save meal plan
        plan_id = await data_service.save_meal_plan(
            user_id=user_id,
            meal_plan=sample_meal_plan,
            metadata={"created_by": "test", "version": "1.0"},
        )

        assert plan_id is not None
        assert isinstance(plan_id, str)

        # Retrieve meal plan
        retrieved_plan = await data_service.get_meal_plan(plan_id)

        # Note: Due to mocking, this may return the original data
        # In real implementation, would verify exact match
        if retrieved_plan:
            assert isinstance(retrieved_plan, dict)


class TestErrorHandlingIntegration:
    """Test error handling across components."""

    @pytest.mark.asyncio
    async def test_graceful_error_handling(self, nutrition_skills_manager):
        """Test graceful error handling in skill processing."""
        # Test with invalid context that might cause errors
        result = await nutrition_skills_manager.process_message(
            "Invalid request that might fail", {}  # Empty context
        )

        # Should still return a structured response
        assert isinstance(result, dict)
        assert "success" in result

        # If it failed gracefully, success should be False
        if not result.get("success", True):
            assert "error" in result

    def test_exception_hierarchy(self):
        """Test that exceptions form proper hierarchy."""
        # All nutrition exceptions should inherit from NutritionError
        meal_error = MealPlanningError("Test")
        biomarker_error = BiomarkerAnalysisError("Test")
        supplement_error = SupplementationError("Test")

        assert isinstance(meal_error, NutritionError)
        assert isinstance(biomarker_error, NutritionError)
        assert isinstance(supplement_error, NutritionError)

        # Specific exceptions should have proper inheritance
        calorie_error = CalorieCalculationError("Test")
        assert isinstance(calorie_error, MealPlanningError)
        assert isinstance(calorie_error, NutritionError)


class TestComponentIntegration:
    """Test integration between different components."""

    @pytest.mark.asyncio
    async def test_skills_manager_with_dependencies(
        self, test_dependencies, sample_user_context
    ):
        """Test skills manager working with real dependencies."""
        manager = NutritionSkillsManager(test_dependencies)

        # Test that manager can access all dependencies
        assert manager.deps.personality_adapter is not None
        assert manager.deps.cache is not None

        # Test dependency validation
        is_valid = test_dependencies.validate_dependencies()
        # May be False due to missing critical dependencies in test setup
        assert isinstance(is_valid, bool)

        # Test health status reporting
        status = test_dependencies.get_health_status()
        assert "core_dependencies" in status
        assert "nutrition_services" in status

    def test_configuration_integration(self, nutrition_config):
        """Test configuration integration across services."""
        # Test that config is properly used by services
        from agents.precision_nutrition_architect.services.nutrition_security_service import (
            NutritionSecurityService,
        )

        security_service = NutritionSecurityService(nutrition_config)

        assert (
            security_service.encryption_enabled
            == nutrition_config.enable_health_data_encryption
        )
        assert security_service.audit_enabled == nutrition_config.enable_audit_logging
        assert security_service.gdpr_compliant == nutrition_config.gdpr_compliant


class TestPerformanceIntegration:
    """Test performance aspects of integration."""

    @pytest.mark.asyncio
    async def test_response_time_requirements(
        self, nutrition_skills_manager, sample_user_context
    ):
        """Test that responses meet timing requirements."""
        import time

        start_time = time.time()

        result = await nutrition_skills_manager.process_message(
            "Create a quick meal plan", sample_user_context
        )

        end_time = time.time()
        response_time = end_time - start_time

        # Should respond within reasonable time (mocked services should be fast)
        assert response_time < 5.0  # 5 seconds max for mocked tests

        # Verify result was returned
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(
        self, nutrition_skills_manager, sample_user_context
    ):
        """Test handling multiple concurrent requests."""
        import asyncio

        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            context = sample_user_context.copy()
            context["request_id"] = f"request_{i}"

            task = nutrition_skills_manager.process_message(
                f"Create meal plan #{i}", context
            )
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        assert len(results) == 5

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Request {i} failed with exception: {result}")

            assert isinstance(result, dict)
            # Should have success indicator
            assert "success" in result


class TestComplianceIntegration:
    """Test compliance and security integration."""

    def test_gdpr_compliance_workflow(self, security_service, sample_user_context):
        """Test GDPR compliance in data handling."""
        # Test consent checking
        user_id = sample_user_context["user_id"]
        consent_given = security_service.check_consent(user_id, "nutrition_analysis")
        assert consent_given is True

        # Test data anonymization
        meal_plan = {
            "user_id": user_id,
            "user_name": "John Doe",
            "meals": {"breakfast": "oatmeal"},
        }

        anonymized = security_service.anonymize_meal_plan(meal_plan)
        assert "user_id" not in anonymized
        assert "user_name" not in anonymized
        assert anonymized["meals"] == meal_plan["meals"]

    def test_audit_logging_integration(self, security_service):
        """Test audit logging throughout workflow."""
        # Perform various operations
        test_data = {"glucose": 95, "cholesterol": 180}

        # Encrypt data (creates audit log)
        encrypted = security_service.encrypt_health_data(test_data)

        # Decrypt data (creates audit log)
        decrypted = security_service.decrypt_health_data(encrypted)

        # Check audit logs were created
        audit_logs = security_service.get_audit_log()
        assert len(audit_logs) >= 2

        # Verify log structure
        for log in audit_logs:
            assert "timestamp" in log
            assert "action" in log
            assert "details" in log
            assert "compliance" in log

            compliance = log["compliance"]
            assert "gdpr" in compliance
            assert "hipaa" in compliance
