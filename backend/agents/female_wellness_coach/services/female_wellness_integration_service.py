"""
Female Wellness Integration Service for LUNA Female Wellness Specialist.
Handles integrations with health APIs, wearable devices, and external wellness platforms.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json

from agents.female_wellness_coach.core.config import LunaConfig
from agents.female_wellness_coach.core.exceptions import (
    ExternalWellnessServiceError,
    LunaValidationError,
)
from agents.female_wellness_coach.core.constants import SERVICE_TIMEOUTS
from core.logging_config import get_logger

logger = get_logger(__name__)


class FemaleWellnessIntegrationService:
    """
    Integration service for external wellness platforms and devices.

    Features:
    - Wearable device data synchronization
    - Health app integrations (Clue, Flo, Apple Health)
    - ElevenLabs voice synthesis integration
    - Circuit breaker pattern for external APIs
    - Data normalization and validation
    """

    def __init__(self, config: LunaConfig):
        self.config = config
        self._session = None
        self._circuit_breakers = {}
        self._integration_cache = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the integration service."""
        try:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30.0),
                headers={"User-Agent": "LUNA-Female-Wellness-Specialist/2.0.0"},
            )

            # Initialize circuit breakers for external services
            await self._initialize_circuit_breakers()

            self._integration_cache = {}
            self._initialized = True

            logger.info("Female wellness integration service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize integration service: {e}")
            raise ExternalWellnessServiceError(
                f"Integration service initialization failed: {e}",
                service_name="initialization",
            )

    async def _initialize_circuit_breakers(self) -> None:
        """Initialize circuit breakers for external services."""
        services = [
            "elevenlabs",
            "apple_health",
            "google_fit",
            "fitbit",
            "garmin",
            "clue_app",
            "flo_app",
            "oura_ring",
        ]

        for service in services:
            self._circuit_breakers[service] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure": None,
                "timeout": 60,  # seconds before trying again
            }

    async def synthesize_voice_response(
        self, text: str, voice_settings: Optional[Dict[str, Any]] = None
    ) -> Optional[bytes]:
        """
        Synthesize voice response using ElevenLabs API.

        Args:
            text: Text to synthesize
            voice_settings: Optional voice configuration

        Returns:
            Optional[bytes]: Audio data or None if synthesis fails
        """
        if not self.config.enable_voice_synthesis:
            return None

        try:
            # Check circuit breaker
            if not await self._check_circuit_breaker("elevenlabs"):
                logger.warning("ElevenLabs circuit breaker is open")
                return None

            # Default voice settings for maternal, warm tone
            default_settings = {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Example voice ID
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": self.config.voice_stability,
                    "similarity_boost": self.config.voice_clarity,
                    "style": 0.6,
                    "use_speaker_boost": True,
                },
            }

            # Merge with provided settings
            if voice_settings:
                default_settings["voice_settings"].update(voice_settings)

            # Prepare request
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{default_settings['voice_id']}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": "your-elevenlabs-api-key",  # Would come from environment
            }

            payload = {
                "text": text,
                "model_id": default_settings["model_id"],
                "voice_settings": default_settings["voice_settings"],
            }

            async with self._session.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.config.elevenlabs_timeout,
            ) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    await self._record_success("elevenlabs")
                    return audio_data
                else:
                    await self._record_failure("elevenlabs")
                    logger.error(f"ElevenLabs API error: {response.status}")
                    return None

        except asyncio.TimeoutError:
            await self._record_failure("elevenlabs")
            logger.error("ElevenLabs API timeout")
            return None
        except Exception as e:
            await self._record_failure("elevenlabs")
            logger.error(f"Voice synthesis failed: {e}")
            return None

    async def sync_apple_health_data(self, user_id: str) -> Dict[str, Any]:
        """
        Sync data from Apple Health (via HealthKit).

        Args:
            user_id: User identifier

        Returns:
            Dict[str, Any]: Synchronized health data
        """
        try:
            if not await self._check_circuit_breaker("apple_health"):
                raise ExternalWellnessServiceError(
                    "Apple Health integration temporarily unavailable",
                    service_name="apple_health",
                )

            # In a real implementation, this would integrate with HealthKit
            # For now, return mock data structure
            mock_data = {
                "menstrual_flow": {
                    "last_period_start": "2024-01-15",
                    "cycle_length_average": 28,
                    "flow_data": ["light", "medium", "heavy", "medium", "light"],
                },
                "symptoms": [
                    {"date": "2024-01-15", "symptoms": ["cramping", "fatigue"]},
                    {"date": "2024-01-16", "symptoms": ["mood_changes"]},
                ],
                "body_measurements": {
                    "weight": 65.5,
                    "bmi": 22.1,
                    "body_fat_percentage": 18.5,
                },
                "activity_data": {
                    "steps_today": 8543,
                    "active_minutes": 45,
                    "calories_burned": 1850,
                },
                "sleep_data": {
                    "hours_last_night": 7.5,
                    "sleep_quality": "good",
                    "deep_sleep_percentage": 23,
                },
                "sync_timestamp": datetime.utcnow().isoformat(),
            }

            await self._record_success("apple_health")
            return mock_data

        except Exception as e:
            await self._record_failure("apple_health")
            logger.error(f"Apple Health sync failed: {e}")
            raise ExternalWellnessServiceError(
                f"Failed to sync Apple Health data: {e}",
                service_name="apple_health",
            )

    async def sync_fitbit_data(self, user_id: str, access_token: str) -> Dict[str, Any]:
        """
        Sync data from Fitbit API.

        Args:
            user_id: User identifier
            access_token: Fitbit API access token

        Returns:
            Dict[str, Any]: Fitbit data
        """
        try:
            if not await self._check_circuit_breaker("fitbit"):
                raise ExternalWellnessServiceError(
                    "Fitbit integration temporarily unavailable",
                    service_name="fitbit",
                )

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }

            # Sync multiple data types
            data_endpoints = {
                "heart_rate": "activities/heart/date/today/1d.json",
                "sleep": "sleep/date/today.json",
                "activity": "activities/date/today.json",
                "body_weight": "body/weight/date/today.json",
            }

            sync_results = {}

            for data_type, endpoint in data_endpoints.items():
                try:
                    url = f"https://api.fitbit.com/1/user/-/{endpoint}"
                    async with self._session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            sync_results[data_type] = data
                        else:
                            logger.warning(
                                f"Fitbit {data_type} sync failed: {response.status}"
                            )
                            sync_results[data_type] = None

                except Exception as e:
                    logger.error(f"Failed to sync {data_type} from Fitbit: {e}")
                    sync_results[data_type] = None

            # Normalize data format
            normalized_data = await self._normalize_fitbit_data(sync_results)

            await self._record_success("fitbit")
            return normalized_data

        except Exception as e:
            await self._record_failure("fitbit")
            logger.error(f"Fitbit sync failed: {e}")
            raise ExternalWellnessServiceError(
                f"Failed to sync Fitbit data: {e}",
                service_name="fitbit",
            )

    async def sync_period_tracking_app(
        self, user_id: str, app_name: str, app_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sync data from period tracking apps (Clue, Flo, etc.).

        Args:
            user_id: User identifier
            app_name: Name of the tracking app
            app_data: App-specific data

        Returns:
            Dict[str, Any]: Normalized cycle data
        """
        try:
            if not await self._check_circuit_breaker(f"{app_name}_app"):
                raise ExternalWellnessServiceError(
                    f"{app_name} integration temporarily unavailable",
                    service_name=f"{app_name}_app",
                )

            # Normalize data based on app format
            if app_name.lower() == "clue":
                normalized_data = await self._normalize_clue_data(app_data)
            elif app_name.lower() == "flo":
                normalized_data = await self._normalize_flo_data(app_data)
            else:
                # Generic normalization
                normalized_data = await self._normalize_generic_cycle_data(app_data)

            # Add metadata
            normalized_data.update(
                {
                    "source_app": app_name,
                    "sync_timestamp": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                }
            )

            await self._record_success(f"{app_name}_app")
            return normalized_data

        except Exception as e:
            await self._record_failure(f"{app_name}_app")
            logger.error(f"Period tracking app sync failed: {e}")
            raise ExternalWellnessServiceError(
                f"Failed to sync {app_name} data: {e}",
                service_name=f"{app_name}_app",
            )

    async def _normalize_fitbit_data(
        self, fitbit_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize Fitbit data to standard format."""
        normalized = {
            "heart_rate": None,
            "sleep_hours": None,
            "steps": None,
            "calories": None,
            "weight": None,
        }

        # Extract heart rate data
        if fitbit_data.get("heart_rate"):
            hr_data = fitbit_data["heart_rate"]
            if "activities-heart" in hr_data:
                normalized["heart_rate"] = (
                    hr_data["activities-heart"][0]
                    .get("value", {})
                    .get("restingHeartRate")
                )

        # Extract sleep data
        if fitbit_data.get("sleep"):
            sleep_data = fitbit_data["sleep"]
            if "sleep" in sleep_data and sleep_data["sleep"]:
                sleep_minutes = sleep_data["sleep"][0].get("minutesAsleep", 0)
                normalized["sleep_hours"] = sleep_minutes / 60

        # Extract activity data
        if fitbit_data.get("activity"):
            activity_data = fitbit_data["activity"]
            if "summary" in activity_data:
                summary = activity_data["summary"]
                normalized["steps"] = summary.get("steps")
                normalized["calories"] = summary.get("caloriesOut")

        # Extract weight data
        if fitbit_data.get("body_weight"):
            weight_data = fitbit_data["body_weight"]
            if "body-weight" in weight_data and weight_data["body-weight"]:
                normalized["weight"] = weight_data["body-weight"][0].get("value")

        return normalized

    async def _normalize_clue_data(self, clue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Clue app data to standard format."""
        return {
            "cycles": clue_data.get("cycles", []),
            "symptoms": clue_data.get("symptoms", []),
            "moods": clue_data.get("moods", []),
            "flow_intensity": clue_data.get("flow", []),
            "app_specific": {
                "pill_reminder": clue_data.get("pill_reminder"),
                "fertility_window": clue_data.get("fertility_window"),
            },
        }

    async def _normalize_flo_data(self, flo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Flo app data to standard format."""
        return {
            "cycles": flo_data.get("periods", []),
            "symptoms": flo_data.get("symptoms", []),
            "moods": flo_data.get("mood_tracking", []),
            "flow_intensity": flo_data.get("flow_tracking", []),
            "app_specific": {
                "pregnancy_mode": flo_data.get("pregnancy_mode"),
                "cycle_predictions": flo_data.get("predictions"),
            },
        }

    async def _normalize_generic_cycle_data(
        self, app_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generic normalization for unknown cycle tracking apps."""
        return {
            "raw_data": app_data,
            "extraction_needed": True,
            "manual_review_required": True,
        }

    async def _check_circuit_breaker(self, service_name: str) -> bool:
        """Check if circuit breaker allows requests to service."""
        if service_name not in self._circuit_breakers:
            return True

        breaker = self._circuit_breakers[service_name]

        if breaker["state"] == "closed":
            return True
        elif breaker["state"] == "open":
            # Check if timeout has passed
            if breaker["last_failure"]:
                time_since_failure = datetime.utcnow() - breaker["last_failure"]
                if time_since_failure.total_seconds() > breaker["timeout"]:
                    # Move to half-open state
                    breaker["state"] = "half_open"
                    return True
            return False
        else:  # half_open
            return True

    async def _record_success(self, service_name: str) -> None:
        """Record successful API call and reset circuit breaker."""
        if service_name in self._circuit_breakers:
            self._circuit_breakers[service_name].update(
                {
                    "state": "closed",
                    "failure_count": 0,
                    "last_failure": None,
                }
            )

    async def _record_failure(self, service_name: str) -> None:
        """Record API failure and update circuit breaker."""
        if service_name not in self._circuit_breakers:
            return

        breaker = self._circuit_breakers[service_name]
        breaker["failure_count"] += 1
        breaker["last_failure"] = datetime.utcnow()

        # Open circuit breaker after 3 failures
        if breaker["failure_count"] >= 3:
            breaker["state"] = "open"
            logger.warning(f"Circuit breaker opened for {service_name}")

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations."""
        status = {
            "initialized": self._initialized,
            "circuit_breakers": {},
            "last_sync_times": {},
            "available_integrations": [
                "elevenlabs_voice",
                "apple_health",
                "fitbit",
                "garmin",
                "clue_app",
                "flo_app",
                "oura_ring",
            ],
        }

        # Get circuit breaker status
        for service, breaker in self._circuit_breakers.items():
            status["circuit_breakers"][service] = {
                "state": breaker["state"],
                "failure_count": breaker["failure_count"],
                "last_failure": (
                    breaker["last_failure"].isoformat()
                    if breaker["last_failure"]
                    else None
                ),
            }

        return status

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._session and not self._session.closed:
            await self._session.close()

        logger.info("Female wellness integration service cleaned up")
