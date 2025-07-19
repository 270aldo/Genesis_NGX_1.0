"""
Custom exceptions for LUNA Female Wellness Specialist.
Provides comprehensive error hierarchy for A+ level error handling.
"""

from typing import List, Optional, Any, Dict


class LunaWellnessError(Exception):
    """
    Base exception for LUNA Female Wellness Specialist agent.

    All agent-specific errors inherit from this base class to enable
    comprehensive error handling and user-friendly error messages.
    """

    def __init__(
        self,
        message: str,
        suggestions: Optional[List[str]] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.suggestions = suggestions or []
        self.error_code = error_code
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "error_code": self.error_code,
            "suggestions": self.suggestions,
            "context": self.context,
        }


class LunaValidationError(LunaWellnessError):
    """
    Raised when input validation fails.

    Used for user input validation, schema validation,
    and parameter validation errors for female wellness data.
    """

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        suggestions = [
            "Check your wellness data format and try again",
            "Ensure all required health fields are provided",
            "Verify data types match expected formats",
        ]
        if field:
            suggestions.insert(0, f"Check the '{field}' field specifically")

        super().__init__(message, suggestions, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field


class MenstrualCycleAnalysisError(LunaWellnessError):
    """
    Raised when menstrual cycle analysis processing fails.

    Used for errors in cycle data processing, pattern analysis,
    and hormonal interpretation failures.
    """

    def __init__(self, message: str, cycle_phase: Optional[str] = None, **kwargs):
        suggestions = [
            "Verify menstrual cycle data format is complete",
            "Check if cycle tracking data spans sufficient time",
            "Try with a different analysis timeframe",
        ]

        super().__init__(
            message, suggestions, error_code="MENSTRUAL_ANALYSIS_ERROR", **kwargs
        )
        self.cycle_phase = cycle_phase


class HormonalDataSecurityError(LunaWellnessError):
    """
    Raised when hormonal/health data security requirements are violated.

    Used for GDPR/HIPAA compliance violations, encryption failures,
    and health data access control violations.
    """

    def __init__(self, message: str, compliance_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Ensure proper consent is obtained for health data",
            "Verify data encryption is enabled for sensitive data",
            "Check access permissions for hormonal health data",
        ]

        super().__init__(
            message, suggestions, error_code="HORMONAL_SECURITY_ERROR", **kwargs
        )
        self.compliance_type = compliance_type


class ExternalWellnessServiceError(LunaWellnessError):
    """
    Raised when external wellness database or service fails.

    Used for health API connection failures, wearable device timeouts,
    and external wellness service integration errors.
    """

    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        suggestions = [
            "Try again in a few moments",
            "Check your internet connection",
            "Verify wearable device connectivity",
            "Contact support if the issue persists",
        ]

        super().__init__(
            message, suggestions, error_code="EXTERNAL_SERVICE_ERROR", **kwargs
        )
        self.service_name = service_name


class PersonalityAdaptationError(LunaWellnessError):
    """
    Raised when ENFJ personality adaptation fails.

    Used for PersonalityAdapter integration failures and
    maternal/empathetic response adaptation errors.
    """

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Response will use default maternal communication style",
            "Check user wellness profile data completeness",
        ]

        super().__init__(
            message, suggestions, error_code="PERSONALITY_ADAPTATION_ERROR", **kwargs
        )


class WellnessConsentError(LunaWellnessError):
    """
    Raised when health data consent is missing or invalid.

    Used for GDPR/HIPAA consent validation and health data
    usage authorization failures.
    """

    def __init__(self, message: str, consent_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Provide explicit consent for health data analysis",
            "Review wellness data usage permissions",
            "Contact support for consent management help",
        ]

        super().__init__(
            message, suggestions, error_code="WELLNESS_CONSENT_ERROR", **kwargs
        )
        self.consent_type = consent_type


class WellnessDataNotFoundError(LunaWellnessError):
    """
    Raised when required wellness data is not found.

    Used when health profiles, cycle data, or analysis results
    are missing or inaccessible.
    """

    def __init__(self, message: str, data_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Upload your wellness data first",
            "Verify health data tracking is active",
            "Check if wellness profile exists for this user",
        ]

        super().__init__(
            message, suggestions, error_code="WELLNESS_DATA_NOT_FOUND", **kwargs
        )
        self.data_type = data_type


class HormonalInterpretationError(LunaWellnessError):
    """
    Raised when hormonal pattern interpretation fails.

    Used for complex hormonal analysis failures, cycle pattern
    determination errors, and interpretation algorithm failures.
    """

    def __init__(self, message: str, hormone_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Try with a simplified analysis approach",
            "Check if hormonal data spans sufficient time",
            "Contact healthcare provider for complex interpretations",
        ]

        super().__init__(
            message, suggestions, error_code="HORMONAL_INTERPRETATION_ERROR", **kwargs
        )
        self.hormone_type = hormone_type


class CycleBasedTrainingError(LunaWellnessError):
    """Specific error for cycle-based training plan failures."""

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Verify menstrual cycle data is available",
            "Check if fitness goals are clearly defined",
            "Try with adjusted training parameters",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="CYCLE_TRAINING_ERROR",
            **kwargs,
        )


class HormonalNutritionError(LunaWellnessError):
    """Specific error for hormonal nutrition analysis failures."""

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Verify hormonal cycle phase data is available",
            "Check if dietary preferences are specified",
            "Try with simplified nutrition recommendations",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="HORMONAL_NUTRITION_ERROR",
            **kwargs,
        )


class MenopauseManagementError(LunaWellnessError):
    """Specific error for menopause management failures."""

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Verify menopause stage information is provided",
            "Check if symptom tracking data is available",
            "Contact healthcare provider for complex management",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="MENOPAUSE_MANAGEMENT_ERROR",
            **kwargs,
        )


class BoneHealthAssessmentError(LunaWellnessError):
    """Specific error for bone health assessment failures."""

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Verify age and hormonal status are provided",
            "Check if lifestyle factors are documented",
            "Consider DEXA scan data if available",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="BONE_HEALTH_ERROR",
            **kwargs,
        )


class EmotionalWellnessError(LunaWellnessError):
    """Specific error for emotional wellness support failures."""

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Verify emotional state data is provided",
            "Check if stress factors are identified",
            "Consider professional counseling for complex issues",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="EMOTIONAL_WELLNESS_ERROR",
            **kwargs,
        )


class VoiceSynthesisError(LunaWellnessError):
    """Specific error for ElevenLabs voice synthesis failures."""

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Response will be provided in text format",
            "Check ElevenLabs API connectivity",
            "Verify voice model availability",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="VOICE_SYNTHESIS_ERROR",
            **kwargs,
        )
