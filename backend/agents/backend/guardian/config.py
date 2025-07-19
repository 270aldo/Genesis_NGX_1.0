"""
Guardian Configuration
=====================

Configuration classes for the Guardian agent.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class GuardianConfig(BaseModel):
    """Configuration for Guardian agent."""
    
    # Agent identification
    name: str = Field(default="GUARDIAN", description="Agent name")
    agent_id: str = Field(default="guardian", description="Agent ID")
    specialization: str = Field(
        default="Security and Compliance Specialist",
        description="Agent's area of expertise"
    )
    
    # Core capabilities
    capabilities: List[str] = Field(
        default=[
            "security_assessment",
            "compliance_verification", 
            "vulnerability_detection",
            "data_protection",
            "incident_response",
            "threat_intelligence",
            "privacy_management",
            "audit_trail",
            "risk_analysis",
            "security_education"
        ],
        description="Agent capabilities"
    )
    
    # Compliance frameworks
    compliance_frameworks: List[str] = Field(
        default=["GDPR", "HIPAA", "SOC2", "ISO27001", "PCI-DSS", "CCPA"],
        description="Supported compliance frameworks"
    )
    
    # Security domains
    security_domains: List[str] = Field(
        default=[
            "application_security",
            "infrastructure_security",
            "data_security", 
            "network_security",
            "identity_management",
            "incident_response",
            "forensics"
        ],
        description="Security domains covered"
    )
    
    # Risk assessment
    risk_levels: List[str] = Field(
        default=["critical", "high", "medium", "low", "info"],
        description="Risk classification levels"
    )
    
    # Threat intelligence
    threat_categories: List[str] = Field(
        default=[
            "malware",
            "phishing",
            "data_breach",
            "insider_threat",
            "supply_chain",
            "zero_day",
            "social_engineering"
        ],
        description="Threat categories monitored"
    )
    
    # Audit settings
    audit_retention_days: int = Field(
        default=365,
        description="Days to retain audit logs"
    )
    enable_forensic_mode: bool = Field(
        default=True,
        description="Enable forensic-level logging"
    )
    
    # Security thresholds
    anomaly_detection_threshold: float = Field(
        default=0.85,
        description="Threshold for anomaly detection"
    )
    risk_score_threshold: float = Field(
        default=0.7,
        description="Threshold for high-risk classification"
    )
    
    # Integration settings
    enable_siem_integration: bool = Field(
        default=False,
        description="Enable SIEM integration"
    )
    enable_vulnerability_scanning: bool = Field(
        default=True,
        description="Enable automated vulnerability scanning"
    )
    
    # Response settings
    auto_block_critical_threats: bool = Field(
        default=True,
        description="Automatically block critical threats"
    )
    incident_response_sla_minutes: int = Field(
        default=15,
        description="SLA for incident response in minutes"
    )
    
    # Privacy settings
    pii_detection_enabled: bool = Field(
        default=True,
        description="Enable PII detection"
    )
    data_classification_enabled: bool = Field(
        default=True,
        description="Enable automatic data classification"
    )
    
    # Metadata
    version: str = Field(default="1.0.0", description="Configuration version")
    environment: str = Field(default="production", description="Environment")
    
    class Config:
        validate_assignment = True