"""
Garmin Connect Integration Adapter

This module implements the Garmin Connect API integration for NGX Agents.
It provides OAuth2 authentication and data retrieval for various metrics.

Garmin API documentation: https://developer.garmin.com/connect-iq/
"""

import asyncio
import base64
import hashlib
import secrets
import urllib.parse
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import aiohttp
from pydantic import BaseModel


@dataclass
class GarminConfig:
    """Configuration for Garmin Connect API"""

    consumer_key: str
    consumer_secret: str
    redirect_uri: str
    base_url: str = "https://connect.garmin.com"
    api_url: str = "https://apis.garmin.com"


@dataclass
class GarminUserProfile:
    """Garmin user profile data"""

    user_id: str
    display_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    profile_image_url: Optional[str]
    gender: Optional[str]
    birth_date: Optional[date]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    email: Optional[str]


@dataclass
class GarminSleepData:
    """Garmin sleep data model"""

    sleep_id: str
    calendar_date: date
    sleep_start_time: datetime
    sleep_end_time: datetime
    sleep_duration_seconds: int
    unmeasurable_sleep_seconds: Optional[int]
    deep_sleep_seconds: Optional[int]
    light_sleep_seconds: Optional[int]
    rem_sleep_seconds: Optional[int]
    awake_seconds: Optional[int]
    sleep_quality_score: Optional[float]
    average_sp_o2: Optional[float]
    lowest_sp_o2: Optional[float]
    average_respiration: Optional[float]
    average_stress: Optional[float]
    rest_heart_rate: Optional[int]
    sleep_feedback: Optional[str]


@dataclass
class GarminActivityData:
    """Garmin activity data model"""

    activity_id: str
    activity_name: str
    activity_type: str
    start_time: datetime
    duration_seconds: int
    distance_meters: Optional[float]
    calories: Optional[int]
    active_calories: Optional[int]
    average_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    steps: Optional[int]
    elevation_gain_meters: Optional[float]
    average_speed_mps: Optional[float]
    max_speed_mps: Optional[float]
    average_power_watts: Optional[float]
    max_power_watts: Optional[float]
    training_effect: Optional[float]
    aerobic_training_effect: Optional[float]
    anaerobic_training_effect: Optional[float]
    activity_training_load: Optional[float]
    laps: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GarminBodyComposition:
    """Garmin body composition data"""

    measurement_date: date
    weight_kg: Optional[float]
    bmi: Optional[float]
    body_fat_percentage: Optional[float]
    body_water_percentage: Optional[float]
    muscle_mass_kg: Optional[float]
    bone_mass_kg: Optional[float]
    metabolic_age: Optional[int]
    visceral_fat_rating: Optional[int]
    physique_rating: Optional[int]


@dataclass
class GarminHeartRateData:
    """Garmin heart rate data"""

    timestamp: datetime
    heart_rate: int
    resting_heart_rate: Optional[int]
    heart_rate_variability: Optional[float]
    stress_level: Optional[int]


@dataclass
class GarminDailyStats:
    """Garmin daily statistics"""

    calendar_date: date
    total_steps: Optional[int]
    total_distance_meters: Optional[float]
    highly_active_minutes: Optional[int]
    active_calories: Optional[int]
    resting_calories: Optional[int]
    total_calories: Optional[int]
    floors_climbed: Optional[int]
    min_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    average_heart_rate: Optional[int]
    resting_heart_rate: Optional[int]
    stress_duration_seconds: Optional[int]
    average_stress_level: Optional[int]
    max_stress_level: Optional[int]
    body_battery_charged_value: Optional[int]
    body_battery_drained_value: Optional[int]
    body_battery_highest_value: Optional[int]
    body_battery_lowest_value: Optional[int]


class GarminAdapter:
    """
    Adapter for Garmin Connect API integration

    This adapter implements OAuth1 for Garmin Connect API and provides
    methods to retrieve various health and fitness data.
    """

    def __init__(self, config: GarminConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.access_token_secret: Optional[str] = None
        self.user_id: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def get_auth_url(self, state: Optional[str] = None) -> str:
        """
        Get the OAuth authorization URL for Garmin Connect

        Note: Garmin uses OAuth 1.0a, so the flow is different from OAuth 2.0

        Args:
            state: Optional state parameter for security

        Returns:
            The authorization URL
        """
        # For OAuth 1.0a, we need to get a request token first
        # This is a simplified version - actual implementation would need
        # proper OAuth 1.0a signature generation
        params = {
            "oauth_callback": self.config.redirect_uri,
            "oauth_consumer_key": self.config.consumer_key,
            "oauth_nonce": secrets.token_urlsafe(32),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(datetime.now().timestamp())),
            "oauth_version": "1.0",
        }

        # In a real implementation, we would:
        # 1. Generate OAuth signature
        # 2. Get request token from Garmin
        # 3. Return authorization URL with request token

        # For now, return a placeholder URL
        auth_url = f"{self.config.base_url}/oauthConfirm"
        if state:
            params["state"] = state

        return f"{auth_url}?{urllib.parse.urlencode(params)}"

    async def exchange_code_for_tokens(
        self, oauth_token: str, oauth_verifier: str
    ) -> Dict[str, Any]:
        """
        Exchange OAuth verifier for access tokens

        Args:
            oauth_token: The OAuth request token
            oauth_verifier: The OAuth verifier from callback

        Returns:
            Dictionary containing access tokens
        """
        # This would implement OAuth 1.0a token exchange
        # For now, return placeholder
        return {
            "access_token": "placeholder_access_token",
            "access_token_secret": "placeholder_access_token_secret",
            "user_id": "placeholder_user_id",
        }

    async def refresh_token(self) -> Dict[str, Any]:
        """
        Garmin OAuth 1.0a tokens don't expire, so no refresh needed

        Returns:
            Current token data
        """
        return {
            "access_token": self.access_token,
            "access_token_secret": self.access_token_secret,
            "user_id": self.user_id,
        }

    async def _make_request(
        self, endpoint: str, method: str = "GET", params: Optional[Dict] = None
    ) -> Union[Dict, List]:
        """
        Make authenticated request to Garmin API

        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters

        Returns:
            JSON response data
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        # OAuth 1.0a signature would be generated here
        headers = {
            "Authorization": f"OAuth oauth_consumer_key={self.config.consumer_key}",
            "Accept": "application/json",
        }

        url = f"{self.config.api_url}/{endpoint}"

        async with self.session.request(
            method, url, headers=headers, params=params
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_user_profile(self) -> GarminUserProfile:
        """
        Get user profile information

        Returns:
            User profile data
        """
        data = await self._make_request("wellness-api/rest/user/profile")

        return GarminUserProfile(
            user_id=data.get("userId", ""),
            display_name=data.get("displayName"),
            first_name=data.get("firstName"),
            last_name=data.get("lastName"),
            profile_image_url=data.get("profileImageUrl"),
            gender=data.get("gender"),
            birth_date=(
                datetime.fromisoformat(data["birthDate"]).date()
                if data.get("birthDate")
                else None
            ),
            height_cm=data.get("height"),
            weight_kg=data.get("weight"),
            email=data.get("email"),
        )

    async def get_sleep_data(
        self, start_date: date, end_date: Optional[date] = None
    ) -> List[GarminSleepData]:
        """
        Get sleep data for date range

        Args:
            start_date: Start date
            end_date: End date (optional, defaults to start_date)

        Returns:
            List of sleep data
        """
        if not end_date:
            end_date = start_date

        params = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }

        data = await self._make_request("wellness-api/rest/sleep/daily", params=params)

        sleep_list = []
        for item in data.get("sleeps", []):
            sleep_list.append(
                GarminSleepData(
                    sleep_id=item.get("id", ""),
                    calendar_date=date.fromisoformat(item["calendarDate"]),
                    sleep_start_time=datetime.fromisoformat(item["sleepStartTime"]),
                    sleep_end_time=datetime.fromisoformat(item["sleepEndTime"]),
                    sleep_duration_seconds=item.get("sleepDurationSeconds", 0),
                    unmeasurable_sleep_seconds=item.get("unmeasurableSleepSeconds"),
                    deep_sleep_seconds=item.get("deepSleepSeconds"),
                    light_sleep_seconds=item.get("lightSleepSeconds"),
                    rem_sleep_seconds=item.get("remSleepSeconds"),
                    awake_seconds=item.get("awakeSeconds"),
                    sleep_quality_score=item.get("sleepQualityScore"),
                    average_sp_o2=item.get("averageSpO2"),
                    lowest_sp_o2=item.get("lowestSpO2"),
                    average_respiration=item.get("averageRespiration"),
                    average_stress=item.get("averageStress"),
                    rest_heart_rate=item.get("restHeartRate"),
                    sleep_feedback=item.get("sleepFeedback"),
                )
            )

        return sleep_list

    async def get_activities(
        self, start_date: date, end_date: Optional[date] = None
    ) -> List[GarminActivityData]:
        """
        Get activity data for date range

        Args:
            start_date: Start date
            end_date: End date (optional, defaults to start_date)

        Returns:
            List of activities
        """
        if not end_date:
            end_date = start_date

        params = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }

        data = await self._make_request("wellness-api/rest/activities", params=params)

        activities = []
        for item in data.get("activities", []):
            activities.append(
                GarminActivityData(
                    activity_id=item.get("activityId", ""),
                    activity_name=item.get("activityName", ""),
                    activity_type=item.get("activityType", ""),
                    start_time=datetime.fromisoformat(item["startTime"]),
                    duration_seconds=item.get("durationSeconds", 0),
                    distance_meters=item.get("distanceMeters"),
                    calories=item.get("calories"),
                    active_calories=item.get("activeCalories"),
                    average_heart_rate=item.get("averageHeartRate"),
                    max_heart_rate=item.get("maxHeartRate"),
                    steps=item.get("steps"),
                    elevation_gain_meters=item.get("elevationGainMeters"),
                    average_speed_mps=item.get("averageSpeedMps"),
                    max_speed_mps=item.get("maxSpeedMps"),
                    average_power_watts=item.get("averagePowerWatts"),
                    max_power_watts=item.get("maxPowerWatts"),
                    training_effect=item.get("trainingEffect"),
                    aerobic_training_effect=item.get("aerobicTrainingEffect"),
                    anaerobic_training_effect=item.get("anaerobicTrainingEffect"),
                    activity_training_load=item.get("activityTrainingLoad"),
                    laps=item.get("laps", []),
                )
            )

        return activities

    async def get_body_composition(
        self, measurement_date: date
    ) -> Optional[GarminBodyComposition]:
        """
        Get body composition data for a specific date

        Args:
            measurement_date: Date of measurement

        Returns:
            Body composition data or None if not found
        """
        params = {"date": measurement_date.isoformat()}

        data = await self._make_request(
            "wellness-api/rest/weight/latest", params=params
        )

        if not data:
            return None

        return GarminBodyComposition(
            measurement_date=measurement_date,
            weight_kg=data.get("weight"),
            bmi=data.get("bmi"),
            body_fat_percentage=data.get("bodyFatPercentage"),
            body_water_percentage=data.get("bodyWaterPercentage"),
            muscle_mass_kg=data.get("muscleMass"),
            bone_mass_kg=data.get("boneMass"),
            metabolic_age=data.get("metabolicAge"),
            visceral_fat_rating=data.get("visceralFatRating"),
            physique_rating=data.get("physiqueRating"),
        )

    async def get_heart_rate_data(
        self, date: date, detailed: bool = False
    ) -> List[GarminHeartRateData]:
        """
        Get heart rate data for a specific date

        Args:
            date: Date to get data for
            detailed: Whether to get detailed minute-by-minute data

        Returns:
            List of heart rate data points
        """
        endpoint = (
            "wellness-api/rest/heartRate/detailed"
            if detailed
            else "wellness-api/rest/heartRate/daily"
        )

        params = {"date": date.isoformat()}
        data = await self._make_request(endpoint, params=params)

        hr_data = []
        for item in data.get("heartRateValues", []):
            hr_data.append(
                GarminHeartRateData(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    heart_rate=item.get("heartRate", 0),
                    resting_heart_rate=item.get("restingHeartRate"),
                    heart_rate_variability=item.get("heartRateVariability"),
                    stress_level=item.get("stressLevel"),
                )
            )

        return hr_data

    async def get_daily_stats(self, date: date) -> Optional[GarminDailyStats]:
        """
        Get aggregated daily statistics

        Args:
            date: Date to get stats for

        Returns:
            Daily statistics or None if not found
        """
        params = {"date": date.isoformat()}
        data = await self._make_request("wellness-api/rest/daily", params=params)

        if not data:
            return None

        return GarminDailyStats(
            calendar_date=date,
            total_steps=data.get("totalSteps"),
            total_distance_meters=data.get("totalDistanceMeters"),
            highly_active_minutes=data.get("highlyActiveMinutes"),
            active_calories=data.get("activeCalories"),
            resting_calories=data.get("restingCalories"),
            total_calories=data.get("totalCalories"),
            floors_climbed=data.get("floorsClimbed"),
            min_heart_rate=data.get("minHeartRate"),
            max_heart_rate=data.get("maxHeartRate"),
            average_heart_rate=data.get("averageHeartRate"),
            resting_heart_rate=data.get("restingHeartRate"),
            stress_duration_seconds=data.get("stressDurationSeconds"),
            average_stress_level=data.get("averageStressLevel"),
            max_stress_level=data.get("maxStressLevel"),
            body_battery_charged_value=data.get("bodyBatteryChargedValue"),
            body_battery_drained_value=data.get("bodyBatteryDrainedValue"),
            body_battery_highest_value=data.get("bodyBatteryHighestValue"),
            body_battery_lowest_value=data.get("bodyBatteryLowestValue"),
        )

    async def get_stress_data(
        self, start_date: date, end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get stress level data for date range

        Args:
            start_date: Start date
            end_date: End date (optional)

        Returns:
            List of stress data points
        """
        if not end_date:
            end_date = start_date

        params = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }

        return await self._make_request("wellness-api/rest/stress", params=params)

    async def get_body_battery(self, date: date) -> List[Dict[str, Any]]:
        """
        Get body battery data for a specific date

        Args:
            date: Date to get data for

        Returns:
            List of body battery data points
        """
        params = {"date": date.isoformat()}
        return await self._make_request("wellness-api/rest/bodyBattery", params=params)

    def set_tokens(
        self, access_token: str, access_token_secret: str, user_id: str
    ) -> None:
        """
        Set access tokens for authenticated requests

        Args:
            access_token: OAuth access token
            access_token_secret: OAuth access token secret
            user_id: User ID
        """
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.user_id = user_id
