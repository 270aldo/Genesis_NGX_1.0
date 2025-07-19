"""
Exceptions module for GUARDIAN Security Compliance agent.
Defines all security, compliance, and audit-related exceptions.
"""

from typing import Optional, Dict, Any


class GuardianSecurityError(Exception):
    """Base exception for all GUARDIAN security errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.error_code = error_code or "GUARDIAN_ERROR"
        self.details = details or {}


class GuardianValidationError(GuardianSecurityError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {},
        )


class ComplianceViolationError(GuardianSecurityError):
    """Raised when a compliance violation is detected."""

    def __init__(
        self,
        message: str,
        framework: str,
        requirement: Optional[str] = None,
        severity: str = "high",
    ):
        super().__init__(
            message,
            error_code="COMPLIANCE_VIOLATION",
            details={
                "framework": framework,
                "requirement": requirement,
                "severity": severity,
            },
        )


class SecurityThreatError(GuardianSecurityError):
    """Raised when a security threat is detected."""

    def __init__(
        self,
        message: str,
        threat_type: str,
        severity: str = "high",
        affected_resources: Optional[list] = None,
    ):
        super().__init__(
            message,
            error_code="SECURITY_THREAT",
            details={
                "threat_type": threat_type,
                "severity": severity,
                "affected_resources": affected_resources or [],
            },
        )


class AuditTrailError(GuardianSecurityError):
    """Raised when audit trail operations fail."""

    def __init__(self, message: str, operation: str, audit_id: Optional[str] = None):
        super().__init__(
            message,
            error_code="AUDIT_TRAIL_ERROR",
            details={"operation": operation, "audit_id": audit_id},
        )


class DataProtectionError(GuardianSecurityError):
    """Raised when data protection mechanisms fail."""

    def __init__(
        self,
        message: str,
        protection_type: str,
        data_classification: Optional[str] = None,
    ):
        super().__init__(
            message,
            error_code="DATA_PROTECTION_ERROR",
            details={
                "protection_type": protection_type,
                "data_classification": data_classification,
            },
        )


class AuthorizationError(GuardianSecurityError):
    """Raised when authorization checks fail."""

    def __init__(
        self,
        message: str,
        required_permission: str,
        user_role: Optional[str] = None,
        resource: Optional[str] = None,
    ):
        super().__init__(
            message,
            error_code="AUTHORIZATION_ERROR",
            details={
                "required_permission": required_permission,
                "user_role": user_role,
                "resource": resource,
            },
        )


class EncryptionError(GuardianSecurityError):
    """Raised when encryption/decryption operations fail."""

    def __init__(self, message: str, operation: str, algorithm: Optional[str] = None):
        super().__init__(
            message,
            error_code="ENCRYPTION_ERROR",
            details={"operation": operation, "algorithm": algorithm},
        )


class MonitoringError(GuardianSecurityError):
    """Raised when security monitoring fails."""

    def __init__(self, message: str, monitor_type: str, target: Optional[str] = None):
        super().__init__(
            message,
            error_code="MONITORING_ERROR",
            details={"monitor_type": monitor_type, "target": target},
        )


class VulnerabilityError(GuardianSecurityError):
    """Raised when vulnerability scanning or assessment fails."""

    def __init__(
        self,
        message: str,
        vulnerability_type: str,
        cvss_score: Optional[float] = None,
        cve_id: Optional[str] = None,
    ):
        super().__init__(
            message,
            error_code="VULNERABILITY_ERROR",
            details={
                "vulnerability_type": vulnerability_type,
                "cvss_score": cvss_score,
                "cve_id": cve_id,
            },
        )


class AccessControlError(GuardianSecurityError):
    """Raised when access control mechanisms fail."""

    def __init__(
        self,
        message: str,
        access_type: str,
        resource: Optional[str] = None,
        user: Optional[str] = None,
    ):
        super().__init__(
            message,
            error_code="ACCESS_CONTROL_ERROR",
            details={"access_type": access_type, "resource": resource, "user": user},
        )


class IntegrityError(GuardianSecurityError):
    """Raised when data or system integrity is compromised."""

    def __init__(
        self,
        message: str,
        integrity_type: str,
        expected_hash: Optional[str] = None,
        actual_hash: Optional[str] = None,
    ):
        super().__init__(
            message,
            error_code="INTEGRITY_ERROR",
            details={
                "integrity_type": integrity_type,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
            },
        )


class PrivacyViolationError(GuardianSecurityError):
    """Raised when privacy violations are detected."""

    def __init__(
        self,
        message: str,
        violation_type: str,
        data_type: Optional[str] = None,
        regulation: Optional[str] = None,
    ):
        super().__init__(
            message,
            error_code="PRIVACY_VIOLATION",
            details={
                "violation_type": violation_type,
                "data_type": data_type,
                "regulation": regulation,
            },
        )


class SecurityConfigurationError(GuardianSecurityError):
    """Raised when security configuration is invalid or insecure."""

    def __init__(
        self, message: str, config_type: str, misconfiguration: Optional[str] = None
    ):
        super().__init__(
            message,
            error_code="SECURITY_CONFIGURATION_ERROR",
            details={"config_type": config_type, "misconfiguration": misconfiguration},
        )


class ThreatDetectionError(GuardianSecurityError):
    """Raised when threat detection mechanisms fail."""

    def __init__(
        self,
        message: str,
        detection_method: str,
        false_positive_rate: Optional[float] = None,
    ):
        super().__init__(
            message,
            error_code="THREAT_DETECTION_ERROR",
            details={
                "detection_method": detection_method,
                "false_positive_rate": false_positive_rate,
            },
        )


class IncidentResponseError(GuardianSecurityError):
    """Raised when incident response procedures fail."""

    def __init__(
        self,
        message: str,
        incident_id: str,
        response_phase: str,
        playbook: Optional[str] = None,
    ):
        super().__init__(
            message,
            error_code="INCIDENT_RESPONSE_ERROR",
            details={
                "incident_id": incident_id,
                "response_phase": response_phase,
                "playbook": playbook,
            },
        )
