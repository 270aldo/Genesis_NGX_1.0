"""
Configuration management for SPARK Motivation Behavior Coach.
Provides centralized configuration with validation and environment-based setup.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class MotivationApproach(Enum):
    """Supported motivation approaches."""

    INTRINSIC = "intrinsic"
    EXTRINSIC = "extrinsic"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


class BehaviorChangeModel(Enum):
    """Supported behavior change models."""

    TRANSTHEORETICAL = "transtheoretical"  # Stages of Change
    SOCIAL_COGNITIVE = "social_cognitive"  # Bandura's model
    HEALTH_BELIEF = "health_belief"  # Health Belief Model
    THEORY_PLANNED_BEHAVIOR = "theory_planned_behavior"  # TPB
    HABIT_LOOP = "habit_loop"  # Habit Loop Model


class CoachingStyle(Enum):
    """Supported coaching styles."""

    DIRECTIVE = "directive"
    NON_DIRECTIVE = "non_directive"
    COLLABORATIVE = "collaborative"
    ADAPTIVE = "adaptive"


@dataclass
class SparkConfig:
    """
    Configuration for SPARK Motivation Behavior Coach.

    Contains all configuration parameters for the agent including
    behavioral analysis settings, motivation strategies, coaching
    approaches, and performance optimization parameters.
    """

    # Basic agent configuration
    agent_id: str = "spark_motivation_coach"
    agent_name: str = "SPARK Motivation & Behavior Coach"
    agent_description: str = (
        "Specialized agent for motivation and behavioral change coaching"
    )

    # Performance and response configuration
    max_response_time: float = 30.0
    default_timeout: float = 25.0
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Behavioral analysis configuration
    default_motivation_approach: MotivationApproach = MotivationApproach.ADAPTIVE
    default_behavior_change_model: BehaviorChangeModel = (
        BehaviorChangeModel.TRANSTHEORETICAL
    )
    default_coaching_style: CoachingStyle = CoachingStyle.COLLABORATIVE

    # Habit formation configuration
    min_habit_duration_days: int = 21
    max_habit_duration_days: int = 90
    habit_check_frequency_days: int = 7
    habit_milestone_intervals: List[int] = field(
        default_factory=lambda: [7, 14, 21, 30, 60, 90]
    )

    # Goal setting configuration
    max_concurrent_goals: int = 5
    goal_review_frequency_days: int = 14
    milestone_celebration_threshold: float = 0.75  # 75% progress

    # Motivation strategies configuration
    strategy_rotation_days: int = 7
    motivation_check_frequency_hours: int = 24
    low_motivation_threshold: float = 0.3  # 30% motivation score
    high_motivation_threshold: float = 0.8  # 80% motivation score

    # Behavioral change configuration
    change_stage_assessment_frequency_days: int = 7
    relapse_prevention_check_days: int = 3
    behavior_tracking_period_days: int = 30

    # Obstacle management configuration
    obstacle_identification_frequency_days: int = 7
    obstacle_severity_threshold: float = 0.6  # 60% severity
    solution_effectiveness_threshold: float = 0.7  # 70% effectiveness

    # Personality adaptation configuration
    personality_adaptation_enabled: bool = True
    prime_focus_areas: List[str] = field(
        default_factory=lambda: [
            "performance_optimization",
            "executive_productivity",
            "competitive_advantage",
            "efficiency_maximization",
            "strategic_goal_achievement",
        ]
    )
    longevity_focus_areas: List[str] = field(
        default_factory=lambda: [
            "sustainable_habits",
            "long_term_wellness",
            "gradual_improvement",
            "life_balance",
            "preventive_care",
        ]
    )

    # AI and ML configuration
    enable_ai_insights: bool = True
    motivation_prediction_enabled: bool = True
    behavior_pattern_analysis_enabled: bool = True
    personalized_recommendations_enabled: bool = True

    # Security and compliance configuration
    enable_audit_logging: bool = True
    data_encryption_enabled: bool = True
    gdpr_compliance_enabled: bool = True
    behavioral_data_retention_days: int = 365

    # Monitoring and health configuration
    enable_health_monitoring: bool = True
    health_check_interval_seconds: int = 60
    enable_performance_metrics: bool = True
    enable_error_tracking: bool = True

    # Cache configuration
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    max_cache_size: int = 1000

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_timeouts()
        self._validate_thresholds()
        self._validate_intervals()
        self._validate_behavioral_settings()

    def _validate_timeouts(self):
        """Validate timeout configurations."""
        if self.max_response_time <= 0:
            raise ValueError("max_response_time must be positive")
        if self.default_timeout <= 0 or self.default_timeout > self.max_response_time:
            raise ValueError(
                "default_timeout must be positive and <= max_response_time"
            )
        if self.retry_delay <= 0:
            raise ValueError("retry_delay must be positive")

    def _validate_thresholds(self):
        """Validate threshold configurations."""
        thresholds = [
            (self.milestone_celebration_threshold, "milestone_celebration_threshold"),
            (self.low_motivation_threshold, "low_motivation_threshold"),
            (self.high_motivation_threshold, "high_motivation_threshold"),
            (self.obstacle_severity_threshold, "obstacle_severity_threshold"),
            (self.solution_effectiveness_threshold, "solution_effectiveness_threshold"),
        ]

        for threshold, name in thresholds:
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")

        if self.low_motivation_threshold >= self.high_motivation_threshold:
            raise ValueError(
                "low_motivation_threshold must be < high_motivation_threshold"
            )

    def _validate_intervals(self):
        """Validate interval configurations."""
        intervals = [
            (self.min_habit_duration_days, "min_habit_duration_days"),
            (self.max_habit_duration_days, "max_habit_duration_days"),
            (self.habit_check_frequency_days, "habit_check_frequency_days"),
            (self.goal_review_frequency_days, "goal_review_frequency_days"),
            (self.strategy_rotation_days, "strategy_rotation_days"),
            (self.motivation_check_frequency_hours, "motivation_check_frequency_hours"),
            (
                self.change_stage_assessment_frequency_days,
                "change_stage_assessment_frequency_days",
            ),
            (self.relapse_prevention_check_days, "relapse_prevention_check_days"),
            (self.behavior_tracking_period_days, "behavior_tracking_period_days"),
            (
                self.obstacle_identification_frequency_days,
                "obstacle_identification_frequency_days",
            ),
        ]

        for interval, name in intervals:
            if interval <= 0:
                raise ValueError(f"{name} must be positive")

        if self.min_habit_duration_days > self.max_habit_duration_days:
            raise ValueError(
                "min_habit_duration_days must be <= max_habit_duration_days"
            )

    def _validate_behavioral_settings(self):
        """Validate behavioral-specific settings."""
        if self.max_concurrent_goals <= 0:
            raise ValueError("max_concurrent_goals must be positive")
        if self.retry_attempts <= 0:
            raise ValueError("retry_attempts must be positive")
        if self.behavioral_data_retention_days <= 0:
            raise ValueError("behavioral_data_retention_days must be positive")
        if self.cache_ttl_seconds <= 0:
            raise ValueError("cache_ttl_seconds must be positive")
        if self.max_cache_size <= 0:
            raise ValueError("max_cache_size must be positive")

    @classmethod
    def from_environment(cls) -> "SparkConfig":
        """
        Create configuration from environment variables.

        Returns:
            SparkConfig: Configuration loaded from environment
        """
        return cls(
            # Basic configuration
            agent_id=os.getenv("SPARK_AGENT_ID", "spark_motivation_coach"),
            agent_name=os.getenv(
                "SPARK_AGENT_NAME", "SPARK Motivation & Behavior Coach"
            ),
            # Performance configuration
            max_response_time=float(os.getenv("SPARK_MAX_RESPONSE_TIME", "30.0")),
            default_timeout=float(os.getenv("SPARK_DEFAULT_TIMEOUT", "25.0")),
            retry_attempts=int(os.getenv("SPARK_RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("SPARK_RETRY_DELAY", "1.0")),
            # Behavioral configuration
            min_habit_duration_days=int(
                os.getenv("SPARK_MIN_HABIT_DURATION_DAYS", "21")
            ),
            max_habit_duration_days=int(
                os.getenv("SPARK_MAX_HABIT_DURATION_DAYS", "90")
            ),
            habit_check_frequency_days=int(
                os.getenv("SPARK_HABIT_CHECK_FREQUENCY_DAYS", "7")
            ),
            max_concurrent_goals=int(os.getenv("SPARK_MAX_CONCURRENT_GOALS", "5")),
            goal_review_frequency_days=int(
                os.getenv("SPARK_GOAL_REVIEW_FREQUENCY_DAYS", "14")
            ),
            # Motivation configuration
            strategy_rotation_days=int(os.getenv("SPARK_STRATEGY_ROTATION_DAYS", "7")),
            motivation_check_frequency_hours=int(
                os.getenv("SPARK_MOTIVATION_CHECK_FREQUENCY_HOURS", "24")
            ),
            low_motivation_threshold=float(
                os.getenv("SPARK_LOW_MOTIVATION_THRESHOLD", "0.3")
            ),
            high_motivation_threshold=float(
                os.getenv("SPARK_HIGH_MOTIVATION_THRESHOLD", "0.8")
            ),
            # Security and compliance
            enable_audit_logging=os.getenv("SPARK_ENABLE_AUDIT_LOGGING", "true").lower()
            == "true",
            data_encryption_enabled=os.getenv(
                "SPARK_DATA_ENCRYPTION_ENABLED", "true"
            ).lower()
            == "true",
            gdpr_compliance_enabled=os.getenv(
                "SPARK_GDPR_COMPLIANCE_ENABLED", "true"
            ).lower()
            == "true",
            behavioral_data_retention_days=int(
                os.getenv("SPARK_BEHAVIORAL_DATA_RETENTION_DAYS", "365")
            ),
            # Feature flags
            enable_ai_insights=os.getenv("SPARK_ENABLE_AI_INSIGHTS", "true").lower()
            == "true",
            motivation_prediction_enabled=os.getenv(
                "SPARK_MOTIVATION_PREDICTION_ENABLED", "true"
            ).lower()
            == "true",
            behavior_pattern_analysis_enabled=os.getenv(
                "SPARK_BEHAVIOR_PATTERN_ANALYSIS_ENABLED", "true"
            ).lower()
            == "true",
            # Monitoring
            enable_health_monitoring=os.getenv(
                "SPARK_ENABLE_HEALTH_MONITORING", "true"
            ).lower()
            == "true",
            health_check_interval_seconds=int(
                os.getenv("SPARK_HEALTH_CHECK_INTERVAL_SECONDS", "60")
            ),
            enable_performance_metrics=os.getenv(
                "SPARK_ENABLE_PERFORMANCE_METRICS", "true"
            ).lower()
            == "true",
            # Cache configuration
            enable_caching=os.getenv("SPARK_ENABLE_CACHING", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("SPARK_CACHE_TTL_SECONDS", "3600")),
            max_cache_size=int(os.getenv("SPARK_MAX_CACHE_SIZE", "1000")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, list):
                result[key] = value.copy()
            else:
                result[key] = value
        return result

    def get_coaching_style_for_program(self, program_type: str) -> CoachingStyle:
        """Get appropriate coaching style for program type."""
        if program_type == "PRIME":
            return CoachingStyle.DIRECTIVE
        elif program_type == "LONGEVITY":
            return CoachingStyle.COLLABORATIVE
        else:
            return self.default_coaching_style

    def get_motivation_approach_for_user(
        self, user_profile: Optional[Dict[str, Any]] = None
    ) -> MotivationApproach:
        """Get appropriate motivation approach for user."""
        if not user_profile:
            return self.default_motivation_approach

        # Analyze user profile to determine best approach
        if user_profile.get("achievement_oriented", False):
            return MotivationApproach.EXTRINSIC
        elif user_profile.get("autonomy_oriented", False):
            return MotivationApproach.INTRINSIC
        else:
            return MotivationApproach.ADAPTIVE
