"""
Core module for GUARDIAN Security Compliance.
Provides foundational components for A+ level architecture.
"""

from .config import GuardianConfig
from .constants import (
    AGENT_ID,
    AGENT_NAME,
    AGENT_VERSION,
    PERSONALITY_CONFIG,
    CORE_SKILLS,
    VISUAL_SKILLS,
    CONVERSATIONAL_SKILLS,
    COMPLIANCE_FRAMEWORKS,
    SECURITY_CONTROLS,
    THREAT_CATEGORIES,
)
from .dependencies import GuardianDependencies, create_guardian_dependencies
from .exceptions import (
    GuardianSecurityError,
    GuardianValidationError,
    ComplianceViolationError,
    SecurityThreatError,
    AuditTrailError,
    DataProtectionError,
    AuthorizationError,
    EncryptionError,
    MonitoringError,
    VulnerabilityError,
    AccessControlError,
    IntegrityError,
    PrivacyViolationError,
    SecurityConfigurationError,
    ThreatDetectionError,
    IncidentResponseError,
)

__all__ = [
    # Config
    "GuardianConfig",
    # Constants
    "AGENT_ID",
    "AGENT_NAME",
    "AGENT_VERSION",
    "PERSONALITY_CONFIG",
    "CORE_SKILLS",
    "VISUAL_SKILLS",
    "CONVERSATIONAL_SKILLS",
    "COMPLIANCE_FRAMEWORKS",
    "SECURITY_CONTROLS",
    "THREAT_CATEGORIES",
    # Dependencies
    "GuardianDependencies",
    "create_guardian_dependencies",
    # Exceptions
    "GuardianSecurityError",
    "GuardianValidationError",
    "ComplianceViolationError",
    "SecurityThreatError",
    "AuditTrailError",
    "DataProtectionError",
    "AuthorizationError",
    "EncryptionError",
    "MonitoringError",
    "VulnerabilityError",
    "AccessControlError",
    "IntegrityError",
    "PrivacyViolationError",
    "SecurityConfigurationError",
    "ThreatDetectionError",
    "IncidentResponseError",
]
