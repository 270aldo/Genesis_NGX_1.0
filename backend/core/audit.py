"""
Comprehensive Audit System for GENESIS
=====================================

GDPR and HIPAA compliant audit trail system that logs all data access,
modifications, and compliance events.
"""

import asyncio
import hashlib
import json
import uuid
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from core.logging_config import get_logger
from core.security.encryption_service import get_encryption_service

logger = get_logger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""

    # Data access events
    DATA_ACCESS = "data_access"
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"

    # Authentication events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    AUTH_FAILURE = "auth_failure"
    PASSWORD_CHANGE = "password_change"

    # Privacy/compliance events
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    DATA_EXPORT = "data_export"
    DATA_DELETION = "data_deletion"
    RIGHT_TO_ACCESS = "right_to_access"

    # Security events
    ENCRYPTION_KEY_ROTATION = "key_rotation"
    SECURITY_INCIDENT = "security_incident"
    VULNERABILITY_DETECTED = "vulnerability_detected"

    # System events
    API_REQUEST = "api_request"
    AGENT_INTERACTION = "agent_interaction"
    SYSTEM_ERROR = "system_error"

    # Admin events
    ADMIN_ACTION = "admin_action"
    CONFIG_CHANGE = "config_change"
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"


class AuditSeverity(Enum):
    """Severity levels for audit events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Represents a single audit event."""

    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: str
    details: Dict[str, Any]
    outcome: str  # success, failure, error
    compliance_tags: List[str]
    data_classification: Optional[str] = None
    retention_period: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit event to dictionary."""
        result = asdict(self)
        result["event_type"] = self.event_type.value
        result["severity"] = self.severity.value
        result["timestamp"] = self.timestamp.isoformat()
        return result

    def get_hash(self) -> str:
        """Get SHA-256 hash of the audit event for integrity verification."""
        # Create deterministic string representation
        data = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action,
            "outcome": self.outcome,
        }
        json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()


class AuditStorage:
    """Interface for audit storage backends."""

    async def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event."""
        raise NotImplementedError

    async def retrieve_events(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """Retrieve audit events with optional filters."""
        raise NotImplementedError

    async def get_event_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total count of audit events matching filters."""
        raise NotImplementedError


class MemoryAuditStorage(AuditStorage):
    """In-memory audit storage for development/testing."""

    def __init__(self):
        self._events: List[AuditEvent] = []
        self._lock = asyncio.Lock()

    async def store_event(self, event: AuditEvent) -> bool:
        """Store an audit event in memory."""
        async with self._lock:
            self._events.append(event)
            return True

    async def retrieve_events(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """Retrieve audit events from memory."""
        async with self._lock:
            events = self._events.copy()

            if filters:
                events = self._apply_filters(events, filters)

            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.timestamp, reverse=True)

            return events[offset : offset + limit]

    async def get_event_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get count of events in memory."""
        async with self._lock:
            events = self._events.copy()

            if filters:
                events = self._apply_filters(events, filters)

            return len(events)

    def _apply_filters(
        self, events: List[AuditEvent], filters: Dict[str, Any]
    ) -> List[AuditEvent]:
        """Apply filters to event list."""
        filtered = events

        if "user_id" in filters:
            filtered = [e for e in filtered if e.user_id == filters["user_id"]]

        if "event_type" in filters:
            event_type = AuditEventType(filters["event_type"])
            filtered = [e for e in filtered if e.event_type == event_type]

        if "start_time" in filters:
            start_time = datetime.fromisoformat(filters["start_time"])
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if "end_time" in filters:
            end_time = datetime.fromisoformat(filters["end_time"])
            filtered = [e for e in filtered if e.timestamp <= end_time]

        if "resource" in filters:
            filtered = [e for e in filtered if e.resource == filters["resource"]]

        if "outcome" in filters:
            filtered = [e for e in filtered if e.outcome == filters["outcome"]]

        if "compliance_tags" in filters:
            tags = filters["compliance_tags"]
            if isinstance(tags, str):
                tags = [tags]
            filtered = [
                e for e in filtered if any(tag in e.compliance_tags for tag in tags)
            ]

        return filtered


class ComplianceAuditLogger:
    """Main audit logging service with compliance features."""

    def __init__(self, storage: Optional[AuditStorage] = None):
        self.storage = storage or MemoryAuditStorage()
        self.encryption_service = get_encryption_service()
        self._context_stack = []

    async def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        outcome: str = "success",
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        compliance_tags: Optional[List[str]] = None,
        data_classification: Optional[str] = None,
    ) -> str:
        """
        Log an audit event.

        Args:
            event_type: Type of event
            action: Description of the action performed
            user_id: ID of the user performing the action
            session_id: Session ID
            ip_address: IP address of the request
            user_agent: User agent string
            resource: Resource being accessed/modified
            details: Additional details about the event
            outcome: Outcome of the action (success, failure, error)
            severity: Severity level of the event
            compliance_tags: Compliance tags (GDPR, HIPAA, etc.)
            data_classification: Data classification level

        Returns:
            Event ID of the logged event
        """
        event_id = str(uuid.uuid4())

        # Default compliance tags based on event type
        if compliance_tags is None:
            compliance_tags = self._get_default_compliance_tags(event_type)

        # Determine retention period
        retention_period = self._get_retention_period(event_type, compliance_tags)

        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            details=details or {},
            outcome=outcome,
            compliance_tags=compliance_tags,
            data_classification=data_classification,
            retention_period=retention_period,
        )

        # Store the event
        try:
            success = await self.storage.store_event(event)
            if success:
                logger.info(f"Audit event logged: {event_id} - {action}")
            else:
                logger.error(f"Failed to store audit event: {event_id}")
        except Exception as e:
            logger.error(f"Error storing audit event {event_id}: {e}")

        return event_id

    def _get_default_compliance_tags(self, event_type: AuditEventType) -> List[str]:
        """Get default compliance tags based on event type."""
        gdpr_events = {
            AuditEventType.DATA_ACCESS,
            AuditEventType.DATA_READ,
            AuditEventType.DATA_WRITE,
            AuditEventType.DATA_UPDATE,
            AuditEventType.DATA_DELETE,
            AuditEventType.CONSENT_GIVEN,
            AuditEventType.CONSENT_WITHDRAWN,
            AuditEventType.DATA_EXPORT,
            AuditEventType.DATA_DELETION,
            AuditEventType.RIGHT_TO_ACCESS,
        }

        hipaa_events = {
            AuditEventType.DATA_ACCESS,
            AuditEventType.DATA_READ,
            AuditEventType.DATA_WRITE,
            AuditEventType.DATA_UPDATE,
            AuditEventType.DATA_DELETE,
        }

        tags = []
        if event_type in gdpr_events:
            tags.append("GDPR")
        if event_type in hipaa_events:
            tags.append("HIPAA")

        return tags

    def _get_retention_period(
        self, event_type: AuditEventType, compliance_tags: List[str]
    ) -> str:
        """Determine retention period based on compliance requirements."""
        if "HIPAA" in compliance_tags:
            return "6_years"  # HIPAA requirement
        elif "GDPR" in compliance_tags:
            return "3_years"  # GDPR recommendation
        else:
            return "1_year"  # Default

    # Convenience methods for common audit events
    async def log_data_access(
        self,
        resource: str,
        user_id: str,
        action: str,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log data access event."""
        return await self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            details=details,
            severity=AuditSeverity.MEDIUM,
            compliance_tags=["GDPR", "HIPAA"],
        )

    async def log_authentication_event(
        self,
        event_type: AuditEventType,
        user_id: str,
        ip_address: str,
        outcome: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log authentication-related event."""
        severity = AuditSeverity.HIGH if outcome != "success" else AuditSeverity.MEDIUM

        return await self.log_event(
            event_type=event_type,
            action=f"User {event_type.value}",
            user_id=user_id,
            ip_address=ip_address,
            outcome=outcome,
            severity=severity,
            details=details,
            compliance_tags=["SECURITY"],
        )

    async def log_consent_event(
        self,
        user_id: str,
        consent_type: str,
        granted: bool,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log consent-related event."""
        event_type = (
            AuditEventType.CONSENT_GIVEN
            if granted
            else AuditEventType.CONSENT_WITHDRAWN
        )

        return await self.log_event(
            event_type=event_type,
            action=f"User {'granted' if granted else 'withdrew'} {consent_type} consent",
            user_id=user_id,
            details=details,
            severity=AuditSeverity.HIGH,
            compliance_tags=["GDPR", "PRIVACY"],
        )

    async def log_privacy_request(
        self,
        request_type: str,
        user_id: str,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log privacy request (data export, deletion, etc.)."""
        event_type_map = {
            "export": AuditEventType.DATA_EXPORT,
            "deletion": AuditEventType.DATA_DELETION,
            "access": AuditEventType.RIGHT_TO_ACCESS,
        }

        event_type = event_type_map.get(request_type, AuditEventType.DATA_ACCESS)

        return await self.log_event(
            event_type=event_type,
            action=f"User requested data {request_type}",
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            severity=AuditSeverity.HIGH,
            compliance_tags=["GDPR", "PRIVACY"],
        )

    async def log_security_incident(
        self,
        incident_type: str,
        severity: AuditSeverity,
        details: Dict[str, Any],
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> str:
        """Log security incident."""
        return await self.log_event(
            event_type=AuditEventType.SECURITY_INCIDENT,
            action=f"Security incident: {incident_type}",
            user_id=user_id,
            ip_address=ip_address,
            severity=severity,
            details=details,
            outcome="incident",
            compliance_tags=["SECURITY", "INCIDENT_RESPONSE"],
        )

    # Query methods
    async def get_user_activity(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Get audit trail for a specific user."""
        filters = {"user_id": user_id}

        if start_time:
            filters["start_time"] = start_time.isoformat()
        if end_time:
            filters["end_time"] = end_time.isoformat()

        return await self.storage.retrieve_events(filters=filters, limit=limit)

    async def get_resource_access_log(
        self,
        resource: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Get access log for a specific resource."""
        filters = {"resource": resource}

        if start_time:
            filters["start_time"] = start_time.isoformat()
        if end_time:
            filters["end_time"] = end_time.isoformat()

        return await self.storage.retrieve_events(filters=filters, limit=limit)

    async def get_compliance_events(
        self,
        compliance_tag: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Get events related to specific compliance requirement."""
        filters = {"compliance_tags": [compliance_tag]}

        if start_time:
            filters["start_time"] = start_time.isoformat()
        if end_time:
            filters["end_time"] = end_time.isoformat()

        return await self.storage.retrieve_events(filters=filters, limit=limit)

    async def get_security_incidents(
        self,
        severity: Optional[AuditSeverity] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Get security incidents."""
        filters = {"event_type": AuditEventType.SECURITY_INCIDENT.value}

        if start_time:
            filters["start_time"] = start_time.isoformat()
        if end_time:
            filters["end_time"] = end_time.isoformat()

        events = await self.storage.retrieve_events(filters=filters, limit=limit)

        if severity:
            events = [e for e in events if e.severity == severity]

        return events

    @asynccontextmanager
    async def audit_context(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ):
        """Context manager for audit logging."""
        context = {
            "user_id": user_id,
            "session_id": session_id,
            "ip_address": ip_address,
        }
        self._context_stack.append(context)

        try:
            yield self
        finally:
            self._context_stack.pop()

    def _get_current_context(self) -> Dict[str, Any]:
        """Get current audit context."""
        return self._context_stack[-1] if self._context_stack else {}


# Global audit logger instance
_audit_logger: Optional[ComplianceAuditLogger] = None


def get_audit_logger() -> ComplianceAuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = ComplianceAuditLogger()
    return _audit_logger


# Decorator for automatic audit logging
def audit_api_call(
    resource: Optional[str] = None,
    action: Optional[str] = None,
    event_type: AuditEventType = AuditEventType.API_REQUEST,
):
    """Decorator to automatically audit API calls."""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            audit_logger = get_audit_logger()

            # Extract user info from request (if available)
            user_id = kwargs.get("current_user", {}).get("id")
            ip_address = (
                kwargs.get("request", {}).remote_addr
                if hasattr(kwargs.get("request", {}), "remote_addr")
                else None
            )

            # Determine resource and action
            resource_name = resource or func.__name__
            action_name = action or f"Called {func.__name__}"

            try:
                result = await func(*args, **kwargs)

                await audit_logger.log_event(
                    event_type=event_type,
                    action=action_name,
                    user_id=user_id,
                    ip_address=ip_address,
                    resource=resource_name,
                    outcome="success",
                    details={"function": func.__name__, "module": func.__module__},
                )

                return result

            except Exception as e:
                await audit_logger.log_event(
                    event_type=event_type,
                    action=action_name,
                    user_id=user_id,
                    ip_address=ip_address,
                    resource=resource_name,
                    outcome="error",
                    severity=AuditSeverity.HIGH,
                    details={
                        "function": func.__name__,
                        "module": func.__module__,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )
                raise

        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
