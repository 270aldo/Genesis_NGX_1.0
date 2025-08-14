"""
HIPAA compliance tests.

Tests all HIPAA requirements including PHI protection,
access controls, audit trails, and security safeguards.
"""

from datetime import datetime, timedelta, timezone

import pytest

from core.audit import AuditEventType, AuditSeverity, get_audit_logger
from core.compliance import get_compliance_controller
from core.data_anonymization import DataSensitivity, get_data_anonymizer
from core.security.encryption_service import (
    ComplianceFieldEncryption,
    decrypt_pii,
    encrypt_pii,
    get_encryption_service,
)


@pytest.mark.asyncio
class TestPHIProtection:
    """Test Protected Health Information (PHI) protection requirements."""

    async def test_phi_identification(self):
        """Test automatic PHI identification."""
        compliance_encryption = ComplianceFieldEncryption()

        # Test data containing PHI
        phi_data = {
            "patient_name": "John Doe",
            "medical_record_number": "MR123456",
            "diagnosis": "Type 2 Diabetes Mellitus",
            "treatment_plan": "Metformin 500mg twice daily",
            "physician": "Dr. Smith",
            "insurance_number": "INS987654321",
            "date_of_birth": "1980-01-15",
            "social_security": "123-45-6789",
            "phone_number": "555-123-4567",
            "address": "123 Main St, Anytown, ST 12345",
            "emergency_contact": "Jane Doe",
            "billing_info": "Account #12345",
        }

        # Identify sensitive fields
        sensitive_fields = compliance_encryption.identify_sensitive_fields(phi_data)

        # Medical information should be classified as PHI
        assert sensitive_fields.get("medical_record_number") == "PHI"
        assert sensitive_fields.get("diagnosis") == "PHI"
        assert sensitive_fields.get("treatment_plan") == "PHI"
        assert sensitive_fields.get("insurance_number") == "PHI"

        # Personal identifiers should be classified as PII
        assert sensitive_fields.get("patient_name") == "PII"
        assert sensitive_fields.get("date_of_birth") == "PII"
        assert sensitive_fields.get("social_security") == "PII"
        assert sensitive_fields.get("phone_number") == "PII"
        assert sensitive_fields.get("address") == "PII"

    async def test_phi_encryption(self):
        """Test PHI encryption with HIPAA-compliant metadata."""
        # Test medical data encryption
        medical_diagnosis = "Patient diagnosed with hypertension and diabetes"

        encrypted_phi = encrypt_pii(medical_diagnosis, data_type="medical")

        # Should have HIPAA compliance tags
        metadata = encrypted_phi["metadata"]
        assert "HIPAA" in metadata["compliance_tags"]
        assert "GDPR" in metadata["compliance_tags"]  # Dual compliance
        assert metadata["data_type"] == "medical"
        assert metadata["retention_period"] == "7_years"  # HIPAA requirement

        # Should be properly encrypted
        assert encrypted_phi["encrypted_data"] != medical_diagnosis

        # Should decrypt correctly
        decrypted = decrypt_pii(encrypted_phi)
        assert decrypted == medical_diagnosis

    async def test_phi_field_level_encryption(self):
        """Test field-level encryption for PHI data."""
        compliance_encryption = ComplianceFieldEncryption()

        medical_record = {
            "patient_id": "P123456",
            "name": "John Doe",
            "diagnosis": "Chronic kidney disease stage 3",
            "medications": ["Lisinopril 10mg", "Metformin 500mg"],
            "lab_results": {"creatinine": 1.8, "bun": 25},
            "provider": "Nephrology Associates",
            "last_visit": "2025-01-10",
        }

        # Encrypt sensitive data automatically
        encrypted_record = compliance_encryption.encrypt_sensitive_data(
            medical_record, auto_detect=True
        )

        # Medical fields should be encrypted with HIPAA compliance
        assert encrypted_record["diagnosis"]["_compliance"] is True
        assert "HIPAA" in encrypted_record["diagnosis"]["metadata"]["compliance_tags"]

        # Personal identifiers should be encrypted
        assert encrypted_record["name"]["_compliance"] is True

        # Verify audit trail
        audit_log = compliance_encryption.get_audit_log()
        phi_encryptions = [
            entry for entry in audit_log if entry["sensitivity_type"] == "PHI"
        ]
        assert len(phi_encryptions) > 0

    async def test_minimum_necessary_standard(self):
        """Test HIPAA minimum necessary standard implementation."""
        compliance_encryption = ComplianceFieldEncryption()

        # Full medical record
        full_record = {
            "patient_name": "John Doe",
            "mrn": "MR123456",
            "diagnosis": "Diabetes Type 2",
            "current_medications": ["Metformin"],
            "allergies": ["Penicillin"],
            "insurance_info": "Blue Cross 123456",
            "emergency_contact": "Jane Doe - 555-0123",
            "social_history": "Non-smoker, occasional alcohol",
            "family_history": "Father had diabetes",
            "lab_results": {"a1c": 7.2, "glucose": 150},
            "billing_address": "123 Main St",
        }

        # Simulate selective decryption for different purposes

        # For billing department - only need billing-related info
        billing_fields = ["patient_name", "mrn", "insurance_info", "billing_address"]

        # For pharmacy - only need medication-related info
        pharmacy_fields = ["patient_name", "mrn", "current_medications", "allergies"]

        # For clinical care - need comprehensive medical info
        clinical_fields = [
            "patient_name",
            "mrn",
            "diagnosis",
            "current_medications",
            "allergies",
            "lab_results",
            "social_history",
            "family_history",
        ]

        # Encrypt all fields first
        encrypted_record = compliance_encryption.encrypt_sensitive_data(full_record)

        # Test selective access patterns
        field_encryption = compliance_encryption

        billing_access = field_encryption.selective_decrypt(
            encrypted_record, billing_fields
        )
        pharmacy_access = field_encryption.selective_decrypt(
            encrypted_record, pharmacy_fields
        )
        clinical_access = field_encryption.selective_decrypt(
            encrypted_record, clinical_fields
        )

        # Verify minimum necessary access
        assert "insurance_info" in billing_access
        assert "diagnosis" not in billing_access or billing_access["diagnosis"].get(
            "_encrypted"
        )

        assert "current_medications" in pharmacy_access
        assert "billing_address" not in pharmacy_access or pharmacy_access[
            "billing_address"
        ].get("_encrypted")

        assert "diagnosis" in clinical_access
        assert "lab_results" in clinical_access


@pytest.mark.asyncio
class TestHIPAAAuditRequirements:
    """Test HIPAA audit and logging requirements."""

    async def test_phi_access_logging(self):
        """Test comprehensive PHI access logging."""
        audit_logger = get_audit_logger()

        # Log PHI access event
        event_id = await audit_logger.log_data_access(
            resource="medical_records",
            user_id="doctor_smith",
            action="Accessed patient medical record for treatment",
            ip_address="192.168.1.100",
            details={
                "patient_mrn": "MR123456",
                "access_reason": "routine_care",
                "data_types_accessed": ["diagnosis", "medications", "lab_results"],
                "access_method": "ehr_system",
            },
        )

        assert event_id is not None

        # Verify event was logged with proper compliance tags
        events = await audit_logger.storage.retrieve_events()
        access_event = next(e for e in events if e.event_id == event_id)

        assert access_event.event_type == AuditEventType.DATA_ACCESS
        assert access_event.resource == "medical_records"
        assert "HIPAA" in access_event.compliance_tags
        assert "PHI" in access_event.details.get("data_types_accessed", [])

        # HIPAA requires specific audit elements
        assert access_event.user_id is not None  # Who accessed
        assert access_event.timestamp is not None  # When accessed
        assert access_event.resource is not None  # What was accessed
        assert access_event.action is not None  # Action performed
        assert access_event.outcome is not None  # Success/failure

    async def test_phi_modification_tracking(self):
        """Test PHI modification tracking and audit."""
        audit_logger = get_audit_logger()

        # Log PHI modification
        event_id = await audit_logger.log_event(
            event_type=AuditEventType.DATA_UPDATE,
            action="Updated patient medication list",
            user_id="doctor_smith",
            ip_address="192.168.1.100",
            resource="patient_medications",
            details={
                "patient_mrn": "MR123456",
                "field_modified": "current_medications",
                "old_value": "Metformin 500mg",
                "new_value": "Metformin 500mg, Lisinopril 10mg",
                "reason": "Added blood pressure medication",
                "authorization": "physician_order",
            },
            severity=AuditSeverity.MEDIUM,
            compliance_tags=["HIPAA", "PHI"],
        )

        # Verify modification was properly logged
        events = await audit_logger.storage.retrieve_events()
        mod_event = next(e for e in events if e.event_id == event_id)

        assert mod_event.event_type == AuditEventType.DATA_UPDATE
        assert "HIPAA" in mod_event.compliance_tags
        assert "old_value" in mod_event.details
        assert "new_value" in mod_event.details
        assert "reason" in mod_event.details

    async def test_unauthorized_access_detection(self):
        """Test detection and logging of unauthorized PHI access attempts."""
        audit_logger = get_audit_logger()

        # Log unauthorized access attempt
        incident_id = await audit_logger.log_security_incident(
            incident_type="unauthorized_phi_access",
            severity=AuditSeverity.CRITICAL,
            details={
                "attempted_resource": "patient_records",
                "target_patient": "MR123456",
                "unauthorized_user": "intern_jones",
                "user_role": "medical_intern",
                "patient_relationship": "none",
                "access_denied_reason": "no_authorized_relationship",
                "detection_method": "automated_rbac_check",
            },
            user_id="intern_jones",
            ip_address="192.168.1.200",
        )

        # Verify incident was logged
        incidents = await audit_logger.get_security_incidents(
            severity=AuditSeverity.CRITICAL
        )

        unauthorized_incident = next(i for i in incidents if i.event_id == incident_id)
        assert unauthorized_incident.severity == AuditSeverity.CRITICAL
        assert "unauthorized_phi_access" in unauthorized_incident.action
        assert "SECURITY" in unauthorized_incident.compliance_tags

    async def test_audit_log_integrity(self):
        """Test audit log integrity and tamper protection."""
        audit_logger = get_audit_logger()

        # Create audit event
        event_id = await audit_logger.log_data_access(
            resource="phi_data",
            user_id="healthcare_provider",
            action="Accessed patient chart for diagnosis",
        )

        # Get the event
        events = await audit_logger.storage.retrieve_events()
        audit_event = next(e for e in events if e.event_id == event_id)

        # Calculate integrity hash
        original_hash = audit_event.get_hash()
        assert len(original_hash) == 64  # SHA-256

        # Verify hash is deterministic
        second_hash = audit_event.get_hash()
        assert original_hash == second_hash

        # Modify event and verify hash changes (tamper detection)
        audit_event.action = "Modified action"
        modified_hash = audit_event.get_hash()
        assert modified_hash != original_hash

    async def test_audit_retention_compliance(self):
        """Test HIPAA audit log retention requirements (6 years)."""
        audit_logger = get_audit_logger()

        # Create events with different timestamps
        current_time = datetime.now(timezone.utc)
        old_time = current_time - timedelta(days=2200)  # > 6 years
        recent_time = current_time - timedelta(days=1000)  # < 6 years

        # Log events (simulating different ages)
        await audit_logger.log_data_access(
            resource="phi_old", user_id="provider1", action="Old PHI access"
        )

        await audit_logger.log_data_access(
            resource="phi_recent", user_id="provider2", action="Recent PHI access"
        )

        # In a real implementation, would test retention policy enforcement
        # Here we verify events can be retrieved for compliance periods
        all_events = await audit_logger.storage.retrieve_events()

        # Should be able to retrieve recent events
        recent_events = await audit_logger.storage.retrieve_events(
            filters={
                "start_time": (
                    current_time - timedelta(days=1095)
                ).isoformat()  # 3 years
            }
        )

        assert len(recent_events) >= 1


@pytest.mark.asyncio
class TestHIPAAAccessControls:
    """Test HIPAA access control requirements."""

    async def test_unique_user_identification(self):
        """Test unique user identification requirement."""
        audit_logger = get_audit_logger()

        # Each user must have unique identifier
        users = ["doctor_smith", "nurse_johnson", "admin_williams", "intern_brown"]

        # Log access events for different users
        for user in users:
            await audit_logger.log_data_access(
                resource="phi_system",
                user_id=user,
                action=f"System access by {user}",
                details={"authentication_method": "secure_login"},
            )

        # Verify each user has unique identification in logs
        events = await audit_logger.storage.retrieve_events()
        user_ids = {event.user_id for event in events if event.user_id}

        assert len(user_ids) == len(users)
        assert all(user in user_ids for user in users)

    async def test_role_based_access_control(self):
        """Test role-based access control for PHI."""
        # Simulate RBAC system
        rbac_rules = {
            "physician": {
                "can_access": [
                    "diagnosis",
                    "treatment_plan",
                    "lab_results",
                    "medications",
                ],
                "can_modify": ["diagnosis", "treatment_plan", "medications"],
            },
            "nurse": {
                "can_access": ["vital_signs", "medications", "care_plan"],
                "can_modify": ["vital_signs", "care_plan"],
            },
            "pharmacist": {
                "can_access": ["medications", "allergies", "patient_name"],
                "can_modify": ["medication_dispensed"],
            },
            "billing_clerk": {
                "can_access": ["patient_name", "insurance", "billing_address"],
                "can_modify": ["billing_status"],
            },
        }

        audit_logger = get_audit_logger()

        # Test access for different roles
        for role, permissions in rbac_rules.items():
            for resource in permissions["can_access"]:
                await audit_logger.log_data_access(
                    resource=resource,
                    user_id=f"{role}_user",
                    action=f"Authorized {role} access to {resource}",
                    details={
                        "user_role": role,
                        "authorization_level": "granted",
                        "access_type": "read",
                    },
                )

        # Verify role-based access is logged
        events = await audit_logger.storage.retrieve_events()

        # Each role should have appropriate number of access events
        physician_events = [e for e in events if "physician" in e.user_id]
        nurse_events = [e for e in events if "nurse" in e.user_id]

        assert len(physician_events) == len(rbac_rules["physician"]["can_access"])
        assert len(nurse_events) == len(rbac_rules["nurse"]["can_access"])

    async def test_automatic_logoff(self):
        """Test automatic logoff requirement simulation."""
        audit_logger = get_audit_logger()

        # Log session start
        login_event_id = await audit_logger.log_authentication_event(
            event_type=AuditEventType.USER_LOGIN,
            user_id="healthcare_user",
            ip_address="192.168.1.50",
            outcome="success",
            details={
                "session_id": "session_12345",
                "authentication_method": "two_factor",
                "session_timeout": "30_minutes",
            },
        )

        # Log automatic logoff (simulated)
        logoff_event_id = await audit_logger.log_authentication_event(
            event_type=AuditEventType.USER_LOGOUT,
            user_id="healthcare_user",
            ip_address="192.168.1.50",
            outcome="success",
            details={
                "session_id": "session_12345",
                "logout_reason": "automatic_timeout",
                "session_duration": "30_minutes",
            },
        )

        # Verify both events logged
        events = await audit_logger.storage.retrieve_events()
        login_event = next(e for e in events if e.event_id == login_event_id)
        logoff_event = next(e for e in events if e.event_id == logoff_event_id)

        assert login_event.event_type == AuditEventType.USER_LOGIN
        assert logoff_event.event_type == AuditEventType.USER_LOGOUT
        assert login_event.details["session_id"] == logoff_event.details["session_id"]


@pytest.mark.asyncio
class TestHIPAADataIntegrity:
    """Test HIPAA data integrity requirements."""

    async def test_phi_integrity_verification(self):
        """Test PHI integrity verification and corruption detection."""
        encryption_service = get_encryption_service()

        # Create PHI data with integrity signature
        phi_data = "Patient John Doe, MRN: 123456, Diagnosis: Diabetes Type 2"

        # Encrypt with integrity protection
        encrypted_phi = encryption_service.encrypt_string(phi_data)
        signature = encryption_service.create_hmac_signature(
            encrypted_phi.encode("utf-8")
        )

        # Verify integrity with correct signature
        integrity_valid = encryption_service.verify_hmac_signature(
            encrypted_phi.encode("utf-8"), signature
        )
        assert integrity_valid is True

        # Test corruption detection
        tampered_data = encrypted_phi[:-10] + "tampered123"
        integrity_invalid = encryption_service.verify_hmac_signature(
            tampered_data.encode("utf-8"), signature
        )
        assert integrity_invalid is False

    async def test_phi_modification_controls(self):
        """Test PHI modification controls and versioning."""
        audit_logger = get_audit_logger()

        # Simulate PHI modification with proper controls
        phi_modifications = [
            {
                "field": "diagnosis",
                "old_value": "Pre-diabetes",
                "new_value": "Type 2 Diabetes Mellitus",
                "modifier": "dr_endocrinologist",
                "reason": "Lab results confirm diagnosis",
                "authorization": "clinical_assessment",
            },
            {
                "field": "medications",
                "old_value": "None",
                "new_value": "Metformin 500mg BID",
                "modifier": "dr_endocrinologist",
                "reason": "Initial diabetes treatment",
                "authorization": "prescription_order",
            },
        ]

        # Log each modification
        for mod in phi_modifications:
            await audit_logger.log_event(
                event_type=AuditEventType.DATA_UPDATE,
                action=f"PHI modification: {mod['field']}",
                user_id=mod["modifier"],
                resource="patient_record_MR123456",
                details={
                    "field_modified": mod["field"],
                    "previous_value": mod["old_value"],
                    "new_value": mod["new_value"],
                    "modification_reason": mod["reason"],
                    "authorization_type": mod["authorization"],
                    "data_integrity_check": "passed",
                },
                compliance_tags=["HIPAA", "PHI", "DATA_INTEGRITY"],
            )

        # Verify modification trail
        events = await audit_logger.storage.retrieve_events()
        modification_events = [
            e for e in events if e.event_type == AuditEventType.DATA_UPDATE
        ]

        assert len(modification_events) == len(phi_modifications)

        for event in modification_events:
            assert "previous_value" in event.details
            assert "new_value" in event.details
            assert "modification_reason" in event.details
            assert "HIPAA" in event.compliance_tags


@pytest.mark.asyncio
class TestHIPAATransmissionSecurity:
    """Test HIPAA transmission security requirements."""

    async def test_phi_transmission_encryption(self):
        """Test PHI transmission encryption requirements."""
        encryption_service = get_encryption_service()

        # Simulate PHI data for transmission
        phi_transmission = {
            "patient_mrn": "MR123456",
            "diagnosis_codes": ["E11.9", "I10"],
            "treatment_summary": "Patient responding well to metformin therapy",
            "next_appointment": "2025-02-15",
            "referring_physician": "Dr. Primary Care",
        }

        # Encrypt for secure transmission
        encrypted_transmission = encryption_service.encrypt_json(phi_transmission)

        # Verify data is encrypted
        assert encrypted_transmission != str(phi_transmission)
        assert len(encrypted_transmission) > 0

        # Verify can be decrypted by recipient
        decrypted_transmission = encryption_service.decrypt_json(encrypted_transmission)
        assert decrypted_transmission == phi_transmission

        # Log transmission for audit
        audit_logger = get_audit_logger()
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="PHI transmitted to external provider",
            user_id="system_transmission",
            resource="phi_transmission",
            details={
                "transmission_type": "encrypted",
                "encryption_algorithm": "AES-256-GCM",
                "recipient": "external_specialist",
                "transmission_size": len(encrypted_transmission),
                "integrity_verified": True,
            },
            compliance_tags=["HIPAA", "TRANSMISSION_SECURITY", "PHI"],
        )

    async def test_phi_at_rest_protection(self):
        """Test PHI at-rest encryption and storage protection."""
        # Test field-level encryption for stored PHI
        compliance_encryption = ComplianceFieldEncryption()

        stored_phi = {
            "medical_record_number": "MR123456789",
            "patient_ssn": "123-45-6789",
            "diagnosis_notes": "Chronic conditions include diabetes and hypertension",
            "prescription_history": ["Metformin 500mg BID", "Lisinopril 10mg daily"],
            "lab_results": {"hba1c": 7.2, "creatinine": 1.1, "cholesterol": 195},
            "provider_notes": "Patient counseled on diet and exercise importance",
        }

        # Encrypt PHI fields for storage
        encrypted_phi = compliance_encryption.encrypt_sensitive_data(stored_phi)

        # Verify PHI fields are encrypted
        phi_fields = [
            "medical_record_number",
            "diagnosis_notes",
            "prescription_history",
            "provider_notes",
        ]

        for field in phi_fields:
            if field in encrypted_phi:
                assert encrypted_phi[field].get("_compliance") is True
                assert "HIPAA" in encrypted_phi[field]["metadata"]["compliance_tags"]

        # Verify can decrypt for authorized access
        decrypted_phi = compliance_encryption.decrypt_fields(encrypted_phi)
        assert decrypted_phi["diagnosis_notes"] == stored_phi["diagnosis_notes"]
        assert (
            decrypted_phi["prescription_history"] == stored_phi["prescription_history"]
        )


@pytest.mark.asyncio
class TestHIPAACompliance:
    """Integration tests for complete HIPAA compliance."""

    async def test_complete_hipaa_workflow(self):
        """Test complete HIPAA-compliant PHI handling workflow."""
        audit_logger = get_audit_logger()
        compliance_controller = get_compliance_controller()

        patient_mrn = "MR_HIPAA_TEST_123456"
        healthcare_provider = "dr_hipaa_test"

        # Step 1: Healthcare provider authentication
        await audit_logger.log_authentication_event(
            event_type=AuditEventType.USER_LOGIN,
            user_id=healthcare_provider,
            ip_address="192.168.1.100",
            outcome="success",
            details={
                "authentication_method": "two_factor",
                "role": "attending_physician",
                "department": "internal_medicine",
            },
        )

        # Step 2: Access patient PHI for treatment
        await audit_logger.log_data_access(
            resource="patient_medical_record",
            user_id=healthcare_provider,
            action="Accessed PHI for treatment purposes",
            ip_address="192.168.1.100",
            details={
                "patient_mrn": patient_mrn,
                "access_purpose": "direct_treatment",
                "data_accessed": ["diagnosis", "medications", "lab_results"],
                "minimum_necessary": True,
            },
        )

        # Step 3: Modify PHI (update treatment plan)
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_UPDATE,
            action="Updated patient treatment plan",
            user_id=healthcare_provider,
            resource=f"treatment_plan_{patient_mrn}",
            details={
                "modification_type": "treatment_update",
                "field_modified": "medications",
                "clinical_justification": "Adjusting diabetes medication based on recent A1C",
                "previous_value": "Metformin 500mg BID",
                "new_value": "Metformin 500mg BID, Glipizide 5mg daily",
                "authorization": "physician_clinical_decision",
            },
            compliance_tags=["HIPAA", "PHI", "TREATMENT"],
        )

        # Step 4: Share PHI with another provider (with patient consent)
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="PHI shared with consulting specialist",
            user_id=healthcare_provider,
            resource=f"phi_sharing_{patient_mrn}",
            details={
                "sharing_purpose": "consultation",
                "recipient_provider": "dr_endocrinologist",
                "patient_consent": "documented",
                "data_shared": ["current_medications", "recent_labs", "diagnosis"],
                "sharing_method": "encrypted_transmission",
            },
            compliance_tags=["HIPAA", "PHI", "DISCLOSURE"],
        )

        # Step 5: Patient requests access to their PHI
        patient_export = (
            await compliance_controller.data_subject_rights.request_data_export(
                user_id=patient_mrn, format_type="json", include_metadata=True
            )
        )

        # Step 6: Log secure logout
        await audit_logger.log_authentication_event(
            event_type=AuditEventType.USER_LOGOUT,
            user_id=healthcare_provider,
            ip_address="192.168.1.100",
            outcome="success",
            details={"logout_method": "manual", "session_duration": "45_minutes"},
        )

        # Verify complete audit trail
        provider_activity = await audit_logger.get_user_activity(healthcare_provider)

        # Should have login, PHI access, modification, sharing, and logout
        event_types = {event.event_type for event in provider_activity}
        assert AuditEventType.USER_LOGIN in event_types
        assert AuditEventType.DATA_ACCESS in event_types
        assert AuditEventType.DATA_UPDATE in event_types
        assert AuditEventType.USER_LOGOUT in event_types

        # All events should have HIPAA compliance tags where appropriate
        hipaa_events = [
            event for event in provider_activity if "HIPAA" in event.compliance_tags
        ]
        assert len(hipaa_events) >= 3  # Access, update, and sharing

        # Verify patient data export includes audit information
        assert patient_export["user_id"] == patient_mrn
        assert "data" in patient_export

    async def test_hipaa_breach_incident_response(self):
        """Test HIPAA breach incident detection and response."""
        audit_logger = get_audit_logger()

        # Simulate potential breach incident
        breach_details = {
            "incident_type": "unauthorized_phi_access",
            "affected_records": 150,
            "data_types_involved": [
                "patient_names",
                "medical_record_numbers",
                "diagnoses",
            ],
            "discovery_method": "automated_monitoring",
            "potential_harm": "low_risk_identity_theft",
            "notification_required": True,
            "breach_location": "database_server_2",
            "unauthorized_access_duration": "2_hours",
        }

        # Log security incident
        incident_id = await audit_logger.log_security_incident(
            incident_type="hipaa_phi_breach",
            severity=AuditSeverity.CRITICAL,
            details=breach_details,
            ip_address="10.0.1.200",
        )

        # Verify incident logged for compliance reporting
        incidents = await audit_logger.get_security_incidents(
            severity=AuditSeverity.CRITICAL
        )

        breach_incident = next(i for i in incidents if i.event_id == incident_id)
        assert breach_incident.severity == AuditSeverity.CRITICAL
        assert "hipaa_phi_breach" in breach_incident.action
        assert breach_incident.details["affected_records"] == 150
        assert breach_incident.details["notification_required"] is True

    async def test_hipaa_anonymization_requirements(self):
        """Test HIPAA-compliant data anonymization."""
        anonymizer = get_data_anonymizer()

        # PHI data requiring anonymization for research/quality purposes
        phi_data = {
            "patient_name": "John Michael Doe",
            "mrn": "MR123456789",
            "date_of_birth": "1975-03-15",
            "address": "123 Main Street, Anytown, ST 12345",
            "phone": "555-123-4567",
            "diagnosis_code": "E11.9",
            "diagnosis_description": "Type 2 diabetes mellitus without complications",
            "treatment_start_date": "2024-01-15",
            "physician": "Dr. Sarah Johnson",
            "hospital_unit": "Internal Medicine Floor 3",
        }

        # Create anonymization rules for PHI
        from core.data_anonymization import AnonymizationRule, AnonymizationType

        hipaa_anonymization_rules = [
            AnonymizationRule(
                field_pattern=r".*name.*",
                technique=AnonymizationType.SYNTHETIC_DATA,
                parameters={"data_type": "name"},
                sensitivity_level=DataSensitivity.RESTRICTED,
            ),
            AnonymizationRule(
                field_pattern=r".*mrn.*",
                technique=AnonymizationType.PSEUDONYMIZATION,
                parameters={"consistent": True},
                sensitivity_level=DataSensitivity.RESTRICTED,
            ),
            AnonymizationRule(
                field_pattern=r".*birth.*",
                technique=AnonymizationType.GENERALIZATION,
                parameters={"precision": "year"},
                sensitivity_level=DataSensitivity.RESTRICTED,
            ),
            AnonymizationRule(
                field_pattern=r".*address.*",
                technique=AnonymizationType.SYNTHETIC_DATA,
                parameters={"data_type": "address"},
                sensitivity_level=DataSensitivity.RESTRICTED,
            ),
            AnonymizationRule(
                field_pattern=r".*phone.*",
                technique=AnonymizationType.SYNTHETIC_DATA,
                parameters={"data_type": "phone"},
                sensitivity_level=DataSensitivity.RESTRICTED,
            ),
        ]

        # Anonymize PHI data
        anonymized_result = anonymizer.anonymize_data(
            data=phi_data, rules=hipaa_anonymization_rules, detect_pii=True
        )

        anonymized_data = anonymized_result["anonymized_data"]
        metadata = anonymized_result["metadata"]

        # Verify sensitive identifiers are anonymized
        assert anonymized_data["patient_name"] != phi_data["patient_name"]
        assert anonymized_data["mrn"] != phi_data["mrn"]
        assert anonymized_data["address"] != phi_data["address"]
        assert anonymized_data["phone"] != phi_data["phone"]

        # Clinical data should be preserved for research value
        assert anonymized_data["diagnosis_code"] == phi_data["diagnosis_code"]
        assert (
            anonymized_data["diagnosis_description"]
            == phi_data["diagnosis_description"]
        )

        # Verify anonymization was properly documented
        assert "pii_detected" in metadata
        assert len(metadata["fields_anonymized"]) > 0
        assert metadata["anonymization_summary"]["anonymization_rate"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
