"""
STELLA Progress Tracker Constants.
Comprehensive constants and enums for A+ architecture with progress tracking definitions.
"""

from enum import Enum
from typing import Dict, List, Any
from dataclasses import dataclass


class ProgressMetricType(Enum):
    """Types of progress metrics that can be tracked."""

    WEIGHT = "weight"
    BODY_FAT = "body_fat"
    MUSCLE_MASS = "muscle_mass"
    MEASUREMENTS = "measurements"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    NUTRITION = "nutrition"
    SLEEP = "sleep"
    ENERGY = "energy"
    MOOD = "mood"
    PERFORMANCE = "performance"
    CONSISTENCY = "consistency"
    CUSTOM = "custom"


class AchievementCategory(Enum):
    """Categories of achievements that can be earned."""

    STRENGTH = "strength"
    ENDURANCE = "endurance"
    CONSISTENCY = "consistency"
    NUTRITION = "nutrition"
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    FLEXIBILITY = "flexibility"
    MENTAL_HEALTH = "mental_health"
    HABIT_FORMATION = "habit_formation"
    GOAL_COMPLETION = "goal_completion"
    MILESTONE = "milestone"
    STREAK = "streak"


class VisualizationType(Enum):
    """Types of visualizations available."""

    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    AREA_CHART = "area_chart"
    PROGRESS_BAR = "progress_bar"
    HEATMAP = "heatmap"
    SCATTER_PLOT = "scatter_plot"
    PIE_CHART = "pie_chart"
    RADAR_CHART = "radar_chart"
    INFOGRAPHIC = "infographic"
    PROGRESS_REPORT = "progress_report"
    COMPARISON_CHART = "comparison_chart"
    TREND_ANALYSIS = "trend_analysis"


class AnalysisType(Enum):
    """Types of progress analysis available."""

    TREND_ANALYSIS = "trend_analysis"
    COMPARISON_ANALYSIS = "comparison_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    CONSISTENCY_ANALYSIS = "consistency_analysis"
    ACHIEVEMENT_ANALYSIS = "achievement_analysis"
    MILESTONE_ANALYSIS = "milestone_analysis"
    BODY_COMPOSITION = "body_composition"


class MilestoneType(Enum):
    """Types of milestones that can be tracked."""

    WEIGHT_TARGET = "weight_target"
    STRENGTH_GOAL = "strength_goal"
    ENDURANCE_GOAL = "endurance_goal"
    CONSISTENCY_STREAK = "consistency_streak"
    MEASUREMENT_TARGET = "measurement_target"
    PERFORMANCE_BENCHMARK = "performance_benchmark"
    HABIT_MILESTONE = "habit_milestone"
    TIME_BASED = "time_based"
    PERCENTAGE_BASED = "percentage_based"
    CUSTOM_GOAL = "custom_goal"


class ComparisonPeriod(Enum):
    """Time periods for progress comparison."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"
    WEEK_TO_WEEK = "week_to_week"
    MONTH_TO_MONTH = "month_to_month"
    YEAR_TO_YEAR = "year_to_year"


class DataQuality(Enum):
    """Data quality levels for progress tracking."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INSUFFICIENT = "insufficient"


class TrendDirection(Enum):
    """Direction of progress trends."""

    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    FLUCTUATING = "fluctuating"
    ACCELERATING = "accelerating"
    DECELERATING = "decelerating"


class PersonalityStyle(Enum):
    """STELLA personality interaction styles."""

    ENTHUSIASTIC = "enthusiastic"
    SUPPORTIVE = "supportive"
    ANALYTICAL = "analytical"
    CELEBRATORY = "celebratory"
    MOTIVATIONAL = "motivational"
    EDUCATIONAL = "educational"


# STELLA Personality Constants
STELLA_PERSONALITY_TRAITS = {
    "type": "ESFJ",  # Extroverted, Sensing, Feeling, Judging
    "core_traits": [
        "enthusiastic",
        "supportive",
        "detail_oriented",
        "celebratory",
        "encouraging",
        "organized",
        "people_focused",
    ],
    "communication_style": {
        "tone": "warm and encouraging",
        "approach": "supportive and detailed",
        "focus": "achievements and progress",
        "energy_level": "high positive energy",
    },
    "responses": {
        "celebration_phrases": [
            "Amazing progress!",
            "You're absolutely crushing it!",
            "This is fantastic improvement!",
            "I'm so proud of your dedication!",
            "What incredible consistency!",
            "You're really making it happen!",
        ],
        "encouragement_phrases": [
            "You've got this!",
            "Keep up the fantastic work!",
            "Every step counts!",
            "Your consistency is inspiring!",
            "Progress is progress, no matter how small!",
            "You're building something amazing!",
        ],
        "analysis_intros": [
            "Let me break down your awesome progress...",
            "Here's what your data is showing...",
            "I'm excited to share your progress insights...",
            "Your numbers tell an amazing story...",
            "Let's dive into your progress journey...",
        ],
    },
}

# Progress Tracking Thresholds
PROGRESS_THRESHOLDS = {
    "significant_improvement": 0.1,  # 10% improvement
    "moderate_improvement": 0.05,  # 5% improvement
    "minimal_improvement": 0.02,  # 2% improvement
    "plateau_threshold": 0.01,  # 1% or less change
    "decline_threshold": -0.02,  # 2% decline
    "significant_decline": -0.1,  # 10% decline
}

# Milestone Detection Criteria
MILESTONE_CRITERIA = {
    "weight_loss": {
        "thresholds": [2, 5, 10, 15, 20, 25, 30, 50],  # pounds lost
        "celebration_level": {
            2: "good",
            5: "great",
            10: "amazing",
            15: "incredible",
            20: "outstanding",
        },
    },
    "consistency": {
        "thresholds": [7, 14, 21, 30, 60, 90, 180, 365],  # days streak
        "celebration_level": {
            7: "good",
            14: "great",
            21: "amazing",
            30: "incredible",
            60: "outstanding",
        },
    },
    "strength": {
        "thresholds": [5, 10, 15, 25, 50, 75, 100],  # percentage increase
        "celebration_level": {
            5: "good",
            10: "great",
            25: "amazing",
            50: "incredible",
            100: "outstanding",
        },
    },
}

# Visualization Color Palettes
VISUALIZATION_COLORS = {
    "primary_palette": [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Yellow
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
        "#F97316",  # Orange
    ],
    "progress_colors": {
        "excellent": "#10B981",  # Green
        "good": "#84CC16",  # Light Green
        "fair": "#F59E0B",  # Yellow
        "poor": "#F97316",  # Orange
        "concerning": "#EF4444",  # Red
    },
    "trend_colors": {
        "improving": "#10B981",
        "stable": "#6B7280",
        "declining": "#EF4444",
        "fluctuating": "#8B5CF6",
    },
}

# Achievement Rewards and Levels
ACHIEVEMENT_SYSTEM = {
    "levels": {
        "bronze": {"min_score": 0, "max_score": 25, "color": "#CD7F32"},
        "silver": {"min_score": 26, "max_score": 50, "color": "#C0C0C0"},
        "gold": {"min_score": 51, "max_score": 75, "color": "#FFD700"},
        "platinum": {"min_score": 76, "max_score": 90, "color": "#E5E4E2"},
        "diamond": {"min_score": 91, "max_score": 100, "color": "#B9F2FF"},
    },
    "categories": {
        AchievementCategory.CONSISTENCY: {
            "weight": 30,
            "metrics": ["workout_frequency", "logging_consistency", "habit_adherence"],
        },
        AchievementCategory.STRENGTH: {
            "weight": 25,
            "metrics": ["strength_gains", "pr_achievements", "progression_rate"],
        },
        AchievementCategory.NUTRITION: {
            "weight": 20,
            "metrics": ["nutrition_consistency", "goal_adherence", "tracking_accuracy"],
        },
        AchievementCategory.ENDURANCE: {
            "weight": 15,
            "metrics": ["cardio_improvements", "endurance_gains", "stamina_progress"],
        },
        AchievementCategory.MENTAL_HEALTH: {
            "weight": 10,
            "metrics": ["mood_improvements", "stress_reduction", "energy_levels"],
        },
    },
}

# Skills and Capabilities
STELLA_SKILLS = {
    "core_skills": [
        "analyze_progress",
        "visualize_progress",
        "compare_progress",
        "analyze_body_progress",
        "generate_progress_visualization",
    ],
    "conversation_skills": [
        "progress_celebration_conversation",
        "milestone_analysis_conversation",
        "goal_adjustment_conversation",
        "motivational_checkin_conversation",
        "achievement_reflection_conversation",
    ],
    "advanced_skills": [
        "generate_progress_chart",
        "generate_nutrition_infographic",
        "generate_progress_report",
        "get_exercise_videos",
    ],
    "vision_skills": [
        "physical_form_analysis",
        "progress_tracking_vision",
        "body_measurement_extraction",
    ],
}

# Data Format Specifications
DATA_FORMATS = {
    "progress_entry": {
        "required_fields": ["user_id", "metric_type", "value", "timestamp"],
        "optional_fields": ["notes", "tags", "context", "unit"],
        "validation_rules": {
            "value": "numeric",
            "timestamp": "iso_datetime",
            "metric_type": "enum:ProgressMetricType",
        },
    },
    "milestone": {
        "required_fields": [
            "user_id",
            "milestone_type",
            "target_value",
            "current_value",
        ],
        "optional_fields": ["description", "deadline", "achievement_date"],
        "validation_rules": {
            "target_value": "numeric",
            "current_value": "numeric",
            "milestone_type": "enum:MilestoneType",
        },
    },
    "achievement": {
        "required_fields": ["user_id", "category", "level", "earned_date"],
        "optional_fields": ["description", "points", "badge_id"],
        "validation_rules": {
            "category": "enum:AchievementCategory",
            "level": "string",
            "earned_date": "iso_datetime",
        },
    },
}

# Error Messages
ERROR_MESSAGES = {
    "insufficient_data": "I need more data points to provide a meaningful analysis. Please log more progress entries and try again!",
    "invalid_time_range": "The time range you specified isn't valid. Please choose a period between 1 day and 2 years.",
    "no_progress_found": "I couldn't find any progress data for the specified criteria. Have you been logging your workouts and measurements?",
    "visualization_error": "I had trouble creating that visualization. Let me try a different format that might work better!",
    "image_processing_error": "I couldn't process that image. Please make sure it's a clear photo in JPG, PNG, or WebP format.",
    "milestone_error": "I couldn't evaluate that milestone. Please check that your targets and current values are properly set.",
    "comparison_error": "I couldn't complete the comparison analysis. Make sure you have data for both time periods you want to compare.",
}


@dataclass
class PerformanceThresholds:
    """Performance thresholds for STELLA operations."""

    response_time_excellent: float = 2.0  # seconds
    response_time_good: float = 5.0  # seconds
    response_time_acceptable: float = 10.0  # seconds

    analysis_time_simple: float = 3.0  # seconds
    analysis_time_complex: float = 10.0  # seconds
    analysis_time_vision: float = 15.0  # seconds

    data_points_minimum: int = 3
    data_points_recommended: int = 10
    data_points_optimal: int = 30

    confidence_threshold_high: float = 0.9
    confidence_threshold_medium: float = 0.7
    confidence_threshold_low: float = 0.5


def get_stella_personality_style(
    program_type: str = None, context: Dict[str, Any] = None
) -> PersonalityStyle:
    """
    Get appropriate STELLA personality style based on program type and context.

    Args:
        program_type: User's program type (PRIME/LONGEVITY)
        context: Additional context for personality adaptation

    Returns:
        Appropriate PersonalityStyle for the situation
    """
    if program_type == "PRIME":
        # More analytical and performance-focused for executives
        return PersonalityStyle.ANALYTICAL
    elif program_type == "LONGEVITY":
        # More supportive and encouraging for wellness
        return PersonalityStyle.SUPPORTIVE
    elif context and context.get("achievement_detected"):
        # Celebratory when achievements are detected
        return PersonalityStyle.CELEBRATORY
    elif context and context.get("needs_motivation"):
        # Motivational when user needs encouragement
        return PersonalityStyle.MOTIVATIONAL
    else:
        # Default enthusiastic STELLA personality
        return PersonalityStyle.ENTHUSIASTIC


def get_visualization_config(viz_type: VisualizationType) -> Dict[str, Any]:
    """
    Get configuration for specific visualization type.

    Args:
        viz_type: Type of visualization

    Returns:
        Configuration dictionary for the visualization
    """
    base_config = {
        "width": 800,
        "height": 600,
        "responsive": True,
        "theme": "stella_progress",
    }

    type_specific_config = {
        VisualizationType.LINE_CHART: {
            "chart_type": "line",
            "smooth_lines": True,
            "show_points": True,
            "colors": VISUALIZATION_COLORS["primary_palette"][:3],
        },
        VisualizationType.BAR_CHART: {
            "chart_type": "bar",
            "orientation": "vertical",
            "show_values": True,
            "colors": VISUALIZATION_COLORS["progress_colors"],
        },
        VisualizationType.PROGRESS_BAR: {
            "chart_type": "progress",
            "show_percentage": True,
            "animate": True,
            "colors": VISUALIZATION_COLORS["trend_colors"],
        },
        VisualizationType.HEATMAP: {
            "chart_type": "heatmap",
            "color_scale": "viridis",
            "show_scale": True,
            "cell_size": "auto",
        },
    }

    base_config.update(type_specific_config.get(viz_type, {}))
    return base_config


def get_achievement_level(score: float) -> str:
    """
    Get achievement level based on score.

    Args:
        score: Achievement score (0-100)

    Returns:
        Achievement level name
    """
    for level, config in ACHIEVEMENT_SYSTEM["levels"].items():
        if config["min_score"] <= score <= config["max_score"]:
            return level
    return "bronze"  # Default fallback


def format_stella_response(
    message: str, personality_style: PersonalityStyle = PersonalityStyle.ENTHUSIASTIC
) -> str:
    """
    Format response message with STELLA personality.

    Args:
        message: Base message to format
        personality_style: Personality style to apply

    Returns:
        Formatted message with STELLA personality
    """
    personality_prefixes = {
        PersonalityStyle.ENTHUSIASTIC: "🌟 ",
        PersonalityStyle.CELEBRATORY: "🎉 ",
        PersonalityStyle.SUPPORTIVE: "💪 ",
        PersonalityStyle.ANALYTICAL: "📊 ",
        PersonalityStyle.MOTIVATIONAL: "🚀 ",
        PersonalityStyle.EDUCATIONAL: "📚 ",
    }

    prefix = personality_prefixes.get(personality_style, "")
    return f"{prefix}{message}"


# Export all constants and utilities
__all__ = [
    # Enums
    "ProgressMetricType",
    "AchievementCategory",
    "VisualizationType",
    "AnalysisType",
    "MilestoneType",
    "ComparisonPeriod",
    "DataQuality",
    "TrendDirection",
    "PersonalityStyle",
    # Constants
    "STELLA_PERSONALITY_TRAITS",
    "PROGRESS_THRESHOLDS",
    "MILESTONE_CRITERIA",
    "VISUALIZATION_COLORS",
    "ACHIEVEMENT_SYSTEM",
    "STELLA_SKILLS",
    "DATA_FORMATS",
    "ERROR_MESSAGES",
    # Classes
    "PerformanceThresholds",
    # Utility Functions
    "get_stella_personality_style",
    "get_visualization_config",
    "get_achievement_level",
    "format_stella_response",
]
