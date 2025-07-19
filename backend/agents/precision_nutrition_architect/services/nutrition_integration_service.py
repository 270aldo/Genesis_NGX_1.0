"""
Integration service for external nutrition APIs and services.
Handles circuit breakers, retries, and API standardization.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import json

from core.circuit_breaker import CircuitBreaker
from ..core.exceptions import IntegrationError, FoodNotFoundError
from ..core.constants import FoodGroup

logger = logging.getLogger(__name__)


class NutritionIntegrationService:
    """
    Manages integrations with external nutrition services including:
    - Food databases (USDA, Nutritionix, etc.)
    - Wearable device APIs
    - Meal tracking services
    - Restaurant menu APIs
    """

    def __init__(self, circuit_breaker: Optional[CircuitBreaker] = None, config: Any = None):
        """Initialize integration service with circuit breaker."""
        self.circuit_breaker = circuit_breaker
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None

        # API endpoints configuration
        self.api_endpoints = {
            "usda": {
                "base_url": "https://api.nal.usda.gov/fdc/v1",
                "api_key": (
                    config.usda_api_key if hasattr(config, "usda_api_key") else None
                ),
            },
            "nutritionix": {
                "base_url": "https://trackapi.nutritionix.com/v2",
                "app_id": (
                    config.nutritionix_app_id
                    if hasattr(config, "nutritionix_app_id")
                    else None
                ),
                "app_key": (
                    config.nutritionix_app_key
                    if hasattr(config, "nutritionix_app_key")
                    else None
                ),
            },
            "myfitnesspal": {
                "base_url": "https://api.myfitnesspal.com/v2",
                "enabled": config.enable_food_database_api,
            },
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def search_food_databases(
        self, query: str, databases: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search multiple food databases for a food item.

        Args:
            query: Food search query
            databases: List of databases to search (defaults to all enabled)

        Returns:
            List of food items from all databases
        """
        if not databases:
            databases = self.config.supported_food_databases

        results = []
        errors = []

        # Search each database concurrently
        search_tasks = []
        for db in databases:
            if db in self.api_endpoints and self._is_database_enabled(db):
                task = self._search_with_circuit_breaker(db, query)
                search_tasks.append(task)

        # Gather results
        search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

        for i, result in enumerate(search_results):
            if isinstance(result, Exception):
                errors.append(str(result))
                logger.warning(f"Search failed for database: {result}")
            else:
                results.extend(result)

        if not results and errors:
            raise IntegrationError(
                f"Failed to search food databases: {', '.join(errors)}",
                service_name="food_databases",
                error_type="search_failure",
            )

        return results

    async def get_restaurant_menu_nutrition(
        self, restaurant: str, item_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get nutrition information for restaurant menu items.

        Args:
            restaurant: Restaurant name
            item_name: Menu item name

        Returns:
            Nutrition information or None
        """
        # This would integrate with restaurant APIs
        # For now, simulate with Nutritionix branded foods
        try:
            if self.circuit_breaker:
                return await self.circuit_breaker.call(
                    self._fetch_restaurant_item, restaurant, item_name
                )
            else:
                return await self._fetch_restaurant_item(restaurant, item_name)

        except Exception as e:
            logger.error(f"Failed to get restaurant nutrition: {e}")
            return None

    async def sync_wearable_nutrition_data(
        self, user_id: str, device_type: str
    ) -> Dict[str, Any]:
        """
        Sync nutrition data from wearable devices.

        Args:
            user_id: User identifier
            device_type: Type of wearable (fitbit, apple_watch, etc.)

        Returns:
            Synced nutrition data
        """
        if not self.config.enable_wearable_integration:
            return {"status": "disabled", "data": {}}

        try:
            # Route to appropriate integration
            if device_type == "myfitnesspal":
                return await self._sync_myfitnesspal_data(user_id)
            elif device_type == "fitbit":
                return await self._sync_fitbit_nutrition(user_id)
            elif device_type == "apple_health":
                return await self._sync_apple_health_nutrition(user_id)
            else:
                raise IntegrationError(
                    f"Unsupported device type: {device_type}",
                    service_name=device_type,
                    error_type="unsupported_device",
                )

        except Exception as e:
            logger.error(f"Failed to sync wearable data: {e}")
            raise

    async def analyze_barcode_nutrition(self, barcode: str) -> Dict[str, Any]:
        """
        Get nutrition information from product barcode.

        Args:
            barcode: Product barcode (UPC/EAN)

        Returns:
            Product nutrition information
        """
        try:
            # Try multiple barcode databases
            result = await self._search_with_circuit_breaker("barcode", barcode)

            if not result:
                raise FoodNotFoundError(
                    f"Product with barcode {barcode} not found",
                    food_name=f"barcode:{barcode}",
                    searched_databases=["openfoodfacts", "nutritionix"],
                )

            return result[0] if isinstance(result, list) else result

        except Exception as e:
            logger.error(f"Barcode lookup failed: {e}")
            raise

    async def get_recipe_nutrition(
        self, ingredients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate nutrition for a recipe based on ingredients.

        Args:
            ingredients: List of ingredients with quantities

        Returns:
            Aggregated nutrition information
        """
        total_nutrition = {
            "calories": 0,
            "macros": {
                "protein": 0,
                "carbohydrates": 0,
                "fat": 0,
                "fiber": 0,
                "sugar": 0,
            },
            "micros": {},
        }

        # Process each ingredient
        for ingredient in ingredients:
            food_name = ingredient.get("name")
            quantity = ingredient.get("quantity", 1)
            unit = ingredient.get("unit", "serving")

            try:
                # Search for ingredient
                food_data = await self.search_food_databases(food_name)
                if food_data:
                    # Use first match and scale by quantity
                    nutrition = self._scale_nutrition(food_data[0], quantity, unit)
                    total_nutrition = self._add_nutrition(total_nutrition, nutrition)

            except Exception as e:
                logger.warning(f"Failed to get nutrition for {food_name}: {e}")
                continue

        return total_nutrition

    def _is_database_enabled(self, database: str) -> bool:
        """Check if a database is enabled and has credentials."""
        if database == "usda":
            return bool(self.api_endpoints["usda"].get("api_key"))
        elif database == "nutritionix":
            return bool(self.api_endpoints["nutritionix"].get("app_id"))
        elif database == "myfitnesspal":
            return self.api_endpoints["myfitnesspal"].get("enabled", False)
        return False

    async def _search_with_circuit_breaker(
        self, database: str, query: str
    ) -> List[Dict[str, Any]]:
        """Search database with circuit breaker protection."""
        if self.circuit_breaker:
            return await self.circuit_breaker.call(
                self._search_database, database, query
            )
        else:
            return await self._search_database(database, query)

    async def _search_database(self, database: str, query: str) -> List[Dict[str, Any]]:
        """Search specific database for food items."""
        if database == "usda":
            return await self._search_usda(query)
        elif database == "nutritionix":
            return await self._search_nutritionix(query)
        elif database == "barcode":
            return await self._search_barcode_databases(query)
        else:
            return []

    async def _search_usda(self, query: str) -> List[Dict[str, Any]]:
        """Search USDA FoodData Central."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        api_key = self.api_endpoints["usda"].get("api_key")
        if not api_key:
            return []

        url = f"{self.api_endpoints['usda']['base_url']}/foods/search"
        params = {"query": query, "api_key": api_key, "limit": 10}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_usda_results(data)
                else:
                    logger.error(f"USDA API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"USDA search failed: {e}")
            return []

    async def _search_nutritionix(self, query: str) -> List[Dict[str, Any]]:
        """Search Nutritionix database."""
        if not self.session:
            self.session = aiohttp.ClientSession()

        app_id = self.api_endpoints["nutritionix"].get("app_id")
        app_key = self.api_endpoints["nutritionix"].get("app_key")

        if not app_id or not app_key:
            return []

        url = f"{self.api_endpoints['nutritionix']['base_url']}/search/instant"
        headers = {"x-app-id": app_id, "x-app-key": app_key}
        params = {"query": query}

        try:
            async with self.session.get(
                url, headers=headers, params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_nutritionix_results(data)
                else:
                    logger.error(f"Nutritionix API error: {response.status}")
                    return []

        except Exception as e:
            logger.error(f"Nutritionix search failed: {e}")
            return []

    def _parse_usda_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse USDA search results to standard format."""
        results = []
        for food in data.get("foods", []):
            nutrients = {}
            for nutrient in food.get("foodNutrients", []):
                nutrients[nutrient["nutrientName"]] = nutrient["value"]

            results.append(
                {
                    "name": food.get("description", ""),
                    "brand": food.get("brandName", ""),
                    "serving_size": 100,
                    "serving_unit": "g",
                    "calories": nutrients.get("Energy", 0),
                    "protein": nutrients.get("Protein", 0),
                    "carbohydrates": nutrients.get("Carbohydrate, by difference", 0),
                    "fat": nutrients.get("Total lipid (fat)", 0),
                    "fiber": nutrients.get("Fiber, total dietary", 0),
                    "source": "usda",
                }
            )

        return results

    def _parse_nutritionix_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Nutritionix results to standard format."""
        results = []

        # Common foods
        for food in data.get("common", []):
            results.append(
                {
                    "name": food.get("food_name", ""),
                    "serving_size": food.get("serving_qty", 1),
                    "serving_unit": food.get("serving_unit", "serving"),
                    "source": "nutritionix_common",
                }
            )

        # Branded foods
        for food in data.get("branded", []):
            results.append(
                {
                    "name": food.get("food_name", ""),
                    "brand": food.get("brand_name", ""),
                    "serving_size": food.get("serving_qty", 1),
                    "serving_unit": food.get("serving_unit", "serving"),
                    "calories": food.get("nf_calories", 0),
                    "source": "nutritionix_branded",
                }
            )

        return results

    def _scale_nutrition(
        self, nutrition: Dict[str, Any], quantity: float, unit: str
    ) -> Dict[str, Any]:
        """Scale nutrition values by quantity."""
        # Simple scaling - in production would handle unit conversions
        scale_factor = quantity

        scaled = nutrition.copy()
        scaled["calories"] *= scale_factor

        if "macros" in scaled:
            for macro in scaled["macros"]:
                scaled["macros"][macro] *= scale_factor

        return scaled

    def _add_nutrition(
        self, total: Dict[str, Any], addition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add nutrition values together."""
        result = total.copy()

        result["calories"] += addition.get("calories", 0)

        # Add macros
        for macro in ["protein", "carbohydrates", "fat", "fiber", "sugar"]:
            if "macros" in addition and macro in addition["macros"]:
                result["macros"][macro] += addition["macros"][macro]

        return result

    async def _sync_myfitnesspal_data(self, user_id: str) -> Dict[str, Any]:
        """Sync nutrition data from MyFitnessPal (mock)."""
        # In production, this would use actual MyFitnessPal API
        return {
            "status": "success",
            "data": {
                "last_sync": datetime.now().isoformat(),
                "meals_today": 3,
                "calories_consumed": 1850,
                "macros": {"protein": 120, "carbohydrates": 200, "fat": 65},
            },
        }

    async def _fetch_restaurant_item(
        self, restaurant: str, item_name: str
    ) -> Dict[str, Any]:
        """Fetch restaurant menu item nutrition (mock)."""
        # In production, would query restaurant APIs
        return {
            "restaurant": restaurant,
            "item": item_name,
            "calories": 650,
            "protein": 35,
            "carbohydrates": 55,
            "fat": 28,
            "sodium": 1200,
        }
