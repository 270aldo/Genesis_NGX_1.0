"""
Configuration management for WAVE Performance Analytics Agent.
Centralizes fusion agent settings for recovery and analytics capabilities.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import os
from pathlib import Path


@dataclass
class WaveAnalyticsConfig:
    """
    Comprehensive configuration for WAVE Performance Analytics fusion agent.
    Combines recovery (WAVE) and analytics (VOLT) settings with fusion capabilities.
    """

    # Performance settings
    max_response_time: float = 25.0
    max_retry_attempts: int = 3
    request_timeout: float = 20.0

    # AI/ML settings
    gemini_model: str = "gemini-1.5-flash-002"
    temperature: float = 0.6  # Slightly lower for more consistent recovery advice
    max_output_tokens: int = 6144
    enable_vision_analysis: bool = True

    # Recovery-specific settings (from WAVE)
    recovery_protocols: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "injury_prevention": {
                "assessment_frequency": "weekly",
                "risk_threshold": 0.7,
                "preventive_actions": ["mobility", "strength", "flexibility"],
            },
            "rehabilitation": {
                "progression_rate": "conservative",
                "pain_threshold": 3,  # 0-10 scale
                "session_duration_minutes": 45,
            },
            "sleep_optimization": {
                "target_sleep_hours": 8,
                "deep_sleep_percentage": 20,
                "rem_sleep_percentage": 25,
            },
            "mobility_assessment": {
                "joint_range_targets": {
                    "ankle": 20,
                    "hip": 90,
                    "shoulder": 180,
                    "spine": 45,
                },
                "assessment_interval_days": 14,
            },
        }
    )

    # Analytics-specific settings (from VOLT)
    analytics_config: Dict[str, Any] = field(
        default_factory=lambda: {
            "biometric_analysis": {
                "hrv_threshold": 30,  # ms
                "rhr_variance_threshold": 10,  # bpm
                "data_smoothing_window": 7,  # days
                "outlier_detection": True,
            },
            "pattern_recognition": {
                "min_data_points": 14,
                "trend_significance": 0.05,
                "correlation_threshold": 0.6,
                "lookback_period_days": 90,
            },
            "data_visualization": {
                "chart_types": ["line", "bar", "scatter", "heatmap"],
                "color_scheme": "recovery_focused",
                "export_formats": ["png", "svg", "pdf"],
            },
        }
    )

    # Fusion-specific settings (new capabilities)
    fusion_config: Dict[str, Any] = field(
        default_factory=lambda: {
            "recovery_analytics_fusion": {
                "integration_weight_recovery": 0.6,
                "integration_weight_analytics": 0.4,
                "fusion_confidence_threshold": 0.75,
                "cross_domain_insights": True,
            },
            "injury_prediction": {
                "prediction_horizon_days": 14,
                "risk_factors": [
                    "hrv_decline",
                    "sleep_quality",
                    "training_load",
                    "previous_injuries",
                    "mobility_scores",
                ],
                "alert_threshold": 0.8,
                "model_retraining_frequency": "monthly",
            },
            "performance_optimization": {
                "optimization_targets": [
                    "recovery_time",
                    "sleep_quality",
                    "mobility_score",
                    "injury_risk",
                    "readiness_score",
                ],
                "adaptation_rate": 0.1,
                "plateau_detection_days": 21,
            },
        }
    )

    # Device integration settings
    wearable_integration: Dict[str, Any] = field(
        default_factory=lambda: {
            "supported_devices": [
                "whoop",
                "oura",
                "apple_watch",
                "garmin",
                "polar",
                "fitbit",
            ],
            "sync_frequency_minutes": 30,
            "data_types": [
                "hrv",
                "sleep",
                "activity",
                "recovery_score",
                "strain",
                "readiness",
                "temperature",
            ],
            "quality_checks": True,
            "outlier_filtering": True,
        }
    )

    # Data retention and privacy
    data_retention: Dict[str, int] = field(
        default_factory=lambda: {
            "biometric_data_days": 365,
            "recovery_sessions_days": 180,
            "analytics_cache_hours": 24,
            "prediction_models_days": 90,
            "user_preferences_days": 730,
        }
    )

    # Security settings
    enable_health_data_encryption: bool = True
    enable_audit_logging: bool = True
    require_consent_for_analytics: bool = True
    anonymize_exported_data: bool = True

    # Cache settings
    cache_recovery_plans: bool = True
    cache_analytics_results: bool = True
    cache_ttl_seconds: int = 1800  # 30 minutes
    max_cached_items: int = 2000

    # Feature flags
    enable_injury_prediction: bool = True
    enable_sleep_coaching: bool = True
    enable_mobility_tracking: bool = True
    enable_recovery_analytics_fusion: bool = True
    enable_performance_optimization: bool = True
    enable_real_time_monitoring: bool = True

    # Compliance settings
    gdpr_compliant: bool = True
    hipaa_compliant: bool = True
    data_residency: str = "eu"  # or "us", "global"

    @classmethod
    def from_environment(cls) -> "WaveAnalyticsConfig":
        """
        Create configuration from environment variables.
        Allows runtime customization without code changes.
        """
        config = cls()

        # Override with environment variables if present
        if max_response := os.getenv("WAVE_MAX_RESPONSE_TIME"):
            config.max_response_time = float(max_response)

        if model := os.getenv("WAVE_GEMINI_MODEL"):
            config.gemini_model = model

        if temperature := os.getenv("WAVE_TEMPERATURE"):
            config.temperature = float(temperature)

        # Security overrides
        if encryption := os.getenv("WAVE_ENABLE_ENCRYPTION"):
            config.enable_health_data_encryption = encryption.lower() == "true"

        if audit := os.getenv("WAVE_ENABLE_AUDIT"):
            config.enable_audit_logging = audit.lower() == "true"

        # Feature flag overrides
        if injury_pred := os.getenv("WAVE_ENABLE_INJURY_PREDICTION"):
            config.enable_injury_prediction = injury_pred.lower() == "true"

        if fusion := os.getenv("WAVE_ENABLE_FUSION"):
            config.enable_recovery_analytics_fusion = fusion.lower() == "true"

        # Data residency
        if residency := os.getenv("WAVE_DATA_RESIDENCY"):
            config.data_residency = residency

        return config

    def validate(self) -> List[str]:
        """
        Validate configuration settings.
        Returns list of validation errors, empty if valid.
        """
        errors = []

        # Validate performance settings
        if self.max_response_time <= 0:
            errors.append("max_response_time must be positive")

        if self.max_retry_attempts < 0:
            errors.append("max_retry_attempts cannot be negative")

        # Validate AI settings
        if self.temperature < 0 or self.temperature > 2:
            errors.append("temperature must be between 0 and 2")

        if self.max_output_tokens <= 0:
            errors.append("max_output_tokens must be positive")

        # Validate recovery settings
        if "injury_prevention" in self.recovery_protocols:
            risk_threshold = self.recovery_protocols["injury_prevention"][
                "risk_threshold"
            ]
            if not 0 <= risk_threshold <= 1:
                errors.append(
                    "injury_prevention risk_threshold must be between 0 and 1"
                )

        if "rehabilitation" in self.recovery_protocols:
            pain_threshold = self.recovery_protocols["rehabilitation"]["pain_threshold"]
            if not 0 <= pain_threshold <= 10:
                errors.append("rehabilitation pain_threshold must be between 0 and 10")

        # Validate analytics settings
        if "pattern_recognition" in self.analytics_config:
            min_points = self.analytics_config["pattern_recognition"]["min_data_points"]
            if min_points < 7:
                errors.append(
                    "pattern_recognition min_data_points should be at least 7"
                )

        # Validate fusion settings
        if "recovery_analytics_fusion" in self.fusion_config:
            fusion_config = self.fusion_config["recovery_analytics_fusion"]
            weight_sum = (
                fusion_config["integration_weight_recovery"]
                + fusion_config["integration_weight_analytics"]
            )
            if abs(weight_sum - 1.0) > 0.01:
                errors.append("fusion integration weights must sum to 1.0")

        # Validate data retention periods
        for key, days in self.data_retention.items():
            if days <= 0:
                errors.append(f"data_retention {key} must be positive")

        return errors

    def get_recovery_protocol(self, protocol_type: str) -> Optional[Dict[str, Any]]:
        """Get specific recovery protocol configuration."""
        return self.recovery_protocols.get(protocol_type)

    def get_analytics_config(self, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Get specific analytics configuration."""
        return self.analytics_config.get(analysis_type)

    def get_fusion_config(self, fusion_type: str) -> Optional[Dict[str, Any]]:
        """Get specific fusion capability configuration."""
        return self.fusion_config.get(fusion_type)

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a specific feature is enabled."""
        feature_flags = {
            "injury_prediction": self.enable_injury_prediction,
            "sleep_coaching": self.enable_sleep_coaching,
            "mobility_tracking": self.enable_mobility_tracking,
            "recovery_analytics_fusion": self.enable_recovery_analytics_fusion,
            "performance_optimization": self.enable_performance_optimization,
            "real_time_monitoring": self.enable_real_time_monitoring,
        }
        return feature_flags.get(feature_name, False)

    def get_device_config(self, device_type: str) -> Optional[Dict[str, Any]]:
        """Get device-specific configuration."""
        if device_type not in self.wearable_integration["supported_devices"]:
            return None

        # Return device-specific settings
        base_config = self.wearable_integration.copy()
        base_config["device_type"] = device_type

        # Device-specific customizations
        if device_type == "whoop":
            base_config["primary_metrics"] = ["hrv", "recovery_score", "strain"]
        elif device_type == "oura":
            base_config["primary_metrics"] = ["sleep", "readiness", "temperature"]
        elif device_type in ["apple_watch", "garmin"]:
            base_config["primary_metrics"] = ["activity", "hrv", "sleep"]

        return base_config

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary for serialization.
        """
        return {
            "performance": {
                "max_response_time": self.max_response_time,
                "max_retry_attempts": self.max_retry_attempts,
                "request_timeout": self.request_timeout,
            },
            "ai_ml": {
                "model": self.gemini_model,
                "temperature": self.temperature,
                "max_tokens": self.max_output_tokens,
                "vision_enabled": self.enable_vision_analysis,
            },
            "recovery": self.recovery_protocols,
            "analytics": self.analytics_config,
            "fusion": self.fusion_config,
            "security": {
                "encryption_enabled": self.enable_health_data_encryption,
                "audit_enabled": self.enable_audit_logging,
                "consent_required": self.require_consent_for_analytics,
                "gdpr_compliant": self.gdpr_compliant,
                "hipaa_compliant": self.hipaa_compliant,
            },
            "features": {
                "injury_prediction": self.enable_injury_prediction,
                "sleep_coaching": self.enable_sleep_coaching,
                "mobility_tracking": self.enable_mobility_tracking,
                "fusion_analytics": self.enable_recovery_analytics_fusion,
                "performance_optimization": self.enable_performance_optimization,
                "real_time_monitoring": self.enable_real_time_monitoring,
            },
            "data_management": {
                "retention": self.data_retention,
                "wearable_integration": self.wearable_integration,
                "cache_settings": {
                    "ttl_seconds": self.cache_ttl_seconds,
                    "max_items": self.max_cached_items,
                },
            },
        }
