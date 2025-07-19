"""
STELLA Progress Tracker Exceptions.
Comprehensive exception handling for A+ architecture with progress tracking specific errors.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import traceback
import functools


class StellaBaseError(Exception):
    """
    Base exception for all STELLA Progress Tracker errors.
    Provides structured error handling with metadata support.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base STELLA error.

        Args:
            message: Human-readable error message
            error_code: Specific error code for categorization
            details: Additional error context and metadata
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        self.stack_trace = traceback.format_exc()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary for serialization.

        Returns:
            Dict representation of the error
        """
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "stack_trace": self.stack_trace,
        }

    def __str__(self) -> str:
        return self.message


# Progress Analysis Errors
class ProgressAnalysisError(StellaBaseError):
    """Error during progress data analysis."""

    pass


class ProgressDataError(StellaBaseError):
    """Error with progress data format or content."""

    pass


class ProgressCalculationError(StellaBaseError):
    """Error during progress calculations or metrics."""

    pass


# Milestone and Achievement Errors
class MilestoneTrackingError(StellaBaseError):
    """Error during milestone tracking or detection."""

    pass


class AchievementProcessingError(StellaBaseError):
    """Error during achievement processing or recognition."""

    pass


class MilestoneValidationError(StellaBaseError):
    """Error validating milestone data or criteria."""

    pass


# Visualization Errors
class VisualizationError(StellaBaseError):
    """Error during chart or visualization generation."""

    pass


class ChartGenerationError(StellaBaseError):
    """Error generating charts or graphs."""

    pass


class InfographicError(StellaBaseError):
    """Error creating infographics or visual reports."""

    pass


# Comparison and Analysis Errors
class ComparisonError(StellaBaseError):
    """Error during progress comparison between periods."""

    pass


class PeriodAnalysisError(StellaBaseError):
    """Error analyzing specific time periods."""

    pass


class TrendAnalysisError(StellaBaseError):
    """Error during trend analysis or prediction."""

    pass


# Vision and Image Processing Errors
class VisionProcessingError(StellaBaseError):
    """Error during image or vision processing."""

    pass


class ImageAnalysisError(StellaBaseError):
    """Error analyzing images for progress tracking."""

    pass


class BodyMeasurementError(StellaBaseError):
    """Error extracting body measurements from images."""

    pass


class FormAnalysisError(StellaBaseError):
    """Error analyzing physical form or technique."""

    pass


# Data Management Errors
class ProgressDataStorageError(StellaBaseError):
    """Error storing or retrieving progress data."""

    pass


class DataValidationError(StellaBaseError):
    """Error validating progress data format or content."""

    pass


class DataCorruptionError(StellaBaseError):
    """Error due to corrupted or invalid data."""

    pass


# AI and Processing Errors
class StellaAIError(StellaBaseError):
    """Error during AI processing or analysis."""

    pass


class PersonalityAdaptationError(StellaBaseError):
    """Error during STELLA personality adaptation."""

    pass


class AnalysisTimeoutError(StellaBaseError):
    """Error due to analysis timeout."""

    pass


# Integration and External Service Errors
class ExternalServiceError(StellaBaseError):
    """Error communicating with external services."""

    pass


class FitnessTrackerError(StellaBaseError):
    """Error integrating with fitness tracking services."""

    pass


class StorageServiceError(StellaBaseError):
    """Error with cloud storage services."""

    pass


# Configuration and Setup Errors
class StellaConfigurationError(StellaBaseError):
    """Error in STELLA configuration or setup."""

    pass


class DependencyError(StellaBaseError):
    """Error with required dependencies or services."""

    pass


class InitializationError(StellaBaseError):
    """Error during STELLA agent initialization."""

    pass


# Security and Privacy Errors
class SecurityError(StellaBaseError):
    """Error related to security or privacy."""

    pass


class DataPrivacyError(StellaBaseError):
    """Error related to data privacy or compliance."""

    pass


class AccessControlError(StellaBaseError):
    """Error related to access control or permissions."""

    pass


def handle_stella_exception(func):
    """
    Decorator for handling STELLA-specific exceptions.
    Provides consistent error handling and logging across the system.

    Args:
        func: Function to decorate

    Returns:
        Decorated function with error handling
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except StellaBaseError:
            # Re-raise STELLA exceptions as-is
            raise
        except Exception as e:
            # Convert other exceptions to STELLA base error
            raise StellaBaseError(
                message=f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                details={
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "original_error": str(e),
                    "error_type": type(e).__name__,
                },
            )

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except StellaBaseError:
            # Re-raise STELLA exceptions as-is
            raise
        except Exception as e:
            # Convert other exceptions to STELLA base error
            raise StellaBaseError(
                message=f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                details={
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "original_error": str(e),
                    "error_type": type(e).__name__,
                },
            )

    # Return appropriate wrapper based on function type
    if hasattr(func, "__call__"):
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return func


def create_error_response(
    error: StellaBaseError, request_id: str = None
) -> Dict[str, Any]:
    """
    Create standardized error response dictionary.

    Args:
        error: STELLA error instance
        request_id: Optional request identifier

    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "error": error.to_dict(),
        "agent_info": {
            "agent_id": "stella_progress_tracker",
            "agent_name": "STELLA Progress Tracker",
            "error_handled": True,
        },
    }

    if request_id:
        response["request_id"] = request_id

    # Add recovery suggestions based on error type
    recovery_suggestions = get_recovery_suggestions(error)
    if recovery_suggestions:
        response["recovery_suggestions"] = recovery_suggestions

    return response


def get_recovery_suggestions(error: StellaBaseError) -> list:
    """
    Get recovery suggestions based on error type.

    Args:
        error: STELLA error instance

    Returns:
        List of recovery suggestions
    """
    error_type = type(error).__name__

    suggestions_map = {
        "ProgressAnalysisError": [
            "Check if progress data is properly formatted",
            "Ensure sufficient data points for analysis",
            "Verify time range parameters are valid",
        ],
        "VisualizationError": [
            "Verify chart parameters are within acceptable ranges",
            "Check if data contains valid numeric values",
            "Try a different visualization type",
        ],
        "VisionProcessingError": [
            "Ensure image format is supported (JPG, PNG, WebP)",
            "Check image size is under the maximum limit",
            "Verify image is not corrupted",
        ],
        "MilestoneTrackingError": [
            "Review milestone criteria and thresholds",
            "Check if baseline data exists for comparison",
            "Ensure milestone type is supported",
        ],
        "StellaAIError": [
            "Retry the request after a brief delay",
            "Check AI service availability",
            "Verify input data meets AI processing requirements",
        ],
        "DataValidationError": [
            "Review data format requirements",
            "Check for missing required fields",
            "Ensure data types match expected formats",
        ],
        "ExternalServiceError": [
            "Check internet connectivity",
            "Verify service credentials are valid",
            "Try again later if service is temporarily unavailable",
        ],
    }

    return suggestions_map.get(
        error_type,
        [
            "Please try your request again",
            "Check if all required parameters are provided",
            "Contact support if the problem persists",
        ],
    )


# Export all exception classes
__all__ = [
    # Base error
    "StellaBaseError",
    # Progress analysis errors
    "ProgressAnalysisError",
    "ProgressDataError",
    "ProgressCalculationError",
    # Milestone and achievement errors
    "MilestoneTrackingError",
    "AchievementProcessingError",
    "MilestoneValidationError",
    # Visualization errors
    "VisualizationError",
    "ChartGenerationError",
    "InfographicError",
    # Comparison and analysis errors
    "ComparisonError",
    "PeriodAnalysisError",
    "TrendAnalysisError",
    # Vision and image processing errors
    "VisionProcessingError",
    "ImageAnalysisError",
    "BodyMeasurementError",
    "FormAnalysisError",
    # Data management errors
    "ProgressDataStorageError",
    "DataValidationError",
    "DataCorruptionError",
    # AI and processing errors
    "StellaAIError",
    "PersonalityAdaptationError",
    "AnalysisTimeoutError",
    # Integration and external service errors
    "ExternalServiceError",
    "FitnessTrackerError",
    "StorageServiceError",
    # Configuration and setup errors
    "StellaConfigurationError",
    "DependencyError",
    "InitializationError",
    # Security and privacy errors
    "SecurityError",
    "DataPrivacyError",
    "AccessControlError",
    # Utility functions
    "handle_stella_exception",
    "create_error_response",
    "get_recovery_suggestions",
]
