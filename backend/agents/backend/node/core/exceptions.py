"""
Custom exceptions for NODE Systems Integration.
Provides comprehensive error hierarchy for A+ level error handling.
"""

from typing import List, Optional, Any, Dict


class NodeIntegrationError(Exception):
    """
    Base exception for NODE Systems Integration agent.

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


class NodeValidationError(NodeIntegrationError):
    """
    Raised when input validation fails.

    Used for request validation, schema validation,
    and parameter validation errors for system integration.
    """

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        suggestions = [
            "Check your integration request format and try again",
            "Ensure all required fields are provided",
            "Verify data types match expected formats",
            "Validate API endpoints and credentials",
        ]
        if field:
            suggestions.insert(0, f"Check the '{field}' field specifically")

        super().__init__(message, suggestions, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field


class SystemIntegrationError(NodeIntegrationError):
    """
    Raised when system integration processing fails.

    Used for errors in API calls, service connections,
    and integration workflow failures.
    """

    def __init__(self, message: str, integration_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Verify system endpoints are accessible",
            "Check network connectivity and firewall rules",
            "Validate API credentials and permissions",
            "Review integration configuration settings",
        ]

        super().__init__(
            message, suggestions, error_code="SYSTEM_INTEGRATION_ERROR", **kwargs
        )
        self.integration_type = integration_type


class ApiConnectionError(NodeIntegrationError):
    """
    Raised when API connection fails.

    Used for HTTP errors, timeout errors, and authentication
    failures with external APIs.
    """

    def __init__(
        self,
        message: str,
        api_endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        suggestions = [
            "Check API endpoint URL and availability",
            "Verify API credentials and authentication",
            "Review rate limiting and quota restrictions",
            "Check network connectivity to the service",
        ]

        super().__init__(
            message, suggestions, error_code="API_CONNECTION_ERROR", **kwargs
        )
        self.api_endpoint = api_endpoint
        self.status_code = status_code


class CircuitBreakerError(NodeIntegrationError):
    """
    Raised when circuit breaker is open.

    Used when external service calls are blocked due to
    circuit breaker pattern protecting against cascading failures.
    """

    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        suggestions = [
            "Wait for circuit breaker to reset automatically",
            "Check external service health and availability",
            "Review error patterns that triggered circuit breaker",
            "Consider implementing fallback mechanisms",
        ]

        super().__init__(
            message, suggestions, error_code="CIRCUIT_BREAKER_ERROR", **kwargs
        )
        self.service_name = service_name


class DataPipelineError(NodeIntegrationError):
    """
    Raised when data pipeline processing fails.

    Used for errors in data transformation, validation,
    and pipeline stage execution.
    """

    def __init__(self, message: str, pipeline_stage: Optional[str] = None, **kwargs):
        suggestions = [
            "Check data format and schema compatibility",
            "Verify pipeline stage configuration",
            "Review data transformation rules",
            "Check for data quality issues",
        ]

        super().__init__(
            message, suggestions, error_code="DATA_PIPELINE_ERROR", **kwargs
        )
        self.pipeline_stage = pipeline_stage


class InfrastructureAutomationError(NodeIntegrationError):
    """
    Raised when infrastructure automation fails.

    Used for deployment, scaling, and infrastructure
    management operation failures.
    """

    def __init__(self, message: str, automation_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Check infrastructure configuration and permissions",
            "Verify cloud service credentials and quotas",
            "Review automation script and parameters",
            "Check resource availability and constraints",
        ]

        super().__init__(
            message, suggestions, error_code="INFRASTRUCTURE_AUTOMATION_ERROR", **kwargs
        )
        self.automation_type = automation_type


class ExternalServiceError(NodeIntegrationError):
    """
    Raised when external service integration fails.

    Used for third-party service failures, API rate limiting,
    and external service unavailability.
    """

    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        suggestions = [
            "Try again after a short delay",
            "Check service status and availability",
            "Verify service credentials and permissions",
            "Review rate limiting and quota usage",
        ]

        super().__init__(
            message, suggestions, error_code="EXTERNAL_SERVICE_ERROR", **kwargs
        )
        self.service_name = service_name


class PersonalityAdaptationError(NodeIntegrationError):
    """
    Raised when INTJ personality adaptation fails.

    Used for PersonalityAdapter integration failures and
    analytical response adaptation errors.
    """

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Response will use default analytical communication style",
            "Check system integration context completeness",
        ]

        super().__init__(
            message, suggestions, error_code="PERSONALITY_ADAPTATION_ERROR", **kwargs
        )


class IntegrationAuthenticationError(NodeIntegrationError):
    """
    Raised when integration authentication fails.

    Used for API key validation, OAuth failures,
    and service authentication errors.
    """

    def __init__(self, message: str, auth_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Verify API credentials and authentication tokens",
            "Check credential expiration and renewal",
            "Review authentication method and configuration",
            "Contact service provider for authentication issues",
        ]

        super().__init__(
            message, suggestions, error_code="INTEGRATION_AUTH_ERROR", **kwargs
        )
        self.auth_type = auth_type


class IntegrationConfigurationError(NodeIntegrationError):
    """
    Raised when integration configuration is invalid.

    Used when service configurations, endpoint mappings,
    or integration parameters are misconfigured.
    """

    def __init__(self, message: str, config_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Review integration configuration settings",
            "Validate endpoint URLs and service parameters",
            "Check configuration file syntax and format",
            "Verify required configuration fields are present",
        ]

        super().__init__(
            message, suggestions, error_code="INTEGRATION_CONFIG_ERROR", **kwargs
        )
        self.config_type = config_type


class RateLimitExceededError(ExternalServiceError):
    """Specific error for API rate limit violations."""

    def __init__(self, message: str, reset_time: Optional[int] = None, **kwargs):
        suggestions = [
            "Wait for rate limit reset period",
            "Implement exponential backoff retry strategy",
            "Review API usage patterns and optimize calls",
            "Consider upgrading service plan for higher limits",
        ]
        super().__init__(
            message,
            service_name="rate_limited_service",
            error_code="RATE_LIMIT_EXCEEDED",
            **kwargs,
        )
        self.reset_time = reset_time


class WebSocketConnectionError(NodeIntegrationError):
    """Specific error for WebSocket connection failures."""

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Check WebSocket endpoint URL and availability",
            "Verify WebSocket protocol compatibility",
            "Review firewall and proxy settings",
            "Check for connection timeout issues",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="WEBSOCKET_CONNECTION_ERROR",
            **kwargs,
        )


class MessageQueueError(NodeIntegrationError):
    """Specific error for message queue integration failures."""

    def __init__(self, message: str, queue_name: Optional[str] = None, **kwargs):
        suggestions = [
            "Check message queue service availability",
            "Verify queue configuration and permissions",
            "Review message format and serialization",
            "Check queue capacity and message limits",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="MESSAGE_QUEUE_ERROR",
            **kwargs,
        )
        self.queue_name = queue_name


class DatabaseIntegrationError(NodeIntegrationError):
    """Specific error for database integration failures."""

    def __init__(self, message: str, database_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Check database connection and credentials",
            "Verify database schema and table permissions",
            "Review SQL queries and data operations",
            "Check database server availability and performance",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="DATABASE_INTEGRATION_ERROR",
            **kwargs,
        )
        self.database_type = database_type


class CloudServiceIntegrationError(NodeIntegrationError):
    """Specific error for cloud service integration failures."""

    def __init__(self, message: str, cloud_provider: Optional[str] = None, **kwargs):
        suggestions = [
            "Check cloud service credentials and permissions",
            "Verify cloud service configuration and region",
            "Review cloud service quotas and billing status",
            "Check cloud service API availability",
        ]
        super().__init__(
            message,
            suggestions,
            error_code="CLOUD_SERVICE_ERROR",
            **kwargs,
        )
        self.cloud_provider = cloud_provider
