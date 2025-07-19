"""
NOVA Biohacking Innovator Exceptions.
Domain-specific exceptions for A+ standardized error handling.
"""

from typing import Dict, Any, Optional


class NovaBaseError(Exception):
    """
    Base exception for NOVA Biohacking Innovator operations.

    All NOVA-specific exceptions inherit from this base class to enable
    structured error handling and appropriate user feedback.
    """

    def __init__(
        self, message: str, error_code: str = None, details: Dict[str, Any] = None
    ):
        self.message = message
        self.error_code = error_code or "NOVA_ERROR"
        self.details = details or {}
        super().__init__(self.message)


# Core Biohacking Exceptions


class BiohackingProtocolError(NovaBaseError):
    """Raised when biohacking protocol generation or validation fails."""

    def __init__(self, message: str, protocol_type: str = None, **kwargs):
        self.protocol_type = protocol_type
        super().__init__(
            message,
            error_code="BIOHACKING_PROTOCOL_ERROR",
            details={"protocol_type": protocol_type, **kwargs},
        )


class LongevityOptimizationError(NovaBaseError):
    """Raised when longevity optimization analysis fails."""

    def __init__(self, message: str, optimization_area: str = None, **kwargs):
        self.optimization_area = optimization_area
        super().__init__(
            message,
            error_code="LONGEVITY_OPTIMIZATION_ERROR",
            details={"optimization_area": optimization_area, **kwargs},
        )


class CognitiveEnhancementError(NovaBaseError):
    """Raised when cognitive enhancement protocol generation fails."""

    def __init__(self, message: str, enhancement_type: str = None, **kwargs):
        self.enhancement_type = enhancement_type
        super().__init__(
            message,
            error_code="COGNITIVE_ENHANCEMENT_ERROR",
            details={"enhancement_type": enhancement_type, **kwargs},
        )


class HormonalOptimizationError(NovaBaseError):
    """Raised when hormonal optimization analysis fails."""

    def __init__(self, message: str, hormone_type: str = None, **kwargs):
        self.hormone_type = hormone_type
        super().__init__(
            message,
            error_code="HORMONAL_OPTIMIZATION_ERROR",
            details={"hormone_type": hormone_type, **kwargs},
        )


# Analysis and Processing Exceptions


class WearableAnalysisError(NovaBaseError):
    """Raised when wearable device data analysis fails."""

    def __init__(self, message: str, device_type: str = None, **kwargs):
        self.device_type = device_type
        super().__init__(
            message,
            error_code="WEARABLE_ANALYSIS_ERROR",
            details={"device_type": device_type, **kwargs},
        )


class BiomarkerAnalysisError(NovaBaseError):
    """Raised when biomarker analysis fails."""

    def __init__(self, message: str, biomarker_type: str = None, **kwargs):
        self.biomarker_type = biomarker_type
        super().__init__(
            message,
            error_code="BIOMARKER_ANALYSIS_ERROR",
            details={"biomarker_type": biomarker_type, **kwargs},
        )


class ResearchSynthesisError(NovaBaseError):
    """Raised when research synthesis and integration fails."""

    def __init__(self, message: str, research_area: str = None, **kwargs):
        self.research_area = research_area
        super().__init__(
            message,
            error_code="RESEARCH_SYNTHESIS_ERROR",
            details={"research_area": research_area, **kwargs},
        )


class ExperimentalProtocolError(NovaBaseError):
    """Raised when experimental protocol generation fails."""

    def __init__(self, message: str, protocol_category: str = None, **kwargs):
        self.protocol_category = protocol_category
        super().__init__(
            message,
            error_code="EXPERIMENTAL_PROTOCOL_ERROR",
            details={"protocol_category": protocol_category, **kwargs},
        )


# Technology and Integration Exceptions


class TechnologyIntegrationError(NovaBaseError):
    """Raised when technology integration analysis fails."""

    def __init__(self, message: str, technology_type: str = None, **kwargs):
        self.technology_type = technology_type
        super().__init__(
            message,
            error_code="TECHNOLOGY_INTEGRATION_ERROR",
            details={"technology_type": technology_type, **kwargs},
        )


class VisionProcessingError(NovaBaseError):
    """Raised when vision processing for biohacking analysis fails."""

    def __init__(self, message: str, processing_type: str = None, **kwargs):
        self.processing_type = processing_type
        super().__init__(
            message,
            error_code="VISION_PROCESSING_ERROR",
            details={"processing_type": processing_type, **kwargs},
        )


class MultimodalAnalysisError(NovaBaseError):
    """Raised when multimodal data analysis fails."""

    def __init__(self, message: str, modality_type: str = None, **kwargs):
        self.modality_type = modality_type
        super().__init__(
            message,
            error_code="MULTIMODAL_ANALYSIS_ERROR",
            details={"modality_type": modality_type, **kwargs},
        )


# Safety and Validation Exceptions


class SafetyValidationError(NovaBaseError):
    """Raised when safety validation of protocols fails."""

    def __init__(self, message: str, validation_type: str = None, **kwargs):
        self.validation_type = validation_type
        super().__init__(
            message,
            error_code="SAFETY_VALIDATION_ERROR",
            details={"validation_type": validation_type, **kwargs},
        )


class SupplementRecommendationError(NovaBaseError):
    """Raised when supplement recommendation generation fails."""

    def __init__(self, message: str, supplement_category: str = None, **kwargs):
        self.supplement_category = supplement_category
        super().__init__(
            message,
            error_code="SUPPLEMENT_RECOMMENDATION_ERROR",
            details={"supplement_category": supplement_category, **kwargs},
        )


class PersonalityAdaptationError(NovaBaseError):
    """Raised when NOVA personality adaptation fails."""

    def __init__(self, message: str, adaptation_context: str = None, **kwargs):
        self.adaptation_context = adaptation_context
        super().__init__(
            message,
            error_code="PERSONALITY_ADAPTATION_ERROR",
            details={"adaptation_context": adaptation_context, **kwargs},
        )


# Data and Configuration Exceptions


class BiohackingDataError(NovaBaseError):
    """Raised when biohacking data processing fails."""

    def __init__(self, message: str, data_type: str = None, **kwargs):
        self.data_type = data_type
        super().__init__(
            message,
            error_code="BIOHACKING_DATA_ERROR",
            details={"data_type": data_type, **kwargs},
        )


class ConfigurationError(NovaBaseError):
    """Raised when NOVA configuration is invalid."""

    def __init__(self, message: str, config_field: str = None, **kwargs):
        self.config_field = config_field
        super().__init__(
            message,
            error_code="CONFIGURATION_ERROR",
            details={"config_field": config_field, **kwargs},
        )


def handle_nova_exception(func):
    """
    Decorator for handling NOVA-specific exceptions with appropriate logging and user feedback.

    This decorator catches NOVA exceptions and converts them to user-friendly responses
    while preserving technical details for logging and debugging.
    """
    from functools import wraps
    from core.logging_config import get_logger

    logger = get_logger(__name__)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NovaBaseError as e:
            logger.error(
                f"NOVA error in {func.__name__}: {e.message}",
                extra={
                    "error_code": e.error_code,
                    "details": e.details,
                    "function": func.__name__,
                },
            )

            # Return user-friendly error response
            return {
                "success": False,
                "error": {
                    "type": e.__class__.__name__,
                    "code": e.error_code,
                    "message": e.message,
                    "user_message": _get_user_friendly_message(e),
                },
                "nova_support": "🔬 Don't worry! Scientific exploration involves experimentation. Let's try a different approach to your biohacking journey! 🚀",
            }
        except Exception as e:
            logger.error(
                f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True
            )

            return {
                "success": False,
                "error": {
                    "type": "UnexpectedError",
                    "code": "NOVA_UNEXPECTED_ERROR",
                    "message": "An unexpected error occurred during biohacking analysis",
                    "user_message": "Something unexpected happened during analysis. Let's explore a different approach!",
                },
                "nova_support": "💡 Innovation requires experimentation! I'm here to help you find the perfect biohacking solution! ✨",
            }

    return wrapper


def _get_user_friendly_message(error: NovaBaseError) -> str:
    """
    Convert technical errors to user-friendly messages with NOVA's innovative personality.

    Args:
        error: The NOVA-specific error that occurred

    Returns:
        User-friendly message with encouraging tone
    """
    if isinstance(error, BiohackingProtocolError):
        return "Let's explore a different biohacking approach! There are so many innovative protocols we can try together! 🔬"

    elif isinstance(error, LongevityOptimizationError):
        return "Longevity optimization is a fascinating field! Let me help you discover cutting-edge strategies for healthy aging! ⏳"

    elif isinstance(error, CognitiveEnhancementError):
        return "Cognitive enhancement is an exciting frontier! Let's find the perfect protocol to boost your mental performance! 🧠"

    elif isinstance(error, HormonalOptimizationError):
        return "Hormonal optimization is complex but incredibly rewarding! Let's explore evidence-based approaches together! ⚖️"

    elif isinstance(error, WearableAnalysisError):
        return "Your wearable data contains valuable insights! Let me try a different analysis approach to unlock its potential! 📱"

    elif isinstance(error, BiomarkerAnalysisError):
        return "Biomarker analysis reveals so much about optimization opportunities! Let's explore your results from a new angle! 🧪"

    elif isinstance(error, ResearchSynthesisError):
        return "The latest research in this area is incredibly exciting! Let me synthesize the findings differently for you! 📚"

    elif isinstance(error, TechnologyIntegrationError):
        return "Technology integration opens amazing possibilities! Let's find the perfect tech solution for your goals! 💻"

    elif isinstance(error, SafetyValidationError):
        return "Safety is crucial in biohacking! Let me help you find protocols that are both innovative and safe! 🛡️"

    else:
        return "Innovation involves experimentation! Let's try a different approach to achieve your biohacking goals! 🚀"
