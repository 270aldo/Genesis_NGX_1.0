"""
Constants for BLAZE Elite Training Strategist.
Centralizes all training-related constants and enumerations.
"""

from enum import Enum
from typing import Dict, List, Set


class TrainingPhase(Enum):
    """Training periodization phases."""

    PREPARATION = "preparation"
    BASE_BUILDING = "base_building"
    BUILD = "build"
    PEAK = "peak"
    COMPETITION = "competition"
    RECOVERY = "recovery"
    TRANSITION = "transition"


class TrainingIntensity(Enum):
    """Training intensity levels."""

    RECOVERY = "recovery"
    EASY = "easy"
    MODERATE = "moderate"
    TEMPO = "tempo"
    THRESHOLD = "threshold"
    VO2_MAX = "vo2_max"
    NEUROMUSCULAR = "neuromuscular"
    ANAEROBIC = "anaerobic"


class ExerciseCategory(Enum):
    """Exercise movement categories."""

    SQUAT = "squat"
    DEADLIFT = "deadlift"
    PRESS = "press"
    PULL = "pull"
    CARRY = "carry"
    LUNGE = "lunge"
    HINGE = "hinge"
    TWIST = "twist"
    GAIT = "gait"


class BodyRegion(Enum):
    """Body regions for training focus."""

    UPPER_BODY = "upper_body"
    LOWER_BODY = "lower_body"
    CORE = "core"
    FULL_BODY = "full_body"
    POSTERIOR_CHAIN = "posterior_chain"
    ANTERIOR_CHAIN = "anterior_chain"


class TrainingGoal(Enum):
    """Primary training goals."""

    STRENGTH = "strength"
    POWER = "power"
    ENDURANCE = "endurance"
    HYPERTROPHY = "hypertrophy"
    FAT_LOSS = "fat_loss"
    ATHLETIC_PERFORMANCE = "athletic_performance"
    INJURY_PREVENTION = "injury_prevention"
    MOBILITY = "mobility"
    REHABILITATION = "rehabilitation"


class AthleteLevel(Enum):
    """Athlete experience and skill levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"
    PROFESSIONAL = "professional"


class RecoveryMethod(Enum):
    """Recovery and regeneration methods."""

    ACTIVE_RECOVERY = "active_recovery"
    PASSIVE_RECOVERY = "passive_recovery"
    MASSAGE = "massage"
    STRETCHING = "stretching"
    FOAM_ROLLING = "foam_rolling"
    ICE_BATH = "ice_bath"
    SAUNA = "sauna"
    SLEEP = "sleep"
    NUTRITION = "nutrition"
    HYDRATION = "hydration"


# Training Parameters
TRAINING_FREQUENCIES = {
    "beginner": range(2, 4),  # 2-3 sessions per week
    "intermediate": range(3, 5),  # 3-4 sessions per week
    "advanced": range(4, 6),  # 4-5 sessions per week
    "elite": range(5, 8),  # 5-7 sessions per week
    "professional": range(6, 15),  # 6-14 sessions per week (multiple daily)
}

INTENSITY_DISTRIBUTIONS = {
    "polarized": {"low": 0.8, "moderate": 0.0, "high": 0.2},
    "pyramidal": {"low": 0.7, "moderate": 0.2, "high": 0.1},
    "threshold": {"low": 0.5, "moderate": 0.35, "high": 0.15},
}

RPE_ZONES = {
    1: "Very Easy",
    2: "Easy",
    3: "Moderate",
    4: "Somewhat Hard",
    5: "Hard",
    6: "Very Hard",
    7: "Extremely Hard",
    8: "Maximum Effort",
    9: "Beyond Maximum",
    10: "Absolute Maximum",
}

HEART_RATE_ZONES = {
    "zone_1": {"percentage": (50, 60), "description": "Active Recovery"},
    "zone_2": {"percentage": (60, 70), "description": "Aerobic Base"},
    "zone_3": {"percentage": (70, 80), "description": "Aerobic Threshold"},
    "zone_4": {"percentage": (80, 90), "description": "Lactate Threshold"},
    "zone_5": {"percentage": (90, 100), "description": "VO2 Max"},
}

# Exercise Database Constants
COMPOUND_MOVEMENTS: Set[str] = {
    "squat",
    "deadlift",
    "bench_press",
    "overhead_press",
    "row",
    "pull_up",
    "chin_up",
    "clean",
    "snatch",
    "thruster",
}

UNILATERAL_MOVEMENTS: Set[str] = {
    "single_leg_squat",
    "lunge",
    "step_up",
    "single_arm_row",
    "single_arm_press",
    "single_leg_deadlift",
    "lateral_lunge",
}

CORRECTIVE_EXERCISES: Dict[str, List[str]] = {
    "rounded_shoulders": ["band_pull_apart", "wall_slides", "doorway_stretch"],
    "anterior_pelvic_tilt": ["dead_bug", "glute_bridge", "hip_flexor_stretch"],
    "knee_valgus": ["clamshells", "lateral_walks", "single_leg_glute_bridge"],
    "ankle_mobility": ["calf_stretch", "ankle_circles", "wall_ankle_mobilization"],
}

# Injury Risk Factors
HIGH_RISK_INDICATORS: Dict[str, float] = {
    "previous_injury": 0.8,
    "muscle_imbalance": 0.7,
    "poor_movement_quality": 0.8,
    "excessive_training_load": 0.9,
    "inadequate_recovery": 0.8,
    "poor_nutrition": 0.6,
    "high_stress": 0.7,
    "poor_sleep": 0.8,
}

# Performance Metrics
STRENGTH_STANDARDS: Dict[str, Dict[str, float]] = {
    "squat": {"beginner": 1.0, "intermediate": 1.5, "advanced": 2.0, "elite": 2.5},
    "deadlift": {
        "beginner": 1.25,
        "intermediate": 1.75,
        "advanced": 2.25,
        "elite": 2.75,
    },
    "bench_press": {
        "beginner": 0.75,
        "intermediate": 1.25,
        "advanced": 1.5,
        "elite": 2.0,
    },
    "overhead_press": {
        "beginner": 0.5,
        "intermediate": 0.75,
        "advanced": 1.0,
        "elite": 1.25,
    },
}

# Voice Coaching Constants
VOICE_COMMANDS: Set[str] = {
    "start",
    "stop",
    "pause",
    "resume",
    "next",
    "previous",
    "faster",
    "slower",
    "harder",
    "easier",
    "rest",
    "go",
}

AUDIO_FEEDBACK_TYPES: Set[str] = {
    "form_correction",
    "intensity_adjustment",
    "motivation",
    "timing_cue",
    "safety_warning",
    "progress_update",
}

# AI Model Configuration
AI_MODEL_PARAMETERS = {
    "training_plan_generation": {
        "model": "gemini-1.5-flash",
        "temperature": 0.3,
        "max_tokens": 2000,
    },
    "performance_analysis": {
        "model": "gemini-1.5-flash",
        "temperature": 0.2,
        "max_tokens": 1500,
    },
    "form_correction": {
        "model": "gemini-1.5-pro-vision",
        "temperature": 0.1,
        "max_tokens": 1000,
    },
    "adaptive_coaching": {
        "model": "gemini-1.5-flash",
        "temperature": 0.4,
        "max_tokens": 800,
    },
}

# Integration Constants
SUPPORTED_DEVICES: Set[str] = {
    "apple_watch",
    "whoop",
    "oura_ring",
    "garmin",
    "polar",
    "fitbit",
    "chest_strap",
    "power_meter",
    "heart_rate_monitor",
}

BIOMETRIC_PARAMETERS: Set[str] = {
    "heart_rate",
    "heart_rate_variability",
    "sleep_quality",
    "recovery_score",
    "strain",
    "readiness",
    "vo2_max",
    "lactate_threshold",
    "power_output",
    "cadence",
}

# Error Codes
ERROR_CODES = {
    "INVALID_ATHLETE_PROFILE": "E001",
    "MISSING_TRAINING_GOALS": "E002",
    "INSUFFICIENT_DATA": "E003",
    "EQUIPMENT_NOT_AVAILABLE": "E004",
    "CONFLICTING_CONSTRAINTS": "E005",
    "INJURY_RISK_TOO_HIGH": "E006",
    "INVALID_TRAINING_PHASE": "E007",
    "BIOMETRIC_CONNECTION_FAILED": "E008",
    "VOICE_SYSTEM_ERROR": "E009",
    "AI_MODEL_ERROR": "E010",
}
