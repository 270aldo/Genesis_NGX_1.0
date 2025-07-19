"""
Centralized Exception Hierarchy for NGX Agents
==============================================

This module consolidates all exceptions used across NGX agents,
eliminating duplication and providing a consistent error handling structure.
"""

from typing import Optional, Dict, Any


# ==================== Base Exceptions ====================

class NGXBaseException(Exception):
    """Base exception for all NGX-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AgentError(NGXBaseException):
    """Base exception for agent-specific errors."""
    pass


class ValidationError(NGXBaseException):
    """Raised when data validation fails."""
    pass


class IntegrationError(NGXBaseException):
    """Base exception for external integration errors."""
    pass


# ==================== Agent-Specific Exceptions ====================

class OrchestratorError(AgentError):
    """Errors specific to the Orchestrator agent."""
    pass


class TrainingError(AgentError):
    """Errors specific to training-related operations (BLAZE)."""
    pass


class NutritionError(AgentError):
    """Errors specific to nutrition-related operations (SAGE)."""
    pass


class WellnessError(AgentError):
    """Errors specific to wellness operations (LUNA)."""
    pass


class MotivationError(AgentError):
    """Errors specific to motivation operations (SPARK)."""
    pass


class ProgressTrackingError(AgentError):
    """Errors specific to progress tracking (STELLA)."""
    pass


class AnalyticsError(AgentError):
    """Errors specific to analytics operations (WAVE)."""
    pass


class BiohackingError(AgentError):
    """Errors specific to biohacking operations (NOVA)."""
    pass


class GeneticError(AgentError):
    """Errors specific to genetic analysis (CODE)."""
    pass


# ==================== Service Exceptions ====================

class DataServiceError(NGXBaseException):
    """Errors in data service operations."""
    pass


class SecurityServiceError(NGXBaseException):
    """Errors in security service operations."""
    pass


class CacheError(NGXBaseException):
    """Errors in caching operations."""
    pass


# ==================== Integration Exceptions ====================

class WearableIntegrationError(IntegrationError):
    """Errors integrating with wearable devices."""
    pass


class APIIntegrationError(IntegrationError):
    """Errors integrating with external APIs."""
    pass


class WebhookError(IntegrationError):
    """Errors processing webhooks."""
    pass


# ==================== Authentication & Authorization ====================

class AuthenticationError(NGXBaseException):
    """Authentication-related errors."""
    pass


class AuthorizationError(NGXBaseException):
    """Authorization-related errors."""
    pass


class TokenError(AuthenticationError):
    """Token validation errors."""
    pass


# ==================== Resource Exceptions ====================

class ResourceNotFoundError(NGXBaseException):
    """Requested resource not found."""
    pass


class ResourceConflictError(NGXBaseException):
    """Resource conflict (e.g., duplicate entry)."""
    pass


class QuotaExceededError(NGXBaseException):
    """Usage quota exceeded."""
    pass


class RateLimitError(NGXBaseException):
    """Rate limit exceeded."""
    pass


# ==================== Compliance Exceptions ====================

class ComplianceError(NGXBaseException):
    """Base exception for compliance-related errors."""
    pass


class HIPAAComplianceError(ComplianceError):
    """HIPAA compliance violation."""
    pass


class GDPRComplianceError(ComplianceError):
    """GDPR compliance violation."""
    pass


# ==================== Circuit Breaker Exceptions ====================

class CircuitBreakerError(NGXBaseException):
    """Circuit breaker is open."""
    pass


class CircuitBreakerTimeoutError(CircuitBreakerError):
    """Operation timed out in circuit breaker."""
    pass


# ==================== Helper Functions ====================

def create_error_response(
    error: NGXBaseException,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response from exception.
    
    Args:
        error: The exception instance
        request_id: Optional request ID for tracking
        
    Returns:
        Dict with error details
    """
    return {
        "success": False,
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
            "details": error.details
        },
        "request_id": request_id,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }


# ==================== Exception Mapping ====================

# Map old exception names to new ones for backwards compatibility
EXCEPTION_MAPPING = {
    # BLAZE exceptions
    "BlazeTrainingError": TrainingError,
    "TrainingPlanGenerationError": TrainingError,
    "TrainingProgressTrackingError": ProgressTrackingError,
    
    # SAGE exceptions  
    "SageNutritionError": NutritionError,
    "NutritionPlanGenerationError": NutritionError,
    "NutritionAnalysisError": NutritionError,
    
    # LUNA exceptions
    "LunaWellnessError": WellnessError,
    "FemaleWellnessError": WellnessError,
    
    # SPARK exceptions
    "SparkMotivationError": MotivationError,
    "MotivationGenerationError": MotivationError,
    
    # STELLA exceptions
    "StellaProgressError": ProgressTrackingError,
    "ProgressAnalysisError": ProgressTrackingError,
    
    # WAVE exceptions
    "WaveAnalyticsError": AnalyticsError,
    "PerformanceAnalysisError": AnalyticsError,
    
    # NOVA exceptions
    "NovaBiohackingError": BiohackingError,
    "BiohackingRecommendationError": BiohackingError,
    
    # CODE exceptions
    "CodeGeneticError": GeneticError,
    "GeneticAnalysisError": GeneticError,
}


def get_exception_class(old_name: str) -> type:
    """
    Get new exception class from old name for backwards compatibility.
    
    Args:
        old_name: Old exception class name
        
    Returns:
        New exception class
    """
    return EXCEPTION_MAPPING.get(old_name, NGXBaseException)