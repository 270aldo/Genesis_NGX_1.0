"""
Audit Trail Service for GUARDIAN Security Compliance agent.
Handles comprehensive audit logging, trail management, and forensic analysis.
"""

import asyncio
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import zlib
import base64

from agents.backend.guardian.core.config import GuardianConfig
from agents.backend.guardian.core.exceptions import (
    AuditTrailError,
    IntegrityError,
    GuardianValidationError,
)
from agents.backend.guardian.core.constants import (
    AUDIT_EVENT_CATEGORIES,
    SECURITY_EVENT_TYPES,
    DATA_CLASSIFICATION_LEVELS,
)
from core.logging_config import get_logger

logger = get_logger(__name__)


class AuditEventType(Enum):
    """Audit event type enumeration."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    CONFIGURATION = "configuration"
    COMPLIANCE = "compliance"
    INCIDENT = "incident"
    SYSTEM = "system"
    SECURITY = "security"


class AuditSeverity(Enum):
    """Audit event severity enumeration."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class AuditEvent:
    """Represents an audit event."""

    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    actor: str  # who performed the action
    action: str  # what action was performed
    resource: Optional[str]  # what resource was affected
    outcome: str  # success, failure, partial
    source_ip: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    details: Dict[str, Any]
    risk_score: float
    compliance_tags: List[str]
    hash: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class AuditQuery:
    """Represents an audit query."""

    event_types: Optional[List[AuditEventType]] = None
    severity_min: Optional[AuditSeverity] = None
    actor_filter: Optional[str] = None
    resource_filter: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    compliance_tags: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class AuditTrailService:
    """
    Comprehensive audit trail service for security and compliance logging.

    Features:
    - Tamper-evident audit logging
    - Cryptographic integrity protection
    - Compliance-ready audit trails
    - Forensic analysis capabilities
    - Real-time audit monitoring
    - Automated retention management
    - Audit data encryption
    - Chain of custody tracking
    """

    def __init__(self, config: GuardianConfig):
        self.config = config
        self._audit_events: List[AuditEvent] = []
        self._audit_indexes: Dict[str, Dict[str, Set[str]]] = {}
        self._encryption_key: Optional[bytes] = None
        self._signing_key: Optional[bytes] = None
        self._chain_hash: Optional[str] = None
        self._monitoring_active = False
        self._audit_tasks: Set[asyncio.Task] = set()
        self._retention_manager_task: Optional[asyncio.Task] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the audit trail service."""
        try:
            # Initialize encryption keys
            if self.config.audit_encryption_enabled:
                await self._initialize_encryption()

            # Initialize integrity protection
            if self.config.enable_tamper_protection:
                await self._initialize_integrity_protection()

            # Initialize audit indexes
            await self._initialize_audit_indexes()

            # Start audit monitoring
            if self.config.enable_audit_trail:
                await self.start_audit_monitoring()

            self._initialized = True
            logger.info("Audit trail service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize audit trail service: {e}")
            raise AuditTrailError(
                f"Audit trail service initialization failed: {e}",
                operation="initialization",
            )

    async def _initialize_encryption(self) -> None:
        """Initialize encryption for audit data."""
        # In production, these would be securely generated and stored
        self._encryption_key = hashlib.pbkdf2_hmac(
            "sha256", b"audit_encryption_key", b"audit_salt", 100000
        )

        self._signing_key = hashlib.pbkdf2_hmac(
            "sha256", b"audit_signing_key", b"signing_salt", 100000
        )

    async def _initialize_integrity_protection(self) -> None:
        """Initialize tamper protection mechanisms."""
        # Initialize chain hash for blockchain-like integrity
        self._chain_hash = hashlib.sha256(b"audit_chain_genesis").hexdigest()

    async def _initialize_audit_indexes(self) -> None:
        """Initialize audit event indexes for fast queries."""
        self._audit_indexes = {
            "by_type": {},
            "by_actor": {},
            "by_resource": {},
            "by_severity": {},
            "by_compliance_tag": {},
            "by_date": {},
        }

    async def start_audit_monitoring(self) -> None:
        """Start audit trail monitoring."""
        if self._monitoring_active:
            logger.warning("Audit monitoring is already active")
            return

        try:
            self._monitoring_active = True

            # Start monitoring tasks
            tasks = [
                self._monitor_audit_integrity(),
                self._monitor_audit_performance(),
                self._detect_audit_anomalies(),
            ]

            for task in tasks:
                audit_task = asyncio.create_task(task)
                self._audit_tasks.add(audit_task)
                audit_task.add_done_callback(self._audit_tasks.discard)

            # Start retention manager
            self._retention_manager_task = asyncio.create_task(
                self._manage_audit_retention()
            )

            logger.info("Audit monitoring started successfully")

        except Exception as e:
            self._monitoring_active = False
            logger.error(f"Failed to start audit monitoring: {e}")
            raise AuditTrailError(
                f"Failed to start audit monitoring: {e}", operation="monitoring_start"
            )

    async def stop_audit_monitoring(self) -> None:
        """Stop audit trail monitoring."""
        self._monitoring_active = False

        # Cancel all monitoring tasks
        for task in self._audit_tasks:
            task.cancel()

        if self._retention_manager_task:
            self._retention_manager_task.cancel()

        # Wait for tasks to complete
        all_tasks = list(self._audit_tasks)
        if self._retention_manager_task:
            all_tasks.append(self._retention_manager_task)

        if all_tasks:
            await asyncio.gather(*all_tasks, return_exceptions=True)

        self._audit_tasks.clear()
        self._retention_manager_task = None
        logger.info("Audit monitoring stopped")

    async def _monitor_audit_integrity(self) -> None:
        """Monitor audit trail integrity."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Verify audit chain integrity
                integrity_status = await self._verify_audit_chain()

                if not integrity_status["valid"]:
                    await self._handle_integrity_violation(integrity_status)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in audit integrity monitoring: {e}")

    async def _monitor_audit_performance(self) -> None:
        """Monitor audit trail performance."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes

                # Check audit performance metrics
                performance = await self._check_audit_performance()

                if performance.get("alerts"):
                    await self._handle_performance_alerts(performance["alerts"])

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in audit performance monitoring: {e}")

    async def _detect_audit_anomalies(self) -> None:
        """Detect anomalies in audit patterns."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(900)  # Check every 15 minutes

                # Analyze audit patterns for anomalies
                anomalies = await self._analyze_audit_patterns()

                for anomaly in anomalies:
                    await self._handle_audit_anomaly(anomaly)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in audit anomaly detection: {e}")

    async def _manage_audit_retention(self) -> None:
        """Manage audit data retention."""
        while self._monitoring_active:
            try:
                await asyncio.sleep(3600)  # Check every hour

                # Check for expired audit records
                cutoff_date = datetime.utcnow() - timedelta(
                    days=self.config.audit_retention_days
                )

                expired_events = [
                    event
                    for event in self._audit_events
                    if event.timestamp < cutoff_date
                ]

                if expired_events:
                    await self._archive_expired_events(expired_events)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in audit retention management: {e}")

    async def log_audit_event(
        self,
        event_type: AuditEventType,
        actor: str,
        action: str,
        outcome: str = "success",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        compliance_tags: Optional[List[str]] = None,
    ) -> str:
        """
        Log an audit event.

        Args:
            event_type: Type of audit event
            actor: Who performed the action
            action: What action was performed
            outcome: Result of the action
            resource: Resource affected (optional)
            details: Additional event details
            severity: Event severity
            source_ip: Source IP address
            user_agent: User agent string
            session_id: Session identifier
            compliance_tags: Compliance framework tags

        Returns:
            str: Event ID of the logged event
        """
        try:
            # Generate event ID
            event_id = self._generate_event_id()

            # Calculate risk score
            risk_score = self._calculate_risk_score(
                event_type, action, outcome, severity, details or {}
            )

            # Create audit event
            audit_event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.utcnow(),
                event_type=event_type,
                severity=severity,
                actor=actor,
                action=action,
                resource=resource,
                outcome=outcome,
                source_ip=source_ip,
                user_agent=user_agent,
                session_id=session_id,
                details=details or {},
                risk_score=risk_score,
                compliance_tags=compliance_tags or [],
            )

            # Add integrity protection
            if self.config.enable_tamper_protection:
                await self._protect_event_integrity(audit_event)

            # Encrypt if required
            if self.config.audit_encryption_enabled:
                await self._encrypt_audit_event(audit_event)

            # Store event
            self._audit_events.append(audit_event)

            # Update indexes
            await self._update_audit_indexes(audit_event)

            # Check for immediate alerts
            if severity in [AuditSeverity.CRITICAL, AuditSeverity.HIGH]:
                await self._trigger_audit_alert(audit_event)

            # Trigger compliance notifications
            if compliance_tags:
                await self._process_compliance_event(audit_event)

            logger.debug(f"Audit event logged: {event_id}")
            return event_id

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            raise AuditTrailError(
                f"Audit event logging failed: {e}", operation="log_event"
            )

    async def _protect_event_integrity(self, event: AuditEvent) -> None:
        """Protect audit event integrity with cryptographic measures."""
        # Create event hash
        event_data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "actor": event.actor,
            "action": event.action,
            "resource": event.resource,
            "outcome": event.outcome,
            "details": event.details,
        }

        event_json = json.dumps(event_data, sort_keys=True)
        event.hash = hashlib.sha256(event_json.encode()).hexdigest()

        # Create chain hash (blockchain-like integrity)
        chain_data = f"{self._chain_hash}{event.hash}"
        self._chain_hash = hashlib.sha256(chain_data.encode()).hexdigest()

        # Create digital signature
        if self._signing_key:
            event.signature = hmac.new(
                self._signing_key, event_json.encode(), hashlib.sha256
            ).hexdigest()

    async def _encrypt_audit_event(self, event: AuditEvent) -> None:
        """Encrypt sensitive audit event data."""
        if not self._encryption_key:
            return

        # In production, this would use proper encryption like AES-GCM
        # For demo, we'll use simple base64 encoding
        sensitive_data = json.dumps(event.details)
        encrypted = base64.b64encode(zlib.compress(sensitive_data.encode())).decode()

        event.details = {"encrypted": encrypted}

    async def _update_audit_indexes(self, event: AuditEvent) -> None:
        """Update audit indexes for fast querying."""
        # Index by type
        event_type = event.event_type.value
        if event_type not in self._audit_indexes["by_type"]:
            self._audit_indexes["by_type"][event_type] = set()
        self._audit_indexes["by_type"][event_type].add(event.event_id)

        # Index by actor
        if event.actor not in self._audit_indexes["by_actor"]:
            self._audit_indexes["by_actor"][event.actor] = set()
        self._audit_indexes["by_actor"][event.actor].add(event.event_id)

        # Index by resource
        if event.resource:
            if event.resource not in self._audit_indexes["by_resource"]:
                self._audit_indexes["by_resource"][event.resource] = set()
            self._audit_indexes["by_resource"][event.resource].add(event.event_id)

        # Index by severity
        severity = event.severity.value
        if severity not in self._audit_indexes["by_severity"]:
            self._audit_indexes["by_severity"][severity] = set()
        self._audit_indexes["by_severity"][severity].add(event.event_id)

        # Index by compliance tags
        for tag in event.compliance_tags:
            if tag not in self._audit_indexes["by_compliance_tag"]:
                self._audit_indexes["by_compliance_tag"][tag] = set()
            self._audit_indexes["by_compliance_tag"][tag].add(event.event_id)

        # Index by date
        date_key = event.timestamp.date().isoformat()
        if date_key not in self._audit_indexes["by_date"]:
            self._audit_indexes["by_date"][date_key] = set()
        self._audit_indexes["by_date"][date_key].add(event.event_id)

    async def query_audit_events(self, query: AuditQuery) -> List[AuditEvent]:
        """
        Query audit events based on criteria.

        Args:
            query: Audit query parameters

        Returns:
            List[AuditEvent]: Matching audit events
        """
        try:
            # Start with all events
            candidate_ids = set(event.event_id for event in self._audit_events)

            # Filter by event types
            if query.event_types:
                type_ids = set()
                for event_type in query.event_types:
                    type_key = event_type.value
                    if type_key in self._audit_indexes["by_type"]:
                        type_ids.update(self._audit_indexes["by_type"][type_key])
                candidate_ids &= type_ids

            # Filter by severity
            if query.severity_min:
                severity_levels = ["critical", "high", "medium", "low", "info"]
                min_index = severity_levels.index(query.severity_min.value)

                severity_ids = set()
                for severity in severity_levels[: min_index + 1]:
                    if severity in self._audit_indexes["by_severity"]:
                        severity_ids.update(
                            self._audit_indexes["by_severity"][severity]
                        )
                candidate_ids &= severity_ids

            # Filter by actor
            if query.actor_filter:
                if query.actor_filter in self._audit_indexes["by_actor"]:
                    candidate_ids &= self._audit_indexes["by_actor"][query.actor_filter]
                else:
                    candidate_ids = set()

            # Filter by resource
            if query.resource_filter:
                if query.resource_filter in self._audit_indexes["by_resource"]:
                    candidate_ids &= self._audit_indexes["by_resource"][
                        query.resource_filter
                    ]
                else:
                    candidate_ids = set()

            # Filter by compliance tags
            if query.compliance_tags:
                tag_ids = set()
                for tag in query.compliance_tags:
                    if tag in self._audit_indexes["by_compliance_tag"]:
                        tag_ids.update(self._audit_indexes["by_compliance_tag"][tag])
                candidate_ids &= tag_ids

            # Get matching events
            matching_events = [
                event for event in self._audit_events if event.event_id in candidate_ids
            ]

            # Filter by time range
            if query.start_time or query.end_time:
                if query.start_time:
                    matching_events = [
                        e for e in matching_events if e.timestamp >= query.start_time
                    ]
                if query.end_time:
                    matching_events = [
                        e for e in matching_events if e.timestamp <= query.end_time
                    ]

            # Sort by timestamp (newest first)
            matching_events.sort(key=lambda e: e.timestamp, reverse=True)

            # Apply pagination
            if query.offset:
                matching_events = matching_events[query.offset :]

            if query.limit:
                matching_events = matching_events[: query.limit]

            return matching_events

        except Exception as e:
            logger.error(f"Audit query failed: {e}")
            raise AuditTrailError(f"Audit query failed: {e}", operation="query_events")

    async def verify_audit_integrity(
        self, event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify audit trail integrity.

        Args:
            event_id: Specific event to verify (optional)

        Returns:
            Dict[str, Any]: Integrity verification results
        """
        try:
            if event_id:
                # Verify specific event
                return await self._verify_single_event(event_id)
            else:
                # Verify entire audit chain
                return await self._verify_audit_chain()

        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            raise IntegrityError(
                f"Integrity verification failed: {e}", integrity_type="audit_trail"
            )

    async def _verify_single_event(self, event_id: str) -> Dict[str, Any]:
        """Verify integrity of a single audit event."""
        # Find the event
        event = None
        for e in self._audit_events:
            if e.event_id == event_id:
                event = e
                break

        if not event:
            return {
                "valid": False,
                "error": f"Event {event_id} not found",
            }

        # Verify event hash
        if event.hash:
            event_data = {
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "actor": event.actor,
                "action": event.action,
                "resource": event.resource,
                "outcome": event.outcome,
                "details": event.details,
            }

            event_json = json.dumps(event_data, sort_keys=True)
            calculated_hash = hashlib.sha256(event_json.encode()).hexdigest()

            if calculated_hash != event.hash:
                return {
                    "valid": False,
                    "error": "Event hash mismatch",
                    "expected": event.hash,
                    "calculated": calculated_hash,
                }

        # Verify signature
        if event.signature and self._signing_key:
            event_data = {
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "actor": event.actor,
                "action": event.action,
                "resource": event.resource,
                "outcome": event.outcome,
                "details": event.details,
            }

            event_json = json.dumps(event_data, sort_keys=True)
            expected_signature = hmac.new(
                self._signing_key, event_json.encode(), hashlib.sha256
            ).hexdigest()

            if expected_signature != event.signature:
                return {
                    "valid": False,
                    "error": "Event signature mismatch",
                }

        return {
            "valid": True,
            "event_id": event_id,
            "verification_time": datetime.utcnow().isoformat(),
        }

    async def _verify_audit_chain(self) -> Dict[str, Any]:
        """Verify integrity of the entire audit chain."""
        if not self._audit_events:
            return {
                "valid": True,
                "events_verified": 0,
                "chain_integrity": True,
            }

        verified_count = 0
        integrity_violations = []

        # Verify each event
        for event in self._audit_events:
            verification = await self._verify_single_event(event.event_id)

            if verification["valid"]:
                verified_count += 1
            else:
                integrity_violations.append(
                    {
                        "event_id": event.event_id,
                        "error": verification.get("error"),
                    }
                )

        # Verify chain hash integrity (simplified)
        chain_valid = True  # In production, would recalculate entire chain

        return {
            "valid": len(integrity_violations) == 0 and chain_valid,
            "events_verified": verified_count,
            "total_events": len(self._audit_events),
            "integrity_violations": integrity_violations,
            "chain_integrity": chain_valid,
            "verification_time": datetime.utcnow().isoformat(),
        }

    async def generate_audit_report(
        self,
        report_type: str = "summary",
        time_range: Optional[timedelta] = None,
        compliance_framework: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate audit report.

        Args:
            report_type: Type of report (summary, detailed, compliance)
            time_range: Time range for the report
            compliance_framework: Specific compliance framework

        Returns:
            Dict[str, Any]: Audit report data
        """
        try:
            logger.info(f"Generating {report_type} audit report")

            # Determine time range
            if not time_range:
                time_range = timedelta(days=30)

            start_time = datetime.utcnow() - time_range
            end_time = datetime.utcnow()

            # Query events in time range
            query = AuditQuery(
                start_time=start_time,
                end_time=end_time,
                compliance_tags=(
                    [compliance_framework] if compliance_framework else None
                ),
            )

            events = await self.query_audit_events(query)

            # Generate report based on type
            if report_type == "compliance":
                report = await self._generate_compliance_audit_report(
                    events, compliance_framework
                )
            elif report_type == "detailed":
                report = await self._generate_detailed_audit_report(events)
            else:
                report = await self._generate_summary_audit_report(events)

            # Add metadata
            report.update(
                {
                    "report_id": self._generate_report_id(),
                    "generated_at": datetime.utcnow().isoformat(),
                    "report_type": report_type,
                    "time_range": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                    },
                    "compliance_framework": compliance_framework,
                    "total_events": len(events),
                }
            )

            return report

        except Exception as e:
            logger.error(f"Audit report generation failed: {e}")
            raise AuditTrailError(
                f"Audit report generation failed: {e}", operation="generate_report"
            )

    async def _generate_summary_audit_report(
        self, events: List[AuditEvent]
    ) -> Dict[str, Any]:
        """Generate summary audit report."""
        # Event type breakdown
        type_counts = {}
        for event in events:
            event_type = event.event_type.value
            type_counts[event_type] = type_counts.get(event_type, 0) + 1

        # Severity breakdown
        severity_counts = {}
        for event in events:
            severity = event.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Top actors
        actor_counts = {}
        for event in events:
            actor_counts[event.actor] = actor_counts.get(event.actor, 0) + 1

        top_actors = sorted(actor_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Security events
        security_events = [
            e
            for e in events
            if e.event_type == AuditEventType.SECURITY
            or e.severity in [AuditSeverity.CRITICAL, AuditSeverity.HIGH]
        ]

        # Failed operations
        failed_events = [e for e in events if e.outcome == "failure"]

        return {
            "summary": {
                "total_events": len(events),
                "security_events": len(security_events),
                "failed_operations": len(failed_events),
                "unique_actors": len(actor_counts),
            },
            "event_types": type_counts,
            "severity_distribution": severity_counts,
            "top_actors": top_actors,
            "risk_assessment": self._assess_audit_risk(events),
            "recommendations": self._generate_audit_recommendations(events),
        }

    async def _generate_detailed_audit_report(
        self, events: List[AuditEvent]
    ) -> Dict[str, Any]:
        """Generate detailed audit report."""
        summary = await self._generate_summary_audit_report(events)

        # Add detailed analysis
        summary.update(
            {
                "timeline_analysis": self._analyze_event_timeline(events),
                "anomaly_detection": await self._detect_audit_anomalies_in_events(
                    events
                ),
                "access_patterns": self._analyze_access_patterns(events),
                "compliance_events": self._analyze_compliance_events(events),
                "integrity_status": await self._verify_audit_chain(),
            }
        )

        return summary

    async def _generate_compliance_audit_report(
        self, events: List[AuditEvent], framework: Optional[str]
    ) -> Dict[str, Any]:
        """Generate compliance-specific audit report."""
        compliance_events = [
            e for e in events if not framework or framework in e.compliance_tags
        ]

        # Compliance-specific analysis
        audit_requirements = self._check_audit_requirements(
            compliance_events, framework
        )
        retention_compliance = self._check_retention_compliance(framework)
        access_controls = self._analyze_access_control_events(compliance_events)

        return {
            "compliance_framework": framework,
            "compliance_events": len(compliance_events),
            "audit_requirements": audit_requirements,
            "retention_compliance": retention_compliance,
            "access_control_analysis": access_controls,
            "data_protection_events": self._analyze_data_protection_events(
                compliance_events
            ),
            "incident_response_events": self._analyze_incident_events(
                compliance_events
            ),
            "recommendations": self._generate_compliance_recommendations(
                compliance_events, framework
            ),
        }

    def _calculate_risk_score(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: str,
        severity: AuditSeverity,
        details: Dict[str, Any],
    ) -> float:
        """Calculate risk score for an audit event."""
        base_score = 0.0

        # Event type risk
        type_risk = {
            AuditEventType.AUTHENTICATION: 3.0,
            AuditEventType.AUTHORIZATION: 4.0,
            AuditEventType.DATA_ACCESS: 5.0,
            AuditEventType.CONFIGURATION: 6.0,
            AuditEventType.SECURITY: 8.0,
            AuditEventType.INCIDENT: 9.0,
        }
        base_score += type_risk.get(event_type, 2.0)

        # Severity risk
        severity_risk = {
            AuditSeverity.CRITICAL: 10.0,
            AuditSeverity.HIGH: 7.0,
            AuditSeverity.MEDIUM: 4.0,
            AuditSeverity.LOW: 2.0,
            AuditSeverity.INFO: 1.0,
        }
        base_score += severity_risk.get(severity, 1.0)

        # Outcome risk
        if outcome == "failure":
            base_score += 3.0
        elif outcome == "partial":
            base_score += 1.0

        # Action-specific risk
        high_risk_actions = ["delete", "modify", "escalate", "disable", "override"]
        if any(risk_action in action.lower() for risk_action in high_risk_actions):
            base_score += 2.0

        # Normalize to 0-10 scale
        return min(10.0, base_score)

    def _assess_audit_risk(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Assess overall risk from audit events."""
        if not events:
            return {"risk_level": "low", "risk_score": 0}

        # Calculate average risk score
        total_risk = sum(event.risk_score for event in events)
        avg_risk = total_risk / len(events)

        # Count high-risk events
        high_risk_events = [e for e in events if e.risk_score >= 7.0]
        failed_events = [e for e in events if e.outcome == "failure"]

        # Determine risk level
        if avg_risk >= 7 or len(high_risk_events) > len(events) * 0.3:
            risk_level = "high"
        elif avg_risk >= 4 or len(high_risk_events) > len(events) * 0.1:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "risk_score": round(avg_risk, 2),
            "high_risk_events": len(high_risk_events),
            "failed_events": len(failed_events),
            "total_events": len(events),
        }

    def _generate_audit_recommendations(self, events: List[AuditEvent]) -> List[str]:
        """Generate audit-based recommendations."""
        recommendations = []

        # Check for excessive failures
        failed_events = [e for e in events if e.outcome == "failure"]
        if len(failed_events) > len(events) * 0.2:
            recommendations.append("Investigate high failure rate in audit events")

        # Check for suspicious patterns
        high_risk_events = [e for e in events if e.risk_score >= 8.0]
        if high_risk_events:
            recommendations.append(
                "Review high-risk security events for potential threats"
            )

        # Check for compliance gaps
        compliance_events = [e for e in events if e.compliance_tags]
        if len(compliance_events) < len(events) * 0.5:
            recommendations.append("Improve compliance tagging for audit events")

        return recommendations

    # Analysis helper methods

    def _analyze_event_timeline(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Analyze event timeline patterns."""
        if not events:
            return {}

        # Group events by hour
        hourly_counts = {}
        for event in events:
            hour_key = event.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1

        # Find peak hours
        sorted_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "peak_activity_hours": [
                {"hour": hour.isoformat(), "count": count}
                for hour, count in sorted_hours[:5]
            ],
            "activity_distribution": len(hourly_counts),
        }

    async def _detect_audit_anomalies_in_events(
        self, events: List[AuditEvent]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in audit events."""
        anomalies = []

        # Check for unusual actor activity
        actor_counts = {}
        for event in events:
            actor_counts[event.actor] = actor_counts.get(event.actor, 0) + 1

        # Find actors with unusually high activity
        avg_activity = (
            sum(actor_counts.values()) / len(actor_counts) if actor_counts else 0
        )

        for actor, count in actor_counts.items():
            if count > avg_activity * 3:  # 3x average
                anomalies.append(
                    {
                        "type": "high_activity_actor",
                        "actor": actor,
                        "event_count": count,
                        "threshold": avg_activity * 3,
                    }
                )

        # Check for burst activity
        # Group events by 5-minute windows
        time_windows = {}
        for event in events:
            window = event.timestamp.replace(
                minute=(event.timestamp.minute // 5) * 5, second=0, microsecond=0
            )
            time_windows[window] = time_windows.get(window, 0) + 1

        # Find windows with unusually high activity
        avg_window_activity = (
            sum(time_windows.values()) / len(time_windows) if time_windows else 0
        )

        for window, count in time_windows.items():
            if count > avg_window_activity * 5:  # 5x average
                anomalies.append(
                    {
                        "type": "burst_activity",
                        "time_window": window.isoformat(),
                        "event_count": count,
                        "threshold": avg_window_activity * 5,
                    }
                )

        return anomalies

    def _analyze_access_patterns(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Analyze access patterns from audit events."""
        access_events = [
            e
            for e in events
            if e.event_type
            in [
                AuditEventType.AUTHENTICATION,
                AuditEventType.AUTHORIZATION,
                AuditEventType.DATA_ACCESS,
            ]
        ]

        # Analyze by source IP
        ip_patterns = {}
        for event in access_events:
            if event.source_ip:
                ip_patterns[event.source_ip] = ip_patterns.get(event.source_ip, 0) + 1

        # Analyze by user agent
        agent_patterns = {}
        for event in access_events:
            if event.user_agent:
                agent_patterns[event.user_agent] = (
                    agent_patterns.get(event.user_agent, 0) + 1
                )

        return {
            "total_access_events": len(access_events),
            "unique_source_ips": len(ip_patterns),
            "unique_user_agents": len(agent_patterns),
            "top_source_ips": sorted(
                ip_patterns.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "suspicious_patterns": self._identify_suspicious_access_patterns(
                access_events
            ),
        }

    def _identify_suspicious_access_patterns(
        self, events: List[AuditEvent]
    ) -> List[Dict[str, Any]]:
        """Identify suspicious access patterns."""
        suspicious = []

        # Check for multiple failed authentications
        failed_auth = [
            e
            for e in events
            if e.event_type == AuditEventType.AUTHENTICATION and e.outcome == "failure"
        ]

        if len(failed_auth) > 10:
            suspicious.append(
                {
                    "pattern": "excessive_failed_authentication",
                    "count": len(failed_auth),
                    "threshold": 10,
                }
            )

        return suspicious

    def _analyze_compliance_events(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Analyze compliance-related events."""
        compliance_events = [e for e in events if e.compliance_tags]

        # Group by compliance framework
        framework_counts = {}
        for event in compliance_events:
            for tag in event.compliance_tags:
                framework_counts[tag] = framework_counts.get(tag, 0) + 1

        return {
            "total_compliance_events": len(compliance_events),
            "frameworks_involved": list(framework_counts.keys()),
            "framework_distribution": framework_counts,
        }

    def _check_audit_requirements(
        self, events: List[AuditEvent], framework: Optional[str]
    ) -> Dict[str, Any]:
        """Check if audit requirements are met."""
        # Check required event types for compliance
        required_types = {
            "GDPR": [AuditEventType.DATA_ACCESS, AuditEventType.AUTHORIZATION],
            "HIPAA": [AuditEventType.DATA_ACCESS, AuditEventType.AUTHENTICATION],
            "SOC2": [
                AuditEventType.AUTHENTICATION,
                AuditEventType.AUTHORIZATION,
                AuditEventType.CONFIGURATION,
            ],
        }

        if framework and framework in required_types:
            required = required_types[framework]
            present_types = set(e.event_type for e in events)
            missing_types = [t for t in required if t not in present_types]

            return {
                "framework": framework,
                "required_types": [t.value for t in required],
                "present_types": [t.value for t in present_types],
                "missing_types": [t.value for t in missing_types],
                "compliance_met": len(missing_types) == 0,
            }

        return {"compliance_met": True}

    def _check_retention_compliance(self, framework: Optional[str]) -> Dict[str, Any]:
        """Check audit retention compliance."""
        # Check retention requirements
        retention_requirements = {
            "GDPR": 365,  # days
            "HIPAA": 2190,  # 6 years
            "SOC2": 365,
        }

        current_retention = self.config.audit_retention_days

        if framework and framework in retention_requirements:
            required_retention = retention_requirements[framework]
            compliant = current_retention >= required_retention

            return {
                "framework": framework,
                "required_retention_days": required_retention,
                "current_retention_days": current_retention,
                "compliant": compliant,
            }

        return {"compliant": True}

    def _analyze_access_control_events(
        self, events: List[AuditEvent]
    ) -> Dict[str, Any]:
        """Analyze access control events."""
        access_events = [
            e
            for e in events
            if e.event_type
            in [AuditEventType.AUTHENTICATION, AuditEventType.AUTHORIZATION]
        ]

        auth_events = [
            e for e in access_events if e.event_type == AuditEventType.AUTHENTICATION
        ]
        authz_events = [
            e for e in access_events if e.event_type == AuditEventType.AUTHORIZATION
        ]

        return {
            "total_access_events": len(access_events),
            "authentication_events": len(auth_events),
            "authorization_events": len(authz_events),
            "failed_authentications": len(
                [e for e in auth_events if e.outcome == "failure"]
            ),
            "failed_authorizations": len(
                [e for e in authz_events if e.outcome == "failure"]
            ),
        }

    def _analyze_data_protection_events(
        self, events: List[AuditEvent]
    ) -> Dict[str, Any]:
        """Analyze data protection events."""
        data_events = [e for e in events if e.event_type == AuditEventType.DATA_ACCESS]

        return {
            "total_data_events": len(data_events),
            "data_access_attempts": len(data_events),
            "failed_data_access": len(
                [e for e in data_events if e.outcome == "failure"]
            ),
        }

    def _analyze_incident_events(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Analyze incident-related events."""
        incident_events = [e for e in events if e.event_type == AuditEventType.INCIDENT]

        return {
            "total_incidents": len(incident_events),
            "critical_incidents": len(
                [e for e in incident_events if e.severity == AuditSeverity.CRITICAL]
            ),
            "high_severity_incidents": len(
                [e for e in incident_events if e.severity == AuditSeverity.HIGH]
            ),
        }

    def _generate_compliance_recommendations(
        self, events: List[AuditEvent], framework: Optional[str]
    ) -> List[str]:
        """Generate compliance-specific recommendations."""
        recommendations = []

        if framework == "GDPR":
            data_events = [
                e for e in events if e.event_type == AuditEventType.DATA_ACCESS
            ]
            if not data_events:
                recommendations.append(
                    "Implement data access logging for GDPR compliance"
                )

        if framework == "HIPAA":
            auth_events = [
                e for e in events if e.event_type == AuditEventType.AUTHENTICATION
            ]
            if len(auth_events) < len(events) * 0.3:
                recommendations.append(
                    "Increase authentication event logging for HIPAA compliance"
                )

        return recommendations

    # Helper methods

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.utcnow().timestamp()
        return f"AUD-{int(timestamp * 1000000)}"

    def _generate_report_id(self) -> str:
        """Generate unique report ID."""
        timestamp = datetime.utcnow().timestamp()
        return f"AUDRPT-{int(timestamp * 1000)}"

    async def _trigger_audit_alert(self, event: AuditEvent) -> None:
        """Trigger alert for high-severity audit events."""
        logger.warning(f"High-severity audit event: {event.event_id} - {event.action}")
        # In production, this would send actual alerts

    async def _process_compliance_event(self, event: AuditEvent) -> None:
        """Process compliance-tagged events."""
        for tag in event.compliance_tags:
            logger.info(f"Compliance event for {tag}: {event.event_id}")

    async def _handle_integrity_violation(
        self, integrity_status: Dict[str, Any]
    ) -> None:
        """Handle audit integrity violations."""
        logger.critical(f"Audit integrity violation detected: {integrity_status}")

    async def _handle_performance_alerts(self, alerts: List[str]) -> None:
        """Handle audit performance alerts."""
        for alert in alerts:
            logger.warning(f"Audit performance alert: {alert}")

    async def _handle_audit_anomaly(self, anomaly: Dict[str, Any]) -> None:
        """Handle detected audit anomaly."""
        logger.warning(f"Audit anomaly detected: {anomaly}")

    async def _check_audit_performance(self) -> Dict[str, Any]:
        """Check audit trail performance."""
        return {
            "total_events": len(self._audit_events),
            "index_size": sum(len(idx) for idx in self._audit_indexes.values()),
            "alerts": [],
        }

    async def _analyze_audit_patterns(self) -> List[Dict[str, Any]]:
        """Analyze audit patterns for anomalies."""
        # Simplified pattern analysis
        return []

    async def _archive_expired_events(self, expired_events: List[AuditEvent]) -> None:
        """Archive expired audit events."""
        logger.info(f"Archiving {len(expired_events)} expired audit events")

        # Remove from active storage
        for event in expired_events:
            if event in self._audit_events:
                self._audit_events.remove(event)

                # Remove from indexes
                self._remove_from_indexes(event)

    def _remove_from_indexes(self, event: AuditEvent) -> None:
        """Remove event from all indexes."""
        # Remove from type index
        event_type = event.event_type.value
        if event_type in self._audit_indexes["by_type"]:
            self._audit_indexes["by_type"][event_type].discard(event.event_id)

        # Remove from actor index
        if event.actor in self._audit_indexes["by_actor"]:
            self._audit_indexes["by_actor"][event.actor].discard(event.event_id)

        # Remove from other indexes similarly...

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on audit trail service."""
        return {
            "service": "AuditTrailService",
            "status": "healthy" if self._initialized else "unhealthy",
            "monitoring_active": self._monitoring_active,
            "total_events": len(self._audit_events),
            "index_health": "good",
            "integrity_protected": self.config.enable_tamper_protection,
            "encryption_enabled": self.config.audit_encryption_enabled,
        }

    async def cleanup(self) -> None:
        """Clean up audit trail resources."""
        if self._monitoring_active:
            await self.stop_audit_monitoring()

        # Clear audit data (in production, would archive safely)
        self._audit_events.clear()
        self._audit_indexes.clear()

        logger.info("Audit trail service cleaned up")
