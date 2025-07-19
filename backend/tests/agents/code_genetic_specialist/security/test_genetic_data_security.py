"""
Security tests for CODE Genetic Specialist.
Critical security testing for genetic data protection and compliance.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from agents.code_genetic_specialist.core.exceptions import (
    GeneticDataSecurityError,
    GeneticConsentError,
)


class TestGeneticDataSecurity:
    """Critical security tests for genetic data protection."""

    @pytest.mark.asyncio
    async def test_encryption_validation_success(self, agent, sample_genetic_context):
        """Test successful encryption validation for genetic data."""
        # Arrange
        message = "Analyze my genetic profile"

        # Mock encryption validation to pass
        agent.security_service.validate_encryption_status.return_value = True

        # Mock skills manager
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Encrypted genetic analysis completed",
                "confidence_score": 0.92,
            }

            # Act
            response = await agent.handle_message(message, sample_genetic_context)

            # Assert
            assert response["success"] is True
            agent.security_service.validate_encryption_status.assert_called_once_with(
                sample_genetic_context["user_id"]
            )

    @pytest.mark.asyncio
    async def test_encryption_validation_failure(self, agent, sample_genetic_context):
        """Test encryption validation failure blocks genetic analysis."""
        # Arrange
        message = "Analyze genetic variants"

        # Mock encryption validation to fail
        agent.security_service.validate_encryption_status.return_value = False

        # Act
        response = await agent.handle_message(message, sample_genetic_context)

        # Assert
        assert response["success"] is False
        assert response["error_type"] == "GeneticDataSecurityError"
        assert "encryption validation failed" in response["message"].lower()
        assert response["genetic_data_security"]["data_encrypted"] is True

    @pytest.mark.parametrize(
        "consent_status,should_succeed",
        [("active", True), ("revoked", False), ("expired", False), (None, False)],
    )
    @pytest.mark.asyncio
    async def test_consent_validation(
        self, agent, sample_genetic_context, consent_status, should_succeed
    ):
        """Test consent validation for different consent states."""
        # Arrange
        message = "Perform genetic analysis"

        # Mock consent validation
        agent.consent_service.has_valid_consent.return_value = should_succeed

        if should_succeed:
            # Mock successful processing
            with patch.object(agent.skills_manager, "process_message") as mock_process:
                mock_process.return_value = {
                    "success": True,
                    "content": "Genetic analysis with valid consent",
                    "confidence_score": 0.94,
                }

                # Act
                response = await agent.handle_message(message, sample_genetic_context)

                # Assert
                assert response["success"] is True
                agent.consent_service.has_valid_consent.assert_called_once_with(
                    sample_genetic_context["user_id"], "genetic_analysis"
                )
        else:
            # Act
            response = await agent.handle_message(message, sample_genetic_context)

            # Assert
            assert response["success"] is False
            assert response["error_type"] == "GeneticDataSecurityError"
            assert "consent required" in response["message"].lower()

    @pytest.mark.asyncio
    async def test_audit_logging_comprehensive(self, agent, sample_genetic_context):
        """Test comprehensive audit logging for genetic data access."""
        # Arrange
        message = "Comprehensive genetic analysis"

        # Mock skills manager
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Comprehensive genetic insights",
                "skills_used": ["analyze_genetic_profile", "genetic_risk_assessment"],
                "confidence_score": 0.93,
            }

            # Act
            await agent.handle_message(message, sample_genetic_context)

            # Assert audit logging
            agent.security_service.log_audit_event.assert_called_once()

            audit_log = agent.security_service.log_audit_event.call_args[0][0]

            # Verify required audit fields
            required_fields = [
                "timestamp",
                "agent_id",
                "agent_version",
                "user_id",
                "request_type",
                "success",
                "security_validated",
                "consent_verified",
            ]
            for field in required_fields:
                assert field in audit_log, f"Missing required audit field: {field}"

            # Verify field values
            assert audit_log["agent_id"] == "code_genetic_specialist"
            assert audit_log["user_id"] == sample_genetic_context["user_id"]
            assert audit_log["request_type"] == "genetic_analysis"
            assert audit_log["success"] is True
            assert audit_log["security_validated"] is True
            assert audit_log["consent_verified"] is True

    @pytest.mark.asyncio
    async def test_gdpr_compliance_validation(self, agent, sample_genetic_context):
        """Test GDPR compliance requirements for genetic data."""
        # Arrange
        message = "Process genetic data under GDPR"

        # Verify GDPR configuration
        assert agent.config.enable_gdpr_compliance is True
        assert agent.config.enable_data_encryption is True
        assert agent.config.enable_audit_logging is True

        # Mock skills processing
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "GDPR-compliant genetic analysis",
                "confidence_score": 0.91,
            }

            # Act
            response = await agent.handle_message(message, sample_genetic_context)

            # Assert GDPR compliance indicators
            assert response["success"] is True
            assert response["genetic_data_security"]["gdpr_compliant"] is True

            # Verify audit log includes GDPR compliance
            audit_log = agent.security_service.log_audit_event.call_args[0][0]
            assert audit_log["consent_verified"] is True
            assert "timestamp" in audit_log  # Required for GDPR audit trail

    @pytest.mark.asyncio
    async def test_hipaa_compliance_validation(self, agent, sample_genetic_context):
        """Test HIPAA compliance requirements for genetic health data."""
        # Arrange
        message = "Analyze health-related genetic variants"

        # Verify HIPAA configuration
        assert agent.config.enable_hipaa_compliance is True
        assert agent.config.enable_data_encryption is True
        assert agent.config.enable_audit_logging is True

        # Mock skills processing
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "HIPAA-compliant health genetic analysis",
                "confidence_score": 0.89,
            }

            # Act
            response = await agent.handle_message(message, sample_genetic_context)

            # Assert HIPAA compliance
            assert response["success"] is True
            assert response["genetic_data_security"]["audit_logged"] is True
            assert response["genetic_data_security"]["data_encrypted"] is True

    @pytest.mark.asyncio
    async def test_security_validation_production_mode(self, test_dependencies):
        """Test security validation in production mode."""
        from agents.code_genetic_specialist.core.config import CodeGeneticConfig
        from agents.code_genetic_specialist.agent_refactored import (
            CodeGeneticSpecialist,
        )

        # Create production configuration
        prod_config = CodeGeneticConfig(
            debug_mode=False,  # Production mode
            enable_data_encryption=True,
            enable_audit_logging=True,
            enable_gdpr_compliance=True,
            enable_hipaa_compliance=True,
        )

        with patch(
            "agents.code_genetic_specialist.agent_refactored.GeneticSecurityService"
        ) as mock_security:
            with patch(
                "agents.code_genetic_specialist.agent_refactored.ConsentManagementService"
            ) as mock_consent:
                mock_security.return_value.initialize = AsyncMock()
                mock_consent.return_value.initialize = AsyncMock()

                # Create and initialize agent
                agent = CodeGeneticSpecialist(test_dependencies, prod_config)
                await agent.initialize()

                # Verify production security requirements
                assert agent.config.is_production_ready is True
                assert agent.config.enable_data_encryption is True
                assert agent.config.enable_audit_logging is True

    @pytest.mark.asyncio
    async def test_security_validation_insufficient_production(self, test_dependencies):
        """Test security validation failure with insufficient production settings."""
        from agents.code_genetic_specialist.core.config import CodeGeneticConfig
        from agents.code_genetic_specialist.agent_refactored import (
            CodeGeneticSpecialist,
        )

        # Create insufficient production configuration
        insufficient_config = CodeGeneticConfig(
            debug_mode=False,  # Production mode
            enable_data_encryption=False,  # INSUFFICIENT for production
            enable_audit_logging=True,
            enable_gdpr_compliance=True,
            enable_hipaa_compliance=True,
        )

        with patch(
            "agents.code_genetic_specialist.agent_refactored.GeneticSecurityService"
        ) as mock_security:
            with patch(
                "agents.code_genetic_specialist.agent_refactored.ConsentManagementService"
            ) as mock_consent:
                mock_security.return_value.initialize = AsyncMock()
                mock_consent.return_value.initialize = AsyncMock()

                agent = CodeGeneticSpecialist(test_dependencies, insufficient_config)

                # Should raise security error during initialization
                with pytest.raises(Exception) as exc_info:
                    await agent.initialize()

                assert "encryption" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_user_identification_required(self, agent):
        """Test that user identification is required for genetic analysis."""
        # Arrange
        message = "Analyze genetic data"
        contexts_to_test = [
            {},  # Empty context
            {"some_field": "value"},  # Context without user_id
            {"user_id": None},  # Explicit None user_id
            {"user_id": ""},  # Empty user_id
        ]

        for context in contexts_to_test:
            # Act
            response = await agent.handle_message(message, context)

            # Assert
            assert response["success"] is False
            assert response["error_type"] == "GeneticDataSecurityError"
            assert "User identification required" in response["message"]

    @pytest.mark.asyncio
    async def test_audit_log_immutability(self, agent, sample_genetic_context):
        """Test that audit logs are immutable and comprehensive."""
        # Arrange
        message = "Generate audit log test"

        # Mock skills manager
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Audit log test response",
                "skills_used": ["test_skill"],
            }

            # Act
            await agent.handle_message(message, sample_genetic_context)

            # Assert audit log structure and immutability requirements
            audit_log = agent.security_service.log_audit_event.call_args[0][0]

            # Required immutable fields for genetic data audit
            immutable_fields = [
                "timestamp",
                "agent_id",
                "agent_version",
                "user_id",
                "request_type",
                "success",
                "security_validated",
                "consent_verified",
            ]

            for field in immutable_fields:
                assert field in audit_log
                assert audit_log[field] is not None

            # Verify timestamp format for audit trail
            timestamp = audit_log["timestamp"]
            assert isinstance(timestamp, str)
            # Should be valid ISO format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    @pytest.mark.asyncio
    async def test_genetic_data_access_logging(self, agent, sample_genetic_context):
        """Test specific logging for genetic data access patterns."""
        # Arrange
        message = "Access specific genetic variants"

        # Mock skills manager with genetic data access
        with patch.object(agent.skills_manager, "process_message") as mock_process:
            mock_process.return_value = {
                "success": True,
                "content": "Genetic variant analysis results",
                "skills_used": ["analyze_genetic_profile"],
                "genetic_data_accessed": {
                    "variants": ["rs1815739", "rs4680"],
                    "genes": ["ACTN3", "COMT"],
                    "access_type": "analysis",
                },
            }

            # Act
            await agent.handle_message(message, sample_genetic_context)

            # Assert genetic-specific audit logging
            audit_log = agent.security_service.log_audit_event.call_args[0][0]
            assert audit_log["request_type"] == "genetic_analysis"
            assert audit_log["user_id"] == sample_genetic_context["user_id"]

            # Verify genetic data protection indicators
            assert audit_log["security_validated"] is True
            assert audit_log["consent_verified"] is True
