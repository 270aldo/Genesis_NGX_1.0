"""
Configuration management for BLAZE Elite Training Strategist.
Centralizes all configuration parameters and environment-specific settings.
"""

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class BlazeAgentConfig:
    """
    Configuration for BLAZE Elite Training Strategist agent.

    Manages all configurable parameters for training program generation,
    performance analysis, and athlete optimization protocols.
    """

    # Agent Identity
    agent_id: str = "elite_training_strategist"
    agent_name: str = "Elite Training Strategist"
    agent_description: str = (
        "Specializes in designing and periodizing training programs for elite athletes."
    )
    default_instruction: str = "Eres un estratega experto en entrenamiento deportivo."
    default_model: str = "gemini-1.5-flash"

    # Performance Parameters
    max_response_time: float = 30.0
    max_training_plan_duration_weeks: int = 52  # Maximum 1 year training plan
    min_training_sessions_per_week: int = 1
    max_training_sessions_per_week: int = 14  # Elite athletes can train twice daily

    # Training Analysis Configuration
    performance_analysis_lookback_days: int = 90
    injury_risk_threshold: float = 0.7  # 0-1 scale
    recovery_optimization_enabled: bool = True
    real_time_form_correction: bool = True

    # AI Enhancement Parameters
    enable_advanced_ai_features: bool = True
    enable_posture_detection: bool = True
    enable_predictive_analytics: bool = True
    enable_adaptive_intensity: bool = True

    # Audio and Voice Configuration
    enable_voice_coaching: bool = True
    voice_language: str = "es"  # Spanish for NGX
    workout_audio_feedback: bool = True

    # Integration Settings
    enable_nutrition_integration: bool = True
    enable_biometric_integration: bool = True
    enable_recovery_integration: bool = True

    # Security and Compliance
    enable_data_encryption: bool = True
    log_training_sessions: bool = True
    enable_performance_tracking: bool = True

    # Performance Optimization
    cache_training_plans: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    enable_batch_processing: bool = True

    @classmethod
    def from_environment(cls) -> "BlazeAgentConfig":
        """
        Create configuration from environment variables.

        Returns:
            Configuration with environment overrides applied
        """
        return cls(
            # Override from environment if available
            default_model=os.getenv("BLAZE_MODEL", cls.default_model),
            max_response_time=float(
                os.getenv("BLAZE_MAX_RESPONSE_TIME", cls.max_response_time)
            ),
            enable_advanced_ai_features=os.getenv("BLAZE_ENABLE_AI", "true").lower()
            == "true",
            enable_voice_coaching=os.getenv("BLAZE_ENABLE_VOICE", "true").lower()
            == "true",
            enable_data_encryption=os.getenv("BLAZE_ENABLE_ENCRYPTION", "true").lower()
            == "true",
            voice_language=os.getenv("BLAZE_VOICE_LANGUAGE", "es"),
        )

    def get_training_parameters(self) -> Dict[str, Any]:
        """
        Get training-specific parameters for AI models.

        Returns:
            Dictionary of training parameters
        """
        return {
            "max_duration_weeks": self.max_training_plan_duration_weeks,
            "min_sessions_per_week": self.min_training_sessions_per_week,
            "max_sessions_per_week": self.max_training_sessions_per_week,
            "injury_risk_threshold": self.injury_risk_threshold,
            "recovery_optimization": self.recovery_optimization_enabled,
            "real_time_correction": self.real_time_form_correction,
        }

    def get_ai_features(self) -> Dict[str, bool]:
        """
        Get enabled AI features configuration.

        Returns:
            Dictionary of AI feature flags
        """
        return {
            "advanced_ai": self.enable_advanced_ai_features,
            "posture_detection": self.enable_posture_detection,
            "predictive_analytics": self.enable_predictive_analytics,
            "adaptive_intensity": self.enable_adaptive_intensity,
            "voice_coaching": self.enable_voice_coaching,
            "nutrition_integration": self.enable_nutrition_integration,
            "biometric_integration": self.enable_biometric_integration,
            "recovery_integration": self.enable_recovery_integration,
        }

    def validate(self) -> List[str]:
        """
        Validate configuration parameters.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if self.max_response_time <= 0:
            errors.append("max_response_time must be positive")

        if self.max_training_plan_duration_weeks < 1:
            errors.append("max_training_plan_duration_weeks must be at least 1")

        if self.min_training_sessions_per_week < 1:
            errors.append("min_training_sessions_per_week must be at least 1")

        if self.max_training_sessions_per_week < self.min_training_sessions_per_week:
            errors.append(
                "max_training_sessions_per_week must be >= min_training_sessions_per_week"
            )

        if not 0 <= self.injury_risk_threshold <= 1:
            errors.append("injury_risk_threshold must be between 0 and 1")

        return errors
