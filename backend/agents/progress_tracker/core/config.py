"""
STELLA Progress Tracker Configuration.
Comprehensive configuration management for A+ architecture with progress tracking settings.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class VisualizationType(Enum):
    """Types of progress visualizations."""

    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PROGRESS_BAR = "progress_bar"
    HEATMAP = "heatmap"
    SCATTER_PLOT = "scatter_plot"
    INFOGRAPHIC = "infographic"


class ComparisonPeriod(Enum):
    """Time periods for progress comparison."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class PersonalityMode(Enum):
    """STELLA personality interaction modes."""

    ENTHUSIASTIC = "enthusiastic"
    SUPPORTIVE = "supportive"
    ANALYTICAL = "analytical"
    CELEBRATORY = "celebratory"


@dataclass
class StellaConfig:
    """
    Configuration for STELLA Progress Tracker with comprehensive progress tracking settings.
    """

    # Core Agent Configuration
    agent_id: str = "stella_progress_tracker"
    agent_name: str = "STELLA Progress Tracker"
    agent_version: str = "2.0.0-A+"
    max_response_time: float = 30.0
    default_timeout: float = 25.0
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Progress Tracking Configuration
    max_progress_entries_per_request: int = 100
    min_comparison_days: int = 7
    max_comparison_days: int = 365
    default_comparison_period: ComparisonPeriod = ComparisonPeriod.WEEKLY
    achievement_detection_enabled: bool = True
    milestone_auto_detection: bool = True

    # Visualization Configuration
    default_visualization_type: VisualizationType = VisualizationType.LINE_CHART
    max_chart_data_points: int = 1000
    chart_width: int = 800
    chart_height: int = 600
    enable_interactive_charts: bool = True
    chart_export_formats: List[str] = None

    # Vision Analysis Configuration
    enable_vision_analysis: bool = True
    max_image_size_mb: float = 10.0
    supported_image_formats: List[str] = None
    vision_analysis_timeout: float = 15.0
    body_measurement_extraction: bool = True
    form_analysis_enabled: bool = True

    # STELLA Personality Configuration
    personality_mode: PersonalityMode = PersonalityMode.ENTHUSIASTIC
    celebration_intensity: float = 0.8  # 0.0 to 1.0
    encouragement_frequency: float = 0.7  # 0.0 to 1.0
    personality_adaptation_enabled: bool = True
    esfj_personality_traits: bool = True

    # Achievement System Configuration
    achievement_categories: List[str] = None
    milestone_sensitivity: float = 0.5  # 0.0 to 1.0
    celebration_threshold: float = 0.1  # Minimum improvement to celebrate
    achievement_persistence_days: int = 30

    # Data Management Configuration
    data_retention_days: int = 365
    cache_ttl_seconds: int = 3600
    max_cache_size: int = 1000
    enable_data_compression: bool = True
    backup_frequency_hours: int = 24

    # Performance Configuration
    max_concurrent_analyses: int = 5
    analysis_batch_size: int = 50
    enable_parallel_processing: bool = True
    memory_limit_mb: int = 512

    # Security Configuration
    enable_audit_logging: bool = True
    data_encryption_enabled: bool = True
    secure_image_handling: bool = True
    privacy_mode_enabled: bool = False

    # AI Configuration
    enable_ai_insights: bool = True
    ai_confidence_threshold: float = 0.7
    enable_predictive_analysis: bool = True
    model_temperature: float = 0.7
    max_tokens_per_request: int = 2000

    # Integration Configuration
    enable_external_integrations: bool = True
    fitness_tracker_sync: bool = True
    nutrition_app_sync: bool = True
    calendar_integration: bool = False

    def __post_init__(self):
        """Initialize default values and validate configuration."""
        # Set default chart export formats
        if self.chart_export_formats is None:
            self.chart_export_formats = ["png", "svg", "pdf"]

        # Set default supported image formats
        if self.supported_image_formats is None:
            self.supported_image_formats = ["jpg", "jpeg", "png", "webp", "bmp", "tiff"]

        # Set default achievement categories
        if self.achievement_categories is None:
            self.achievement_categories = [
                "strength",
                "endurance",
                "consistency",
                "nutrition",
                "weight_loss",
                "muscle_gain",
                "flexibility",
                "mental_health",
            ]

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate configuration values."""
        if self.max_response_time <= 0:
            raise ValueError("max_response_time must be positive")

        if self.default_timeout >= self.max_response_time:
            raise ValueError("default_timeout must be less than max_response_time")

        if self.retry_attempts < 0:
            raise ValueError("retry_attempts must be non-negative")

        if not (0 <= self.celebration_intensity <= 1):
            raise ValueError("celebration_intensity must be between 0.0 and 1.0")

        if not (0 <= self.encouragement_frequency <= 1):
            raise ValueError("encouragement_frequency must be between 0.0 and 1.0")

        if not (0 <= self.milestone_sensitivity <= 1):
            raise ValueError("milestone_sensitivity must be between 0.0 and 1.0")

        if self.max_image_size_mb <= 0:
            raise ValueError("max_image_size_mb must be positive")

        if self.min_comparison_days >= self.max_comparison_days:
            raise ValueError(
                "min_comparison_days must be less than max_comparison_days"
            )

        if not (0 <= self.ai_confidence_threshold <= 1):
            raise ValueError("ai_confidence_threshold must be between 0.0 and 1.0")

    @classmethod
    def from_environment(cls) -> "StellaConfig":
        """
        Create configuration from environment variables.

        Returns:
            StellaConfig instance with values from environment
        """
        env_config = {}

        # Core configuration
        if agent_id := os.getenv("STELLA_AGENT_ID"):
            env_config["agent_id"] = agent_id

        if max_response_time := os.getenv("STELLA_MAX_RESPONSE_TIME"):
            env_config["max_response_time"] = float(max_response_time)

        if retry_attempts := os.getenv("STELLA_RETRY_ATTEMPTS"):
            env_config["retry_attempts"] = int(retry_attempts)

        # Progress tracking configuration
        if max_entries := os.getenv("STELLA_MAX_PROGRESS_ENTRIES"):
            env_config["max_progress_entries_per_request"] = int(max_entries)

        if comparison_period := os.getenv("STELLA_DEFAULT_COMPARISON_PERIOD"):
            env_config["default_comparison_period"] = ComparisonPeriod(
                comparison_period
            )

        # Visualization configuration
        if viz_type := os.getenv("STELLA_DEFAULT_VISUALIZATION_TYPE"):
            env_config["default_visualization_type"] = VisualizationType(viz_type)

        if chart_width := os.getenv("STELLA_CHART_WIDTH"):
            env_config["chart_width"] = int(chart_width)

        if chart_height := os.getenv("STELLA_CHART_HEIGHT"):
            env_config["chart_height"] = int(chart_height)

        # Personality configuration
        if personality_mode := os.getenv("STELLA_PERSONALITY_MODE"):
            env_config["personality_mode"] = PersonalityMode(personality_mode)

        if celebration_intensity := os.getenv("STELLA_CELEBRATION_INTENSITY"):
            env_config["celebration_intensity"] = float(celebration_intensity)

        # Security configuration
        if audit_logging := os.getenv("STELLA_ENABLE_AUDIT_LOGGING"):
            env_config["enable_audit_logging"] = audit_logging.lower() == "true"

        if data_encryption := os.getenv("STELLA_DATA_ENCRYPTION_ENABLED"):
            env_config["data_encryption_enabled"] = data_encryption.lower() == "true"

        # AI configuration
        if ai_insights := os.getenv("STELLA_ENABLE_AI_INSIGHTS"):
            env_config["enable_ai_insights"] = ai_insights.lower() == "true"

        if ai_threshold := os.getenv("STELLA_AI_CONFIDENCE_THRESHOLD"):
            env_config["ai_confidence_threshold"] = float(ai_threshold)

        return cls(**env_config)

    def get_personality_style_for_program(self, program_type: str) -> PersonalityMode:
        """
        Get appropriate personality style based on program type.

        Args:
            program_type: User's program type (PRIME/LONGEVITY)

        Returns:
            Appropriate PersonalityMode for the program
        """
        if program_type == "PRIME":
            # More analytical and performance-focused for executives
            return PersonalityMode.ANALYTICAL
        elif program_type == "LONGEVITY":
            # More supportive and encouraging for wellness
            return PersonalityMode.SUPPORTIVE
        else:
            # Default to enthusiastic STELLA personality
            return self.personality_mode

    def get_visualization_config(self) -> Dict[str, Any]:
        """
        Get visualization-specific configuration.

        Returns:
            Dict containing visualization settings
        """
        return {
            "default_type": self.default_visualization_type.value,
            "max_data_points": self.max_chart_data_points,
            "width": self.chart_width,
            "height": self.chart_height,
            "interactive": self.enable_interactive_charts,
            "export_formats": self.chart_export_formats,
            "supported_types": [vt.value for vt in VisualizationType],
        }

    def get_analysis_config(self) -> Dict[str, Any]:
        """
        Get analysis-specific configuration.

        Returns:
            Dict containing analysis settings
        """
        return {
            "ai_enabled": self.enable_ai_insights,
            "vision_enabled": self.enable_vision_analysis,
            "predictive_enabled": self.enable_predictive_analysis,
            "confidence_threshold": self.ai_confidence_threshold,
            "max_concurrent": self.max_concurrent_analyses,
            "batch_size": self.analysis_batch_size,
            "timeout": self.vision_analysis_timeout,
        }

    def get_achievement_config(self) -> Dict[str, Any]:
        """
        Get achievement system configuration.

        Returns:
            Dict containing achievement settings
        """
        return {
            "categories": self.achievement_categories,
            "detection_enabled": self.achievement_detection_enabled,
            "milestone_auto_detection": self.milestone_auto_detection,
            "sensitivity": self.milestone_sensitivity,
            "celebration_threshold": self.celebration_threshold,
            "persistence_days": self.achievement_persistence_days,
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dict representation of configuration
        """
        config_dict = {}

        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, Enum):
                config_dict[field_name] = field_value.value
            else:
                config_dict[field_name] = field_value

        return config_dict
