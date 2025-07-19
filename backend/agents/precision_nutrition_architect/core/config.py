"""
Configuration management for Precision Nutrition Architect Agent.
Centralizes all configuration settings following A+ standards.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import os
from pathlib import Path


@dataclass
class NutritionConfig:
    """
    Comprehensive configuration for SAGE nutrition agent.
    All settings are centralized and type-safe.
    """

    # Performance settings
    max_response_time: float = 30.0
    max_retry_attempts: int = 3
    request_timeout: float = 25.0

    # AI/ML settings
    gemini_model: str = "gemini-1.5-flash-002"
    temperature: float = 0.7
    max_output_tokens: int = 8192
    enable_vision_analysis: bool = True

    # Nutrition-specific settings
    default_calorie_targets: Dict[str, int] = field(
        default_factory=lambda: {
            "sedentary": 2000,
            "lightly_active": 2200,
            "moderately_active": 2500,
            "very_active": 2800,
            "extremely_active": 3200,
        }
    )

    macro_ratio_presets: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: {
            "balanced": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
            "low_carb": {"protein": 0.35, "carbs": 0.20, "fat": 0.45},
            "high_protein": {"protein": 0.40, "carbs": 0.35, "fat": 0.25},
            "mediterranean": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
            "ketogenic": {"protein": 0.25, "carbs": 0.05, "fat": 0.70},
        }
    )

    # Biomarker reference ranges
    biomarker_ranges: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "glucose_fasting": {"min": 70, "max": 100, "unit": "mg/dL"},
            "hba1c": {"min": 4.0, "max": 5.6, "unit": "%"},
            "cholesterol_total": {"min": 125, "max": 200, "unit": "mg/dL"},
            "hdl": {"min": 40, "max": 200, "unit": "mg/dL"},
            "ldl": {"min": 0, "max": 100, "unit": "mg/dL"},
            "triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
        }
    )

    # Security settings
    enable_health_data_encryption: bool = True
    enable_audit_logging: bool = True
    max_health_record_retention_days: int = 365
    require_consent_for_analysis: bool = True

    # Cache settings
    cache_meal_plans: bool = True
    cache_ttl_seconds: int = 3600
    max_cached_items: int = 1000

    # Integration settings
    enable_wearable_integration: bool = True
    enable_food_database_api: bool = True
    supported_food_databases: List[str] = field(
        default_factory=lambda: ["usda", "nutritionix", "myfitnesspal", "custom"]
    )

    # Validation settings
    min_calories_per_meal: int = 200
    max_calories_per_meal: int = 1500
    min_meals_per_day: int = 3
    max_meals_per_day: int = 6

    # Feature flags
    enable_chrononutrition: bool = True
    enable_genetic_optimization: bool = True
    enable_microbiome_analysis: bool = False
    enable_continuous_glucose_monitoring: bool = True

    # Compliance settings
    gdpr_compliant: bool = True
    hipaa_compliant: bool = True
    data_retention_policy: str = "strict"

    @classmethod
    def from_environment(cls) -> "NutritionConfig":
        """
        Create configuration from environment variables.
        Allows runtime customization without code changes.
        """
        config = cls()

        # Override with environment variables if present
        if max_response := os.getenv("SAGE_MAX_RESPONSE_TIME"):
            config.max_response_time = float(max_response)

        if model := os.getenv("SAGE_GEMINI_MODEL"):
            config.gemini_model = model

        if temperature := os.getenv("SAGE_TEMPERATURE"):
            config.temperature = float(temperature)

        # Security overrides
        if encryption := os.getenv("SAGE_ENABLE_ENCRYPTION"):
            config.enable_health_data_encryption = encryption.lower() == "true"

        if audit := os.getenv("SAGE_ENABLE_AUDIT"):
            config.enable_audit_logging = audit.lower() == "true"

        # Feature flag overrides
        if chrono := os.getenv("SAGE_ENABLE_CHRONONUTRITION"):
            config.enable_chrononutrition = chrono.lower() == "true"

        if genetic := os.getenv("SAGE_ENABLE_GENETIC"):
            config.enable_genetic_optimization = genetic.lower() == "true"

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

        # Validate nutrition settings
        if self.min_calories_per_meal >= self.max_calories_per_meal:
            errors.append(
                "min_calories_per_meal must be less than max_calories_per_meal"
            )

        if self.min_meals_per_day > self.max_meals_per_day:
            errors.append(
                "min_meals_per_day must be less than or equal to max_meals_per_day"
            )

        # Validate macro ratios
        for preset, ratios in self.macro_ratio_presets.items():
            total = sum(ratios.values())
            if abs(total - 1.0) > 0.01:  # Allow small floating point errors
                errors.append(
                    f"Macro ratios for '{preset}' must sum to 1.0, got {total}"
                )

        # Validate AI settings
        if self.temperature < 0 or self.temperature > 2:
            errors.append("temperature must be between 0 and 2")

        if self.max_output_tokens <= 0:
            errors.append("max_output_tokens must be positive")

        return errors

    def get_macro_ratios(self, preset: str) -> Dict[str, float]:
        """
        Get macro ratios for a given preset with validation.
        """
        if preset not in self.macro_ratio_presets:
            return self.macro_ratio_presets["balanced"]
        return self.macro_ratio_presets[preset]

    def get_biomarker_range(self, biomarker: str) -> Optional[Dict[str, Any]]:
        """
        Get reference range for a specific biomarker.
        """
        return self.biomarker_ranges.get(biomarker)

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
            "security": {
                "encryption_enabled": self.enable_health_data_encryption,
                "audit_enabled": self.enable_audit_logging,
                "gdpr_compliant": self.gdpr_compliant,
                "hipaa_compliant": self.hipaa_compliant,
            },
            "features": {
                "chrononutrition": self.enable_chrononutrition,
                "genetic_optimization": self.enable_genetic_optimization,
                "microbiome_analysis": self.enable_microbiome_analysis,
                "cgm_integration": self.enable_continuous_glucose_monitoring,
            },
        }
