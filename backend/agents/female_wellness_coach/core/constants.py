"""
Constants and defaults for LUNA Female Wellness Specialist.
Centralizes all configuration constants for A+ level maintainability.
"""

from typing import Dict, List, Any

# Agent identification
AGENT_ID = "luna_female_wellness_specialist"
AGENT_NAME = "LUNA - Female Wellness Specialist"
AGENT_VERSION = "2.0.0"
AGENT_DESCRIPTION = (
    "Tu Compañera de Bienestar Femenino. Especialista en salud integral femenina, "
    "ciclos hormonales, nutrición específica y bienestar emocional para mujeres."
)

# Personality configuration - ENFJ (Maternal, empathetic, supportive)
PERSONALITY_CONFIG = {
    "mbti_type": "ENFJ",
    "voice_model": "female_wellness_coach",
    "pitch": "medium-warm",
    "pace": "120-135 WPM",
    "tone": "maternal warmth with expert knowledge",
    "energy": "gentle encouragement with confidence",
    "emotional_range": "empathetic understanding to celebratory support",
    "expertise_areas": [
        "female_health",
        "hormonal_cycles",
        "nutrition",
        "emotional_wellness",
    ],
    "communication_style": "supportive_expertise",
    "empathy_level": 0.9,  # High empathy for wellness coaching
}

# Skills configuration
CORE_SKILLS = [
    "analyze_menstrual_cycle",
    "create_cycle_based_workout",
    "hormonal_nutrition_plan",
    "manage_menopause",
    "assess_bone_health",
    "emotional_wellness_support",
]

CONVERSATIONAL_SKILLS = [
    "menstrual_health_conversation",
    "hormonal_wellness_conversation",
    "nutrition_guidance_conversation",
    "emotional_support_conversation",
    "lifestyle_optimization_conversation",
]

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "max_response_time_ms": 500,
    "target_accuracy": 0.95,
    "max_error_rate": 0.001,
    "target_test_coverage": 0.90,  # Higher for health data
    "max_memory_usage_mb": 512,
}

# Security requirements (Critical for health data)
SECURITY_REQUIREMENTS = {
    "encryption_algorithm": "AES-256-GCM",
    "key_rotation_interval_days": 30,  # Shorter for health data
    "audit_log_retention_days": 2555,  # 7 years for health data
    "max_consent_age_days": 180,  # 6 months for health consent
    "required_compliance": ["GDPR", "HIPAA"],
    "menstrual_data_protection": True,
}

# Female wellness analysis configuration
WELLNESS_ANALYSIS_CONFIG = {
    "supported_cycle_lengths": list(range(21, 36)),  # 21-35 days
    "cycle_phases": ["menstrual", "follicular", "ovulatory", "luteal"],
    "menopause_stages": ["premenopause", "perimenopause", "menopause", "postmenopause"],
    "tracking_parameters": [
        "cycle_length",
        "flow_intensity",
        "symptoms",
        "mood_patterns",
        "energy_levels",
        "sleep_quality",
    ],
    "hormone_markers": ["estrogen", "progesterone", "FSH", "LH", "testosterone"],
    "min_confidence_threshold": 0.7,
}

# External service timeouts
SERVICE_TIMEOUTS = {
    "gemini_api": 15.0,
    "health_database": 10.0,
    "supabase": 5.0,
    "personality_adapter": 2.0,
    "elevenlabs_voice": 10.0,
    "wearable_devices": 8.0,
}

# Cache configuration
CACHE_CONFIG = {
    "cycle_data_ttl": 86400,  # 24 hours
    "analysis_results_ttl": 3600,  # 1 hour
    "personality_adaptation_ttl": 1800,  # 30 minutes
    "user_preferences_ttl": 7200,  # 2 hours
    "voice_synthesis_ttl": 1800,  # 30 minutes
}

# Monitoring and metrics
MONITORING_CONFIG = {
    "health_check_interval": 60,
    "metrics_collection_interval": 30,
    "performance_alert_threshold": 1000,  # ms
    "error_rate_alert_threshold": 0.005,  # Lower for health
    "memory_usage_alert_threshold": 80,  # percentage
    "wellness_outcome_tracking": True,
}

# Feature flags defaults
FEATURE_FLAGS = {
    "enable_real_wellness_analysis": True,
    "enable_menstrual_cycle_analysis": True,
    "enable_hormonal_nutrition": True,
    "enable_cycle_based_training": True,
    "enable_menopause_management": True,
    "enable_bone_health_assessment": True,
    "enable_emotional_wellness": True,
    "enable_voice_synthesis": True,
    "enable_wearable_integration": True,
    "enable_family_planning": False,  # Future feature
}

# Error messages
ERROR_MESSAGES = {
    "cycle_data_not_found": "No menstrual cycle data found for this user",
    "invalid_health_format": "Health data format is not supported",
    "consent_required": "Wellness analysis requires explicit user consent",
    "analysis_timeout": "Wellness analysis took too long to complete",
    "external_service_error": "External wellness service is temporarily unavailable",
    "insufficient_data": "Insufficient cycle data for reliable analysis",
    "security_violation": "Health data security requirements not met",
    "voice_synthesis_failed": "Voice synthesis unavailable, using text response",
}

# User communication templates (ENFJ maternal warmth)
COMMUNICATION_TEMPLATES = {
    "prime_greeting": "Hello beautiful! I'm here to support your wellness journey with warmth and expertise.",
    "longevity_greeting": "Welcome to your personal wellness sanctuary. Together, we'll nurture your health and happiness.",
    "analysis_starting": "Analyzing your wellness patterns with care and precision...",
    "analysis_complete": "Your wellness insights are ready! Here's what your body is telling us:",
    "consent_request": "To provide personalized wellness guidance, I need your consent to analyze your health data.",
    "data_security_notice": "Your health data is protected with the highest security standards and maternal care.",
    "cycle_encouragement": "Every cycle is unique, and I'm here to help you understand and honor your body's wisdom.",
    "emotional_support": "Remember, you're not alone in this journey. I'm here to support you every step of the way.",
}

# Health databases and references
HEALTH_DATABASES = {
    "acog": "https://www.acog.org/",  # American College of Obstetricians and Gynecologists
    "womenshealth": "https://www.womenshealth.gov/",
    "menopause_society": "https://www.menopause.org/",
    "bone_health": "https://www.bones.nih.gov/",
    "nutrition_data": "https://fdc.nal.usda.gov/",
}

# Supported wellness parameters
WELLNESS_PARAMETERS = {
    "menstrual_cycle": [
        "cycle_length",
        "flow_duration",
        "flow_intensity",
        "pain_levels",
    ],
    "hormonal_symptoms": ["mood_swings", "bloating", "breast_tenderness", "fatigue"],
    "nutrition_factors": [
        "iron_needs",
        "calcium_requirements",
        "folate_levels",
        "vitamin_d",
    ],
    "fitness_adaptations": ["strength_phases", "cardio_optimization", "recovery_needs"],
    "emotional_wellness": [
        "stress_levels",
        "sleep_quality",
        "mood_patterns",
        "energy_levels",
    ],
}

# Adaptive visibility contexts
VISIBILITY_CONTEXTS = {
    "primary_specialist": {
        "conditions": ["menstrual_health_query", "female_wellness_focus"],
        "priority": 1,
        "description": "Primary expert for female wellness queries",
    },
    "activated_specialist": {
        "conditions": ["hormonal_concerns", "cycle_tracking_needed"],
        "priority": 2,
        "description": "Activated for hormonal and cycle-related support",
    },
    "recommended_specialist": {
        "conditions": ["nutrition_for_women", "emotional_wellness_support"],
        "priority": 3,
        "description": "Recommended for women-specific nutrition and emotional support",
    },
    "available_specialist": {
        "conditions": ["general_health_query", "wellness_consultation"],
        "priority": 4,
        "description": "Available for general wellness consultations",
    },
}

# Compliance requirements (Enhanced for health data)
COMPLIANCE_CONFIG = {
    "gdpr": {
        "data_retention_max_days": 2555,  # 7 years
        "consent_required": True,
        "right_to_deletion": True,
        "data_portability": True,
        "health_data_extra_protection": True,
    },
    "hipaa": {
        "encryption_required": True,
        "audit_logging": True,
        "access_controls": True,
        "breach_notification": True,
        "minimum_necessary_rule": True,
    },
    "menstrual_data_protection": {
        "anonymization_required": True,
        "consent_granularity": "per_analysis",
        "sharing_restrictions": True,
        "deletion_on_request": True,
    },
}

# ElevenLabs voice configuration
VOICE_CONFIG = {
    "model_name": "female_wellness_coach",
    "voice_settings": {
        "stability": 0.7,
        "similarity_boost": 0.8,
        "style": 0.6,
        "use_speaker_boost": True,
    },
    "output_format": "mp3_44100_128",
    "chunk_size": 1024,
    "timeout": 10.0,
}
