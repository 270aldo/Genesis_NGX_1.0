"""
SAGE Agent Configuration
========================

Centralized configuration for the SAGE Precision Nutrition Architect agent.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from core.settings import Settings

settings = Settings()


class SageConfig(BaseModel):
    """Configuration for SAGE agent."""
    
    model_config = {
        "protected_namespaces": (),
        "use_enum_values": True,
        "validate_assignment": True
    }
    
    # Agent identity
    agent_id: str = Field(default="sage_nutrition")
    agent_name: str = Field(default="SAGE Precision Nutrition Architect")
    
    # Model configuration
    model_id: str = Field(default="gemini-2.0-flash-exp")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048)
    
    # A2A configuration
    a2a_server_url: str = Field(
        default_factory=lambda: f"http://{settings.A2A_HOST}:{settings.A2A_PORT}"
    )
    
    # Personality settings
    personality_type: str = Field(default="longevity")  # prime or longevity
    nutrition_philosophy: str = Field(default="evidence_based")  # evidence_based, functional, integrative
    
    # Feature flags
    enable_biomarker_analysis: bool = Field(default=True)
    enable_chrononutrition: bool = Field(default=True)
    enable_supplement_stacking: bool = Field(default=True)
    enable_food_image_analysis: bool = Field(default=True)
    
    # Cache settings
    cache_ttl: int = Field(default=7200)  # 2 hours for nutrition plans
    enable_response_cache: bool = Field(default=True)
    
    # Integration settings
    nutrition_api_key: Optional[str] = Field(default=None)
    training_agent_id: str = Field(default="blaze_elite_training")
    
    # Nutrition defaults
    default_meal_frequency: int = Field(default=3)  # meals per day
    default_calorie_adjustment: float = Field(default=1.0)  # multiplier
    macro_split_default: Dict[str, float] = Field(
        default_factory=lambda: {
            "protein": 0.30,
            "carbs": 0.40,
            "fats": 0.30
        }
    )
    
    # Safety settings
    allergen_check_enabled: bool = Field(default=True)
    medical_disclaimer_required: bool = Field(default=True)
    max_supplement_stack: int = Field(default=10)
    
    # Biomarker thresholds
    biomarker_optimal_ranges: Dict[str, Dict[str, float]] = Field(
        default_factory=lambda: {
            "vitamin_d": {"min": 30, "max": 100},
            "b12": {"min": 300, "max": 900},
            "ferritin": {"min": 30, "max": 300},
            "hba1c": {"min": 4.0, "max": 5.6}
        }
    )
    
    # Security and compliance settings
    enable_health_data_encryption: bool = Field(default=True)
    enable_audit_logging: bool = Field(default=True)
    gdpr_compliant: bool = Field(default=True)
    hipaa_compliant: bool = Field(default=True)
    require_consent_for_analysis: bool = Field(default=True)
    max_health_record_retention_days: int = Field(default=365)  # 1 year
    
    # External API configurations
    usda_api_key: Optional[str] = Field(default=None)
    nutritionix_app_id: Optional[str] = Field(default=None)
    nutritionix_app_key: Optional[str] = Field(default=None)
    enable_food_database_api: bool = Field(default=True)
    enable_wearable_integration: bool = Field(default=True)
    supported_food_databases: List[str] = Field(default_factory=lambda: ["usda", "nutritionix", "custom"])
    
    # Capabilities
    capabilities: List[str] = Field(default_factory=lambda: [
        "meal_plan_generation",
        "macro_calculation",
        "supplement_recommendation",
        "biomarker_analysis",
        "chrononutrition_planning",
        "food_image_analysis",
        "allergen_detection",
        "nutrient_timing",
        "metabolic_optimization"
    ])


# Nutrition categories
class FoodCategory:
    """Food categorization."""
    PROTEINS = "proteins"
    CARBOHYDRATES = "carbohydrates"
    FATS = "fats"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    DAIRY = "dairy"
    GRAINS = "grains"


# Meal types
class MealType:
    """Meal type definitions."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"


# Dietary preferences
class DietaryPreference:
    """Common dietary preferences."""
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    PESCATARIAN = "pescatarian"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    LOW_CARB = "low_carb"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"


# Default food database (subset)
DEFAULT_FOODS = {
    "chicken_breast": {
        "category": FoodCategory.PROTEINS,
        "macros_per_100g": {"protein": 31, "carbs": 0, "fats": 3.6},
        "calories_per_100g": 165,
        "micronutrients": {"b12": 0.3, "iron": 1.0}
    },
    "brown_rice": {
        "category": FoodCategory.GRAINS,
        "macros_per_100g": {"protein": 2.6, "carbs": 23, "fats": 0.9},
        "calories_per_100g": 111,
        "micronutrients": {"magnesium": 43, "fiber": 1.8}
    },
    "avocado": {
        "category": FoodCategory.FATS,
        "macros_per_100g": {"protein": 2, "carbs": 8.5, "fats": 14.7},
        "calories_per_100g": 160,
        "micronutrients": {"potassium": 485, "folate": 81}
    },
    "spinach": {
        "category": FoodCategory.VEGETABLES,
        "macros_per_100g": {"protein": 2.9, "carbs": 3.6, "fats": 0.4},
        "calories_per_100g": 23,
        "micronutrients": {"iron": 2.7, "vitamin_k": 483}
    }
}


# Supplement database (subset)
DEFAULT_SUPPLEMENTS = {
    "vitamin_d3": {
        "category": "vitamins",
        "typical_dose": "1000-5000 IU",
        "timing": "morning with fat",
        "interactions": ["calcium", "magnesium"]
    },
    "omega_3": {
        "category": "fatty_acids",
        "typical_dose": "1-3g EPA/DHA",
        "timing": "with meals",
        "interactions": ["blood_thinners"]
    },
    "magnesium_glycinate": {
        "category": "minerals",
        "typical_dose": "200-400mg",
        "timing": "evening",
        "interactions": ["antibiotics", "calcium"]
    },
    "probiotics": {
        "category": "gut_health",
        "typical_dose": "10-50 billion CFU",
        "timing": "empty stomach",
        "interactions": ["antibiotics"]
    }
}