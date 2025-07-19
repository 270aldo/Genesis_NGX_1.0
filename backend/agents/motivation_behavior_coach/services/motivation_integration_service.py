"""
Integration service for SPARK Motivation Behavior Coach.
Provides external API integrations and service coordination.
"""

import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from core.logging_config import get_logger

logger = get_logger(__name__)


class IntegrationStatus(Enum):
    """Status of external integrations."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass
class ExternalService:
    """Configuration for external service."""

    name: str
    endpoint: str
    timeout_seconds: int
    retry_attempts: int
    circuit_breaker_threshold: int
    health_check_interval: int


class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution."""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if (
                self.last_failure_time
                and time.time() - self.last_failure_time > self.timeout_seconds
            ):
                self.state = "half-open"
                return True
            return False
        elif self.state == "half-open":
            return True
        return False

    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class MotivationIntegrationService:
    """
    Integration service for external APIs and services.

    Provides robust integration with external motivation and behavioral
    services including fitness trackers, wellness apps, and coaching platforms.
    """

    def __init__(self):
        """
        Initialize integration service.
        """
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.service_configs: Dict[str, ExternalService] = {}
        self.integration_cache: Dict[str, tuple] = {}  # (data, timestamp)
        self.cache_ttl_seconds = 300  # 5 minutes

        # Initialize external service configurations
        self._initialize_service_configs()

        logger.info("MotivationIntegrationService initialized")

    def _initialize_service_configs(self):
        """Initialize configurations for external services."""
        self.service_configs = {
            "fitness_tracker": ExternalService(
                name="Fitness Tracker API",
                endpoint="https://api.fitnesstracker.com/v1",
                timeout_seconds=10,
                retry_attempts=2,
                circuit_breaker_threshold=3,
                health_check_interval=60,
            ),
            "wellness_platform": ExternalService(
                name="Wellness Platform API",
                endpoint="https://api.wellnessplatform.com/v2",
                timeout_seconds=15,
                retry_attempts=3,
                circuit_breaker_threshold=5,
                health_check_interval=120,
            ),
            "coaching_service": ExternalService(
                name="Coaching Service API",
                endpoint="https://api.coachingservice.com/v1",
                timeout_seconds=20,
                retry_attempts=2,
                circuit_breaker_threshold=4,
                health_check_interval=90,
            ),
            "notification_service": ExternalService(
                name="Notification Service",
                endpoint="https://api.notifications.internal/v1",
                timeout_seconds=5,
                retry_attempts=1,
                circuit_breaker_threshold=2,
                health_check_interval=30,
            ),
        }

        # Initialize circuit breakers
        for service_name, config in self.service_configs.items():
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=config.circuit_breaker_threshold, timeout_seconds=60
            )

    async def get_user_fitness_data(
        self, user_id: str, date_range: Optional[int] = 7
    ) -> Dict[str, Any]:
        """
        Get fitness data from external fitness tracker.

        Args:
            user_id: User identifier
            date_range: Number of days to retrieve (default: 7)

        Returns:
            Dict containing fitness data or error information
        """
        service_name = "fitness_tracker"
        cache_key = f"fitness_data_{user_id}_{date_range}"

        try:
            # Check cache first
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data

            # Check circuit breaker
            if not self.circuit_breakers[service_name].can_execute():
                return self._create_fallback_response(
                    "fitness_data", "Service temporarily unavailable"
                )

            # Make API call
            config = self.service_configs[service_name]
            url = f"{config.endpoint}/users/{user_id}/fitness"
            params = {"days": date_range}

            fitness_data = await self._make_api_call(
                service_name=service_name,
                url=url,
                params=params,
                timeout=config.timeout_seconds,
            )

            if fitness_data.get("success"):
                # Cache successful response
                self._store_in_cache(cache_key, fitness_data)
                return fitness_data
            else:
                return self._create_fallback_response(
                    "fitness_data", "Failed to retrieve fitness data"
                )

        except Exception as e:
            logger.error(f"Error getting fitness data: {str(e)}")
            return self._create_fallback_response("fitness_data", f"Error: {str(e)}")

    async def sync_motivation_data(
        self, user_id: str, motivation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sync motivation data with external wellness platform.

        Args:
            user_id: User identifier
            motivation_data: Motivation data to sync

        Returns:
            Dict containing sync results
        """
        service_name = "wellness_platform"

        try:
            # Check circuit breaker
            if not self.circuit_breakers[service_name].can_execute():
                return {
                    "success": False,
                    "message": "Sync service temporarily unavailable",
                    "fallback_applied": True,
                }

            # Prepare data for sync
            sync_payload = {
                "user_id": user_id,
                "data_type": "motivation_metrics",
                "timestamp": datetime.utcnow().isoformat(),
                "data": motivation_data,
            }

            # Make API call
            config = self.service_configs[service_name]
            url = f"{config.endpoint}/sync/motivation"

            result = await self._make_api_call(
                service_name=service_name,
                url=url,
                method="POST",
                json_data=sync_payload,
                timeout=config.timeout_seconds,
            )

            return result

        except Exception as e:
            logger.error(f"Error syncing motivation data: {str(e)}")
            return {
                "success": False,
                "message": f"Sync failed: {str(e)}",
                "error": True,
            }

    async def request_coaching_intervention(
        self, user_id: str, intervention_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Request coaching intervention from external coaching service.

        Args:
            user_id: User identifier
            intervention_type: Type of coaching intervention needed
            context: Context information for the intervention

        Returns:
            Dict containing intervention response
        """
        service_name = "coaching_service"

        try:
            # Check circuit breaker
            if not self.circuit_breakers[service_name].can_execute():
                return self._create_fallback_coaching_response(intervention_type)

            # Prepare intervention request
            request_payload = {
                "user_id": user_id,
                "intervention_type": intervention_type,
                "context": context,
                "timestamp": datetime.utcnow().isoformat(),
                "requester": "spark_motivation_coach",
            }

            # Make API call
            config = self.service_configs[service_name]
            url = f"{config.endpoint}/interventions/request"

            result = await self._make_api_call(
                service_name=service_name,
                url=url,
                method="POST",
                json_data=request_payload,
                timeout=config.timeout_seconds,
            )

            return result

        except Exception as e:
            logger.error(f"Error requesting coaching intervention: {str(e)}")
            return self._create_fallback_coaching_response(intervention_type)

    async def send_motivation_reminder(
        self,
        user_id: str,
        reminder_type: str,
        message: str,
        schedule_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Send motivation reminder through notification service.

        Args:
            user_id: User identifier
            reminder_type: Type of reminder
            message: Reminder message
            schedule_time: When to send the reminder (optional)

        Returns:
            Dict containing notification result
        """
        service_name = "notification_service"

        try:
            # Check circuit breaker
            if not self.circuit_breakers[service_name].can_execute():
                return {
                    "success": False,
                    "message": "Notification service temporarily unavailable",
                    "fallback_applied": True,
                }

            # Prepare notification payload
            notification_payload = {
                "user_id": user_id,
                "type": "motivation_reminder",
                "subtype": reminder_type,
                "message": message,
                "schedule_time": schedule_time.isoformat() if schedule_time else None,
                "sender": "spark_motivation_coach",
            }

            # Make API call
            config = self.service_configs[service_name]
            url = f"{config.endpoint}/notifications/send"

            result = await self._make_api_call(
                service_name=service_name,
                url=url,
                method="POST",
                json_data=notification_payload,
                timeout=config.timeout_seconds,
            )

            return result

        except Exception as e:
            logger.error(f"Error sending motivation reminder: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send reminder: {str(e)}",
                "error": True,
            }

    async def _make_api_call(
        self,
        service_name: str,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        timeout: int = 10,
    ) -> Dict[str, Any]:
        """
        Make API call with circuit breaker protection.

        Args:
            service_name: Name of the service
            url: API endpoint URL
            method: HTTP method
            params: Query parameters
            json_data: JSON payload for POST requests
            timeout: Request timeout

        Returns:
            Dict containing API response
        """
        circuit_breaker = self.circuit_breakers[service_name]

        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(
                        url, params=params, timeout=timeout
                    ) as response:
                        result = await response.json()
                elif method.upper() == "POST":
                    async with session.post(
                        url, json=json_data, timeout=timeout
                    ) as response:
                        result = await response.json()
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Record success
                circuit_breaker.record_success()

                return result

        except Exception as e:
            # Record failure
            circuit_breaker.record_failure()
            logger.error(f"API call failed for {service_name}: {str(e)}")
            raise

    def _create_fallback_response(self, data_type: str, message: str) -> Dict[str, Any]:
        """Create fallback response when external service is unavailable."""
        return {
            "success": False,
            "data_type": data_type,
            "message": message,
            "fallback_applied": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _create_fallback_coaching_response(
        self, intervention_type: str
    ) -> Dict[str, Any]:
        """Create fallback coaching response."""
        fallback_interventions = {
            "motivation_boost": {
                "message": "Remember your goals and take one small step forward today.",
                "actions": [
                    "Review your progress",
                    "Celebrate small wins",
                    "Take a mindful break",
                ],
            },
            "habit_reinforcement": {
                "message": "Consistency builds lasting change. Focus on your daily routine.",
                "actions": [
                    "Complete your habit check-in",
                    "Plan tomorrow's routine",
                    "Reflect on your progress",
                ],
            },
            "obstacle_support": {
                "message": "Challenges are opportunities to grow stronger. You've got this.",
                "actions": [
                    "Break the problem into smaller parts",
                    "Ask for support",
                    "Try a different approach",
                ],
            },
        }

        default_response = {
            "message": "Stay focused on your goals and trust the process.",
            "actions": [
                "Take a deep breath",
                "Review your why",
                "Take one positive action",
            ],
        }

        intervention = fallback_interventions.get(intervention_type, default_response)

        return {
            "success": True,
            "intervention_type": intervention_type,
            "response": intervention,
            "fallback_applied": True,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from integration cache."""
        if key in self.integration_cache:
            data, timestamp = self.integration_cache[key]
            if time.time() - timestamp < self.cache_ttl_seconds:
                return data
            else:
                del self.integration_cache[key]
        return None

    def _store_in_cache(self, key: str, data: Dict[str, Any]):
        """Store data in integration cache."""
        self.integration_cache[key] = (data, time.time())

    async def check_service_health(
        self, service_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check health status of external services.

        Args:
            service_name: Specific service to check (optional)

        Returns:
            Dict containing health status
        """
        if service_name:
            services_to_check = (
                [service_name] if service_name in self.service_configs else []
            )
        else:
            services_to_check = list(self.service_configs.keys())

        health_status = {}

        for service in services_to_check:
            circuit_breaker = self.circuit_breakers[service]
            config = self.service_configs[service]

            if circuit_breaker.state == "open":
                status = IntegrationStatus.UNAVAILABLE
            elif circuit_breaker.state == "half-open":
                status = IntegrationStatus.DEGRADED
            else:
                try:
                    # Perform basic health check
                    health_url = f"{config.endpoint}/health"
                    result = await self._make_api_call(
                        service_name=service, url=health_url, timeout=5
                    )
                    status = (
                        IntegrationStatus.HEALTHY
                        if result.get("healthy")
                        else IntegrationStatus.DEGRADED
                    )
                except Exception:
                    status = IntegrationStatus.ERROR

            health_status[service] = {
                "status": status.value,
                "circuit_breaker_state": circuit_breaker.state,
                "failure_count": circuit_breaker.failure_count,
                "last_check": datetime.utcnow().isoformat(),
            }

        return {
            "overall_status": self._calculate_overall_status(health_status),
            "services": health_status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_overall_status(self, service_statuses: Dict[str, Dict]) -> str:
        """Calculate overall integration status."""
        status_counts = {}
        for service_status in service_statuses.values():
            status = service_status["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        if status_counts.get("error", 0) > 0 or status_counts.get("unavailable", 0) > 2:
            return "critical"
        elif status_counts.get("degraded", 0) > 1:
            return "degraded"
        elif all(status == "healthy" for status in status_counts.keys()):
            return "healthy"
        else:
            return "degraded"

    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get current integration service status.

        Returns:
            Dict containing service status information
        """
        return {
            "configured_services": len(self.service_configs),
            "active_circuit_breakers": len(self.circuit_breakers),
            "cache_entries": len(self.integration_cache),
            "service_status": "operational",
        }
