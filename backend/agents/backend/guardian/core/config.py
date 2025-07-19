"""
Configuration module for GUARDIAN Security Compliance agent.
Manages all security, compliance, and audit settings.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import os
from datetime import timedelta


@dataclass
class GuardianConfig:
    """
    Configuration for GUARDIAN Security Compliance agent.

    This class manages all security and compliance settings including:
    - Security monitoring and threat detection
    - Compliance framework configurations
    - Audit trail management
    - Data protection and privacy settings
    - Access control and authorization
    """

    # Core configuration
    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "production")
    )
    agent_id: str = "guardian_security_compliance"
    agent_name: str = "GUARDIAN Security Compliance"
    agent_version: str = "2.0.0"

    # Security configuration
    enable_security_monitoring: bool = True
    enable_threat_detection: bool = True
    enable_vulnerability_scanning: bool = True
    enable_intrusion_detection: bool = True
    enable_anomaly_detection: bool = True
    threat_level_threshold: str = "medium"  # low, medium, high, critical

    # Compliance configuration
    enable_compliance_monitoring: bool = True
    compliance_frameworks: List[str] = field(
        default_factory=lambda: ["GDPR", "HIPAA", "SOC2", "ISO27001", "PCI-DSS", "CCPA"]
    )
    compliance_check_interval: int = 3600  # seconds (1 hour)
    enable_automated_remediation: bool = True

    # Audit configuration
    enable_audit_trail: bool = True
    audit_retention_days: int = 365  # 1 year retention
    enable_tamper_protection: bool = True
    audit_encryption_enabled: bool = True
    audit_log_level: str = "detailed"  # minimal, standard, detailed

    # Data protection configuration
    enable_data_encryption: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    enable_data_masking: bool = True
    enable_pii_detection: bool = True
    data_classification_enabled: bool = True

    # Access control configuration
    enable_role_based_access: bool = True
    enable_multi_factor_auth: bool = True
    session_timeout_minutes: int = 30
    max_failed_login_attempts: int = 3
    account_lockout_duration_minutes: int = 15

    # Monitoring and alerting
    enable_real_time_monitoring: bool = True
    alert_channels: List[str] = field(
        default_factory=lambda: ["email", "sms", "webhook", "dashboard"]
    )
    critical_alert_response_time: int = 60  # seconds
    monitoring_retention_days: int = 90

    # Performance and resource limits
    max_concurrent_scans: int = 10
    scan_timeout_seconds: int = 300
    max_audit_records_per_batch: int = 1000
    monitoring_sample_rate: float = 1.0  # 100% sampling

    # Integration settings
    enable_siem_integration: bool = True
    enable_soar_integration: bool = True
    enable_threat_intelligence: bool = True
    threat_feed_update_interval: int = 3600  # 1 hour

    # Incident response
    enable_incident_response: bool = True
    incident_severity_levels: List[str] = field(
        default_factory=lambda: ["info", "low", "medium", "high", "critical"]
    )
    auto_containment_enabled: bool = True
    incident_response_playbooks: bool = True

    # Privacy configuration
    enable_privacy_protection: bool = True
    data_minimization_enabled: bool = True
    consent_management_enabled: bool = True
    right_to_erasure_enabled: bool = True

    # AI and ML security
    enable_ai_security_monitoring: bool = True
    model_integrity_checks: bool = True
    adversarial_detection: bool = True
    bias_detection_enabled: bool = True

    def get_security_config(self) -> Dict[str, Any]:
        """Get security-specific configuration."""
        return {
            "monitoring_enabled": self.enable_security_monitoring,
            "threat_detection": self.enable_threat_detection,
            "vulnerability_scanning": self.enable_vulnerability_scanning,
            "intrusion_detection": self.enable_intrusion_detection,
            "anomaly_detection": self.enable_anomaly_detection,
            "threat_threshold": self.threat_level_threshold,
            "real_time_monitoring": self.enable_real_time_monitoring,
        }

    def get_compliance_config(self) -> Dict[str, Any]:
        """Get compliance-specific configuration."""
        return {
            "frameworks": self.compliance_frameworks,
            "check_interval": self.compliance_check_interval,
            "automated_remediation": self.enable_automated_remediation,
            "monitoring_enabled": self.enable_compliance_monitoring,
        }

    def get_audit_config(self) -> Dict[str, Any]:
        """Get audit trail configuration."""
        return {
            "enabled": self.enable_audit_trail,
            "retention_days": self.audit_retention_days,
            "tamper_protection": self.enable_tamper_protection,
            "encryption": self.audit_encryption_enabled,
            "log_level": self.audit_log_level,
            "max_records_per_batch": self.max_audit_records_per_batch,
        }

    def get_data_protection_config(self) -> Dict[str, Any]:
        """Get data protection configuration."""
        return {
            "encryption_enabled": self.enable_data_encryption,
            "encryption_algorithm": self.encryption_algorithm,
            "data_masking": self.enable_data_masking,
            "pii_detection": self.enable_pii_detection,
            "classification": self.data_classification_enabled,
            "privacy_protection": self.enable_privacy_protection,
        }

    def get_access_control_config(self) -> Dict[str, Any]:
        """Get access control configuration."""
        return {
            "rbac_enabled": self.enable_role_based_access,
            "mfa_enabled": self.enable_multi_factor_auth,
            "session_timeout": self.session_timeout_minutes,
            "max_failed_attempts": self.max_failed_login_attempts,
            "lockout_duration": self.account_lockout_duration_minutes,
        }

    def get_incident_response_config(self) -> Dict[str, Any]:
        """Get incident response configuration."""
        return {
            "enabled": self.enable_incident_response,
            "severity_levels": self.incident_severity_levels,
            "auto_containment": self.auto_containment_enabled,
            "playbooks_enabled": self.incident_response_playbooks,
            "response_time": self.critical_alert_response_time,
        }

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values."""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")

    def validate_config(self) -> bool:
        """Validate configuration values."""
        validations = [
            self.threat_level_threshold in ["low", "medium", "high", "critical"],
            self.audit_log_level in ["minimal", "standard", "detailed"],
            self.compliance_check_interval > 0,
            self.audit_retention_days > 0,
            self.session_timeout_minutes > 0,
            self.max_failed_login_attempts > 0,
            0.0 < self.monitoring_sample_rate <= 1.0,
        ]

        return all(validations)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "security": self.get_security_config(),
            "compliance": self.get_compliance_config(),
            "audit": self.get_audit_config(),
            "data_protection": self.get_data_protection_config(),
            "access_control": self.get_access_control_config(),
            "incident_response": self.get_incident_response_config(),
        }
