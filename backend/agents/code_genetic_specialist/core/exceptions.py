"""
Custom exceptions for CODE Genetic Specialist.
Provides comprehensive error hierarchy for A+ level error handling.
"""

from typing import List, Optional, Any, Dict


class CodeGeneticError(Exception):
    """
    Base exception for CODE Genetic Specialist agent.

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


class CodeGeneticValidationError(CodeGeneticError):
    """
    Raised when input validation fails.

    Used for user input validation, schema validation,
    and parameter validation errors.
    """

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        suggestions = [
            "Check your input format and try again",
            "Ensure all required fields are provided",
            "Verify data types match expected formats",
        ]
        if field:
            suggestions.insert(0, f"Check the '{field}' field specifically")

        super().__init__(message, suggestions, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field


class GeneticAnalysisError(CodeGeneticError):
    """
    Raised when genetic analysis processing fails.

    Used for errors in genetic data processing, variant analysis,
    and interpretation failures.
    """

    def __init__(self, message: str, analysis_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Verify genetic data format is supported",
            "Check if genetic profile is complete",
            "Try with a different analysis approach",
        ]

        super().__init__(
            message, suggestions, error_code="GENETIC_ANALYSIS_ERROR", **kwargs
        )
        self.analysis_type = analysis_type


class GeneticDataSecurityError(CodeGeneticError):
    """
    Raised when genetic data security requirements are violated.

    Used for GDPR/HIPAA compliance violations, encryption failures,
    and data access control violations.
    """

    def __init__(self, message: str, compliance_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Ensure proper consent is obtained",
            "Verify data encryption is enabled",
            "Check access permissions for genetic data",
        ]

        super().__init__(
            message, suggestions, error_code="GENETIC_SECURITY_ERROR", **kwargs
        )
        self.compliance_type = compliance_type


class ExternalGeneticServiceError(CodeGeneticError):
    """
    Raised when external genetic database or service fails.

    Used for genetic database connection failures, API timeouts,
    and external service integration errors.
    """

    def __init__(self, message: str, service_name: Optional[str] = None, **kwargs):
        suggestions = [
            "Try again in a few moments",
            "Check your internet connection",
            "Contact support if the issue persists",
        ]

        super().__init__(
            message, suggestions, error_code="EXTERNAL_SERVICE_ERROR", **kwargs
        )
        self.service_name = service_name


class PersonalityAdaptationError(CodeGeneticError):
    """
    Raised when personality adaptation fails.

    Used for PersonalityAdapter integration failures and
    response adaptation errors.
    """

    def __init__(self, message: str, **kwargs):
        suggestions = [
            "Response will use default communication style",
            "Check user profile data completeness",
        ]

        super().__init__(
            message, suggestions, error_code="PERSONALITY_ADAPTATION_ERROR", **kwargs
        )


class GeneticConsentError(CodeGeneticError):
    """
    Raised when genetic data consent is missing or invalid.

    Used for GDPR/HIPAA consent validation and genetic data
    usage authorization failures.
    """

    def __init__(self, message: str, consent_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Provide explicit consent for genetic analysis",
            "Review genetic data usage permissions",
            "Contact support for consent management help",
        ]

        super().__init__(
            message, suggestions, error_code="GENETIC_CONSENT_ERROR", **kwargs
        )
        self.consent_type = consent_type


class GeneticDataNotFoundError(CodeGeneticError):
    """
    Raised when required genetic data is not found.

    Used when genetic profiles, variants, or analysis results
    are missing or inaccessible.
    """

    def __init__(self, message: str, data_type: Optional[str] = None, **kwargs):
        suggestions = [
            "Upload your genetic data first",
            "Verify genetic data processing is complete",
            "Check if genetic profile exists for this user",
        ]

        super().__init__(
            message, suggestions, error_code="GENETIC_DATA_NOT_FOUND", **kwargs
        )
        self.data_type = data_type


class GeneticInterpretationError(CodeGeneticError):
    """
    Raised when genetic variant interpretation fails.

    Used for complex genetic analysis failures, variant
    significance determination errors, and interpretation
    algorithm failures.
    """

    def __init__(self, message: str, variant_id: Optional[str] = None, **kwargs):
        suggestions = [
            "Try with a simplified analysis approach",
            "Check if genetic variant is in supported databases",
            "Contact genetic counselor for complex interpretations",
        ]

        super().__init__(
            message, suggestions, error_code="GENETIC_INTERPRETATION_ERROR", **kwargs
        )
        self.variant_id = variant_id


class NutrigenomicsError(GeneticAnalysisError):
    """Specific error for nutrigenomics analysis failures."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            analysis_type="nutrigenomics",
            error_code="NUTRIGENOMICS_ERROR",
            **kwargs,
        )


class PharmacogenomicsError(GeneticAnalysisError):
    """Specific error for pharmacogenomics analysis failures."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            analysis_type="pharmacogenomics",
            error_code="PHARMACOGENOMICS_ERROR",
            **kwargs,
        )


class SportGeneticsError(GeneticAnalysisError):
    """Specific error for sport genetics analysis failures."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            analysis_type="sport_genetics",
            error_code="SPORT_GENETICS_ERROR",
            **kwargs,
        )


class EpigeneticAnalysisError(GeneticAnalysisError):
    """Specific error for epigenetic analysis failures."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            analysis_type="epigenetics",
            error_code="EPIGENETIC_ANALYSIS_ERROR",
            **kwargs,
        )
