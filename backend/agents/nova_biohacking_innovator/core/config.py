"""
NOVA Biohacking Innovator Configuration.
A+ standardized configuration management for biohacking innovation capabilities.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum

from core.logging_config import get_logger

logger = get_logger(__name__)


class BiohackingComplexity(Enum):
    """Levels of biohacking protocol complexity."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERIMENTAL = "experimental"


class ResearchFocus(Enum):
    """Areas of biohacking research focus."""

    LONGEVITY = "longevity"
    COGNITIVE = "cognitive"
    HORMONAL = "hormonal"
    METABOLIC = "metabolic"
    CELLULAR = "cellular"
    NEUROLOGICAL = "neurological"
    PERFORMANCE = "performance"


class PersonalityMode(Enum):
    """NOVA's personality expression modes."""

    SCIENTIFIC_EXPLORER = "scientific_explorer"
    INNOVATION_CATALYST = "innovation_catalyst"
    RESEARCH_SYNTHESIZER = "research_synthesizer"
    EXPERIMENTAL_GUIDE = "experimental_guide"


@dataclass
class NovaConfig:
    """
    Configuration for NOVA Biohacking Innovator Agent.

    Comprehensive configuration for biohacking innovation capabilities,
    research analysis, experimental protocols, and cutting-edge optimization.
    """

    # Agent Identity
    agent_id: str = "nova_biohacking_innovator"
    agent_name: str = "NOVA Biohacking Innovator"
    agent_version: str = "2.0.0-A+"

    # Performance Configuration
    max_response_time: float = 45.0  # Longer for complex biohacking analysis
    default_timeout: float = 35.0
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Biohacking-Specific Configuration
    max_protocols_per_request: int = 5
    min_research_citations: int = 3
    max_research_citations: int = 10
    complexity_level: BiohackingComplexity = BiohackingComplexity.INTERMEDIATE
    research_focus_areas: List[ResearchFocus] = field(
        default_factory=lambda: [
            ResearchFocus.LONGEVITY,
            ResearchFocus.COGNITIVE,
            ResearchFocus.PERFORMANCE,
        ]
    )

    # Safety and Validation
    experimental_protocols_enabled: bool = True
    safety_validation_required: bool = True
    medical_disclaimer_required: bool = True
    supplement_recommendations_enabled: bool = True
    max_supplement_recommendations: int = 8

    # Vision and Analysis Configuration
    enable_wearable_analysis: bool = True
    enable_biomarker_analysis: bool = True
    enable_research_synthesis: bool = True
    max_image_size_mb: float = 10.0
    supported_wearable_devices: List[str] = field(
        default_factory=lambda: [
            "oura",
            "whoop",
            "apple_watch",
            "garmin",
            "fitbit",
            "continuous_glucose_monitor",
            "heart_rate_monitor",
            "sleep_tracker",
            "hrv_monitor",
        ]
    )

    # Personality and Communication
    personality_mode: PersonalityMode = PersonalityMode.SCIENTIFIC_EXPLORER
    innovation_enthusiasm: float = 0.9  # 0.0-1.0 scale
    research_depth: float = 0.8  # 0.0-1.0 scale
    experimental_openness: float = 0.7  # 0.0-1.0 scale
    personality_adaptation_enabled: bool = True

    # Data Management
    enable_audit_logging: bool = True
    data_encryption_enabled: bool = True
    cache_ttl_seconds: int = 1800  # 30 minutes for research data
    max_cache_size: int = 200

    # Research and Protocol Configuration
    research_database_enabled: bool = True
    protocol_validation_enabled: bool = True
    cutting_edge_research_threshold: int = 365  # Research within last year
    peer_review_requirement: bool = True

    # AI Enhancement Settings
    enable_ai_insights: bool = True
    ai_creativity_level: float = 0.8  # For innovative protocols
    ai_accuracy_threshold: float = 0.75
    enable_multimodal_analysis: bool = True

    @classmethod
    def from_environment(cls) -> "NovaConfig":
        """
        Create configuration from environment variables.

        Returns:
            NovaConfig instance with environment-based settings
        """
        try:
            config = cls()

            # Performance settings
            config.max_response_time = float(
                os.getenv("NOVA_MAX_RESPONSE_TIME", config.max_response_time)
            )
            config.default_timeout = float(
                os.getenv("NOVA_DEFAULT_TIMEOUT", config.default_timeout)
            )
            config.retry_attempts = int(
                os.getenv("NOVA_RETRY_ATTEMPTS", config.retry_attempts)
            )

            # Biohacking settings
            config.max_protocols_per_request = int(
                os.getenv("NOVA_MAX_PROTOCOLS", config.max_protocols_per_request)
            )
            config.experimental_protocols_enabled = (
                os.getenv("NOVA_EXPERIMENTAL_ENABLED", "true").lower() == "true"
            )
            config.safety_validation_required = (
                os.getenv("NOVA_SAFETY_VALIDATION", "true").lower() == "true"
            )

            # Complexity level
            complexity_env = os.getenv(
                "NOVA_COMPLEXITY_LEVEL", config.complexity_level.value
            )
            try:
                config.complexity_level = BiohackingComplexity(complexity_env)
            except ValueError:
                logger.warning(
                    f"Invalid complexity level {complexity_env}, using default"
                )

            # Personality settings
            config.innovation_enthusiasm = float(
                os.getenv("NOVA_INNOVATION_ENTHUSIASM", config.innovation_enthusiasm)
            )
            config.research_depth = float(
                os.getenv("NOVA_RESEARCH_DEPTH", config.research_depth)
            )
            config.experimental_openness = float(
                os.getenv("NOVA_EXPERIMENTAL_OPENNESS", config.experimental_openness)
            )

            # Personality mode
            personality_env = os.getenv(
                "NOVA_PERSONALITY_MODE", config.personality_mode.value
            )
            try:
                config.personality_mode = PersonalityMode(personality_env)
            except ValueError:
                logger.warning(
                    f"Invalid personality mode {personality_env}, using default"
                )

            # Vision and analysis settings
            config.enable_wearable_analysis = (
                os.getenv("NOVA_WEARABLE_ANALYSIS", "true").lower() == "true"
            )
            config.enable_biomarker_analysis = (
                os.getenv("NOVA_BIOMARKER_ANALYSIS", "true").lower() == "true"
            )
            config.max_image_size_mb = float(
                os.getenv("NOVA_MAX_IMAGE_SIZE_MB", config.max_image_size_mb)
            )

            # Data management settings
            config.enable_audit_logging = (
                os.getenv("NOVA_AUDIT_LOGGING", "true").lower() == "true"
            )
            config.data_encryption_enabled = (
                os.getenv("NOVA_DATA_ENCRYPTION", "true").lower() == "true"
            )
            config.cache_ttl_seconds = int(
                os.getenv("NOVA_CACHE_TTL_SECONDS", config.cache_ttl_seconds)
            )

            # AI settings
            config.enable_ai_insights = (
                os.getenv("NOVA_AI_INSIGHTS", "true").lower() == "true"
            )
            config.ai_creativity_level = float(
                os.getenv("NOVA_AI_CREATIVITY", config.ai_creativity_level)
            )
            config.ai_accuracy_threshold = float(
                os.getenv("NOVA_AI_ACCURACY_THRESHOLD", config.ai_accuracy_threshold)
            )

            logger.info("NOVA configuration loaded from environment variables")
            return config

        except Exception as e:
            logger.error(f"Error loading NOVA configuration from environment: {str(e)}")
            logger.info("Using default NOVA configuration")
            return cls()

    def get_biohacking_config(self) -> Dict[str, Any]:
        """
        Get biohacking-specific configuration.

        Returns:
            Dict with biohacking protocol and research settings
        """
        return {
            "complexity_level": self.complexity_level.value,
            "research_focus_areas": [area.value for area in self.research_focus_areas],
            "experimental_protocols_enabled": self.experimental_protocols_enabled,
            "safety_validation_required": self.safety_validation_required,
            "max_protocols_per_request": self.max_protocols_per_request,
            "supplement_recommendations_enabled": self.supplement_recommendations_enabled,
            "max_supplement_recommendations": self.max_supplement_recommendations,
            "research_database_enabled": self.research_database_enabled,
            "cutting_edge_research_threshold": self.cutting_edge_research_threshold,
            "peer_review_requirement": self.peer_review_requirement,
        }

    def get_analysis_config(self) -> Dict[str, Any]:
        """
        Get vision and analysis configuration.

        Returns:
            Dict with vision processing and analysis settings
        """
        return {
            "enable_wearable_analysis": self.enable_wearable_analysis,
            "enable_biomarker_analysis": self.enable_biomarker_analysis,
            "enable_research_synthesis": self.enable_research_synthesis,
            "max_image_size_mb": self.max_image_size_mb,
            "supported_wearable_devices": self.supported_wearable_devices,
            "enable_multimodal_analysis": self.enable_multimodal_analysis,
        }

    def get_personality_config(self) -> Dict[str, Any]:
        """
        Get NOVA personality configuration.

        Returns:
            Dict with personality and communication settings
        """
        return {
            "personality_mode": self.personality_mode.value,
            "innovation_enthusiasm": self.innovation_enthusiasm,
            "research_depth": self.research_depth,
            "experimental_openness": self.experimental_openness,
            "personality_adaptation_enabled": self.personality_adaptation_enabled,
            "ai_creativity_level": self.ai_creativity_level,
        }

    def validate_configuration(self) -> bool:
        """
        Validate configuration settings.

        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate numeric ranges
            if not (0.0 <= self.innovation_enthusiasm <= 1.0):
                logger.error("Innovation enthusiasm must be between 0.0 and 1.0")
                return False

            if not (0.0 <= self.research_depth <= 1.0):
                logger.error("Research depth must be between 0.0 and 1.0")
                return False

            if not (0.0 <= self.experimental_openness <= 1.0):
                logger.error("Experimental openness must be between 0.0 and 1.0")
                return False

            if not (0.0 <= self.ai_creativity_level <= 1.0):
                logger.error("AI creativity level must be between 0.0 and 1.0")
                return False

            if not (0.0 <= self.ai_accuracy_threshold <= 1.0):
                logger.error("AI accuracy threshold must be between 0.0 and 1.0")
                return False

            # Validate positive values
            if self.max_response_time <= 0:
                logger.error("Max response time must be positive")
                return False

            if self.max_protocols_per_request <= 0:
                logger.error("Max protocols per request must be positive")
                return False

            if self.max_image_size_mb <= 0:
                logger.error("Max image size must be positive")
                return False

            # Validate required features
            if not self.research_focus_areas:
                logger.error("At least one research focus area must be specified")
                return False

            logger.info("NOVA configuration validation successful")
            return True

        except Exception as e:
            logger.error(f"Configuration validation error: {str(e)}")
            return False
