"""
Training-specific exceptions for BLAZE Elite Training Strategist.
Provides detailed error handling for training program generation and athlete optimization.
"""

from typing import Optional, Dict, Any


class BlazeTrainingError(Exception):
    """Base exception for all BLAZE training-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}


class TrainingPlanGenerationError(BlazeTrainingError):
    """Error during training plan generation."""

    pass


class InvalidTrainingParametersError(BlazeTrainingError):
    """Invalid training parameters provided."""

    pass


class AthleteProfileError(BlazeTrainingError):
    """Error with athlete profile data."""

    pass


class PerformanceAnalysisError(BlazeTrainingError):
    """Error during performance data analysis."""

    pass


class PostureDetectionError(BlazeTrainingError):
    """Error during posture/form analysis."""

    pass


class TrainingIntensityError(BlazeTrainingError):
    """Error with training intensity calculations."""

    pass


class ExercisePrescriptionError(BlazeTrainingError):
    """Error during exercise routine prescription."""

    pass


class AdaptiveTrainingError(BlazeTrainingError):
    """Error during adaptive training adjustments."""

    pass


class NutritionIntegrationError(BlazeTrainingError):
    """Error during nutrition integration with training."""

    pass


class BiometricIntegrationError(BlazeTrainingError):
    """Error during biometric data integration."""

    pass


class VoiceCoachingError(BlazeTrainingError):
    """Error during voice coaching functionality."""

    pass


class InjuryRiskAssessmentError(BlazeTrainingError):
    """Error during injury risk assessment."""

    pass


class RecoveryOptimizationError(BlazeTrainingError):
    """Error during recovery protocol optimization."""

    pass


class TrainingProgressTrackingError(BlazeTrainingError):
    """Error during training progress tracking."""

    pass


def create_training_error_response(error: BlazeTrainingError) -> Dict[str, Any]:
    """
    Create standardized error response for training errors.

    Args:
        error: The training error that occurred

    Returns:
        Standardized error response dictionary
    """
    return {
        "error": True,
        "error_type": error.__class__.__name__,
        "error_code": error.error_code,
        "message": str(error),
        "context": error.context,
        "suggestions": _get_error_suggestions(error),
    }


def _get_error_suggestions(error: BlazeTrainingError) -> list:
    """
    Get helpful suggestions based on error type.

    Args:
        error: The training error

    Returns:
        List of helpful suggestions
    """
    suggestions = {
        TrainingPlanGenerationError: [
            "Verify athlete profile data is complete",
            "Check if training goals are realistic",
            "Ensure no conflicting constraints",
        ],
        InvalidTrainingParametersError: [
            "Review provided training parameters",
            "Check parameter ranges and types",
            "Ensure all required parameters are provided",
        ],
        AthleteProfileError: [
            "Complete missing athlete profile fields",
            "Verify athlete data accuracy",
            "Check for data consistency",
        ],
        PerformanceAnalysisError: [
            "Ensure sufficient performance data is available",
            "Check data quality and format",
            "Verify analysis timeframe",
        ],
        PostureDetectionError: [
            "Check image/video quality",
            "Ensure proper lighting and camera angle",
            "Verify exercise is supported for analysis",
        ],
        TrainingIntensityError: [
            "Review athlete fitness level",
            "Check for realistic intensity targets",
            "Ensure proper progression protocols",
        ],
        ExercisePrescriptionError: [
            "Verify exercise database availability",
            "Check equipment constraints",
            "Review exercise modifications needed",
        ],
        AdaptiveTrainingError: [
            "Check biometric feedback quality",
            "Verify adaptation parameters",
            "Review athlete response patterns",
        ],
        NutritionIntegrationError: [
            "Verify nutrition data availability",
            "Check integration settings",
            "Review dietary restrictions",
        ],
        BiometricIntegrationError: [
            "Check device connectivity",
            "Verify data synchronization",
            "Review biometric data quality",
        ],
        VoiceCoachingError: [
            "Check audio system functionality",
            "Verify language settings",
            "Test microphone and speakers",
        ],
        InjuryRiskAssessmentError: [
            "Review movement patterns",
            "Check assessment parameters",
            "Verify risk calculation methods",
        ],
        RecoveryOptimizationError: [
            "Check recovery data availability",
            "Review optimization algorithms",
            "Verify recovery protocols",
        ],
        TrainingProgressTrackingError: [
            "Ensure tracking data is available",
            "Check progress calculation methods",
            "Review tracking timeframes",
        ],
    }

    return suggestions.get(
        type(error),
        [
            "Check system logs for more details",
            "Verify all input parameters",
            "Contact support if issue persists",
        ],
    )
