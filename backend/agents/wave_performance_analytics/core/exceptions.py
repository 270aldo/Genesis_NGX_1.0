"""
Domain-specific exceptions for WAVE Performance Analytics Agent.
Handles errors for recovery, analytics, and fusion capabilities.
"""

from typing import Optional, Dict, Any, List


class WaveAnalyticsError(Exception):
    """Base exception for all WAVE Performance Analytics errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


# Recovery-specific exceptions (from WAVE)
class RecoveryError(WaveAnalyticsError):
    """Base exception for recovery-related errors."""

    pass


class InjuryPreventionError(RecoveryError):
    """Raised when injury prevention protocols fail."""

    def __init__(
        self,
        message: str,
        injury_type: Optional[str] = None,
        risk_level: Optional[float] = None,
    ):
        details = {}
        if injury_type:
            details["injury_type"] = injury_type
        if risk_level is not None:
            details["risk_level"] = risk_level
        super().__init__(message, details)


class RehabilitationError(RecoveryError):
    """Raised when rehabilitation protocols encounter issues."""

    def __init__(
        self,
        message: str,
        exercise_type: Optional[str] = None,
        pain_level: Optional[int] = None,
        session_id: Optional[str] = None,
    ):
        details = {}
        if exercise_type:
            details["exercise_type"] = exercise_type
        if pain_level is not None:
            details["pain_level"] = pain_level
        if session_id:
            details["session_id"] = session_id
        super().__init__(message, details)


class SleepOptimizationError(RecoveryError):
    """Raised when sleep optimization encounters issues."""

    def __init__(
        self,
        message: str,
        sleep_metric: Optional[str] = None,
        target_value: Optional[float] = None,
        actual_value: Optional[float] = None,
    ):
        details = {}
        if sleep_metric:
            details["sleep_metric"] = sleep_metric
        if target_value is not None:
            details["target_value"] = target_value
        if actual_value is not None:
            details["actual_value"] = actual_value
        super().__init__(message, details)


class MobilityAssessmentError(RecoveryError):
    """Raised when mobility assessment fails."""

    def __init__(
        self,
        message: str,
        joint_type: Optional[str] = None,
        measurement_error: Optional[str] = None,
    ):
        details = {}
        if joint_type:
            details["joint_type"] = joint_type
        if measurement_error:
            details["measurement_error"] = measurement_error
        super().__init__(message, details)


# Analytics-specific exceptions (from VOLT)
class AnalyticsError(WaveAnalyticsError):
    """Base exception for analytics-related errors."""

    pass


class BiometricAnalysisError(AnalyticsError):
    """Raised when biometric analysis fails."""

    def __init__(
        self,
        message: str,
        metric_name: str,
        value: Any,
        expected_range: Optional[Dict[str, float]] = None,
    ):
        details = {"metric": metric_name, "value": value}
        if expected_range:
            details["expected_range"] = expected_range
        super().__init__(message, details)


class PatternRecognitionError(AnalyticsError):
    """Raised when pattern recognition fails."""

    def __init__(
        self,
        message: str,
        data_points: Optional[int] = None,
        pattern_type: Optional[str] = None,
        confidence: Optional[float] = None,
    ):
        details = {}
        if data_points is not None:
            details["data_points"] = data_points
        if pattern_type:
            details["pattern_type"] = pattern_type
        if confidence is not None:
            details["confidence"] = confidence
        super().__init__(message, details)


class TrendAnalysisError(AnalyticsError):
    """Raised when trend analysis encounters issues."""

    def __init__(
        self,
        message: str,
        metric: Optional[str] = None,
        time_period: Optional[str] = None,
        insufficient_data: bool = False,
    ):
        details = {}
        if metric:
            details["metric"] = metric
        if time_period:
            details["time_period"] = time_period
        if insufficient_data:
            details["insufficient_data"] = insufficient_data
        super().__init__(message, details)


class DataVisualizationError(AnalyticsError):
    """Raised when data visualization fails."""

    def __init__(
        self,
        message: str,
        chart_type: Optional[str] = None,
        data_format: Optional[str] = None,
    ):
        details = {}
        if chart_type:
            details["chart_type"] = chart_type
        if data_format:
            details["data_format"] = data_format
        super().__init__(message, details)


# Fusion-specific exceptions (new capabilities)
class FusionError(WaveAnalyticsError):
    """Base exception for fusion-related errors."""

    pass


class RecoveryAnalyticsFusionError(FusionError):
    """Raised when recovery-analytics fusion fails."""

    def __init__(
        self,
        message: str,
        recovery_component: Optional[str] = None,
        analytics_component: Optional[str] = None,
        fusion_confidence: Optional[float] = None,
    ):
        details = {}
        if recovery_component:
            details["recovery_component"] = recovery_component
        if analytics_component:
            details["analytics_component"] = analytics_component
        if fusion_confidence is not None:
            details["fusion_confidence"] = fusion_confidence
        super().__init__(message, details)


class InjuryPredictionError(FusionError):
    """Raised when injury prediction models fail."""

    def __init__(
        self,
        message: str,
        prediction_horizon: Optional[int] = None,
        risk_factors: Optional[List[str]] = None,
        model_accuracy: Optional[float] = None,
    ):
        details = {}
        if prediction_horizon is not None:
            details["prediction_horizon_days"] = prediction_horizon
        if risk_factors:
            details["risk_factors"] = risk_factors
        if model_accuracy is not None:
            details["model_accuracy"] = model_accuracy
        super().__init__(message, details)


class PerformanceOptimizationError(FusionError):
    """Raised when performance optimization fails."""

    def __init__(
        self,
        message: str,
        optimization_target: Optional[str] = None,
        current_value: Optional[float] = None,
        target_value: Optional[float] = None,
    ):
        details = {}
        if optimization_target:
            details["optimization_target"] = optimization_target
        if current_value is not None:
            details["current_value"] = current_value
        if target_value is not None:
            details["target_value"] = target_value
        super().__init__(message, details)


class HolisticWellnessDashboardError(FusionError):
    """Raised when holistic wellness dashboard creation fails."""

    def __init__(
        self,
        message: str,
        missing_metrics: Optional[List[str]] = None,
        dashboard_type: Optional[str] = None,
    ):
        details = {}
        if missing_metrics:
            details["missing_metrics"] = missing_metrics
        if dashboard_type:
            details["dashboard_type"] = dashboard_type
        super().__init__(message, details)


# Data and integration exceptions
class WearableIntegrationError(WaveAnalyticsError):
    """Raised when wearable device integration fails."""

    def __init__(
        self,
        message: str,
        device_type: str,
        error_type: Optional[str] = None,
        sync_status: Optional[str] = None,
    ):
        details = {"device_type": device_type}
        if error_type:
            details["error_type"] = error_type
        if sync_status:
            details["sync_status"] = sync_status
        super().__init__(message, details)


class DataSyncError(WaveAnalyticsError):
    """Raised when data synchronization fails."""

    def __init__(
        self,
        message: str,
        data_source: str,
        sync_type: Optional[str] = None,
        failed_records: Optional[int] = None,
    ):
        details = {"data_source": data_source}
        if sync_type:
            details["sync_type"] = sync_type
        if failed_records is not None:
            details["failed_records"] = failed_records
        super().__init__(message, details)


class ModelTrainingError(WaveAnalyticsError):
    """Raised when ML model training/retraining fails."""

    def __init__(
        self,
        message: str,
        model_type: str,
        training_data_size: Optional[int] = None,
        validation_accuracy: Optional[float] = None,
    ):
        details = {"model_type": model_type}
        if training_data_size is not None:
            details["training_data_size"] = training_data_size
        if validation_accuracy is not None:
            details["validation_accuracy"] = validation_accuracy
        super().__init__(message, details)


# Privacy and security exceptions
class HealthDataPrivacyError(WaveAnalyticsError):
    """Raised when health data privacy is compromised."""

    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        privacy_violation: Optional[str] = None,
    ):
        details = {}
        if data_type:
            details["data_type"] = data_type
        if privacy_violation:
            details["privacy_violation"] = privacy_violation
        super().__init__(message, details)


class ConsentRequiredError(HealthDataPrivacyError):
    """Raised when user consent is required but not provided."""

    def __init__(
        self, message: str, consent_type: str, analytics_type: Optional[str] = None
    ):
        details = {"consent_type": consent_type}
        if analytics_type:
            details["analytics_type"] = analytics_type
        super().__init__(message, details)


class DataRetentionViolationError(HealthDataPrivacyError):
    """Raised when data retention policies are violated."""

    def __init__(self, message: str, retention_period: int, data_age: int):
        details = {"retention_period_days": retention_period, "data_age_days": data_age}
        super().__init__(message, details)


# Validation exceptions
class RecoveryValidationError(WaveAnalyticsError):
    """Raised when recovery data validation fails."""

    def __init__(
        self,
        message: str,
        field_name: str,
        invalid_value: Any,
        validation_rule: Optional[str] = None,
    ):
        details = {"field_name": field_name, "invalid_value": invalid_value}
        if validation_rule:
            details["validation_rule"] = validation_rule
        super().__init__(message, details)


class AnalyticsValidationError(WaveAnalyticsError):
    """Raised when analytics data validation fails."""

    def __init__(
        self,
        message: str,
        metric_name: str,
        value: Any,
        expected_type: Optional[str] = None,
        valid_range: Optional[Dict] = None,
    ):
        details = {"metric_name": metric_name, "value": value}
        if expected_type:
            details["expected_type"] = expected_type
        if valid_range:
            details["valid_range"] = valid_range
        super().__init__(message, details)


class FusionValidationError(WaveAnalyticsError):
    """Raised when fusion capability validation fails."""

    def __init__(
        self,
        message: str,
        fusion_type: str,
        component_errors: Optional[List[str]] = None,
    ):
        details = {"fusion_type": fusion_type}
        if component_errors:
            details["component_errors"] = component_errors
        super().__init__(message, details)
