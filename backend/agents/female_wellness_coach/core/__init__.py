"""
Core module for LUNA Female Wellness Specialist.
Provides foundational components for A+ level architecture.
"""

from .config import LunaConfig
from .constants import (
    AGENT_ID,
    AGENT_NAME,
    AGENT_VERSION,
    PERSONALITY_CONFIG,
    CORE_SKILLS,
    CONVERSATIONAL_SKILLS,
    WELLNESS_ANALYSIS_CONFIG,
    VISIBILITY_CONTEXTS,
)
from .dependencies import LunaDependencies, create_luna_dependencies
from .exceptions import (
    LunaWellnessError,
    LunaValidationError,
    MenstrualCycleAnalysisError,
    HormonalDataSecurityError,
    WellnessConsentError,
    CycleBasedTrainingError,
    HormonalNutritionError,
    MenopauseManagementError,
    BoneHealthAssessmentError,
    EmotionalWellnessError,
    VoiceSynthesisError,
)

__all__ = [
    # Config
    "LunaConfig",
    # Constants
    "AGENT_ID",
    "AGENT_NAME",
    "AGENT_VERSION",
    "PERSONALITY_CONFIG",
    "CORE_SKILLS",
    "CONVERSATIONAL_SKILLS",
    "WELLNESS_ANALYSIS_CONFIG",
    "VISIBILITY_CONTEXTS",
    # Dependencies
    "LunaDependencies",
    "create_luna_dependencies",
    # Exceptions
    "LunaWellnessError",
    "LunaValidationError",
    "MenstrualCycleAnalysisError",
    "HormonalDataSecurityError",
    "WellnessConsentError",
    "CycleBasedTrainingError",
    "HormonalNutritionError",
    "MenopauseManagementError",
    "BoneHealthAssessmentError",
    "EmotionalWellnessError",
    "VoiceSynthesisError",
]
