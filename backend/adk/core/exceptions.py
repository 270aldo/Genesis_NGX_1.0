"""
Exception Classes for NGX ADK
=============================

This module defines custom exceptions used throughout the ADK framework
to provide clear and actionable error messages.
"""

from typing import Optional, Dict, Any


class ADKError(Exception):
    """Base exception for all ADK-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class AgentValidationError(ADKError):
    """Raised when agent input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        if field:
            self.details["field"] = field


class AgentExecutionError(ADKError):
    """Raised when agent execution fails."""
    
    def __init__(self, message: str, agent_id: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="EXECUTION_ERROR", **kwargs)
        if agent_id:
            self.details["agent_id"] = agent_id


class AgentTimeoutError(ADKError):
    """Raised when agent execution times out."""
    
    def __init__(self, message: str, timeout: Optional[int] = None, **kwargs):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)
        if timeout:
            self.details["timeout_seconds"] = timeout


class AgentRateLimitError(ADKError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, error_code="RATE_LIMIT_ERROR", **kwargs)
        if limit:
            self.details["limit"] = limit
        if retry_after:
            self.details["retry_after_seconds"] = retry_after


class AgentConfigurationError(ADKError):
    """Raised when agent configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        if config_key:
            self.details["config_key"] = config_key


class SkillNotFoundError(ADKError):
    """Raised when a requested skill is not found."""
    
    def __init__(self, skill_name: str, agent_id: Optional[str] = None, **kwargs):
        message = f"Skill '{skill_name}' not found"
        if agent_id:
            message += f" in agent '{agent_id}'"
        super().__init__(message, error_code="SKILL_NOT_FOUND", **kwargs)
        self.details["skill_name"] = skill_name
        if agent_id:
            self.details["agent_id"] = agent_id


class SkillExecutionError(ADKError):
    """Raised when skill execution fails."""
    
    def __init__(
        self,
        message: str,
        skill_name: Optional[str] = None,
        agent_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="SKILL_EXECUTION_ERROR", **kwargs)
        if skill_name:
            self.details["skill_name"] = skill_name
        if agent_id:
            self.details["agent_id"] = agent_id


class LLMError(ADKError):
    """Raised when LLM interaction fails."""
    
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="LLM_ERROR", **kwargs)
        if model:
            self.details["model"] = model
        if provider:
            self.details["provider"] = provider


class CacheError(ADKError):
    """Raised when cache operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="CACHE_ERROR", **kwargs)
        if operation:
            self.details["operation"] = operation


class AuthenticationError(ADKError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, error_code="AUTHENTICATION_ERROR", **kwargs)


class AuthorizationError(ADKError):
    """Raised when authorization fails."""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_permission: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="AUTHORIZATION_ERROR", **kwargs)
        if required_permission:
            self.details["required_permission"] = required_permission


class IntegrationError(ADKError):
    """Raised when external integration fails."""
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="INTEGRATION_ERROR", **kwargs)
        if service:
            self.details["service"] = service
        if endpoint:
            self.details["endpoint"] = endpoint


class CircuitBreakerError(ADKError):
    """Raised when circuit breaker is open."""
    
    def __init__(
        self,
        message: str = "Circuit breaker is open",
        service: Optional[str] = None,
        reset_time: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, error_code="CIRCUIT_BREAKER_OPEN", **kwargs)
        if service:
            self.details["service"] = service
        if reset_time:
            self.details["reset_after_seconds"] = reset_time


class RetryExhaustedError(ADKError):
    """Raised when all retry attempts have been exhausted."""
    
    def __init__(
        self,
        message: str,
        attempts: Optional[int] = None,
        last_error: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="RETRY_EXHAUSTED", **kwargs)
        if attempts:
            self.details["attempts"] = attempts
        if last_error:
            self.details["last_error"] = last_error


# Exception handler for converting exceptions to API responses
def handle_adk_error(error: ADKError) -> Dict[str, Any]:
    """Convert ADK error to API response format."""
    return {
        "success": False,
        "error": error.to_dict(),
        "status_code": get_status_code_for_error(error)
    }


def get_status_code_for_error(error: ADKError) -> int:
    """Get appropriate HTTP status code for error type."""
    error_status_map = {
        "VALIDATION_ERROR": 400,
        "AUTHENTICATION_ERROR": 401,
        "AUTHORIZATION_ERROR": 403,
        "SKILL_NOT_FOUND": 404,
        "RATE_LIMIT_ERROR": 429,
        "TIMEOUT_ERROR": 408,
        "CIRCUIT_BREAKER_OPEN": 503,
        "EXECUTION_ERROR": 500,
        "LLM_ERROR": 502,
        "INTEGRATION_ERROR": 502,
        "CONFIGURATION_ERROR": 500,
        "CACHE_ERROR": 500,
        "RETRY_EXHAUSTED": 500,
    }
    
    return error_status_map.get(error.error_code, 500)