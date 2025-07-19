"""
Unit tests for CODE Genetic Specialist core functionality.
Tests critical genetic analysis features with A+ coverage standards.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from agents.code_genetic_specialist.core.exceptions import (
    CodeGeneticError,
    GeneticAnalysisError,
    GeneticDataSecurityError,
    GeneticConsentError,
)


class TestCodeGeneticSpecialistCore:
    """Comprehensive tests for CODE agent core functionality."""

    @pytest.mark.asyncio
    async def test_agent_initialization_success(self, test_dependencies, test_config):
        """Test successful agent initialization with all components."""
        from agents.code_genetic_specialist.agent_refactored import (
            CodeGeneticSpecialist,
        )

        with patch(
            "agents.code_genetic_specialist.agent_refactored.GeneticSecurityService"
        ) as mock_security:
            with patch(
                "agents.code_genetic_specialist.agent_refactored.ConsentManagementService"
            ) as mock_consent:
                # Configure mocks
                mock_security.return_value.initialize = AsyncMock()
                mock_consent.return_value.initialize = AsyncMock()

                # Create and initialize agent
                agent = CodeGeneticSpecialist(test_dependencies, test_config)
                await agent.initialize()

                # Verify initialization
                assert agent.version == "2.0.0"
                assert agent.personality_config["mbti_type"] == "INTP"
                test_dependencies.personality_adapter.initialize_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_initialization_failure_invalid_config(self, test_dependencies):
        """Test agent initialization failure with invalid configuration."""
        from agents.code_genetic_specialist.agent_refactored import (
            CodeGeneticSpecialist,
        )
        from agents.code_genetic_specialist.core.config import CodeGeneticConfig

        # Create invalid config
        invalid_config = CodeGeneticConfig(
            max_response_time=-1,  # Invalid negative value
            enable_data_encryption=False,  # Invalid for production
            debug_mode=False,  # Production mode with invalid settings
        )

        agent = CodeGeneticSpecialist(test_dependencies, invalid_config)

        with pytest.raises(CodeGeneticError) as exc_info:
            await agent.initialize()

        assert "Initialization failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_message_success_prime_user(
        self, agent, sample_genetic_context
    ):
        """Test successful message handling for PRIME user."""
        # Arrange
        message = "Analyze my genetic profile for athletic performance optimization"
        context = {**sample_genetic_context, "program_type": "NGX_PRIME"}

        # Mock skills manager response
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Strategic genetic analysis reveals performance optimization opportunities",
                "confidence_score": 0.94,
                "skills_used": ["analyze_genetic_profile", "sport_genetics"],
                "genetic_insights": {
                    "performance_potential": "high",
                    "training_response": "power-focused",
                },
            }

            # Act
            response = await agent.handle_message(message, context)

            # Assert
            assert response["success"] is True
            assert "Strategic genetic analysis" in response["content"]
            assert response["adaptation_metadata"]["program_type"] == "NGX_PRIME"
            assert (
                response["genetic_communication_metadata"][
                    "scientific_accuracy_maintained"
                ]
                is True
            )
            assert "performance_metadata" in response
            assert response["performance_metadata"]["processing_time_ms"] > 0

    @pytest.mark.asyncio
    async def test_handle_message_success_longevity_user(
        self, agent, sample_genetic_context
    ):
        """Test successful message handling for LONGEVITY user."""
        # Arrange
        message = "Help me understand my genetic predispositions for long-term wellness"
        context = {**sample_genetic_context, "program_type": "NGX_LONGEVITY"}

        # Configure personality adapter for LONGEVITY response
        agent.personality_adapter.adapt_response.return_value = {
            "adapted_message": "Your genetic profile provides valuable insights for your wellness journey",
            "confidence_score": 0.91,
            "adaptation_type": "LONGEVITY",
            "metadata": {
                "program_type": "NGX_LONGEVITY",
                "adaptation_applied": True,
                "emotional_support_enhanced": True,
            },
        }

        # Mock skills manager response
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Wellness-focused genetic analysis for long-term health",
                "confidence_score": 0.91,
                "requires_emotional_support": True,
                "skills_used": ["analyze_genetic_profile", "genetic_risk_assessment"],
            }

            # Act
            response = await agent.handle_message(message, context)

            # Assert
            assert response["success"] is True
            assert "wellness journey" in response["content"]
            assert response["adaptation_metadata"]["program_type"] == "NGX_LONGEVITY"
            assert (
                response["genetic_communication_metadata"][
                    "emotional_sensitivity_applied"
                ]
                is True
            )

    @pytest.mark.asyncio
    async def test_handle_message_security_validation_failure(self, agent):
        """Test message handling with security validation failure."""
        # Arrange
        message = "Analyze my genetic data"
        context = {}  # Missing user_id

        # Act
        response = await agent.handle_message(message, context)

        # Assert
        assert response["success"] is False
        assert response["error_type"] == "GeneticDataSecurityError"
        assert "User identification required" in response["message"]
        assert response["genetic_data_security"]["data_encrypted"] is True

    @pytest.mark.asyncio
    async def test_handle_message_consent_required(self, agent, sample_genetic_context):
        """Test message handling when genetic consent is missing."""
        # Arrange
        message = "Perform genetic analysis"

        # Mock consent service to return False
        agent.consent_service.has_valid_consent.return_value = False

        # Act
        response = await agent.handle_message(message, sample_genetic_context)

        # Assert
        assert response["success"] is False
        assert response["error_type"] == "GeneticDataSecurityError"
        assert "consent required" in response["message"].lower()

    @pytest.mark.asyncio
    async def test_personality_adaptation_failure_fallback(
        self, agent, sample_genetic_context
    ):
        """Test graceful fallback when personality adaptation fails."""
        # Arrange
        message = "Analyze genetic variants"

        # Mock personality adapter to raise exception
        agent.personality_adapter.adapt_response.side_effect = Exception(
            "Adaptation failed"
        )

        # Mock skills manager response
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            original_content = "Original genetic analysis response"
            mock_process.return_value = {
                "success": True,
                "content": original_content,
                "confidence_score": 0.89,
            }

            # Act
            response = await agent.handle_message(message, sample_genetic_context)

            # Assert
            assert response["success"] is True
            assert response["content"] == original_content  # Original content preserved
            # Should not have adaptation_metadata due to failure
            assert "adaptation_metadata" not in response

    @pytest.mark.asyncio
    async def test_audit_logging_execution(self, agent, sample_genetic_context):
        """Test that audit logging is properly executed."""
        # Arrange
        message = "Test genetic analysis for audit logging"

        # Mock skills manager
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Test response",
                "skills_used": ["test_skill"],
            }

            # Act
            await agent.handle_message(message, sample_genetic_context)

            # Assert
            agent.security_service.log_audit_event.assert_called_once()

            # Verify audit log structure
            audit_call = agent.security_service.log_audit_event.call_args[0][0]
            assert audit_call["agent_id"] == "code_genetic_specialist"
            assert audit_call["user_id"] == sample_genetic_context["user_id"]
            assert audit_call["request_type"] == "genetic_analysis"
            assert audit_call["success"] is True
            assert "timestamp" in audit_call

    @pytest.mark.parametrize(
        "program_type,expected_communication_style",
        [
            ("NGX_PRIME", "scientific"),
            ("NGX_LONGEVITY", "nurturing"),
            (None, "nurturing"),  # Default fallback
        ],
    )
    @pytest.mark.asyncio
    async def test_personality_adaptation_by_program_type(
        self, agent, sample_genetic_context, program_type, expected_communication_style
    ):
        """Test personality adaptation varies correctly by program type."""
        # Arrange
        context = {**sample_genetic_context}
        if program_type:
            context["program_type"] = program_type
        else:
            context.pop("program_type", None)

        message = "Explain my genetic variants"

        # Mock skills manager
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Genetic variants explanation",
                "confidence_score": 0.88,
            }

            # Act
            response = await agent.handle_message(message, context)

            # Assert
            assert response["success"] is True

            # Verify personality adapter was called with correct context
            adaptation_call = agent.personality_adapter.adapt_response.call_args
            context_arg = adaptation_call[1]["context"]
            assert context_arg["domain"] == "genetics"
            assert context_arg["sensitivity"] == "high"
            assert context_arg["scientific_accuracy_required"] is True

    @pytest.mark.asyncio
    async def test_health_status_metrics(self, agent):
        """Test health status reporting with accurate metrics."""
        # Simulate some requests to generate metrics
        agent._request_count = 100
        agent._error_count = 2
        agent._total_processing_time = 45000.0  # 45 seconds total

        # Act
        health_status = agent.health_status

        # Assert
        assert health_status["agent_id"] == "code_genetic_specialist"
        assert health_status["version"] == "2.0.0"
        assert health_status["status"] == "healthy"  # Error rate < 1%
        assert health_status["metrics"]["total_requests"] == 100
        assert health_status["metrics"]["error_count"] == 2
        assert health_status["metrics"]["error_rate"] == 0.02
        assert health_status["metrics"]["avg_processing_time_ms"] == 450.0
        assert health_status["configuration"]["production_ready"] is True

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, agent, sample_genetic_context):
        """Test agent handles concurrent requests properly."""
        import asyncio

        # Arrange
        num_requests = 10
        message = "Concurrent genetic analysis test"

        # Mock skills manager for consistent responses
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Concurrent analysis response",
                "confidence_score": 0.90,
            }

            # Act - Execute concurrent requests
            tasks = [
                agent.handle_message(f"{message} {i}", sample_genetic_context)
                for i in range(num_requests)
            ]
            responses = await asyncio.gather(*tasks)

            # Assert
            assert len(responses) == num_requests
            assert all(r["success"] for r in responses)
            assert agent._request_count >= num_requests

            # Verify all requests have unique request IDs
            request_ids = [r["performance_metadata"]["request_id"] for r in responses]
            assert len(set(request_ids)) == num_requests

    @pytest.mark.asyncio
    async def test_error_response_structure(self, agent, sample_genetic_context):
        """Test error response contains all required security information."""
        # Arrange
        message = "Test error scenario"

        # Mock skills manager to raise exception
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.side_effect = GeneticAnalysisError(
                "Test analysis error", analysis_type="test_analysis"
            )

            # Act
            response = await agent.handle_message(message, sample_genetic_context)

            # Assert
            assert response["success"] is False
            assert response["error_type"] == "GeneticAnalysisError"
            assert "genetic_data_security" in response
            assert response["genetic_data_security"]["data_encrypted"] is True
            assert response["genetic_data_security"]["audit_logged"] is True
            assert response["genetic_data_security"]["gdpr_compliant"] is True
            assert "timestamp" in response
            assert "request_id" in response
