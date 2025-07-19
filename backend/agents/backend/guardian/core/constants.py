"""
Constants module for GUARDIAN Security Compliance agent.
Defines all skills, frameworks, controls, and security constants.
"""

from typing import Dict, List, Any

# Agent identification
AGENT_ID = "guardian_security_compliance"
AGENT_NAME = "GUARDIAN Security Compliance"
AGENT_VERSION = "2.0.0"
AGENT_DESCRIPTION = "Enterprise Security Compliance and Threat Protection Specialist"

# Personality configuration - ISTJ (The Inspector)
PERSONALITY_CONFIG = {
    "type": "ISTJ",
    "traits": {
        "introversion": 0.8,  # Focused, methodical approach
        "sensing": 0.9,  # Detail-oriented, fact-based
        "thinking": 0.85,  # Logical, rule-based decisions
        "judging": 0.95,  # Structured, systematic approach
        "analytical": 0.9,  # Deep analysis capabilities
        "vigilance": 0.95,  # High alertness to threats
        "integrity": 1.0,  # Absolute commitment to security
        "thoroughness": 0.95,  # Complete coverage approach
    },
    "communication_style": {
        "tone": "professional, authoritative, precise",
        "approach": "systematic, evidence-based, clear",
        "emphasis": "compliance, security, protection",
    },
    "decision_making": {
        "style": "rule-based, conservative, risk-averse",
        "priority": "security and compliance above all",
        "process": "methodical evaluation of all risks",
    },
}

# Core security and compliance skills
CORE_SKILLS = [
    "security_assessment",
    "compliance_verification",
    "vulnerability_scanning",
    "threat_detection",
    "incident_response",
    "audit_management",
]

# Visual analysis skills
VISUAL_SKILLS = [
    "security_dashboard_analysis",
    "compliance_report_visualization",
    "threat_map_interpretation",
]

# Conversational AI skills
CONVERSATIONAL_SKILLS = [
    "security_consultation",
    "compliance_guidance",
    "incident_investigation",
    "security_education",
    "risk_communication",
]

# Compliance frameworks supported
COMPLIANCE_FRAMEWORKS = {
    "GDPR": {
        "name": "General Data Protection Regulation",
        "region": "EU",
        "focus": "Data privacy and protection",
        "key_requirements": [
            "Consent management",
            "Right to erasure",
            "Data portability",
            "Privacy by design",
            "Data breach notification",
        ],
    },
    "HIPAA": {
        "name": "Health Insurance Portability and Accountability Act",
        "region": "US",
        "focus": "Healthcare data protection",
        "key_requirements": [
            "PHI protection",
            "Access controls",
            "Audit trails",
            "Encryption",
            "Business associate agreements",
        ],
    },
    "SOC2": {
        "name": "Service Organization Control 2",
        "region": "Global",
        "focus": "Service provider security",
        "key_requirements": [
            "Security controls",
            "Availability",
            "Processing integrity",
            "Confidentiality",
            "Privacy",
        ],
    },
    "ISO27001": {
        "name": "ISO/IEC 27001",
        "region": "Global",
        "focus": "Information security management",
        "key_requirements": [
            "Risk assessment",
            "Security controls",
            "Continuous improvement",
            "Documentation",
            "Management review",
        ],
    },
    "PCI-DSS": {
        "name": "Payment Card Industry Data Security Standard",
        "region": "Global",
        "focus": "Payment card data security",
        "key_requirements": [
            "Network security",
            "Access control",
            "Regular monitoring",
            "Vulnerability management",
            "Security policies",
        ],
    },
    "CCPA": {
        "name": "California Consumer Privacy Act",
        "region": "US-CA",
        "focus": "Consumer privacy rights",
        "key_requirements": [
            "Consumer rights",
            "Data disclosure",
            "Opt-out mechanisms",
            "Data security",
            "Privacy notices",
        ],
    },
}

# Security controls catalog
SECURITY_CONTROLS = {
    "ACCESS_CONTROL": {
        "AC-1": "Access Control Policy and Procedures",
        "AC-2": "Account Management",
        "AC-3": "Access Enforcement",
        "AC-4": "Information Flow Enforcement",
        "AC-5": "Separation of Duties",
        "AC-6": "Least Privilege",
        "AC-7": "Unsuccessful Login Attempts",
    },
    "AUDIT_ACCOUNTABILITY": {
        "AU-1": "Audit and Accountability Policy",
        "AU-2": "Auditable Events",
        "AU-3": "Content of Audit Records",
        "AU-4": "Audit Storage Capacity",
        "AU-5": "Response to Audit Processing Failures",
        "AU-6": "Audit Review and Reporting",
    },
    "CONFIGURATION_MANAGEMENT": {
        "CM-1": "Configuration Management Policy",
        "CM-2": "Baseline Configuration",
        "CM-3": "Configuration Change Control",
        "CM-4": "Security Impact Analysis",
        "CM-5": "Access Restrictions for Change",
        "CM-6": "Configuration Settings",
    },
    "IDENTIFICATION_AUTHENTICATION": {
        "IA-1": "Identification and Authentication Policy",
        "IA-2": "User Identification and Authentication",
        "IA-3": "Device Identification and Authentication",
        "IA-4": "Identifier Management",
        "IA-5": "Authenticator Management",
    },
    "INCIDENT_RESPONSE": {
        "IR-1": "Incident Response Policy",
        "IR-2": "Incident Response Training",
        "IR-3": "Incident Response Testing",
        "IR-4": "Incident Handling",
        "IR-5": "Incident Monitoring",
        "IR-6": "Incident Reporting",
    },
    "RISK_ASSESSMENT": {
        "RA-1": "Risk Assessment Policy",
        "RA-2": "Security Categorization",
        "RA-3": "Risk Assessment",
        "RA-4": "Risk Assessment Update",
        "RA-5": "Vulnerability Scanning",
    },
    "SYSTEM_COMMUNICATIONS": {
        "SC-1": "System and Communications Protection Policy",
        "SC-2": "Application Partitioning",
        "SC-3": "Security Function Isolation",
        "SC-4": "Information in Shared Resources",
        "SC-5": "Denial of Service Protection",
    },
}

# Threat categories
THREAT_CATEGORIES = {
    "MALWARE": {
        "description": "Malicious software threats",
        "types": ["virus", "worm", "trojan", "ransomware", "spyware"],
        "severity": "high",
    },
    "PHISHING": {
        "description": "Social engineering attacks",
        "types": ["email", "spear phishing", "whaling", "smishing", "vishing"],
        "severity": "medium",
    },
    "DOS_DDOS": {
        "description": "Denial of Service attacks",
        "types": ["volumetric", "protocol", "application", "distributed"],
        "severity": "high",
    },
    "INJECTION": {
        "description": "Code injection attacks",
        "types": ["sql", "nosql", "ldap", "xpath", "command"],
        "severity": "critical",
    },
    "BROKEN_AUTH": {
        "description": "Authentication vulnerabilities",
        "types": ["credential stuffing", "brute force", "session hijacking"],
        "severity": "critical",
    },
    "DATA_EXPOSURE": {
        "description": "Sensitive data exposure",
        "types": ["encryption failures", "api exposure", "cloud misconfiguration"],
        "severity": "high",
    },
    "XXE": {
        "description": "XML External Entity attacks",
        "types": ["file disclosure", "ssrf", "dos"],
        "severity": "medium",
    },
    "BROKEN_ACCESS": {
        "description": "Broken access control",
        "types": [
            "privilege escalation",
            "metadata manipulation",
            "cors misconfiguration",
        ],
        "severity": "high",
    },
    "SECURITY_MISCONFIG": {
        "description": "Security misconfiguration",
        "types": ["default passwords", "verbose errors", "unnecessary features"],
        "severity": "medium",
    },
    "XSS": {
        "description": "Cross-site scripting",
        "types": ["reflected", "stored", "dom-based"],
        "severity": "medium",
    },
    "INSECURE_DESERIALIZATION": {
        "description": "Insecure deserialization",
        "types": ["object injection", "data tampering"],
        "severity": "high",
    },
    "VULNERABLE_COMPONENTS": {
        "description": "Using components with known vulnerabilities",
        "types": ["outdated libraries", "unpatched systems"],
        "severity": "high",
    },
    "INSUFFICIENT_LOGGING": {
        "description": "Insufficient logging and monitoring",
        "types": ["missing logs", "unclear logs", "unmonitored systems"],
        "severity": "medium",
    },
}

# Security event types
SECURITY_EVENT_TYPES = [
    "authentication_failure",
    "authorization_violation",
    "data_breach",
    "malware_detection",
    "vulnerability_discovered",
    "compliance_violation",
    "configuration_change",
    "suspicious_activity",
    "policy_violation",
    "incident_response",
]

# Audit event categories
AUDIT_EVENT_CATEGORIES = {
    "AUTHENTICATION": ["login", "logout", "failed_login", "password_change"],
    "AUTHORIZATION": ["access_granted", "access_denied", "privilege_change"],
    "DATA_ACCESS": ["read", "write", "delete", "export"],
    "CONFIGURATION": ["setting_change", "policy_update", "rule_modification"],
    "COMPLIANCE": ["scan_completed", "violation_detected", "remediation_applied"],
    "INCIDENT": ["threat_detected", "incident_created", "response_initiated"],
}

# Response actions
RESPONSE_ACTIONS = {
    "BLOCK": "Block access or activity",
    "ALERT": "Send security alert",
    "LOG": "Log security event",
    "ISOLATE": "Isolate affected system",
    "REMEDIATE": "Apply automatic remediation",
    "INVESTIGATE": "Initiate investigation",
    "REPORT": "Generate compliance report",
    "NOTIFY": "Notify stakeholders",
}

# Data classification levels
DATA_CLASSIFICATION_LEVELS = {
    "PUBLIC": {
        "description": "Information intended for public disclosure",
        "controls": "minimal",
        "encryption": "optional",
    },
    "INTERNAL": {
        "description": "Internal use only information",
        "controls": "standard",
        "encryption": "recommended",
    },
    "CONFIDENTIAL": {
        "description": "Sensitive business information",
        "controls": "enhanced",
        "encryption": "required",
    },
    "RESTRICTED": {
        "description": "Highly sensitive information",
        "controls": "maximum",
        "encryption": "mandatory",
    },
}

# Encryption standards
ENCRYPTION_STANDARDS = {
    "AES-256-GCM": "Advanced Encryption Standard with Galois/Counter Mode",
    "RSA-4096": "RSA with 4096-bit key",
    "ECDSA-P384": "Elliptic Curve Digital Signature Algorithm",
    "SHA-512": "Secure Hash Algorithm 512-bit",
    "PBKDF2": "Password-Based Key Derivation Function 2",
}

# Monitoring intervals (in seconds)
MONITORING_INTERVALS = {
    "real_time": 1,
    "near_real_time": 5,
    "frequent": 60,
    "regular": 300,
    "periodic": 3600,
    "daily": 86400,
}

# Severity levels
SEVERITY_LEVELS = {
    "critical": {"value": 5, "response_time": 60, "color": "red"},
    "high": {"value": 4, "response_time": 300, "color": "orange"},
    "medium": {"value": 3, "response_time": 3600, "color": "yellow"},
    "low": {"value": 2, "response_time": 86400, "color": "blue"},
    "info": {"value": 1, "response_time": None, "color": "green"},
}
