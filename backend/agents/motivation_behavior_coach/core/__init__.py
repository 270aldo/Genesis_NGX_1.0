"""
Core module for SPARK Motivation Behavior Coach.
Provides centralized access to core components.
"""

from .dependencies import (
    SparkDependencies,
    create_production_dependencies,
    create_test_dependencies,
)
from .config import SparkConfig, MotivationApproach, BehaviorChangeModel, CoachingStyle
from .exceptions import (
    SparkBaseError,
    MotivationAnalysisError,
    BehaviorChangeError,
    HabitFormationError,
    GoalSettingError,
    ObstacleManagementError,
    CoachingError,
    PersonalizationError,
    create_error_response,
    handle_spark_exception,
)
from .constants import (
    MotivationType,
    StageOfChange,
    BehaviorChangeProcess,
    HabitLoopComponent,
    MotivationStrategy,
    CoachingModel,
    InterventionType,
    ProgramType,
    PRIME_PERSONALITY_STYLE,
    LONGEVITY_PERSONALITY_STYLE,
    get_personality_style,
    get_skill_definition,
    validate_motivation_score,
)

__all__ = [
    # Dependencies
    "SparkDependencies",
    "create_production_dependencies",
    "create_test_dependencies",
    # Configuration
    "SparkConfig",
    "MotivationApproach",
    "BehaviorChangeModel",
    "CoachingStyle",
    # Exceptions
    "SparkBaseError",
    "MotivationAnalysisError",
    "BehaviorChangeError",
    "HabitFormationError",
    "GoalSettingError",
    "ObstacleManagementError",
    "CoachingError",
    "PersonalizationError",
    "create_error_response",
    "handle_spark_exception",
    # Constants and enums
    "MotivationType",
    "StageOfChange",
    "BehaviorChangeProcess",
    "HabitLoopComponent",
    "MotivationStrategy",
    "CoachingModel",
    "InterventionType",
    "ProgramType",
    "PRIME_PERSONALITY_STYLE",
    "LONGEVITY_PERSONALITY_STYLE",
    "get_personality_style",
    "get_skill_definition",
    "validate_motivation_score",
]
