"""
Domain-specific exceptions for SPARK Motivation Behavior Coach.
Provides specialized error handling for motivation and behavioral change operations.
"""

from typing import Optional, Dict, Any


class SparkBaseError(Exception):
    """Base exception for all SPARK-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# Motivation-specific exceptions
class MotivationAnalysisError(SparkBaseError):
    """Raised when motivation analysis fails."""

    pass


class MotivationStrategyError(SparkBaseError):
    """Raised when motivation strategy generation or application fails."""

    pass


class MotivationAssessmentError(SparkBaseError):
    """Raised when motivation assessment cannot be completed."""

    pass


class MotivationPredictionError(SparkBaseError):
    """Raised when motivation prediction models fail."""

    pass


# Behavior change exceptions
class BehaviorAnalysisError(SparkBaseError):
    """Raised when behavior pattern analysis fails."""

    pass


class BehaviorChangeError(SparkBaseError):
    """Raised when behavior change interventions fail."""

    pass


class BehaviorTrackingError(SparkBaseError):
    """Raised when behavior tracking operations fail."""

    pass


class BehaviorModelError(SparkBaseError):
    """Raised when behavior change models encounter errors."""

    pass


# Habit formation exceptions
class HabitFormationError(SparkBaseError):
    """Raised when habit formation processes fail."""

    pass


class HabitAnalysisError(SparkBaseError):
    """Raised when habit pattern analysis fails."""

    pass


class HabitTrackingError(SparkBaseError):
    """Raised when habit tracking operations fail."""

    pass


class HabitReinforcementError(SparkBaseError):
    """Raised when habit reinforcement strategies fail."""

    pass


# Goal setting exceptions
class GoalSettingError(SparkBaseError):
    """Raised when goal setting processes fail."""

    pass


class GoalValidationError(SparkBaseError):
    """Raised when goal validation fails."""

    pass


class GoalTrackingError(SparkBaseError):
    """Raised when goal tracking operations fail."""

    pass


class GoalAchievementError(SparkBaseError):
    """Raised when goal achievement assessment fails."""

    pass


# Obstacle management exceptions
class ObstacleIdentificationError(SparkBaseError):
    """Raised when obstacle identification fails."""

    pass


class ObstacleAnalysisError(SparkBaseError):
    """Raised when obstacle analysis processes fail."""

    pass


class ObstacleSolutionError(SparkBaseError):
    """Raised when obstacle solution generation fails."""

    pass


class ObstacleManagementError(SparkBaseError):
    """Raised when obstacle management strategies fail."""

    pass


# Coaching and intervention exceptions
class CoachingError(SparkBaseError):
    """Raised when coaching interventions fail."""

    pass


class InterventionError(SparkBaseError):
    """Raised when behavioral interventions fail."""

    pass


class PersonalizationError(SparkBaseError):
    """Raised when personalization algorithms fail."""

    pass


class CoachingStyleError(SparkBaseError):
    """Raised when coaching style adaptation fails."""

    pass


# Data and validation exceptions
class BehavioralDataError(SparkBaseError):
    """Raised when behavioral data operations fail."""

    pass


class DataValidationError(SparkBaseError):
    """Raised when input data validation fails."""

    pass


class DataIntegrityError(SparkBaseError):
    """Raised when data integrity checks fail."""

    pass


# AI and ML exceptions
class AIAnalysisError(SparkBaseError):
    """Raised when AI-powered analysis fails."""

    pass


class ModelPredictionError(SparkBaseError):
    """Raised when ML model predictions fail."""

    pass


class PatternRecognitionError(SparkBaseError):
    """Raised when pattern recognition algorithms fail."""

    pass


# Integration and external service exceptions
class ExternalServiceError(SparkBaseError):
    """Raised when external service integrations fail."""

    pass


class DatabaseOperationError(SparkBaseError):
    """Raised when database operations fail."""

    pass


class CacheOperationError(SparkBaseError):
    """Raised when cache operations fail."""

    pass


# Security and compliance exceptions
class SecurityValidationError(SparkBaseError):
    """Raised when security validation fails."""

    pass


class ComplianceError(SparkBaseError):
    """Raised when compliance requirements are not met."""

    pass


class AuditLoggingError(SparkBaseError):
    """Raised when audit logging operations fail."""

    pass


# Configuration and initialization exceptions
class ConfigurationError(SparkBaseError):
    """Raised when configuration is invalid or missing."""

    pass


class InitializationError(SparkBaseError):
    """Raised when agent initialization fails."""

    pass


class DependencyError(SparkBaseError):
    """Raised when dependency injection or validation fails."""

    pass


def create_error_response(
    error: SparkBaseError, include_details: bool = False
) -> Dict[str, Any]:
    """
    Create standardized error response from SPARK exception.

    Args:
        error: SPARK exception to convert
        include_details: Whether to include detailed error information

    Returns:
        Dict containing standardized error response
    """
    response = {
        "success": False,
        "error_type": error.__class__.__name__,
        "error_code": error.error_code,
        "message": error.message,
    }

    if include_details and error.details:
        response["details"] = error.details

    return response


def handle_spark_exception(func):
    """
    Decorator to handle SPARK exceptions and return standardized responses.

    Args:
        func: Function to wrap with exception handling

    Returns:
        Wrapped function with exception handling
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SparkBaseError as e:
            return create_error_response(e, include_details=True)
        except Exception as e:
            # Convert unexpected exceptions to SPARK exceptions
            spark_error = SparkBaseError(
                message=f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                details={"original_error": str(e), "function": func.__name__},
            )
            return create_error_response(spark_error, include_details=True)

    return wrapper
