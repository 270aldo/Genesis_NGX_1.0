"""
Comprehensive audit system compliance tests.

Tests audit trail functionality for GDPR and HIPAA compliance,
including event logging, data access tracking, and compliance reporting.
"""

from datetime import datetime, timedelta, timezone

import pytest

from core.audit import (
    AuditEvent,
    AuditEventType,
    AuditSeverity,
    ComplianceAuditLogger,
    MemoryAuditStorage,
    audit_api_call,
    get_audit_logger,
)


class TestAuditEvent:
    """Test audit event functionality."""

    def test_audit_event_creation(self):
        """Test audit event creation and serialization."""
        event = AuditEvent(
            event_id="test-123",
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.MEDIUM,
            timestamp=datetime.now(timezone.utc),
            user_id="user123",
            session_id="session456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            resource="user_profile",
            action="Read user profile",
            details={"field_accessed": "email", "access_method": "api"},
            outcome="success",
            compliance_tags=["GDPR", "PII"],
        )

        assert event.event_id == "test-123"
        assert event.event_type == AuditEventType.DATA_ACCESS
        assert event.severity == AuditSeverity.MEDIUM
        assert event.user_id == "user123"
        assert event.outcome == "success"
        assert "GDPR" in event.compliance_tags

    def test_audit_event_to_dict(self):
        """Test audit event dictionary serialization."""
        event = AuditEvent(
            event_id="test-123",
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.HIGH,
            timestamp=datetime.now(timezone.utc),
            user_id="user123",
            session_id=None,
            ip_address="192.168.1.1",
            user_agent=None,
            resource="medical_records",
            action="Access PHI",
            details={"record_type": "diagnosis"},
            outcome="success",
            compliance_tags=["HIPAA", "PHI"],
        )

        event_dict = event.to_dict()

        assert event_dict["event_id"] == "test-123"
        assert event_dict["event_type"] == "data_access"
        assert event_dict["severity"] == "high"
        assert isinstance(event_dict["timestamp"], str)
        assert event_dict["compliance_tags"] == ["HIPAA", "PHI"]

    def test_audit_event_hash(self):
        """Test audit event integrity hash generation."""
        event = AuditEvent(
            event_id="test-123",
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.MEDIUM,
            timestamp=datetime.now(timezone.utc),
            user_id="user123",
            session_id="session456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            resource="user_profile",
            action="Read user profile",
            details={},
            outcome="success",
            compliance_tags=["GDPR"],
        )

        hash1 = event.get_hash()
        hash2 = event.get_hash()

        # Hash should be deterministic
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex digest

        # Different events should have different hashes
        event.outcome = "failure"
        hash3 = event.get_hash()
        assert hash1 != hash3


@pytest.mark.asyncio
class TestMemoryAuditStorage:
    """Test in-memory audit storage functionality."""

    async def test_store_and_retrieve_events(self):
        """Test storing and retrieving audit events."""
        storage = MemoryAuditStorage()

        event1 = AuditEvent(
            event_id="event-1",
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.MEDIUM,
            timestamp=datetime.now(timezone.utc),
            user_id="user123",
            session_id=None,
            ip_address="192.168.1.1",
            user_agent=None,
            resource="profile",
            action="View profile",
            details={},
            outcome="success",
            compliance_tags=["GDPR"],
        )

        event2 = AuditEvent(
            event_id="event-2",
            event_type=AuditEventType.USER_LOGIN,
            severity=AuditSeverity.LOW,
            timestamp=datetime.now(timezone.utc),
            user_id="user123",
            session_id="session456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            resource=None,
            action="User login",
            details={},
            outcome="success",
            compliance_tags=["SECURITY"],
        )

        # Store events
        assert await storage.store_event(event1) is True
        assert await storage.store_event(event2) is True

        # Retrieve all events
        events = await storage.retrieve_events()
        assert len(events) == 2

        # Events should be sorted by timestamp (newest first)
        assert events[0].timestamp >= events[1].timestamp

    async def test_event_filtering(self):
        """Test event filtering functionality."""
        storage = MemoryAuditStorage()

        # Create events with different characteristics
        base_time = datetime.now(timezone.utc)

        events_data = [
            {
                "event_id": "event-1",
                "user_id": "user123",
                "event_type": AuditEventType.DATA_ACCESS,
                "resource": "profile",
                "outcome": "success",
                "timestamp": base_time,
            },
            {
                "event_id": "event-2",
                "user_id": "user456",
                "event_type": AuditEventType.DATA_ACCESS,
                "resource": "medical_records",
                "outcome": "failure",
                "timestamp": base_time + timedelta(minutes=1),
            },
            {
                "event_id": "event-3",
                "user_id": "user123",
                "event_type": AuditEventType.USER_LOGIN,
                "resource": None,
                "outcome": "success",
                "timestamp": base_time + timedelta(minutes=2),
            },
        ]

        # Store test events
        for event_data in events_data:
            event = AuditEvent(
                event_id=event_data["event_id"],
                event_type=event_data["event_type"],
                severity=AuditSeverity.MEDIUM,
                timestamp=event_data["timestamp"],
                user_id=event_data["user_id"],
                session_id=None,
                ip_address="192.168.1.1",
                user_agent=None,
                resource=event_data["resource"],
                action="Test action",
                details={},
                outcome=event_data["outcome"],
                compliance_tags=["TEST"],
            )
            await storage.store_event(event)

        # Test user filtering
        user123_events = await storage.retrieve_events(filters={"user_id": "user123"})
        assert len(user123_events) == 2
        assert all(e.user_id == "user123" for e in user123_events)

        # Test event type filtering
        data_access_events = await storage.retrieve_events(
            filters={"event_type": AuditEventType.DATA_ACCESS.value}
        )
        assert len(data_access_events) == 2
        assert all(
            e.event_type == AuditEventType.DATA_ACCESS for e in data_access_events
        )

        # Test outcome filtering
        success_events = await storage.retrieve_events(filters={"outcome": "success"})
        assert len(success_events) == 2
        assert all(e.outcome == "success" for e in success_events)

        # Test time range filtering
        time_filtered_events = await storage.retrieve_events(
            filters={
                "start_time": (base_time + timedelta(minutes=0.5)).isoformat(),
                "end_time": (base_time + timedelta(minutes=1.5)).isoformat(),
            }
        )
        assert len(time_filtered_events) == 1
        assert time_filtered_events[0].event_id == "event-2"

    async def test_event_count(self):
        """Test event count functionality."""
        storage = MemoryAuditStorage()

        # Initially no events
        count = await storage.get_event_count()
        assert count == 0

        # Add some events
        for i in range(5):
            event = AuditEvent(
                event_id=f"event-{i}",
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.MEDIUM,
                timestamp=datetime.now(timezone.utc),
                user_id=f"user{i}",
                session_id=None,
                ip_address="192.168.1.1",
                user_agent=None,
                resource="test",
                action="Test action",
                details={},
                outcome="success",
                compliance_tags=["TEST"],
            )
            await storage.store_event(event)

        # Count all events
        total_count = await storage.get_event_count()
        assert total_count == 5

        # Count with filter
        filtered_count = await storage.get_event_count(filters={"user_id": "user1"})
        assert filtered_count == 1


@pytest.mark.asyncio
class TestComplianceAuditLogger:
    """Test compliance audit logger functionality."""

    async def test_basic_event_logging(self):
        """Test basic audit event logging."""
        logger = ComplianceAuditLogger()

        event_id = await logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="User accessed profile data",
            user_id="user123",
            ip_address="192.168.1.1",
            resource="user_profile",
        )

        assert event_id is not None
        assert len(event_id) > 0

    async def test_data_access_logging(self):
        """Test data access event logging."""
        logger = ComplianceAuditLogger()

        event_id = await logger.log_data_access(
            resource="medical_records",
            user_id="user123",
            action="Retrieved patient diagnosis",
            ip_address="192.168.1.1",
            details={"record_id": "MR-12345", "data_type": "PHI"},
        )

        assert event_id is not None

        # Verify event was logged
        events = await logger.storage.retrieve_events()
        assert len(events) == 1

        event = events[0]
        assert event.event_type == AuditEventType.DATA_ACCESS
        assert event.resource == "medical_records"
        assert "GDPR" in event.compliance_tags
        assert "HIPAA" in event.compliance_tags

    async def test_authentication_event_logging(self):
        """Test authentication event logging."""
        logger = ComplianceAuditLogger()

        # Successful login
        success_event_id = await logger.log_authentication_event(
            event_type=AuditEventType.USER_LOGIN,
            user_id="user123",
            ip_address="192.168.1.1",
            outcome="success",
        )

        # Failed login
        failure_event_id = await logger.log_authentication_event(
            event_type=AuditEventType.AUTH_FAILURE,
            user_id="user123",
            ip_address="192.168.1.1",
            outcome="failure",
            details={"reason": "invalid_password", "attempts": 3},
        )

        assert success_event_id != failure_event_id

        # Check events
        events = await logger.storage.retrieve_events()
        assert len(events) == 2

        # Failed login should have higher severity
        failure_event = next(e for e in events if e.outcome == "failure")
        success_event = next(e for e in events if e.outcome == "success")

        assert failure_event.severity == AuditSeverity.HIGH
        assert success_event.severity == AuditSeverity.MEDIUM

    async def test_consent_event_logging(self):
        """Test consent event logging."""
        logger = ComplianceAuditLogger()

        # Consent granted
        grant_event_id = await logger.log_consent_event(
            user_id="user123",
            consent_type="medical_data",
            granted=True,
            details={"purpose": "personalized_coaching", "duration": "1_year"},
        )

        # Consent withdrawn
        withdraw_event_id = await logger.log_consent_event(
            user_id="user123",
            consent_type="medical_data",
            granted=False,
            details={"reason": "user_request"},
        )

        assert grant_event_id != withdraw_event_id

        # Check events
        events = await logger.storage.retrieve_events()
        assert len(events) == 2

        for event in events:
            assert event.severity == AuditSeverity.HIGH
            assert "GDPR" in event.compliance_tags
            assert "PRIVACY" in event.compliance_tags

    async def test_privacy_request_logging(self):
        """Test privacy request logging."""
        logger = ComplianceAuditLogger()

        # Data export request
        export_event_id = await logger.log_privacy_request(
            request_type="export",
            user_id="user123",
            ip_address="192.168.1.1",
            details={"format": "json", "include_metadata": True},
        )

        # Data deletion request
        deletion_event_id = await logger.log_privacy_request(
            request_type="deletion",
            user_id="user123",
            ip_address="192.168.1.1",
            details={"reason": "account_closure", "retain_legal": True},
        )

        assert export_event_id != deletion_event_id

        # Check events
        events = await logger.storage.retrieve_events()
        assert len(events) == 2

        export_event = next(
            e for e in events if e.event_type == AuditEventType.DATA_EXPORT
        )
        deletion_event = next(
            e for e in events if e.event_type == AuditEventType.DATA_DELETION
        )

        assert "GDPR" in export_event.compliance_tags
        assert "GDPR" in deletion_event.compliance_tags

    async def test_security_incident_logging(self):
        """Test security incident logging."""
        logger = ComplianceAuditLogger()

        event_id = await logger.log_security_incident(
            incident_type="unauthorized_access_attempt",
            severity=AuditSeverity.CRITICAL,
            details={
                "source_ip": "192.168.1.100",
                "target_resource": "admin_panel",
                "attack_vector": "brute_force",
                "blocked": True,
            },
            ip_address="192.168.1.100",
        )

        assert event_id is not None

        # Check event
        events = await logger.storage.retrieve_events()
        assert len(events) == 1

        event = events[0]
        assert event.event_type == AuditEventType.SECURITY_INCIDENT
        assert event.severity == AuditSeverity.CRITICAL
        assert event.outcome == "incident"
        assert "SECURITY" in event.compliance_tags

    async def test_user_activity_retrieval(self):
        """Test user activity retrieval."""
        logger = ComplianceAuditLogger()

        # Log multiple events for different users
        await logger.log_data_access(
            "profile", "user123", "View profile", "192.168.1.1"
        )
        await logger.log_data_access(
            "settings", "user123", "Update settings", "192.168.1.1"
        )
        await logger.log_data_access(
            "profile", "user456", "View profile", "192.168.1.2"
        )

        # Get activity for specific user
        user123_activity = await logger.get_user_activity("user123")
        assert len(user123_activity) == 2
        assert all(event.user_id == "user123" for event in user123_activity)

        user456_activity = await logger.get_user_activity("user456")
        assert len(user456_activity) == 1
        assert user456_activity[0].user_id == "user456"

    async def test_resource_access_log(self):
        """Test resource access log retrieval."""
        logger = ComplianceAuditLogger()

        # Log access to different resources
        await logger.log_data_access(
            "medical_records", "user123", "View records", "192.168.1.1"
        )
        await logger.log_data_access(
            "medical_records", "user456", "View records", "192.168.1.2"
        )
        await logger.log_data_access(
            "profile", "user123", "View profile", "192.168.1.1"
        )

        # Get access log for specific resource
        medical_access = await logger.get_resource_access_log("medical_records")
        assert len(medical_access) == 2
        assert all(event.resource == "medical_records" for event in medical_access)

        profile_access = await logger.get_resource_access_log("profile")
        assert len(profile_access) == 1
        assert profile_access[0].resource == "profile"

    async def test_compliance_events_retrieval(self):
        """Test compliance events retrieval."""
        logger = ComplianceAuditLogger()

        # Log different types of compliance events
        await logger.log_consent_event("user123", "marketing", True)
        await logger.log_privacy_request("export", "user123")
        await logger.log_data_access(
            "profile", "user123", "View profile", compliance_tags=["GDPR"]
        )
        await logger.log_authentication_event(
            AuditEventType.USER_LOGIN, "user123", "192.168.1.1", "success"
        )

        # Get GDPR compliance events
        gdpr_events = await logger.get_compliance_events("GDPR")
        assert len(gdpr_events) >= 3  # At least consent, export, and data access

        # Get PRIVACY compliance events
        privacy_events = await logger.get_compliance_events("PRIVACY")
        assert len(privacy_events) >= 2  # At least consent and export

    async def test_security_incidents_retrieval(self):
        """Test security incidents retrieval."""
        logger = ComplianceAuditLogger()

        # Log security incidents with different severities
        await logger.log_security_incident(
            "minor_violation", AuditSeverity.LOW, {"type": "policy_violation"}
        )
        await logger.log_security_incident(
            "data_breach", AuditSeverity.CRITICAL, {"records_affected": 1000}
        )
        await logger.log_security_incident(
            "suspicious_activity", AuditSeverity.MEDIUM, {"user_id": "user123"}
        )

        # Get all security incidents
        all_incidents = await logger.get_security_incidents()
        assert len(all_incidents) == 3

        # Get only critical incidents
        critical_incidents = await logger.get_security_incidents(
            severity=AuditSeverity.CRITICAL
        )
        assert len(critical_incidents) == 1
        assert critical_incidents[0].severity == AuditSeverity.CRITICAL

    async def test_default_compliance_tags(self):
        """Test default compliance tags assignment."""
        logger = ComplianceAuditLogger()

        # Test GDPR events
        await logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="Access user data",
            user_id="user123",
        )

        await logger.log_event(
            event_type=AuditEventType.CONSENT_GIVEN,
            action="User granted consent",
            user_id="user123",
        )

        # Test HIPAA events
        await logger.log_event(
            event_type=AuditEventType.DATA_READ,
            action="Read medical records",
            user_id="user123",
        )

        events = await logger.storage.retrieve_events()

        # Check that appropriate compliance tags were assigned
        for event in events:
            if event.event_type in [
                AuditEventType.DATA_ACCESS,
                AuditEventType.DATA_READ,
            ]:
                assert "GDPR" in event.compliance_tags
                assert "HIPAA" in event.compliance_tags
            elif event.event_type == AuditEventType.CONSENT_GIVEN:
                assert "GDPR" in event.compliance_tags

    async def test_audit_context_manager(self):
        """Test audit context manager."""
        logger = ComplianceAuditLogger()

        async with logger.audit_context(
            user_id="user123", session_id="session456", ip_address="192.168.1.1"
        ):
            # Context should be available
            context = logger._get_current_context()
            assert context["user_id"] == "user123"
            assert context["session_id"] == "session456"
            assert context["ip_address"] == "192.168.1.1"

        # Context should be cleared after exiting
        context = logger._get_current_context()
        assert context == {}


class TestAuditDecorator:
    """Test audit logging decorator."""

    @pytest.mark.asyncio
    async def test_async_function_audit(self):
        """Test auditing of async functions."""
        logger = ComplianceAuditLogger()

        @audit_api_call(resource="test_resource", action="test_action")
        async def test_async_function():
            return "success"

        # Mock function call
        result = await test_async_function()
        assert result == "success"

        # Check that audit event was logged
        events = await logger.storage.retrieve_events()
        assert len(events) == 1

        event = events[0]
        assert event.event_type == AuditEventType.API_REQUEST
        assert event.resource == "test_resource"
        assert event.outcome == "success"

    @pytest.mark.asyncio
    async def test_function_audit_with_exception(self):
        """Test auditing when function raises exception."""
        logger = ComplianceAuditLogger()

        @audit_api_call(resource="test_resource", action="test_action_fail")
        async def test_failing_function():
            raise ValueError("Test error")

        # Function should raise exception
        with pytest.raises(ValueError):
            await test_failing_function()

        # Check that audit event was logged with error outcome
        events = await logger.storage.retrieve_events()
        assert len(events) == 1

        event = events[0]
        assert event.event_type == AuditEventType.API_REQUEST
        assert event.resource == "test_resource"
        assert event.outcome == "error"
        assert event.severity == AuditSeverity.HIGH
        assert "error" in event.details
        assert "error_type" in event.details


class TestGlobalAuditLogger:
    """Test global audit logger functionality."""

    @pytest.mark.asyncio
    async def test_singleton_behavior(self):
        """Test that global audit logger is singleton."""
        logger1 = get_audit_logger()
        logger2 = get_audit_logger()

        assert logger1 is logger2

    @pytest.mark.asyncio
    async def test_global_logger_functionality(self):
        """Test global logger basic functionality."""
        logger = get_audit_logger()

        event_id = await logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="Global logger test",
            user_id="test_user",
        )

        assert event_id is not None

        # Verify event was stored
        events = await logger.storage.retrieve_events()
        assert len(events) >= 1

        # Find our test event
        test_event = next((e for e in events if e.action == "Global logger test"), None)
        assert test_event is not None
        assert test_event.user_id == "test_user"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
