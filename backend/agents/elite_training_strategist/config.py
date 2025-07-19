"""
BLAZE Agent Configuration
=========================

Centralized configuration for the BLAZE Elite Training Strategist agent.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from core.settings import Settings

settings = Settings()


class BlazeConfig(BaseModel):
    """Configuration for BLAZE agent."""
    
    model_config = {
        "protected_namespaces": (),
        "use_enum_values": True,
        "validate_assignment": True
    }
    
    # Agent identity
    agent_id: str = Field(default="blaze_elite_training")
    agent_name: str = Field(default="BLAZE Elite Training Strategist")
    
    # Model configuration
    model_id: str = Field(default="gemini-2.5-pro")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048)
    
    # A2A configuration
    a2a_server_url: str = Field(
        default_factory=lambda: f"http://{settings.A2A_HOST}:{settings.A2A_PORT}"
    )
    
    # Personality settings
    personality_type: str = Field(default="prime")  # prime or longevity
    motivation_style: str = Field(default="intense")  # intense, supportive, balanced
    
    # Feature flags
    enable_wearable_sync: bool = Field(default=True)
    enable_injury_prevention: bool = Field(default=True)
    enable_nutrition_integration: bool = Field(default=True)
    enable_recovery_tracking: bool = Field(default=True)
    
    # Cache settings
    cache_ttl: int = Field(default=3600)  # 1 hour
    enable_response_cache: bool = Field(default=True)
    
    # Integration settings
    wearable_api_key: Optional[str] = Field(default=None)
    nutrition_agent_id: str = Field(default="sage_nutrition")
    
    # Training defaults
    default_training_phase: str = Field(default="preparation")
    default_intensity_scale: str = Field(default="rpe")  # rpe or percentage
    max_weekly_volume_increase: float = Field(default=0.1)  # 10% max increase
    
    # Safety settings
    injury_risk_threshold: float = Field(default=0.7)
    fatigue_threshold: float = Field(default=0.8)
    overtraining_markers: Dict[str, float] = Field(
        default_factory=lambda: {
            "hrv_drop": 0.2,  # 20% HRV drop
            "sleep_quality": 0.6,  # Below 60% quality
            "mood_score": 0.5  # Below 50%
        }
    )
    
    # Prompt settings
    prompt_style: str = Field(default="technical")  # technical, conversational, mixed
    include_scientific_references: bool = Field(default=True)
    


# Training phases enum
class TrainingPhase:
    """Training phase definitions."""
    PREPARATION = "preparation"
    BASE_BUILDING = "base_building"
    STRENGTH = "strength"
    POWER = "power"
    COMPETITION = "competition"
    RECOVERY = "recovery"
    TRANSITION = "transition"


# Training goals enum
class TrainingGoal:
    """Common training goals."""
    STRENGTH = "strength"
    MUSCLE_GAIN = "muscle_gain"
    FAT_LOSS = "fat_loss"
    ENDURANCE = "endurance"
    POWER = "power"
    ATHLETIC_PERFORMANCE = "athletic_performance"
    GENERAL_FITNESS = "general_fitness"
    REHABILITATION = "rehabilitation"


# Athlete levels
class AthleteLevel:
    """Athlete experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite"
    PROFESSIONAL = "professional"


# Exercise categories
class ExerciseCategory:
    """Exercise categorization."""
    COMPOUND = "compound"
    ISOLATION = "isolation"
    PLYOMETRIC = "plyometric"
    OLYMPIC = "olympic"
    CARDIO = "cardio"
    MOBILITY = "mobility"
    CORRECTIVE = "corrective"


# Default exercise database (subset)
DEFAULT_EXERCISES = {
    "squat": {
        "category": ExerciseCategory.COMPOUND,
        "muscle_groups": ["quadriceps", "glutes", "core"],
        "equipment": ["barbell", "dumbbell", "bodyweight"],
        "difficulty": 3
    },
    "deadlift": {
        "category": ExerciseCategory.COMPOUND,
        "muscle_groups": ["hamstrings", "glutes", "back", "core"],
        "equipment": ["barbell", "dumbbell", "trap_bar"],
        "difficulty": 4
    },
    "bench_press": {
        "category": ExerciseCategory.COMPOUND,
        "muscle_groups": ["chest", "shoulders", "triceps"],
        "equipment": ["barbell", "dumbbell"],
        "difficulty": 3
    },
    "pull_up": {
        "category": ExerciseCategory.COMPOUND,
        "muscle_groups": ["back", "biceps", "core"],
        "equipment": ["pull_up_bar", "assisted_machine"],
        "difficulty": 4
    }
}


# Training templates
TRAINING_TEMPLATES = {
    "strength_beginner": {
        "frequency": 3,
        "duration_weeks": 12,
        "phase_progression": [
            TrainingPhase.PREPARATION,
            TrainingPhase.BASE_BUILDING,
            TrainingPhase.STRENGTH
        ],
        "primary_exercises": ["squat", "deadlift", "bench_press", "pull_up"],
        "rep_ranges": {"strength": "3-5", "hypertrophy": "8-12", "endurance": "15+"}
    },
    "endurance_intermediate": {
        "frequency": 4,
        "duration_weeks": 16,
        "phase_progression": [
            TrainingPhase.BASE_BUILDING,
            TrainingPhase.STRENGTH,
            TrainingPhase.POWER,
            TrainingPhase.COMPETITION
        ],
        "primary_focus": ["aerobic_capacity", "lactate_threshold", "vo2_max"],
        "strength_maintenance": 2  # sessions per week
    }
}