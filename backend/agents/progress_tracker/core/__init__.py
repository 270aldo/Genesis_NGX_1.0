"""
STELLA Progress Tracker - Core Module.
A+ standardized implementation with modular architecture.
"""

from .dependencies import (
    StellaDependencies,
    create_production_dependencies,
    create_test_dependencies,
)
from .config import StellaConfig
from .exceptions import (
    StellaBaseError,
    ProgressAnalysisError,
    MilestoneTrackingError,
    AchievementProcessingError,
    VisualizationError,
    ComparisonError,
    handle_stella_exception,
)
from .constants import (
    ProgressMetricType,
    AchievementCategory,
    VisualizationType,
    AnalysisType,
    MilestoneType,
    ComparisonPeriod,
    get_stella_personality_style,
)

__all__ = [
    # Dependencies
    "StellaDependencies",
    "create_production_dependencies",
    "create_test_dependencies",
    # Configuration
    "StellaConfig",
    # Exceptions
    "StellaBaseError",
    "ProgressAnalysisError",
    "MilestoneTrackingError",
    "AchievementProcessingError",
    "VisualizationError",
    "ComparisonError",
    "handle_stella_exception",
    # Constants
    "ProgressMetricType",
    "AchievementCategory",
    "VisualizationType",
    "AnalysisType",
    "MilestoneType",
    "ComparisonPeriod",
    "get_stella_personality_style",
]
