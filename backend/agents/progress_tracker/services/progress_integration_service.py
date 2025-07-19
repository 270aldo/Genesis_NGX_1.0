"""
STELLA Progress Integration Service.
External service integrations with circuit breakers and fallback mechanisms.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from ..core.exceptions import (
    ExternalServiceError,
    FitnessTrackerError,
    StorageServiceError,
)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Circuit breaker for external service calls."""

    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_max_calls: int = 3

    def __post_init__(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0

    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution."""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if (
                self.last_failure_time
                and (datetime.utcnow() - self.last_failure_time).total_seconds()
                > self.timeout_seconds
            ):
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False

        if self.state == CircuitBreakerState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls

        return False

    def record_success(self):
        """Record successful call."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self):
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class ProgressIntegrationService:
    """
    Comprehensive integration service for STELLA Progress Tracker.
    Handles external APIs with circuit breakers, fallbacks, and health monitoring.
    """

    def __init__(self):
        """Initialize integration service with circuit breakers."""
        self.circuit_breakers = {
            "fitness_tracker": CircuitBreaker(failure_threshold=3, timeout_seconds=30),
            "nutrition_service": CircuitBreaker(
                failure_threshold=5, timeout_seconds=60
            ),
            "body_analyzer": CircuitBreaker(failure_threshold=2, timeout_seconds=45),
            "workout_library": CircuitBreaker(failure_threshold=4, timeout_seconds=120),
            "progress_storage": CircuitBreaker(failure_threshold=2, timeout_seconds=30),
            "notification_service": CircuitBreaker(
                failure_threshold=5, timeout_seconds=60
            ),
        }

        # Service configurations
        self.service_configs = {
            "fitness_tracker": {
                "base_url": "https://api.fitness-tracker.com/v1",
                "timeout": 10,
                "retry_attempts": 2,
            },
            "nutrition_service": {
                "base_url": "https://api.nutrition-db.com/v2",
                "timeout": 15,
                "retry_attempts": 3,
            },
            "body_analyzer": {
                "base_url": "https://api.body-analysis.com/v1",
                "timeout": 20,
                "retry_attempts": 1,
            },
            "workout_library": {
                "base_url": "https://api.exercise-library.com/v1",
                "timeout": 8,
                "retry_attempts": 2,
            },
        }

        # Health status tracking
        self.service_health = {}
        self.last_health_check = {}

        # Integration statistics
        self.integration_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_breaker_trips": 0,
            "fallback_responses": 0,
        }

    async def get_fitness_tracker_data(
        self, user_id: str, data_type: str, date_range: int = 30
    ) -> Dict[str, Any]:
        """
        Retrieve data from fitness tracker service.

        Args:
            user_id: User identifier
            data_type: Type of data to retrieve
            date_range: Number of days to retrieve

        Returns:
            Fitness tracker data or fallback response
        """
        service_name = "fitness_tracker"
        circuit_breaker = self.circuit_breakers[service_name]

        if not circuit_breaker.can_execute():
            self.integration_stats["circuit_breaker_trips"] += 1
            return self._get_fitness_fallback_response(user_id, data_type)

        try:
            self.integration_stats["total_calls"] += 1

            # Make API call
            config = self.service_configs[service_name]
            url = f"{config['base_url']}/users/{user_id}/data/{data_type}"
            params = {"days": date_range}

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config["timeout"])
            ) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        circuit_breaker.record_success()
                        self.integration_stats["successful_calls"] += 1

                        return {
                            "success": True,
                            "data": data,
                            "source": "fitness_tracker",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                        )

        except Exception as e:
            circuit_breaker.record_failure()
            self.integration_stats["failed_calls"] += 1

            return self._get_fitness_fallback_response(user_id, data_type, str(e))

    async def get_nutrition_analysis(
        self, food_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get nutrition analysis from external service.

        Args:
            food_data: List of food items to analyze

        Returns:
            Nutrition analysis or fallback response
        """
        service_name = "nutrition_service"
        circuit_breaker = self.circuit_breakers[service_name]

        if not circuit_breaker.can_execute():
            self.integration_stats["circuit_breaker_trips"] += 1
            return self._get_nutrition_fallback_response(food_data)

        try:
            self.integration_stats["total_calls"] += 1

            config = self.service_configs[service_name]
            url = f"{config['base_url']}/analyze"

            payload = {"foods": food_data, "analysis_type": "comprehensive"}

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config["timeout"])
            ) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        circuit_breaker.record_success()
                        self.integration_stats["successful_calls"] += 1

                        return {
                            "success": True,
                            "analysis": data,
                            "source": "nutrition_service",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                        )

        except Exception as e:
            circuit_breaker.record_failure()
            self.integration_stats["failed_calls"] += 1

            return self._get_nutrition_fallback_response(food_data, str(e))

    async def analyze_body_image(
        self, image_url: str, analysis_type: str
    ) -> Dict[str, Any]:
        """
        Analyze body image using external service.

        Args:
            image_url: URL of image to analyze
            analysis_type: Type of analysis to perform

        Returns:
            Body analysis results or fallback response
        """
        service_name = "body_analyzer"
        circuit_breaker = self.circuit_breakers[service_name]

        if not circuit_breaker.can_execute():
            self.integration_stats["circuit_breaker_trips"] += 1
            return self._get_body_analysis_fallback_response(analysis_type)

        try:
            self.integration_stats["total_calls"] += 1

            config = self.service_configs[service_name]
            url = f"{config['base_url']}/analyze/body"

            payload = {
                "image_url": image_url,
                "analysis_type": analysis_type,
                "privacy_mode": True,
            }

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config["timeout"])
            ) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        circuit_breaker.record_success()
                        self.integration_stats["successful_calls"] += 1

                        return {
                            "success": True,
                            "analysis": data,
                            "source": "body_analyzer",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                        )

        except Exception as e:
            circuit_breaker.record_failure()
            self.integration_stats["failed_calls"] += 1

            return self._get_body_analysis_fallback_response(analysis_type, str(e))

    async def get_exercise_recommendations(
        self, user_profile: Dict[str, Any], goals: List[str]
    ) -> Dict[str, Any]:
        """
        Get exercise recommendations from workout library.

        Args:
            user_profile: User fitness profile
            goals: List of fitness goals

        Returns:
            Exercise recommendations or fallback response
        """
        service_name = "workout_library"
        circuit_breaker = self.circuit_breakers[service_name]

        if not circuit_breaker.can_execute():
            self.integration_stats["circuit_breaker_trips"] += 1
            return self._get_workout_fallback_response(goals)

        try:
            self.integration_stats["total_calls"] += 1

            config = self.service_configs[service_name]
            url = f"{config['base_url']}/recommendations"

            payload = {
                "user_profile": user_profile,
                "goals": goals,
                "difficulty_level": user_profile.get("experience_level", "beginner"),
                "equipment": user_profile.get("available_equipment", []),
            }

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config["timeout"])
            ) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        circuit_breaker.record_success()
                        self.integration_stats["successful_calls"] += 1

                        return {
                            "success": True,
                            "recommendations": data.get("exercises", []),
                            "workout_plan": data.get("plan", {}),
                            "source": "workout_library",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    else:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                        )

        except Exception as e:
            circuit_breaker.record_failure()
            self.integration_stats["failed_calls"] += 1

            return self._get_workout_fallback_response(goals, str(e))

    async def sync_progress_data(
        self, user_id: str, progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sync progress data to external storage.

        Args:
            user_id: User identifier
            progress_data: Progress data to sync

        Returns:
            Sync result
        """
        service_name = "progress_storage"
        circuit_breaker = self.circuit_breakers[service_name]

        if not circuit_breaker.can_execute():
            self.integration_stats["circuit_breaker_trips"] += 1
            return {
                "success": False,
                "message": "Storage service temporarily unavailable",
                "fallback_applied": True,
                "local_backup": True,
            }

        try:
            self.integration_stats["total_calls"] += 1

            # Simulate external storage API call
            await asyncio.sleep(0.1)  # Simulate network delay

            # In real implementation, this would make actual API call
            circuit_breaker.record_success()
            self.integration_stats["successful_calls"] += 1

            return {
                "success": True,
                "sync_id": f"sync_{user_id}_{int(datetime.utcnow().timestamp())}",
                "timestamp": datetime.utcnow().isoformat(),
                "records_synced": len(progress_data.get("entries", [])),
            }

        except Exception as e:
            circuit_breaker.record_failure()
            self.integration_stats["failed_calls"] += 1

            return {
                "success": False,
                "error": str(e),
                "fallback_applied": True,
                "local_backup": True,
            }

    async def send_progress_notification(
        self, user_id: str, notification_type: str, content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send progress notification to user.

        Args:
            user_id: User identifier
            notification_type: Type of notification
            content: Notification content

        Returns:
            Notification result
        """
        service_name = "notification_service"
        circuit_breaker = self.circuit_breakers[service_name]

        if not circuit_breaker.can_execute():
            self.integration_stats["circuit_breaker_trips"] += 1
            return {
                "success": False,
                "message": "Notification service temporarily unavailable",
                "fallback_applied": True,
            }

        try:
            self.integration_stats["total_calls"] += 1

            # Simulate notification API call
            await asyncio.sleep(0.05)  # Simulate network delay

            circuit_breaker.record_success()
            self.integration_stats["successful_calls"] += 1

            return {
                "success": True,
                "notification_id": f"notif_{user_id}_{int(datetime.utcnow().timestamp())}",
                "delivery_status": "sent",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            circuit_breaker.record_failure()
            self.integration_stats["failed_calls"] += 1

            return {"success": False, "error": str(e), "fallback_applied": True}

    async def check_service_health(self) -> Dict[str, Any]:
        """
        Check health of all integrated services.

        Returns:
            Service health status
        """
        health_results = {}
        overall_healthy = True

        for service_name in self.service_configs:
            try:
                # Simple health check - ping the service
                config = self.service_configs[service_name]
                health_url = f"{config['base_url']}/health"

                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as session:
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            health_results[service_name] = {
                                "status": "healthy",
                                "response_time": response.headers.get(
                                    "X-Response-Time", "unknown"
                                ),
                                "last_check": datetime.utcnow().isoformat(),
                            }
                        else:
                            health_results[service_name] = {
                                "status": "unhealthy",
                                "http_status": response.status,
                                "last_check": datetime.utcnow().isoformat(),
                            }
                            overall_healthy = False

            except Exception as e:
                health_results[service_name] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat(),
                }
                overall_healthy = False

        # Include circuit breaker status
        circuit_status = {}
        for service_name, breaker in self.circuit_breakers.items():
            circuit_status[service_name] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "last_failure": (
                    breaker.last_failure_time.isoformat()
                    if breaker.last_failure_time
                    else None
                ),
            }

        return {
            "overall_status": "healthy" if overall_healthy else "degraded",
            "services": health_results,
            "circuit_breakers": circuit_status,
            "integration_stats": self.integration_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # Fallback response methods
    def _get_fitness_fallback_response(
        self, user_id: str, data_type: str, error: str = None
    ) -> Dict[str, Any]:
        """Generate fallback response for fitness tracker data."""
        self.integration_stats["fallback_responses"] += 1

        fallback_data = {
            "weight": [{"date": "2024-01-01", "value": 70.0, "note": "Sample data"}],
            "steps": [{"date": "2024-01-01", "value": 8000, "note": "Sample data"}],
            "workouts": [{"date": "2024-01-01", "type": "strength", "duration": 45}],
        }

        return {
            "success": False,
            "message": "Fitness tracker service temporarily unavailable",
            "fallback_applied": True,
            "fallback_data": fallback_data.get(data_type, []),
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_nutrition_fallback_response(
        self, food_data: List[Dict[str, Any]], error: str = None
    ) -> Dict[str, Any]:
        """Generate fallback response for nutrition analysis."""
        self.integration_stats["fallback_responses"] += 1

        return {
            "success": False,
            "message": "Nutrition service temporarily unavailable",
            "fallback_applied": True,
            "fallback_analysis": {
                "total_calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "note": "Analysis unavailable - please try again later",
            },
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_body_analysis_fallback_response(
        self, analysis_type: str, error: str = None
    ) -> Dict[str, Any]:
        """Generate fallback response for body analysis."""
        self.integration_stats["fallback_responses"] += 1

        return {
            "success": False,
            "message": "Body analysis service temporarily unavailable",
            "fallback_applied": True,
            "fallback_analysis": {
                "analysis_type": analysis_type,
                "status": "service_unavailable",
                "note": "Please try uploading your image again later",
            },
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_workout_fallback_response(
        self, goals: List[str], error: str = None
    ) -> Dict[str, Any]:
        """Generate fallback response for workout recommendations."""
        self.integration_stats["fallback_responses"] += 1

        basic_workouts = [
            {"name": "Push-ups", "type": "strength", "difficulty": "beginner"},
            {"name": "Squats", "type": "strength", "difficulty": "beginner"},
            {"name": "Plank", "type": "core", "difficulty": "beginner"},
            {"name": "Walking", "type": "cardio", "difficulty": "beginner"},
        ]

        return {
            "success": False,
            "message": "Workout library temporarily unavailable",
            "fallback_applied": True,
            "recommendations": basic_workouts,
            "workout_plan": {
                "frequency": "3x per week",
                "duration": "30 minutes",
                "note": "Basic fallback routine",
            },
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration service statistics."""
        success_rate = (
            self.integration_stats["successful_calls"]
            / max(1, self.integration_stats["total_calls"])
        ) * 100

        return {
            **self.integration_stats,
            "success_rate": round(success_rate, 2),
            "circuit_breaker_status": {
                name: breaker.state.value
                for name, breaker in self.circuit_breakers.items()
            },
            "services_configured": len(self.service_configs),
            "last_health_check": (
                max(self.last_health_check.values()) if self.last_health_check else None
            ),
        }
