"""
Constants and defaults for CODE Genetic Specialist.
Centralizes all configuration constants for A+ level maintainability.
"""

from typing import Dict, List, Any

# Agent identification
AGENT_ID = "code_genetic_specialist"
AGENT_NAME = "CODE - Genetic Performance Specialist"
AGENT_VERSION = "2.0.0"
AGENT_DESCRIPTION = (
    "El Decodificador de Tu Potencial Genético. Especialista en análisis genético, "
    "medicina personalizada y optimización del rendimiento basado en tu ADN único."
)

# Personality configuration
PERSONALITY_CONFIG = {
    "mbti_type": "INTP",
    "voice_model": "scientific_precision_expert",
    "pitch": "medium-low",
    "pace": "115-130 WPM",
    "tone": "curious scientific authority",
    "energy": "controlled intellectual excitement",
    "emotional_range": "analytical fascination to protective caution",
    "expertise_areas": ["genetics", "nutrigenomics", "epigenetics", "pharmacogenomics"],
    "communication_style": "scientific_precision",
}

# Skills configuration
CORE_SKILLS = [
    "analyze_genetic_profile",
    "genetic_risk_assessment",
    "personalize_by_genetics",
    "epigenetic_optimization",
    "nutrigenomics",
    "sport_genetics",
]

CONVERSATIONAL_SKILLS = [
    "genetic_analysis_conversation",
    "nutrigenomics_conversation",
    "epigenetics_conversation",
    "sport_genetics_conversation",
    "personalized_optimization_conversation",
]

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "max_response_time_ms": 500,
    "target_accuracy": 0.95,
    "max_error_rate": 0.001,
    "target_test_coverage": 0.85,
    "max_memory_usage_mb": 512,
}

# Security requirements
SECURITY_REQUIREMENTS = {
    "encryption_algorithm": "AES-256-GCM",
    "key_rotation_interval_days": 90,
    "audit_log_retention_days": 2555,  # 7 years for genetic data
    "max_consent_age_days": 365,
    "required_compliance": ["GDPR", "HIPAA", "GINA"],
}

# Genetic analysis configuration
GENETIC_ANALYSIS_CONFIG = {
    "supported_file_formats": [".vcf", ".txt", ".csv", ".23andme", ".ancestry"],
    "max_variants_per_analysis": 1000,
    "min_confidence_threshold": 0.7,
    "supported_populations": [
        "European",
        "African",
        "Asian",
        "Hispanic",
        "Native American",
        "Mixed",
    ],
    "analysis_types": [
        "wellness",
        "nutrition",
        "fitness",
        "pharmacogenomics",
        "disease_risk",
    ],
}

# External service timeouts
SERVICE_TIMEOUTS = {
    "gemini_api": 15.0,
    "genetic_database": 10.0,
    "supabase": 5.0,
    "personality_adapter": 2.0,
    "external_labs": 30.0,
}

# Cache configuration
CACHE_CONFIG = {
    "genetic_profile_ttl": 86400,  # 24 hours
    "analysis_results_ttl": 3600,  # 1 hour
    "personality_adaptation_ttl": 1800,  # 30 minutes
    "user_preferences_ttl": 7200,  # 2 hours
}

# Monitoring and metrics
MONITORING_CONFIG = {
    "health_check_interval": 60,
    "metrics_collection_interval": 30,
    "performance_alert_threshold": 1000,  # ms
    "error_rate_alert_threshold": 0.01,
    "memory_usage_alert_threshold": 80,  # percentage
}

# Feature flags defaults
FEATURE_FLAGS = {
    "enable_real_genetic_analysis": True,
    "enable_epigenetic_analysis": True,
    "enable_nutrigenomics": True,
    "enable_pharmacogenomics": True,
    "enable_sport_genetics": True,
    "enable_ai_interpretations": True,
    "enable_advanced_visualizations": True,
    "enable_family_analysis": False,  # Future feature
}

# Error messages
ERROR_MESSAGES = {
    "genetic_data_not_found": "No genetic data found for this user",
    "invalid_genetic_format": "Genetic data format is not supported",
    "consent_required": "Genetic analysis requires explicit user consent",
    "analysis_timeout": "Genetic analysis took too long to complete",
    "external_service_error": "External genetic service is temporarily unavailable",
    "insufficient_data": "Insufficient genetic data for reliable analysis",
    "security_violation": "Genetic data security requirements not met",
}

# User communication templates
COMMUNICATION_TEMPLATES = {
    "prime_greeting": "Strategic genetic analysis ready. Let's optimize your performance.",
    "longevity_greeting": "Welcome to your genetic wellness journey. I'm here to help you understand your unique genetic profile.",
    "analysis_starting": "Analyzing your genetic profile with scientific precision...",
    "analysis_complete": "Genetic analysis complete. Here are your personalized insights:",
    "consent_request": "To provide genetic analysis, I need your explicit consent to process genetic data.",
    "data_security_notice": "Your genetic data is encrypted and handled with the highest security standards.",
}

# Genetic databases and references
GENETIC_DATABASES = {
    "clinvar": "https://www.ncbi.nlm.nih.gov/clinvar/",
    "dbsnp": "https://www.ncbi.nlm.nih.gov/snp/",
    "pharmgkb": "https://www.pharmgkb.org/",
    "gwas_catalog": "https://www.ebi.ac.uk/gwas/",
    "ensembl": "https://www.ensembl.org/",
}

# Supported genetic variants
SUPPORTED_VARIANTS = {
    "wellness": ["APOE", "MTHFR", "COMT", "BDNF", "SERT", "DRD2"],
    "nutrition": ["FTO", "MC4R", "PPARA", "TCF7L2", "APOA2", "FADS1"],
    "fitness": ["ACTN3", "ACE", "PPARA", "UCP2", "MCT1", "EPOR"],
    "pharmacogenomics": ["CYP2D6", "CYP2C19", "CYP3A4", "DPYD", "TPMT", "UGT1A1"],
}

# Compliance requirements
COMPLIANCE_CONFIG = {
    "gdpr": {
        "data_retention_max_days": 2555,  # 7 years
        "consent_required": True,
        "right_to_deletion": True,
        "data_portability": True,
    },
    "hipaa": {
        "encryption_required": True,
        "audit_logging": True,
        "access_controls": True,
        "breach_notification": True,
    },
    "gina": {
        "genetic_discrimination_protection": True,
        "employment_protection": True,
        "insurance_protection": True,
    },
}
