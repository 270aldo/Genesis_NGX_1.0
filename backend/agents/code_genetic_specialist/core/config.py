"""
Configuration for CODE Genetic Specialist agent.
Defines all configurable parameters for A+ level operation.
"""

import os
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CodeGeneticConfig:
    """
    Configuration for CODE Genetic Specialist agent.

    Defines all configurable parameters including performance settings,
    security options, and feature flags for optimal A+ level operation.
    """

    # Performance settings
    max_response_time: float = 30.0
    retry_attempts: int = 3
    cache_ttl: int = 3600
    concurrent_analysis_limit: int = 5

    # Personality adaptation
    enable_personality_adaptation: bool = True
    personality_cache_ttl: int = 1800

    # Security settings
    enable_audit_logging: bool = True
    enable_data_encryption: bool = True
    enable_gdpr_compliance: bool = True
    enable_hipaa_compliance: bool = True

    # Genetic analysis settings
    enable_real_genetic_analysis: bool = True  # Set to False for mock mode
    genetic_database_timeout: float = 10.0
    max_genetic_variants_per_analysis: int = 1000

    # Feature flags
    enable_epigenetic_analysis: bool = True
    enable_nutrigenomics: bool = True
    enable_pharmacogenomics: bool = True
    enable_sport_genetics: bool = True

    # External service settings
    gemini_timeout: float = 15.0
    supabase_timeout: float = 5.0

    # Monitoring and telemetry
    enable_performance_monitoring: bool = True
    enable_business_metrics: bool = True
    metrics_collection_interval: int = 60

    # Debug settings
    debug_mode: bool = False
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "CodeGeneticConfig":
        """
        Create configuration from environment variables.

        Returns:
            CodeGeneticConfig: Configuration loaded from environment
        """
        return cls(
            # Performance
            max_response_time=float(os.getenv("CODE_MAX_RESPONSE_TIME", "30.0")),
            retry_attempts=int(os.getenv("CODE_RETRY_ATTEMPTS", "3")),
            cache_ttl=int(os.getenv("CODE_CACHE_TTL", "3600")),
            # Personality
            enable_personality_adaptation=os.getenv(
                "CODE_ENABLE_PERSONALITY", "true"
            ).lower()
            == "true",
            # Security
            enable_audit_logging=os.getenv("CODE_ENABLE_AUDIT", "true").lower()
            == "true",
            enable_data_encryption=os.getenv("CODE_ENABLE_ENCRYPTION", "true").lower()
            == "true",
            enable_gdpr_compliance=os.getenv("CODE_ENABLE_GDPR", "true").lower()
            == "true",
            enable_hipaa_compliance=os.getenv("CODE_ENABLE_HIPAA", "true").lower()
            == "true",
            # Genetic analysis
            enable_real_genetic_analysis=os.getenv(
                "CODE_ENABLE_REAL_ANALYSIS", "true"
            ).lower()
            == "true",
            # Feature flags
            enable_epigenetic_analysis=os.getenv(
                "CODE_ENABLE_EPIGENETICS", "true"
            ).lower()
            == "true",
            enable_nutrigenomics=os.getenv("CODE_ENABLE_NUTRIGENOMICS", "true").lower()
            == "true",
            enable_pharmacogenomics=os.getenv(
                "CODE_ENABLE_PHARMACOGENOMICS", "true"
            ).lower()
            == "true",
            enable_sport_genetics=os.getenv(
                "CODE_ENABLE_SPORT_GENETICS", "true"
            ).lower()
            == "true",
            # Debug
            debug_mode=os.getenv("CODE_DEBUG_MODE", "false").lower() == "true",
            log_level=os.getenv("CODE_LOG_LEVEL", "INFO").upper(),
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

        # Security validation for production
        if not self.debug_mode:
            if not self.enable_data_encryption:
                raise ValueError("Data encryption must be enabled in production")
            if not self.enable_audit_logging:
                raise ValueError("Audit logging must be enabled in production")

    @property
    def is_production_ready(self) -> bool:
        """
        Check if configuration is ready for production.

        Returns:
            bool: True if configuration meets production standards
        """
        try:
            self.validate()
            return (
                self.enable_data_encryption
                and self.enable_audit_logging
                and self.enable_gdpr_compliance
                and self.enable_hipaa_compliance
                and not self.debug_mode
            )
        except ValueError:
            return False
