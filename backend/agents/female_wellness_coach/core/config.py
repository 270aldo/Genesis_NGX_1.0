"""
Configuration for LUNA Female Wellness Specialist agent.
Defines all configurable parameters for A+ level operation.
"""

import os
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class LunaConfig:
    """
    Configuration for LUNA Female Wellness Specialist agent.

    Defines all configurable parameters including performance settings,
    security options, and feature flags for optimal A+ level operation
    specialized for female wellness with GDPR/HIPAA compliance.
    """

    # Performance settings
    max_response_time: float = 30.0
    retry_attempts: int = 3
    cache_ttl: int = 3600
    concurrent_analysis_limit: int = 5

    # Personality adaptation (ENFJ - Maternal, empathetic, supportive)
    enable_personality_adaptation: bool = True
    personality_cache_ttl: int = 1800
    enfj_empathy_level: float = 0.9  # High empathy for wellness coaching

    # Security settings (Critical for health data)
    enable_audit_logging: bool = True
    enable_data_encryption: bool = True
    enable_gdpr_compliance: bool = True
    enable_hipaa_compliance: bool = True
    enable_menstrual_data_protection: bool = True

    # Female wellness analysis settings
    enable_real_wellness_analysis: bool = True  # Set to False for mock mode
    menstrual_cycle_timeout: float = 10.0
    max_health_data_points_per_analysis: int = 1000
    enable_hormonal_pattern_detection: bool = True

    # Feature flags - Female wellness specializations
    enable_menstrual_cycle_analysis: bool = True
    enable_hormonal_nutrition: bool = True
    enable_cycle_based_training: bool = True
    enable_menopause_management: bool = True
    enable_bone_health_assessment: bool = True
    enable_emotional_wellness: bool = True

    # ElevenLabs voice synthesis settings
    enable_voice_synthesis: bool = True
    voice_model: str = "female_wellness_coach"
    voice_stability: float = 0.7
    voice_clarity: float = 0.8

    # External service settings
    gemini_timeout: float = 15.0
    supabase_timeout: float = 5.0
    elevenlabs_timeout: float = 10.0

    # Monitoring and telemetry
    enable_performance_monitoring: bool = True
    enable_business_metrics: bool = True
    metrics_collection_interval: int = 60
    enable_wellness_outcome_tracking: bool = True

    # Debug settings
    debug_mode: bool = False
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "LunaConfig":
        """
        Create configuration from environment variables.

        Returns:
            LunaConfig: Configuration loaded from environment
        """
        return cls(
            # Performance
            max_response_time=float(os.getenv("LUNA_MAX_RESPONSE_TIME", "30.0")),
            retry_attempts=int(os.getenv("LUNA_RETRY_ATTEMPTS", "3")),
            cache_ttl=int(os.getenv("LUNA_CACHE_TTL", "3600")),
            # Personality
            enable_personality_adaptation=os.getenv(
                "LUNA_ENABLE_PERSONALITY", "true"
            ).lower()
            == "true",
            enfj_empathy_level=float(os.getenv("LUNA_ENFJ_EMPATHY", "0.9")),
            # Security
            enable_audit_logging=os.getenv("LUNA_ENABLE_AUDIT", "true").lower()
            == "true",
            enable_data_encryption=os.getenv("LUNA_ENABLE_ENCRYPTION", "true").lower()
            == "true",
            enable_gdpr_compliance=os.getenv("LUNA_ENABLE_GDPR", "true").lower()
            == "true",
            enable_hipaa_compliance=os.getenv("LUNA_ENABLE_HIPAA", "true").lower()
            == "true",
            # Wellness analysis
            enable_real_wellness_analysis=os.getenv(
                "LUNA_ENABLE_REAL_ANALYSIS", "true"
            ).lower()
            == "true",
            # Feature flags
            enable_menstrual_cycle_analysis=os.getenv(
                "LUNA_ENABLE_MENSTRUAL", "true"
            ).lower()
            == "true",
            enable_hormonal_nutrition=os.getenv(
                "LUNA_ENABLE_HORMONAL_NUTRITION", "true"
            ).lower()
            == "true",
            enable_cycle_based_training=os.getenv(
                "LUNA_ENABLE_CYCLE_TRAINING", "true"
            ).lower()
            == "true",
            enable_menopause_management=os.getenv(
                "LUNA_ENABLE_MENOPAUSE", "true"
            ).lower()
            == "true",
            # Voice settings
            enable_voice_synthesis=os.getenv("LUNA_ENABLE_VOICE", "true").lower()
            == "true",
            voice_model=os.getenv("LUNA_VOICE_MODEL", "female_wellness_coach"),
            # Debug
            debug_mode=os.getenv("LUNA_DEBUG_MODE", "false").lower() == "true",
            log_level=os.getenv("LUNA_LOG_LEVEL", "INFO").upper(),
        )

    def validate(self) -> None:
        """
        Validate configuration parameters.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.max_response_time <= 0:
            raise ValueError("max_response_time must be positive")

        if self.retry_attempts < 0:
            raise ValueError("retry_attempts cannot be negative")

        if self.cache_ttl <= 0:
            raise ValueError("cache_ttl must be positive")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log_level: {self.log_level}")

        if not (0.0 <= self.enfj_empathy_level <= 1.0):
            raise ValueError("enfj_empathy_level must be between 0.0 and 1.0")

        # Security validation for production (critical for health data)
        if not self.debug_mode:
            if not self.enable_data_encryption:
                raise ValueError("Data encryption must be enabled in production")
            if not self.enable_audit_logging:
                raise ValueError("Audit logging must be enabled in production")
            if not self.enable_gdpr_compliance:
                raise ValueError("GDPR compliance must be enabled for health data")
            if not self.enable_hipaa_compliance:
                raise ValueError("HIPAA compliance must be enabled for health data")

    @property
    def is_production_ready(self) -> bool:
        """
        Check if configuration is ready for production.

        Returns:
            bool: True if configuration meets production standards for health data
        """
        try:
            self.validate()
            return (
                self.enable_data_encryption
                and self.enable_audit_logging
                and self.enable_gdpr_compliance
                and self.enable_hipaa_compliance
                and self.enable_menstrual_data_protection
                and not self.debug_mode
            )
        except ValueError:
            return False
