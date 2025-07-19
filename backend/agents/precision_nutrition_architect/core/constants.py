"""
Constants and enumerations for Precision Nutrition Architect Agent.
Centralizes all nutrition-related constants following A+ standards.
"""

from enum import Enum
from typing import Dict, List, Tuple, Any


class ActivityLevel(str, Enum):
    """Physical activity levels for calorie calculations."""

    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class DietType(str, Enum):
    """Supported dietary patterns."""

    BALANCED = "balanced"
    LOW_CARB = "low_carb"
    KETOGENIC = "ketogenic"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    HIGH_PROTEIN = "high_protein"
    WHOLE30 = "whole30"
    DASH = "dash"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"


class MealType(str, Enum):
    """Types of meals throughout the day."""

    BREAKFAST = "breakfast"
    MORNING_SNACK = "morning_snack"
    LUNCH = "lunch"
    AFTERNOON_SNACK = "afternoon_snack"
    DINNER = "dinner"
    EVENING_SNACK = "evening_snack"
    PRE_WORKOUT = "pre_workout"
    POST_WORKOUT = "post_workout"


class NutrientUnit(str, Enum):
    """Units for various nutrients."""

    GRAM = "g"
    MILLIGRAM = "mg"
    MICROGRAM = "mcg"
    IU = "IU"
    CALORIE = "kcal"
    PERCENT = "%"
    MILLILITER = "ml"
    LITER = "L"


class BiomarkerCategory(str, Enum):
    """Categories of biomarkers for analysis."""

    METABOLIC = "metabolic"
    CARDIOVASCULAR = "cardiovascular"
    HORMONAL = "hormonal"
    INFLAMMATORY = "inflammatory"
    NUTRITIONAL = "nutritional"
    LIVER = "liver"
    KIDNEY = "kidney"
    THYROID = "thyroid"
    IMMUNE = "immune"


class HealthGoal(str, Enum):
    """Common health and nutrition goals."""

    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"
    LONGEVITY = "longevity"
    DISEASE_MANAGEMENT = "disease_management"
    ENERGY_OPTIMIZATION = "energy_optimization"
    GUT_HEALTH = "gut_health"
    COGNITIVE_FUNCTION = "cognitive_function"


class FoodGroup(str, Enum):
    """Major food groups for categorization."""

    PROTEINS = "proteins"
    CARBOHYDRATES = "carbohydrates"
    FATS = "fats"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    DAIRY = "dairy"
    GRAINS = "grains"
    NUTS_SEEDS = "nuts_seeds"
    LEGUMES = "legumes"
    HERBS_SPICES = "herbs_spices"


# Macronutrient calorie values
CALORIES_PER_GRAM: Dict[str, float] = {
    "protein": 4.0,
    "carbohydrate": 4.0,
    "fat": 9.0,
    "alcohol": 7.0,
    "fiber": 2.0,
}

# Daily Value percentages for common nutrients (based on 2000 calorie diet)
DAILY_VALUES: Dict[str, Dict[str, float]] = {
    "protein": {"value": 50, "unit": "g"},
    "total_fat": {"value": 65, "unit": "g"},
    "saturated_fat": {"value": 20, "unit": "g"},
    "cholesterol": {"value": 300, "unit": "mg"},
    "sodium": {"value": 2300, "unit": "mg"},
    "total_carbohydrate": {"value": 300, "unit": "g"},
    "dietary_fiber": {"value": 25, "unit": "g"},
    "total_sugars": {"value": 50, "unit": "g"},
    "vitamin_a": {"value": 900, "unit": "mcg"},
    "vitamin_c": {"value": 90, "unit": "mg"},
    "vitamin_d": {"value": 20, "unit": "mcg"},
    "vitamin_e": {"value": 15, "unit": "mg"},
    "vitamin_k": {"value": 120, "unit": "mcg"},
    "calcium": {"value": 1300, "unit": "mg"},
    "iron": {"value": 18, "unit": "mg"},
    "potassium": {"value": 2500, "unit": "mg"},
}

# Activity level multipliers for calorie calculations
ACTIVITY_MULTIPLIERS: Dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY: 1.2,
    ActivityLevel.LIGHTLY_ACTIVE: 1.375,
    ActivityLevel.MODERATELY_ACTIVE: 1.55,
    ActivityLevel.VERY_ACTIVE: 1.725,
    ActivityLevel.EXTREMELY_ACTIVE: 1.9,
}

# Ideal meal timing windows (hours from wake time)
MEAL_TIMING_WINDOWS: Dict[MealType, Tuple[float, float]] = {
    MealType.BREAKFAST: (0.5, 2.0),
    MealType.MORNING_SNACK: (3.0, 4.0),
    MealType.LUNCH: (4.5, 6.5),
    MealType.AFTERNOON_SNACK: (7.5, 9.0),
    MealType.DINNER: (10.0, 12.0),
    MealType.EVENING_SNACK: (13.0, 14.0),
}

# Common allergens to check
COMMON_ALLERGENS: List[str] = [
    "milk",
    "eggs",
    "fish",
    "shellfish",
    "tree_nuts",
    "peanuts",
    "wheat",
    "soybeans",
    "sesame",
]

# Supplement interaction matrix (simplified)
SUPPLEMENT_INTERACTIONS: Dict[str, List[str]] = {
    "iron": ["calcium", "zinc", "magnesium"],
    "calcium": ["iron", "zinc"],
    "zinc": ["iron", "calcium", "copper"],
    "vitamin_k": ["warfarin", "vitamin_e"],
    "vitamin_e": ["vitamin_k", "warfarin"],
    "magnesium": ["calcium", "iron"],
}

# Maximum safe daily doses for common supplements
MAX_SAFE_DOSES: Dict[str, Dict[str, float]] = {
    "vitamin_d": {"value": 4000, "unit": "IU"},
    "vitamin_c": {"value": 2000, "unit": "mg"},
    "vitamin_e": {"value": 1000, "unit": "IU"},
    "iron": {"value": 45, "unit": "mg"},
    "calcium": {"value": 2500, "unit": "mg"},
    "magnesium": {"value": 350, "unit": "mg"},
    "zinc": {"value": 40, "unit": "mg"},
    "omega_3": {"value": 3000, "unit": "mg"},
}

# Biomarker optimal ranges (general population)
BIOMARKER_OPTIMAL_RANGES: Dict[str, Dict[str, Any]] = {
    "glucose_fasting": {"min": 75, "max": 95, "unit": "mg/dL"},
    "hba1c": {"min": 4.5, "max": 5.4, "unit": "%"},
    "cholesterol_total": {"min": 150, "max": 180, "unit": "mg/dL"},
    "hdl": {"min": 50, "max": 80, "unit": "mg/dL"},
    "ldl": {"min": 60, "max": 100, "unit": "mg/dL"},
    "triglycerides": {"min": 50, "max": 100, "unit": "mg/dL"},
    "vitamin_d": {"min": 30, "max": 60, "unit": "ng/mL"},
    "b12": {"min": 400, "max": 900, "unit": "pg/mL"},
    "ferritin": {"min": 30, "max": 200, "unit": "ng/mL"},
    "tsh": {"min": 0.5, "max": 2.5, "unit": "mIU/L"},
}

# Food quality scoring weights
FOOD_QUALITY_WEIGHTS: Dict[str, float] = {
    "nutrient_density": 0.3,
    "processing_level": 0.2,
    "glycemic_impact": 0.15,
    "inflammatory_score": 0.15,
    "micronutrient_content": 0.2,
}

# Chrono-nutrition meal distribution
CHRONO_MEAL_DISTRIBUTION: Dict[str, Dict[str, float]] = {
    "morning_focused": {
        "breakfast": 0.35,
        "lunch": 0.30,
        "dinner": 0.25,
        "snacks": 0.10,
    },
    "evening_focused": {
        "breakfast": 0.20,
        "lunch": 0.30,
        "dinner": 0.35,
        "snacks": 0.15,
    },
    "balanced": {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snacks": 0.10},
}

# Genetic SNPs affecting nutrition (simplified)
NUTRITION_SNPS: Dict[str, Dict[str, str]] = {
    "MTHFR_C677T": {"nutrient": "folate", "impact": "reduced_conversion"},
    "VDR_Taq1": {"nutrient": "vitamin_d", "impact": "reduced_absorption"},
    "FTO_rs9939609": {"nutrient": "general", "impact": "increased_hunger"},
    "APOE_e4": {"nutrient": "fat", "impact": "altered_metabolism"},
    "CYP1A2": {"nutrient": "caffeine", "impact": "slow_metabolism"},
}
