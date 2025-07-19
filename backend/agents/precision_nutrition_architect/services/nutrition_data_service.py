"""
Data service for nutrition-related database operations.
Handles caching, validation, and data persistence.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from uuid import uuid4

from ..core.exceptions import (
    ValidationError,
    FoodNotFoundError,
    NutrientDeficiencyError,
)
from ..core.constants import DAILY_VALUES, CALORIES_PER_GRAM, FoodGroup, MealType

logger = logging.getLogger(__name__)


class NutritionDataService:
    """
    Manages nutrition data operations including:
    - Food database queries
    - Meal plan storage and retrieval
    - Nutrition calculation caching
    - User preference management
    """

    def __init__(self, supabase_client: Any, cache: Any, config: Any):
        """Initialize data service with dependencies."""
        self.supabase = supabase_client
        self.cache = cache
        self.config = config
        self._food_db_cache = {}

    async def get_food_item(
        self, food_name: str, database: str = "usda"
    ) -> Dict[str, Any]:
        """
        Retrieve food item nutritional data from database.

        Args:
            food_name: Name of the food
            database: Database to search (usda, nutritionix, etc.)

        Returns:
            Food nutritional data

        Raises:
            FoodNotFoundError if food not found
        """
        # Check cache first
        cache_key = f"food:{database}:{food_name.lower()}"
        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.debug(f"Food item '{food_name}' found in cache")
                return cached_data

        try:
            # Query database based on source
            if database == "usda":
                food_data = await self._query_usda_database(food_name)
            elif database == "nutritionix":
                food_data = await self._query_nutritionix_database(food_name)
            elif database == "custom":
                food_data = await self._query_custom_database(food_name)
            else:
                raise ValueError(f"Unsupported database: {database}")

            # Validate and normalize data
            normalized_data = self._normalize_food_data(food_data)

            # Cache the result
            if self.cache:
                await self.cache.set(cache_key, normalized_data, ttl=3600)

            return normalized_data

        except Exception as e:
            logger.error(f"Failed to retrieve food item '{food_name}': {e}")
            raise FoodNotFoundError(
                f"Food item '{food_name}' not found",
                food_name=food_name,
                searched_databases=[database],
            )

    async def save_meal_plan(
        self,
        user_id: str,
        meal_plan: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save a meal plan to database.

        Args:
            user_id: User identifier
            meal_plan: Meal plan data
            metadata: Additional metadata

        Returns:
            Meal plan ID
        """
        if not self.supabase:
            logger.warning("No database connection, returning mock ID")
            return str(uuid4())

        try:
            # Prepare data for storage
            plan_data = {
                "id": str(uuid4()),
                "user_id": user_id,
                "meal_plan": json.dumps(meal_plan),
                "created_at": datetime.now().isoformat(),
                "metadata": json.dumps(metadata or {}),
                "total_calories": self._calculate_total_calories(meal_plan),
                "macro_breakdown": self._calculate_macro_breakdown(meal_plan),
            }

            # Insert into database
            result = self.supabase.table("meal_plans").insert(plan_data).execute()

            # Cache the meal plan for quick retrieval
            if self.cache:
                cache_key = f"meal_plan:{plan_data['id']}"
                await self.cache.set(cache_key, meal_plan, ttl=7200)

            logger.info(f"Saved meal plan {plan_data['id']} for user {user_id}")
            return plan_data["id"]

        except Exception as e:
            logger.error(f"Failed to save meal plan: {e}")
            raise

    async def get_meal_plan(self, meal_plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a meal plan by ID.

        Args:
            meal_plan_id: Meal plan identifier

        Returns:
            Meal plan data or None if not found
        """
        # Check cache first
        cache_key = f"meal_plan:{meal_plan_id}"
        if self.cache:
            cached_plan = await self.cache.get(cache_key)
            if cached_plan:
                return cached_plan

        if not self.supabase:
            return None

        try:
            # Query database
            result = (
                self.supabase.table("meal_plans")
                .select("*")
                .eq("id", meal_plan_id)
                .single()
                .execute()
            )

            if result.data:
                meal_plan = json.loads(result.data["meal_plan"])

                # Cache for future requests
                if self.cache:
                    await self.cache.set(cache_key, meal_plan, ttl=7200)

                return meal_plan

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve meal plan {meal_plan_id}: {e}")
            return None

    async def get_user_meal_history(
        self, user_id: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get user's meal plan history.

        Args:
            user_id: User identifier
            days: Number of days to retrieve

        Returns:
            List of meal plans
        """
        if not self.supabase:
            return []

        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Query database
            result = (
                self.supabase.table("meal_plans")
                .select("*")
                .eq("user_id", user_id)
                .gte("created_at", start_date.isoformat())
                .lte("created_at", end_date.isoformat())
                .order("created_at", desc=True)
                .execute()
            )

            meal_plans = []
            for record in result.data:
                meal_plan = json.loads(record["meal_plan"])
                meal_plan["created_at"] = record["created_at"]
                meal_plan["id"] = record["id"]
                meal_plans.append(meal_plan)

            return meal_plans

        except Exception as e:
            logger.error(f"Failed to retrieve meal history for user {user_id}: {e}")
            return []

    async def save_biomarker_data(
        self,
        user_id: str,
        biomarkers: Dict[str, Any],
        test_date: Optional[datetime] = None,
    ) -> str:
        """
        Save biomarker test results.

        Args:
            user_id: User identifier
            biomarkers: Biomarker values
            test_date: Date of test (defaults to now)

        Returns:
            Biomarker record ID
        """
        if not self.supabase:
            return str(uuid4())

        try:
            # Prepare data
            record_data = {
                "id": str(uuid4()),
                "user_id": user_id,
                "biomarkers": json.dumps(biomarkers),
                "test_date": (test_date or datetime.now()).isoformat(),
                "created_at": datetime.now().isoformat(),
            }

            # Insert into database
            result = (
                self.supabase.table("biomarker_records").insert(record_data).execute()
            )

            logger.info(f"Saved biomarker data {record_data['id']} for user {user_id}")
            return record_data["id"]

        except Exception as e:
            logger.error(f"Failed to save biomarker data: {e}")
            raise

    async def get_latest_biomarkers(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's most recent biomarker data.

        Args:
            user_id: User identifier

        Returns:
            Latest biomarker data or None
        """
        if not self.supabase:
            return None

        try:
            # Query for latest record
            result = (
                self.supabase.table("biomarker_records")
                .select("*")
                .eq("user_id", user_id)
                .order("test_date", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                record = result.data[0]
                biomarkers = json.loads(record["biomarkers"])
                biomarkers["test_date"] = record["test_date"]
                return biomarkers

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve biomarkers for user {user_id}: {e}")
            return None

    async def analyze_nutrient_gaps(
        self, consumed_nutrients: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Analyze nutrient gaps against daily values.

        Args:
            consumed_nutrients: Nutrients consumed

        Returns:
            Analysis of deficiencies and excesses
        """
        gaps = {"deficiencies": {}, "excesses": {}, "adequate": []}

        for nutrient, dv_info in DAILY_VALUES.items():
            if nutrient in consumed_nutrients:
                consumed = consumed_nutrients[nutrient]
                dv_value = dv_info["value"]
                percentage = (consumed / dv_value) * 100

                if percentage < 80:
                    gaps["deficiencies"][nutrient] = {
                        "consumed": consumed,
                        "daily_value": dv_value,
                        "percentage": percentage,
                        "unit": dv_info["unit"],
                    }
                elif percentage > 150:
                    gaps["excesses"][nutrient] = {
                        "consumed": consumed,
                        "daily_value": dv_value,
                        "percentage": percentage,
                        "unit": dv_info["unit"],
                    }
                else:
                    gaps["adequate"].append(nutrient)

        # Log significant deficiencies
        if len(gaps["deficiencies"]) > 3:
            logger.warning(
                f"Multiple nutrient deficiencies detected: {list(gaps['deficiencies'].keys())}"
            )

        return gaps

    def _normalize_food_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize food data to standard format."""
        normalized = {
            "name": raw_data.get("name", "Unknown"),
            "serving_size": raw_data.get("serving_size", 100),
            "serving_unit": raw_data.get("serving_unit", "g"),
            "calories": raw_data.get("calories", 0),
            "macros": {
                "protein": raw_data.get("protein", 0),
                "carbohydrates": raw_data.get("carbohydrates", 0),
                "fat": raw_data.get("fat", 0),
                "fiber": raw_data.get("fiber", 0),
                "sugar": raw_data.get("sugar", 0),
            },
            "micros": {
                "sodium": raw_data.get("sodium", 0),
                "potassium": raw_data.get("potassium", 0),
                "calcium": raw_data.get("calcium", 0),
                "iron": raw_data.get("iron", 0),
                "vitamin_c": raw_data.get("vitamin_c", 0),
                "vitamin_d": raw_data.get("vitamin_d", 0),
            },
            "food_group": self._categorize_food_group(raw_data),
        }

        return normalized

    def _categorize_food_group(self, food_data: Dict[str, Any]) -> str:
        """Categorize food into appropriate food group."""
        # Simple heuristic based on macros
        protein = food_data.get("protein", 0)
        carbs = food_data.get("carbohydrates", 0)
        fat = food_data.get("fat", 0)

        if protein > carbs and protein > fat:
            return FoodGroup.PROTEINS.value
        elif carbs > protein and carbs > fat:
            return FoodGroup.CARBOHYDRATES.value
        elif fat > protein and fat > carbs:
            return FoodGroup.FATS.value
        else:
            return FoodGroup.VEGETABLES.value  # Default

    def _calculate_total_calories(self, meal_plan: Dict[str, Any]) -> float:
        """Calculate total calories in meal plan."""
        total = 0
        for meal_type, meals in meal_plan.get("meals", {}).items():
            for meal in meals:
                total += meal.get("calories", 0)
        return total

    def _calculate_macro_breakdown(self, meal_plan: Dict[str, Any]) -> Dict[str, float]:
        """Calculate macro breakdown for meal plan."""
        totals = {"protein": 0, "carbohydrates": 0, "fat": 0}

        for meal_type, meals in meal_plan.get("meals", {}).items():
            for meal in meals:
                macros = meal.get("macros", {})
                totals["protein"] += macros.get("protein", 0)
                totals["carbohydrates"] += macros.get("carbohydrates", 0)
                totals["fat"] += macros.get("fat", 0)

        return totals

    async def _query_usda_database(self, food_name: str) -> Dict[str, Any]:
        """Query USDA food database (mock implementation)."""
        # In production, this would call the actual USDA API
        # For now, return mock data
        return {
            "name": food_name,
            "serving_size": 100,
            "calories": 150,
            "protein": 10,
            "carbohydrates": 20,
            "fat": 5,
        }

    async def _query_nutritionix_database(self, food_name: str) -> Dict[str, Any]:
        """Query Nutritionix database (mock implementation)."""
        # In production, this would call the actual Nutritionix API
        return {
            "name": food_name,
            "serving_size": 100,
            "calories": 160,
            "protein": 12,
            "carbohydrates": 18,
            "fat": 6,
        }

    async def _query_custom_database(self, food_name: str) -> Dict[str, Any]:
        """Query custom food database."""
        if not self.supabase:
            raise FoodNotFoundError(
                f"Custom food '{food_name}' not found",
                food_name=food_name,
                searched_databases=["custom"],
            )

        try:
            result = (
                self.supabase.table("custom_foods")
                .select("*")
                .ilike("name", f"%{food_name}%")
                .limit(1)
                .execute()
            )

            if result.data:
                return result.data[0]
            else:
                raise FoodNotFoundError(
                    f"Custom food '{food_name}' not found",
                    food_name=food_name,
                    searched_databases=["custom"],
                )

        except Exception as e:
            logger.error(f"Failed to query custom database: {e}")
            raise
