"""
Domain-specific exceptions for Precision Nutrition Architect Agent.
Provides comprehensive error handling for nutrition-related operations.
"""

from typing import Optional, Dict, Any


class NutritionError(Exception):
    """Base exception for all nutrition-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class MealPlanningError(NutritionError):
    """Raised when meal planning operations fail."""

    pass


class CalorieCalculationError(MealPlanningError):
    """Raised when calorie calculations are invalid."""

    def __init__(
        self,
        message: str,
        target_calories: Optional[float] = None,
        actual_calories: Optional[float] = None,
    ):
        details = {}
        if target_calories is not None:
            details["target_calories"] = target_calories
        if actual_calories is not None:
            details["actual_calories"] = actual_calories
        super().__init__(message, details)


class MacroBalanceError(MealPlanningError):
    """Raised when macronutrient balance cannot be achieved."""

    def __init__(
        self,
        message: str,
        target_macros: Optional[Dict[str, float]] = None,
        actual_macros: Optional[Dict[str, float]] = None,
    ):
        details = {}
        if target_macros:
            details["target_macros"] = target_macros
        if actual_macros:
            details["actual_macros"] = actual_macros
        super().__init__(message, details)


class DietaryRestrictionError(MealPlanningError):
    """Raised when dietary restrictions cannot be satisfied."""

    def __init__(
        self,
        message: str,
        restrictions: Optional[list] = None,
        conflicting_items: Optional[list] = None,
    ):
        details = {}
        if restrictions:
            details["restrictions"] = restrictions
        if conflicting_items:
            details["conflicting_items"] = conflicting_items
        super().__init__(message, details)


class BiomarkerAnalysisError(NutritionError):
    """Raised when biomarker analysis fails."""

    pass


class InvalidBiomarkerError(BiomarkerAnalysisError):
    """Raised when biomarker values are invalid or out of range."""

    def __init__(
        self,
        message: str,
        biomarker_name: str,
        value: Any,
        expected_range: Optional[Dict[str, float]] = None,
    ):
        details = {"biomarker": biomarker_name, "value": value}
        if expected_range:
            details["expected_range"] = expected_range
        super().__init__(message, details)


class BiomarkerDataMissingError(BiomarkerAnalysisError):
    """Raised when required biomarker data is missing."""

    def __init__(self, message: str, missing_biomarkers: Optional[list] = None):
        details = {}
        if missing_biomarkers:
            details["missing_biomarkers"] = missing_biomarkers
        super().__init__(message, details)


class SupplementationError(NutritionError):
    """Raised when supplement recommendation fails."""

    pass


class SupplementInteractionError(SupplementationError):
    """Raised when supplement interactions are detected."""

    def __init__(
        self,
        message: str,
        supplements: Optional[list] = None,
        interactions: Optional[list] = None,
    ):
        details = {}
        if supplements:
            details["supplements"] = supplements
        if interactions:
            details["interactions"] = interactions
        super().__init__(message, details)


class SupplementDosageError(SupplementationError):
    """Raised when supplement dosage is unsafe."""

    def __init__(
        self,
        message: str,
        supplement: str,
        recommended_dose: float,
        max_safe_dose: float,
    ):
        details = {
            "supplement": supplement,
            "recommended_dose": recommended_dose,
            "max_safe_dose": max_safe_dose,
        }
        super().__init__(message, details)


class FoodAnalysisError(NutritionError):
    """Raised when food analysis operations fail."""

    pass


class FoodNotFoundError(FoodAnalysisError):
    """Raised when a food item cannot be found in databases."""

    def __init__(
        self, message: str, food_name: str, searched_databases: Optional[list] = None
    ):
        details = {"food_name": food_name}
        if searched_databases:
            details["searched_databases"] = searched_databases
        super().__init__(message, details)


class ImageAnalysisError(FoodAnalysisError):
    """Raised when food image analysis fails."""

    def __init__(
        self,
        message: str,
        image_path: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        details = {}
        if image_path:
            details["image_path"] = image_path
        if reason:
            details["reason"] = reason
        super().__init__(message, details)


class NutrientDeficiencyError(NutritionError):
    """Raised when nutrient deficiencies are detected."""

    def __init__(
        self, message: str, deficient_nutrients: Optional[Dict[str, float]] = None
    ):
        details = {}
        if deficient_nutrients:
            details["deficient_nutrients"] = deficient_nutrients
        super().__init__(message, details)


class ChronoNutritionError(NutritionError):
    """Raised when chrono-nutrition timing fails."""

    def __init__(self, message: str, meal_timing: Optional[Dict[str, str]] = None):
        details = {}
        if meal_timing:
            details["meal_timing"] = meal_timing
        super().__init__(message, details)


class HealthDataSecurityError(NutritionError):
    """Raised when health data security is compromised."""

    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        security_issue: Optional[str] = None,
    ):
        details = {}
        if data_type:
            details["data_type"] = data_type
        if security_issue:
            details["security_issue"] = security_issue
        super().__init__(message, details)


class ConsentRequiredError(HealthDataSecurityError):
    """Raised when user consent is required but not provided."""

    def __init__(
        self, message: str, consent_type: str, data_usage: Optional[str] = None
    ):
        details = {"consent_type": consent_type}
        if data_usage:
            details["data_usage"] = data_usage
        super().__init__(message, details)


class DataRetentionError(HealthDataSecurityError):
    """Raised when data retention policies are violated."""

    def __init__(self, message: str, retention_days: int, policy_limit: int):
        details = {"retention_days": retention_days, "policy_limit": policy_limit}
        super().__init__(message, details)


class IntegrationError(NutritionError):
    """Raised when external integrations fail."""

    def __init__(
        self, message: str, service_name: str, error_type: Optional[str] = None
    ):
        details = {"service_name": service_name}
        if error_type:
            details["error_type"] = error_type
        super().__init__(message, details)


class ValidationError(NutritionError):
    """Raised when input validation fails."""

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
