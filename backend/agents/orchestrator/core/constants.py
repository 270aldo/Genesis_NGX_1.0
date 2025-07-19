"""
NEXUS ENHANCED - Orchestration and Client Success Constants
===========================================================

Constantes centralizadas para orchestration, client success, intents,
agent routing, y configuraciones específicas del dominio.

Arquitectura A+ - Módulo Core
Líneas objetivo: <300
"""

from enum import Enum
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


# ===== ORCHESTRATION CONSTANTS =====


class IntentCategory(Enum):
    """Categorías principales de intención del usuario."""

    TRAINING = "training"
    NUTRITION = "nutrition"
    GENETICS = "genetics"
    BIOMETRICS = "biometrics"
    RECOVERY = "recovery"
    MOTIVATION = "motivation"
    PROGRESS = "progress"
    BIOHACKING = "biohacking"
    FEMALE_HEALTH = "female_health"
    CLIENT_SUCCESS = "client_success"
    GENERAL = "general"


class AgentPriority(Enum):
    """Prioridades de routing para agentes."""

    CRITICAL = 1  # Orchestrator, emergencias
    HIGH = 2  # BLAZE, SAGE, CODE - agentes core
    MEDIUM = 3  # WAVE, SPARK, STELLA - agentes especializados
    LOW = 4  # NOVA, LUNA - agentes contextuales
    BACKEND = 5  # NODE, GUARDIAN - infraestructura


# Intent to Agent Mapping - Configuración centralizada
INTENT_TO_AGENT_MAP: Dict[str, List[str]] = {
    # Core fitness/wellness intents
    "plan_entrenamiento": ["elite_training_strategist"],
    "elite_training_strategist": ["elite_training_strategist"],
    "generar_plan_entrenamiento": ["elite_training_strategist"],
    "training_ai": ["elite_training_strategist"],
    "consultar_ejercicio": ["elite_training_strategist"],
    # Nutrition intents
    "analizar_nutricion": ["precision_nutrition_architect"],
    "recomendar_receta": ["precision_nutrition_architect"],
    "nutrition_ai": ["precision_nutrition_architect"],
    "meal_planning": ["precision_nutrition_architect"],
    # Genetic analysis intents
    "genetic_analysis": ["code_genetic_specialist"],
    "genetic_profile": ["code_genetic_specialist"],
    "genetic_risk": ["code_genetic_specialist"],
    "genetic_optimization": ["code_genetic_specialist"],
    "epigenetics": ["code_genetic_specialist"],
    "nutrigenomics": ["code_genetic_specialist"],
    "sport_genetics": ["code_genetic_specialist"],
    # Biometric and performance analytics (WAVE ENHANCED)
    "biometric_analysis": ["wave_performance_analytics"],
    "analyze_biometrics": ["wave_performance_analytics"],
    "recovery": ["wave_performance_analytics"],
    "injury_prevention": ["wave_performance_analytics"],
    "performance_analytics": ["wave_performance_analytics"],
    # Motivation and behavior
    "motivation": ["motivation_behavior_coach"],
    "behavior_change": ["motivation_behavior_coach"],
    "habit_formation": ["motivation_behavior_coach"],
    # Progress tracking
    "track_progress": ["progress_tracker"],
    "progress_analysis": ["progress_tracker"],
    "progress_ai": ["progress_tracker"],
    "celebrate_milestone": ["progress_tracker"],
    # Biohacking and optimization
    "biohacking": ["nova_biohacking_innovator"],
    "optimization": ["nova_biohacking_innovator"],
    "longevity": ["nova_biohacking_innovator"],
    # Female health (LUNA)
    "female_health_query": ["female_wellness_coach"],
    "menstrual_cycle_query": ["female_wellness_coach"],
    "hormonal_support": ["female_wellness_coach"],
    "menopause_support": ["female_wellness_coach"],
    # Client success intents (handled by NEXUS Enhanced directly)
    "onboarding": ["ngx_nexus_orchestrator_enhanced"],
    "support": ["ngx_nexus_orchestrator_enhanced"],
    "help": ["ngx_nexus_orchestrator_enhanced"],
    "community": ["ngx_nexus_orchestrator_enhanced"],
    "celebration": ["ngx_nexus_orchestrator_enhanced"],
    "milestone": ["ngx_nexus_orchestrator_enhanced"],
    "feedback": ["ngx_nexus_orchestrator_enhanced"],
    "check_in": ["ngx_nexus_orchestrator_enhanced"],
    "retention": ["ngx_nexus_orchestrator_enhanced"],
    # Backend services (invisible to user)
    "integration": ["node_systems_integration_ops"],
    "sync_data": ["node_systems_integration_ops"],
    "security": ["security_compliance_guardian"],
    "compliance": ["security_compliance_guardian"],
    # General fallback
    "general": ["ngx_nexus_orchestrator_enhanced"],
}


# ===== CLIENT SUCCESS CONSTANTS =====


class ClientSuccessEvent(Enum):
    """Tipos de eventos de client success."""

    ONBOARDING_START = "onboarding_start"
    ONBOARDING_COMPLETE = "onboarding_complete"
    FIRST_GOAL_SET = "first_goal_set"
    FIRST_WORKOUT_COMPLETE = "first_workout_complete"
    WEEK_ONE_MILESTONE = "week_one_milestone"
    MONTH_ONE_MILESTONE = "month_one_milestone"
    GOAL_ACHIEVED = "goal_achieved"
    STREAK_MILESTONE = "streak_milestone"
    PLATEAU_DETECTED = "plateau_detected"
    CHURN_RISK_DETECTED = "churn_risk_detected"
    SUPPORT_REQUEST = "support_request"
    FEEDBACK_POSITIVE = "feedback_positive"
    FEEDBACK_NEGATIVE = "feedback_negative"
    COMMUNITY_ENGAGEMENT = "community_engagement"


class OnboardingStage(Enum):
    """Etapas del proceso de onboarding."""

    WELCOME = "welcome"
    PROFILE_SETUP = "profile_setup"
    GOAL_SETTING = "goal_setting"
    AGENT_INTRODUCTION = "agent_introduction"
    FIRST_INTERACTION = "first_interaction"
    WEEK_ONE_CHECK_IN = "week_one_check_in"
    ONBOARDING_COMPLETE = "onboarding_complete"


class MilestoneType(Enum):
    """Tipos de hitos a celebrar."""

    FIRST_WORKOUT = "first_workout"
    CONSISTENCY_WEEK = "consistency_week"
    CONSISTENCY_MONTH = "consistency_month"
    WEIGHT_GOAL = "weight_goal"
    STRENGTH_GOAL = "strength_goal"
    HABIT_FORMATION = "habit_formation"
    COMMUNITY_ENGAGEMENT = "community_engagement"
    KNOWLEDGE_MILESTONE = "knowledge_milestone"
    CHALLENGE_COMPLETION = "challenge_completion"


# Onboarding Flow Configuration
ONBOARDING_TOUCHPOINTS: List[Tuple[str, int]] = [
    ("welcome_message", 0),  # Immediate
    ("profile_setup", 1),  # Day 1
    ("agent_introduction", 1),  # Day 1
    ("goal_setting", 2),  # Day 2
    ("first_interaction", 3),  # Day 3
    ("week_one_check_in", 7),  # Day 7
    ("onboarding_complete", 7),  # Day 7
]

# Proactive Check-in Schedule (days)
PROACTIVE_CHECKIN_SCHEDULE: Dict[str, int] = {
    "new_user": 3,  # Every 3 days for first month
    "active_user": 7,  # Weekly for active users
    "at_risk_user": 1,  # Daily for at-risk users
    "returning_user": 14,  # Bi-weekly for returning users
}


# ===== CONVERSATIONAL CONSTANTS =====


class ConversationalMode(Enum):
    """Modos de conversación."""

    TEXT_ONLY = "text_only"
    VOICE_ONLY = "voice_only"
    MULTIMODAL = "multimodal"
    ADAPTIVE = "adaptive"


class VoiceProvider(Enum):
    """Proveedores de síntesis de voz."""

    ELEVENLABS = "elevenlabs"
    GOOGLE_TTS = "google_tts"
    AZURE_TTS = "azure_tts"


# ElevenLabs Voice Configuration for NEXUS
NEXUS_VOICE_CONFIG = {
    "voice_id": "EkK5I93UQWFDigLMpZcX",  # James - Professional voice
    "voice_name": "James",
    "model_id": "eleven_flash_v2_5",
    "voice_settings": {
        "stability": 0.75,
        "similarity_boost": 0.85,
        "style_exaggeration": 0.65,
        "use_speaker_boost": True,
    },
}


# ===== PERFORMANCE AND MONITORING CONSTANTS =====


class PerformanceMetric(Enum):
    """Métricas de performance."""

    RESPONSE_TIME = "response_time"
    INTENT_CONFIDENCE = "intent_confidence"
    AGENT_SUCCESS_RATE = "agent_success_rate"
    USER_SATISFACTION = "user_satisfaction"
    CONVERSATION_LENGTH = "conversation_length"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"


# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "response_time_ms": 3000,  # Max 3 seconds
    "intent_confidence": 0.7,  # Min 70% confidence
    "agent_success_rate": 0.95,  # Min 95% success rate
    "error_rate": 0.01,  # Max 1% error rate
    "cache_hit_rate": 0.8,  # Min 80% cache hit rate
}

# Cache TTL Configuration (seconds)
CACHE_TTL_CONFIG = {
    "intent_analysis": 300,  # 5 minutes
    "agent_responses": 600,  # 10 minutes
    "user_context": 1800,  # 30 minutes
    "conversation_state": 3600,  # 1 hour
}


# ===== PERSONALITY AND PROGRAM CONSTANTS =====


class ProgramType(Enum):
    """Tipos de programa NGX."""

    PRIME = "PRIME"
    LONGEVITY = "LONGEVITY"
    GENERAL = "GENERAL"


class PersonalityTrait(Enum):
    """Traits de personalidad para NEXUS Enhanced."""

    STRATEGIC_THINKING = "strategic_thinking"
    WARM_AUTHORITY = "warm_authority"
    ANALYTICAL_APPROACH = "analytical_approach"
    EMPATHETIC_COMMUNICATION = "empathetic_communication"
    PROFESSIONAL_CONSULTANT = "professional_consultant"
    EFFICIENT_COORDINATOR = "efficient_coordinator"


# NEXUS Personality Profile
NEXUS_PERSONALITY_PROFILE = {
    "mbti_type": "INTJ + ESFP",  # Architect + Entertainer fusion
    "core_traits": [
        PersonalityTrait.STRATEGIC_THINKING,
        PersonalityTrait.WARM_AUTHORITY,
        PersonalityTrait.ANALYTICAL_APPROACH,
        PersonalityTrait.EMPATHETIC_COMMUNICATION,
    ],
    "communication_style": {
        "PRIME": {
            "tone": "strategic_executive",
            "language": "technical_strategic",
            "focus": "coordination_efficiency",
            "urgency": "high_performance",
        },
        "LONGEVITY": {
            "tone": "consultive_empathetic",
            "language": "clear_explanatory",
            "focus": "holistic_guidance",
            "urgency": "gradual_sustainable",
        },
    },
}


# ===== SYSTEM CONSTANTS =====

# Agent Health Check Configuration
HEALTH_CHECK_CONFIG = {
    "interval_seconds": 30,
    "timeout_seconds": 5,
    "max_failures": 3,
    "recovery_time_seconds": 60,
}

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 60,
    "burst_limit": 10,
    "cooldown_seconds": 60,
}

# Error Recovery Configuration
ERROR_RECOVERY_CONFIG = {
    "max_retry_attempts": 3,
    "retry_delay_seconds": 1,
    "exponential_backoff": True,
    "circuit_breaker_threshold": 5,
}


@dataclass
class SystemLimits:
    """Límites del sistema para orchestration."""

    max_concurrent_conversations: int = 100
    max_conversation_duration_minutes: int = 60
    max_message_length: int = 4000
    max_agent_response_time_seconds: float = 30.0
    max_total_response_time_seconds: float = 45.0
    max_intent_cache_size: int = 10000
    max_conversation_history_items: int = 50


# Default system limits instance
DEFAULT_SYSTEM_LIMITS = SystemLimits()


# ===== VALIDATION CONSTANTS =====

# Valid Agent IDs in the system
VALID_AGENT_IDS: Set[str] = {
    "ngx_nexus_orchestrator_enhanced",
    "elite_training_strategist",
    "precision_nutrition_architect",
    "code_genetic_specialist",
    "wave_performance_analytics",
    "motivation_behavior_coach",
    "progress_tracker",
    "nova_biohacking_innovator",
    "female_wellness_coach",
    "node_systems_integration_ops",
    "security_compliance_guardian",
}

# Client Success Keywords for Intent Detection
CLIENT_SUCCESS_KEYWORDS: Set[str] = {
    "help",
    "support",
    "onboarding",
    "welcome",
    "getting started",
    "problem",
    "issue",
    "stuck",
    "error",
    "bug",
    "feedback",
    "suggestion",
    "improvement",
    "complaint",
    "community",
    "connect",
    "share",
    "others",
    "friends",
    "milestone",
    "achievement",
    "goal",
    "progress",
    "success",
    "celebration",
    "congratulations",
    "well done",
    "great job",
    "check in",
    "how are you",
    "status",
    "update",
    "cancel",
    "quit",
    "stop",
    "unsubscribe",
    "frustrated",
}

# Supported Languages for Internationalization
SUPPORTED_LANGUAGES: Set[str] = {
    "es",  # Spanish (primary)
    "en",  # English (secondary)
}

# Default Fallback Messages
FALLBACK_MESSAGES = {
    "intent_analysis_failed": "No entendí tu consulta. ¿Podrías reformularla de otra manera?",
    "no_agent_available": "No estoy seguro de cómo ayudarte con esa consulta específica. ¿Podrías ser más específico?",
    "agent_timeout": "La operación está tomando más tiempo del esperado. Por favor intenta nuevamente.",
    "system_error": "Ocurrió un error temporal en el sistema. Por favor intenta nuevamente en un momento.",
    "service_unavailable": "El servicio no está disponible temporalmente. Nuestro equipo está trabajando en ello.",
}
