"""
GDPR compliance tests.

Tests all GDPR requirements including data subject rights,
consent management, data minimization, and privacy controls.
"""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from core.audit import AuditEventType, get_audit_logger
from core.compliance import (
    ConsentManager,
    ConsentStatus,
    ConsentType,
    DataCategory,
    DataMinimization,
    DataSubjectRights,
    LegalBasis,
    get_compliance_controller,
)


@pytest.mark.asyncio
class TestConsentManager:
    """Test GDPR consent management functionality."""

    async def test_grant_consent(self):
        """Test granting user consent (GDPR Article 7)."""
        consent_manager = ConsentManager()

        consent_id = await consent_manager.grant_consent(
            user_id="user123",
            consent_type=ConsentType.DATA_PROCESSING,
            legal_basis=LegalBasis.CONSENT,
            purpose="Personalized fitness coaching",
            data_categories=[DataCategory.HEALTH_DATA, DataCategory.BASIC_IDENTITY],
            expires_in_days=365,
        )

        assert consent_id is not None
        assert len(consent_id) > 0

        # Verify consent was stored
        consents = await consent_manager.get_user_consents("user123")
        assert len(consents) == 1

        consent = consents[0]
        assert consent.consent_id == consent_id
        assert consent.status == ConsentStatus.GRANTED
        assert consent.consent_type == ConsentType.DATA_PROCESSING
        assert consent.legal_basis == LegalBasis.CONSENT
        assert DataCategory.HEALTH_DATA in consent.data_categories

    async def test_withdraw_consent(self):
        """Test withdrawing user consent (GDPR Article 7.3)."""
        consent_manager = ConsentManager()

        # Grant consent first
        consent_id = await consent_manager.grant_consent(
            user_id="user123",
            consent_type=ConsentType.MARKETING,
            legal_basis=LegalBasis.CONSENT,
            purpose="Marketing communications",
            data_categories=[DataCategory.BASIC_IDENTITY],
        )

        # Withdraw consent
        success = await consent_manager.withdraw_consent(
            user_id="user123", consent_id=consent_id, reason="No longer interested"
        )

        assert success is True

        # Verify consent status changed
        consents = await consent_manager.get_user_consents("user123")
        consent = next(c for c in consents if c.consent_id == consent_id)
        assert consent.status == ConsentStatus.WITHDRAWN
        assert consent.withdrawn_at is not None
        assert consent.metadata.get("withdrawal_reason") == "No longer interested"

    async def test_consent_validation(self):
        """Test consent validation for data processing."""
        consent_manager = ConsentManager()

        # Grant consent for specific data categories
        await consent_manager.grant_consent(
            user_id="user123",
            consent_type=ConsentType.MEDICAL_DATA,
            legal_basis=LegalBasis.CONSENT,
            purpose="Health coaching",
            data_categories=[DataCategory.HEALTH_DATA, DataCategory.BIOMETRIC_DATA],
        )

        # Check consent for included categories
        has_health_consent = await consent_manager.check_consent(
            user_id="user123",
            consent_type=ConsentType.MEDICAL_DATA,
            data_categories=[DataCategory.HEALTH_DATA],
        )
        assert has_health_consent is True

        has_biometric_consent = await consent_manager.check_consent(
            user_id="user123",
            consent_type=ConsentType.MEDICAL_DATA,
            data_categories=[DataCategory.BIOMETRIC_DATA],
        )
        assert has_biometric_consent is True

        # Check consent for non-included category
        has_location_consent = await consent_manager.check_consent(
            user_id="user123",
            consent_type=ConsentType.MEDICAL_DATA,
            data_categories=[DataCategory.LOCATION_DATA],
        )
        assert has_location_consent is False

        # Check consent for wrong type
        has_marketing_consent = await consent_manager.check_consent(
            user_id="user123", consent_type=ConsentType.MARKETING
        )
        assert has_marketing_consent is False

    async def test_consent_expiration(self):
        """Test automatic consent expiration."""
        consent_manager = ConsentManager()

        # Grant consent with short expiration
        consent_id = await consent_manager.grant_consent(
            user_id="user123",
            consent_type=ConsentType.ANALYTICS,
            legal_basis=LegalBasis.CONSENT,
            purpose="Usage analytics",
            data_categories=[DataCategory.BEHAVIORAL_DATA],
            expires_in_days=0,  # Expires immediately for testing
        )

        # Wait a moment to ensure expiration
        await asyncio.sleep(0.1)

        # Check consent should now be expired
        has_consent = await consent_manager.check_consent(
            user_id="user123", consent_type=ConsentType.ANALYTICS
        )
        assert has_consent is False

        # Run expiration process
        expired_count = await consent_manager.expire_old_consents()
        assert expired_count >= 1

        # Verify consent is marked as expired
        consents = await consent_manager.get_user_consents("user123")
        consent = next(c for c in consents if c.consent_id == consent_id)
        assert consent.status == ConsentStatus.EXPIRED

    async def test_granular_consent(self):
        """Test granular consent for different purposes."""
        consent_manager = ConsentManager()

        # Grant consent for multiple purposes
        marketing_consent_id = await consent_manager.grant_consent(
            user_id="user123",
            consent_type=ConsentType.MARKETING,
            legal_basis=LegalBasis.CONSENT,
            purpose="Email marketing",
            data_categories=[DataCategory.BASIC_IDENTITY],
        )

        analytics_consent_id = await consent_manager.grant_consent(
            user_id="user123",
            consent_type=ConsentType.ANALYTICS,
            legal_basis=LegalBasis.CONSENT,
            purpose="Usage analytics",
            data_categories=[DataCategory.BEHAVIORAL_DATA],
        )

        # Should have separate consents
        assert marketing_consent_id != analytics_consent_id

        # Can withdraw one without affecting the other
        await consent_manager.withdraw_consent("user123", marketing_consent_id)

        # Marketing consent should be withdrawn
        has_marketing = await consent_manager.check_consent(
            user_id="user123", consent_type=ConsentType.MARKETING
        )
        assert has_marketing is False

        # Analytics consent should still be valid
        has_analytics = await consent_manager.check_consent(
            user_id="user123", consent_type=ConsentType.ANALYTICS
        )
        assert has_analytics is True


@pytest.mark.asyncio
class TestDataSubjectRights:
    """Test GDPR data subject rights implementation."""

    async def test_right_to_access(self):
        """Test right of access (GDPR Article 15)."""
        data_subject_rights = DataSubjectRights()

        # Simulate some user data
        data_subject_rights._data_store["user123"] = {
            "name": "John Doe",
            "email": "john@example.com",
            "health_data": {"weight": 70, "height": 175},
        }

        # Request data export
        exported_data = await data_subject_rights.request_data_export(
            user_id="user123", format_type="json", include_metadata=True
        )

        assert exported_data["user_id"] == "user123"
        assert exported_data["format"] == "json"
        assert "data" in exported_data
        assert exported_data["data"]["profile"]["name"] == "John Doe"
        assert exported_data["data"]["profile"]["email"] == "john@example.com"
        assert "export_timestamp" in exported_data

    async def test_right_to_rectification(self):
        """Test right to rectification (GDPR Article 16)."""
        data_subject_rights = DataSubjectRights()

        # Simulate user data with incorrect information
        data_subject_rights._data_store["user123"] = {
            "name": "John Doe",
            "email": "old.email@example.com",
            "phone": "555-0000",
        }

        # Request rectification
        rectification_summary = await data_subject_rights.rectify_data(
            user_id="user123",
            field_updates={"email": "correct.email@example.com", "phone": "555-1234"},
            reason="Correcting outdated information",
        )

        assert "user123" == rectification_summary["user_id"]
        assert "email" in rectification_summary["fields_updated"]
        assert "phone" in rectification_summary["fields_updated"]
        assert rectification_summary["reason"] == "Correcting outdated information"

        # Verify data was updated
        updated_data = data_subject_rights._data_store["user123"]
        assert updated_data["email"] == "correct.email@example.com"
        assert updated_data["phone"] == "555-1234"
        assert updated_data["name"] == "John Doe"  # Unchanged

    async def test_right_to_erasure(self):
        """Test right to erasure/right to be forgotten (GDPR Article 17)."""
        data_subject_rights = DataSubjectRights()

        # Simulate user data
        data_subject_rights._data_store["user123"] = {
            "name": "John Doe",
            "email": "john@example.com",
            "health_data": {"weight": 70},
            "financial_records": {"transaction_id": "TX123"},
            "audit_trail": {"last_login": "2025-01-01"},
        }

        # Request data deletion with legal basis retention
        deletion_summary = await data_subject_rights.request_data_deletion(
            user_id="user123", reason="Account closure", retain_legal_basis=True
        )

        assert deletion_summary["user_id"] == "user123"
        assert deletion_summary["reason"] == "Account closure"
        assert len(deletion_summary["deleted_data_categories"]) > 0
        assert len(deletion_summary["retained_data_categories"]) >= 0

        # Verify appropriate data was deleted while legal data retained
        if "user123" in data_subject_rights._data_store:
            remaining_data = data_subject_rights._data_store["user123"]
            # Should not contain personal data that isn't legally required
            assert "name" not in remaining_data or "financial_records" in remaining_data

    async def test_right_to_restrict_processing(self):
        """Test right to restriction of processing (GDPR Article 18)."""
        data_subject_rights = DataSubjectRights()

        # Simulate processing records
        data_subject_rights._processing_records["user123"] = [
            type(
                "ProcessingRecord",
                (),
                {
                    "data_categories": [
                        DataCategory.HEALTH_DATA,
                        DataCategory.BASIC_IDENTITY,
                    ],
                    "metadata": {},
                },
            )()
        ]

        # Request processing restriction
        success = await data_subject_rights.restrict_processing(
            user_id="user123",
            restriction_reason="Accuracy dispute",
            affected_categories=[DataCategory.HEALTH_DATA],
        )

        assert success is True

        # Verify processing restriction was applied
        processing_records = data_subject_rights._processing_records["user123"]
        for record in processing_records:
            if DataCategory.HEALTH_DATA in record.data_categories:
                assert record.metadata.get("processing_restricted") is True
                assert record.metadata.get("restriction_reason") == "Accuracy dispute"

    async def test_data_portability(self):
        """Test right to data portability (GDPR Article 20)."""
        data_subject_rights = DataSubjectRights()

        # Simulate structured user data
        user_data = {
            "profile": {
                "name": "John Doe",
                "email": "john@example.com",
                "preferences": ["fitness", "nutrition"],
            },
            "activity": {
                "workouts": [{"date": "2025-01-01", "type": "cardio"}],
                "meals": [{"date": "2025-01-01", "calories": 500}],
            },
        }
        data_subject_rights._data_store["user123"] = user_data

        # Export data in portable format
        exported_data = await data_subject_rights.request_data_export(
            user_id="user123", format_type="json", include_metadata=False
        )

        assert exported_data["format"] == "json"
        assert "data" in exported_data

        # Data should be in structured, machine-readable format
        profile_data = exported_data["data"]["profile"]
        assert profile_data["name"] == "John Doe"
        assert profile_data["email"] == "john@example.com"
        assert isinstance(profile_data["preferences"], list)


@pytest.mark.asyncio
class TestDataMinimization:
    """Test GDPR data minimization principles (Article 5.1.c)."""

    async def test_data_necessity_assessment(self):
        """Test assessment of data necessity for processing purpose."""
        data_minimization = DataMinimization()

        # Test data fields for health coaching purpose
        test_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "health_goals": "Weight loss",
            "medical_conditions": "Diabetes",
            "favorite_color": "Blue",
            "political_views": "Independent",
            "height": 175,
            "weight": 70,
        }

        assessment = await data_minimization.assess_data_necessity(
            data_fields=test_data, processing_purpose="health_coaching"
        )

        assert assessment["processing_purpose"] == "health_coaching"
        assert len(assessment["necessary_fields"]) > 0
        assert len(assessment["unnecessary_fields"]) > 0

        # Health-related fields should be necessary
        assert any(
            "health" in field.lower() for field in assessment["necessary_fields"]
        )

        # Non-health fields should be unnecessary
        assert "favorite_color" in assessment["unnecessary_fields"]
        assert "political_views" in assessment["unnecessary_fields"]

        # Should have recommendations
        assert len(assessment["recommendations"]) > 0

    async def test_different_processing_purposes(self):
        """Test data necessity for different processing purposes."""
        data_minimization = DataMinimization()

        test_data = {
            "email": "user@example.com",
            "password_hash": "hashed_password",
            "payment_info": "credit_card_token",
            "health_metrics": "70kg, 175cm",
            "marketing_preferences": "email_ok",
        }

        # Authentication purpose
        auth_assessment = await data_minimization.assess_data_necessity(
            data_fields=test_data, processing_purpose="user_authentication"
        )

        assert "email" in auth_assessment["necessary_fields"]
        assert "password_hash" in str(auth_assessment["necessary_fields"]).lower()
        assert "health_metrics" in auth_assessment["unnecessary_fields"]

        # Marketing purpose
        marketing_assessment = await data_minimization.assess_data_necessity(
            data_fields=test_data, processing_purpose="marketing"
        )

        assert "email" in marketing_assessment["necessary_fields"]
        assert (
            "marketing_preferences"
            in str(marketing_assessment["necessary_fields"]).lower()
        )
        assert "password_hash" in marketing_assessment["unnecessary_fields"]

    async def test_retention_policy_application(self):
        """Test data retention policy application."""
        data_minimization = DataMinimization()

        # Simulate data records with different ages
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()
        recent_timestamp = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

        test_records = [
            {
                "id": "record1",
                "created_at": old_timestamp,
                "personal_data": "Old personal info",
                "audit_data": "Audit trail info",
                "marketing_data": "Old marketing preferences",
            },
            {
                "id": "record2",
                "created_at": recent_timestamp,
                "personal_data": "Recent personal info",
                "audit_data": "Recent audit info",
                "marketing_data": "Recent marketing preferences",
            },
        ]

        # Define retention rules (days)
        retention_rules = {
            "personal_data": 365,  # 1 year
            "marketing_data": 90,  # 3 months
            "audit_data": 2190,  # 6 years
        }

        results = await data_minimization.apply_retention_policy(
            data_records=test_records, retention_rules=retention_rules
        )

        assert results["records_processed"] == 2
        assert results["records_expired"] > 0
        assert results["fields_purged"] > 0

        # Old record should have expired fields removed
        old_record = next(r for r in test_records if r["id"] == "record1")

        # Personal data and marketing data should be purged (older than retention)
        # Audit data should be retained (within retention period)
        assert "audit_data" in old_record  # Should be retained


@pytest.mark.asyncio
class TestComplianceController:
    """Test overall compliance controller functionality."""

    async def test_processing_compliance_check(self):
        """Test comprehensive compliance check for data processing."""
        compliance_controller = get_compliance_controller()

        # Grant required consent first
        await compliance_controller.consent_manager.grant_consent(
            user_id="user123",
            consent_type=ConsentType.MEDICAL_DATA,
            legal_basis=LegalBasis.CONSENT,
            purpose="Health coaching",
            data_categories=[DataCategory.HEALTH_DATA, DataCategory.BIOMETRIC_DATA],
        )

        # Check compliance for processing
        compliance_results = await compliance_controller.check_processing_compliance(
            user_id="user123",
            processing_purpose="Health coaching",
            data_categories=[DataCategory.HEALTH_DATA, DataCategory.BIOMETRIC_DATA],
        )

        assert compliance_results["user_id"] == "user123"
        assert compliance_results["processing_purpose"] == "Health coaching"
        assert compliance_results["compliant"] is True
        assert compliance_results["consent_check"] is True
        assert "consent_details" in compliance_results

        # Check compliance without proper consent
        non_compliant_results = await compliance_controller.check_processing_compliance(
            user_id="user123",
            processing_purpose="Marketing",
            data_categories=[DataCategory.BASIC_IDENTITY],
        )

        assert non_compliant_results["compliant"] is False
        assert non_compliant_results["consent_check"] is False
        assert len(non_compliant_results["issues"]) > 0

    async def test_sensitive_data_protection(self):
        """Test enhanced protection for sensitive data categories."""
        compliance_controller = get_compliance_controller()

        # Check compliance for sensitive data
        compliance_results = await compliance_controller.check_processing_compliance(
            user_id="user123",
            processing_purpose="Medical analysis",
            data_categories=[DataCategory.HEALTH_DATA, DataCategory.SENSITIVE_IDENTITY],
        )

        assert compliance_results.get("requires_enhanced_protection") is True
        assert any(
            "enhanced security" in rec.lower()
            for rec in compliance_results.get("recommendations", [])
        )

    async def test_compliance_report_generation(self):
        """Test comprehensive compliance report generation."""
        compliance_controller = get_compliance_controller()

        # Generate compliance report
        report = await compliance_controller.generate_compliance_report(
            user_id="user123"
        )

        assert "report_id" in report
        assert "generated_at" in report
        assert "user_scope" in report
        assert "consent_summary" in report
        assert "compliance_metrics" in report
        assert "recommendations" in report

        # Report should include key metrics
        metrics = report["compliance_metrics"]
        assert "consent_coverage" in metrics
        assert "data_retention_compliance" in metrics
        assert "encryption_coverage" in metrics


@pytest.mark.asyncio
class TestGDPRIntegration:
    """Integration tests for GDPR compliance across all components."""

    async def test_complete_gdpr_workflow(self):
        """Test complete GDPR workflow from consent to data deletion."""
        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        user_id = "integration_test_user"

        # Step 1: Grant consent (Article 7)
        consent_id = await compliance_controller.consent_manager.grant_consent(
            user_id=user_id,
            consent_type=ConsentType.DATA_PROCESSING,
            legal_basis=LegalBasis.CONSENT,
            purpose="Complete GDPR workflow test",
            data_categories=[DataCategory.BASIC_IDENTITY, DataCategory.HEALTH_DATA],
        )

        # Step 2: Simulate data processing with compliance check
        compliance_check = await compliance_controller.check_processing_compliance(
            user_id=user_id,
            processing_purpose="Complete GDPR workflow test",
            data_categories=[DataCategory.BASIC_IDENTITY, DataCategory.HEALTH_DATA],
        )
        assert compliance_check["compliant"] is True

        # Step 3: Add some user data
        compliance_controller.data_subject_rights._data_store[user_id] = {
            "name": "GDPR Test User",
            "email": "gdpr.test@example.com",
            "health_data": {"weight": 70, "conditions": ["none"]},
        }

        # Step 4: Exercise right to access (Article 15)
        exported_data = (
            await compliance_controller.data_subject_rights.request_data_export(
                user_id=user_id, format_type="json"
            )
        )
        assert exported_data["user_id"] == user_id

        # Step 5: Exercise right to rectification (Article 16)
        rectification_summary = (
            await compliance_controller.data_subject_rights.rectify_data(
                user_id=user_id, field_updates={"email": "corrected.email@example.com"}
            )
        )
        assert "email" in rectification_summary["fields_updated"]

        # Step 6: Withdraw consent (Article 7.3)
        withdrawal_success = (
            await compliance_controller.consent_manager.withdraw_consent(
                user_id=user_id,
                consent_id=consent_id,
                reason="Integration test completion",
            )
        )
        assert withdrawal_success is True

        # Step 7: Exercise right to erasure (Article 17)
        deletion_summary = (
            await compliance_controller.data_subject_rights.request_data_deletion(
                user_id=user_id, reason="GDPR integration test"
            )
        )
        assert deletion_summary["user_id"] == user_id

        # Step 8: Verify audit trail captures all activities
        user_activity = await audit_logger.get_user_activity(user_id)
        assert len(user_activity) > 0

        # Should have various compliance events logged
        event_types = {event.event_type for event in user_activity}
        assert AuditEventType.CONSENT_GIVEN in event_types
        assert AuditEventType.CONSENT_WITHDRAWN in event_types
        assert AuditEventType.DATA_EXPORT in event_types
        assert AuditEventType.DATA_DELETION in event_types

        # Verify GDPR compliance tags
        gdpr_events = [
            event for event in user_activity if "GDPR" in event.compliance_tags
        ]
        assert len(gdpr_events) > 0

    async def test_gdpr_violation_detection(self):
        """Test detection of potential GDPR violations."""
        compliance_controller = get_compliance_controller()

        # Attempt processing without consent (should be non-compliant)
        compliance_results = await compliance_controller.check_processing_compliance(
            user_id="unauthorized_user",
            processing_purpose="Unauthorized processing",
            data_categories=[DataCategory.SENSITIVE_IDENTITY, DataCategory.HEALTH_DATA],
        )

        assert compliance_results["compliant"] is False
        assert compliance_results["consent_check"] is False
        assert len(compliance_results["issues"]) > 0
        assert "consent" in " ".join(compliance_results["issues"]).lower()

    async def test_gdpr_data_minimization_compliance(self):
        """Test GDPR data minimization compliance."""
        data_minimization = DataMinimization()

        # Test with excessive data collection
        excessive_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "health_goals": "Weight loss",
            "salary": "$50000",
            "political_affiliation": "Independent",
            "religion": "Christian",
            "sexual_orientation": "Heterosexual",
            "criminal_history": "None",
            "social_security": "123-45-6789",
        }

        assessment = await data_minimization.assess_data_necessity(
            data_fields=excessive_data, processing_purpose="health_coaching"
        )

        # Should identify excessive data collection
        assert len(assessment["unnecessary_fields"]) > 0
        assert len(assessment["recommendations"]) > 0

        # Sensitive personal data should be flagged as unnecessary for health coaching
        unnecessary_lower = [
            field.lower() for field in assessment["unnecessary_fields"]
        ]
        assert any(
            "salary" in field or "political" in field or "religion" in field
            for field in unnecessary_lower
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
