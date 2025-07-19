"""
Oura Ring API Integration (v2)
Provides access to Oura sleep, activity, readiness, and heart rate data
Documentation: https://cloud.ouraring.com/v2/docs
"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import aiohttp
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@dataclass
class OuraConfig:
    """Oura API configuration"""

    client_id: str
    client_secret: str
    redirect_uri: str
    base_url: str = "https://api.ouraring.com"
    auth_url: str = "https://cloud.ouraring.com"


@dataclass
class OuraPersonalInfo:
    """Oura user personal information"""

    user_id: str
    age: Optional[int]
    weight: Optional[float]
    height: Optional[float]
    biological_sex: Optional[str]
    email: Optional[str]


@dataclass
class OuraSleepData:
    """Oura sleep data model"""

    sleep_id: str
    day: date
    bedtime_start: datetime
    bedtime_end: datetime
    average_breath: Optional[float]
    average_heart_rate: Optional[float]
    average_hrv: Optional[float]
    awake_time: Optional[int]
    deep_sleep_duration: Optional[int]
    efficiency: Optional[int]
    latency: Optional[int]
    light_sleep_duration: Optional[int]
    low_battery_alert: bool
    lowest_heart_rate: Optional[int]
    movement_30_sec: Optional[str]
    period_id: int
    readiness_score_delta: Optional[float]
    rem_sleep_duration: Optional[int]
    restless_periods: Optional[int]
    sleep_phase_5_min: Optional[str]
    sleep_score_delta: Optional[float]
    sleep_algorithm_version: Optional[str]
    time_in_bed: int
    total_sleep_duration: Optional[int]
    type: str


@dataclass
class OuraActivityData:
    """Oura activity data model"""

    activity_id: str
    day: date
    timestamp: datetime
    activity_type: str
    calories: Optional[int]
    distance: Optional[float]
    duration: Optional[int]
    steps: Optional[int]
    active_calories: Optional[int]
    average_met_minutes: Optional[float]
    contributors: Dict[str, Any]
    equivalent_walking_distance: Optional[int]
    high_activity_met_minutes: Optional[int]
    high_activity_time: Optional[int]
    inactivity_alerts: Optional[int]
    low_activity_met_minutes: Optional[int]
    low_activity_time: Optional[int]
    medium_activity_met_minutes: Optional[int]
    medium_activity_time: Optional[int]
    met: Dict[str, Any]
    meters_to_target: Optional[int]
    non_wear_time: Optional[int]
    resting_time: Optional[int]
    sedentary_met_minutes: Optional[int]
    sedentary_time: Optional[int]
    steps_to_target: Optional[int]
    target_calories: Optional[int]
    target_meters: Optional[int]
    total_calories: Optional[int]


@dataclass
class OuraReadinessData:
    """Oura readiness data model"""

    readiness_id: str
    day: date
    score: Optional[int]
    temperature_deviation: Optional[float]
    temperature_trend_deviation: Optional[float]
    timestamp: datetime
    contributors: Dict[str, Any]


@dataclass
class OuraHeartRateData:
    """Oura heart rate data model"""

    timestamp: datetime
    bpm: int
    source: str


class OuraAdapter:
    """
    Oura Ring API adapter for NGX Agents
    Handles OAuth authentication and data retrieval
    """

    def __init__(self, config: OuraConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def get_auth_url(self, state: str = None) -> str:
        """
        Generate OAuth authorization URL

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL for user to grant permissions
        """
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": "personal daily heartrate workout tag",
        }

        if state:
            params["state"] = state

        return f"{self.config.auth_url}/oauth/authorize?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token, refresh_token, expires_in
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use as async context manager.")

        data = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": self.config.redirect_uri,
            "code": code,
        }

        async with self.session.post(
            f"{self.config.base_url}/oauth/token", data=data
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(
                    f"Token exchange failed: {response.status} - {error_text}"
                )

            token_data = await response.json()

            # Store tokens
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]
            expires_in = token_data["expires_in"]
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            logger.info("Successfully exchanged code for Oura tokens")
            return token_data

    async def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh access token using refresh token

        Returns:
            New token response
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        if not self.session:
            raise RuntimeError("Session not initialized. Use as async context manager.")

        data = {
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "refresh_token": self.refresh_token,
        }

        async with self.session.post(
            f"{self.config.base_url}/oauth/token", data=data
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(
                    f"Token refresh failed: {response.status} - {error_text}"
                )

            token_data = await response.json()

            # Update tokens
            self.access_token = token_data["access_token"]
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]
            expires_in = token_data["expires_in"]
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            logger.info("Successfully refreshed Oura access token")
            return token_data

    async def _ensure_valid_token(self):
        """Ensure we have a valid access token, refresh if needed"""
        if not self.access_token:
            raise ValueError("No access token available. Complete OAuth flow first.")

        if self.token_expires_at and datetime.utcnow() >= self.token_expires_at:
            logger.info("Access token expired, refreshing...")
            await self.refresh_access_token()

    async def _make_request(
        self, endpoint: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated API request

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters

        Returns:
            API response data
        """
        await self._ensure_valid_token()

        if not self.session:
            raise RuntimeError("Session not initialized. Use as async context manager.")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        url = f"{self.config.base_url}{endpoint}"

        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status == 401:
                # Token might be expired, try to refresh
                logger.info("Received 401, attempting token refresh...")
                await self.refresh_access_token()
                headers["Authorization"] = f"Bearer {self.access_token}"

                # Retry request
                async with self.session.get(
                    url, headers=headers, params=params
                ) as retry_response:
                    if retry_response.status != 200:
                        error_text = await retry_response.text()
                        raise Exception(
                            f"API request failed after token refresh: {retry_response.status} - {error_text}"
                        )
                    return await retry_response.json()

            elif response.status != 200:
                error_text = await response.text()
                raise Exception(f"API request failed: {response.status} - {error_text}")

            return await response.json()

    async def get_personal_info(self) -> OuraPersonalInfo:
        """Get user personal information"""
        response = await self._make_request("/v2/usercollection/personal_info")

        return OuraPersonalInfo(
            user_id=response.get("id", ""),
            age=response.get("age"),
            weight=response.get("weight"),
            height=response.get("height"),
            biological_sex=response.get("biological_sex"),
            email=response.get("email"),
        )

    async def get_sleep_data(
        self, start_date: date = None, end_date: date = None
    ) -> List[OuraSleepData]:
        """
        Get sleep data for date range

        Args:
            start_date: Start date for data retrieval
            end_date: End date for data retrieval

        Returns:
            List of sleep records
        """
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = await self._make_request("/v2/usercollection/sleep", params)

        sleep_records = []
        for item in response.get("data", []):
            sleep = OuraSleepData(
                sleep_id=item["id"],
                day=date.fromisoformat(item["day"]),
                bedtime_start=datetime.fromisoformat(
                    item["bedtime_start"].replace("Z", "+00:00")
                ),
                bedtime_end=datetime.fromisoformat(
                    item["bedtime_end"].replace("Z", "+00:00")
                ),
                average_breath=item.get("average_breath"),
                average_heart_rate=item.get("average_heart_rate"),
                average_hrv=item.get("average_hrv"),
                awake_time=item.get("awake_time"),
                deep_sleep_duration=item.get("deep_sleep_duration"),
                efficiency=item.get("efficiency"),
                latency=item.get("latency"),
                light_sleep_duration=item.get("light_sleep_duration"),
                low_battery_alert=item.get("low_battery_alert", False),
                lowest_heart_rate=item.get("lowest_heart_rate"),
                movement_30_sec=item.get("movement_30_sec"),
                period_id=item.get("period_id", 0),
                readiness_score_delta=item.get("readiness_score_delta"),
                rem_sleep_duration=item.get("rem_sleep_duration"),
                restless_periods=item.get("restless_periods"),
                sleep_phase_5_min=item.get("sleep_phase_5_min"),
                sleep_score_delta=item.get("sleep_score_delta"),
                sleep_algorithm_version=item.get("sleep_algorithm_version"),
                time_in_bed=item.get("time_in_bed", 0),
                total_sleep_duration=item.get("total_sleep_duration"),
                type=item.get("type", "sleep"),
            )
            sleep_records.append(sleep)

        return sleep_records

    async def get_activity_data(
        self, start_date: date = None, end_date: date = None
    ) -> List[OuraActivityData]:
        """
        Get activity data for date range

        Args:
            start_date: Start date for data retrieval
            end_date: End date for data retrieval

        Returns:
            List of activity records
        """
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = await self._make_request("/v2/usercollection/daily_activity", params)

        activities = []
        for item in response.get("data", []):
            activity = OuraActivityData(
                activity_id=item["id"],
                day=date.fromisoformat(item["day"]),
                timestamp=datetime.fromisoformat(
                    item["timestamp"].replace("Z", "+00:00")
                ),
                activity_type=item.get("class_5_min", ""),
                calories=item.get("calories"),
                distance=item.get("distance"),
                duration=item.get("duration"),
                steps=item.get("steps"),
                active_calories=item.get("active_calories"),
                average_met_minutes=item.get("average_met_minutes"),
                contributors=item.get("contributors", {}),
                equivalent_walking_distance=item.get("equivalent_walking_distance"),
                high_activity_met_minutes=item.get("high_activity_met_minutes"),
                high_activity_time=item.get("high_activity_time"),
                inactivity_alerts=item.get("inactivity_alerts"),
                low_activity_met_minutes=item.get("low_activity_met_minutes"),
                low_activity_time=item.get("low_activity_time"),
                medium_activity_met_minutes=item.get("medium_activity_met_minutes"),
                medium_activity_time=item.get("medium_activity_time"),
                met=item.get("met", {}),
                meters_to_target=item.get("meters_to_target"),
                non_wear_time=item.get("non_wear_time"),
                resting_time=item.get("resting_time"),
                sedentary_met_minutes=item.get("sedentary_met_minutes"),
                sedentary_time=item.get("sedentary_time"),
                steps_to_target=item.get("steps_to_target"),
                target_calories=item.get("target_calories"),
                target_meters=item.get("target_meters"),
                total_calories=item.get("total_calories"),
            )
            activities.append(activity)

        return activities

    async def get_readiness_data(
        self, start_date: date = None, end_date: date = None
    ) -> List[OuraReadinessData]:
        """
        Get readiness data for date range

        Args:
            start_date: Start date for data retrieval
            end_date: End date for data retrieval

        Returns:
            List of readiness records
        """
        params = {}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = await self._make_request(
            "/v2/usercollection/daily_readiness", params
        )

        readiness_records = []
        for item in response.get("data", []):
            readiness = OuraReadinessData(
                readiness_id=item["id"],
                day=date.fromisoformat(item["day"]),
                score=item.get("score"),
                temperature_deviation=item.get("temperature_deviation"),
                temperature_trend_deviation=item.get("temperature_trend_deviation"),
                timestamp=datetime.fromisoformat(
                    item["timestamp"].replace("Z", "+00:00")
                ),
                contributors=item.get("contributors", {}),
            )
            readiness_records.append(readiness)

        return readiness_records

    async def get_heart_rate_data(
        self, start_datetime: datetime = None, end_datetime: datetime = None
    ) -> List[OuraHeartRateData]:
        """
        Get heart rate data for datetime range

        Args:
            start_datetime: Start datetime for data retrieval
            end_datetime: End datetime for data retrieval

        Returns:
            List of heart rate records
        """
        params = {}
        if start_datetime:
            params["start_datetime"] = start_datetime.isoformat()
        if end_datetime:
            params["end_datetime"] = end_datetime.isoformat()

        response = await self._make_request("/v2/usercollection/heartrate", params)

        heart_rates = []
        for item in response.get("data", []):
            hr = OuraHeartRateData(
                timestamp=datetime.fromisoformat(
                    item["timestamp"].replace("Z", "+00:00")
                ),
                bpm=item["bpm"],
                source=item.get("source", "unknown"),
            )
            heart_rates.append(hr)

        return heart_rates


# Example usage
async def example_usage():
    """Example of how to use the Oura adapter"""
    config = OuraConfig(
        client_id="your_client_id",
        client_secret="your_client_secret",
        redirect_uri="http://localhost:8000/wearables/auth/oura/callback",
    )

    async with OuraAdapter(config) as oura:
        # Step 1: Get authorization URL
        auth_url = oura.get_auth_url(state="random_state_string")
        print(f"Visit this URL to authorize: {auth_url}")

        # Step 2: After user authorizes, exchange code for tokens
        # authorization_code = "code_from_callback"
        # await oura.exchange_code_for_tokens(authorization_code)

        # Step 3: Get user data
        # personal_info = await oura.get_personal_info()
        # sleep_data = await oura.get_sleep_data()
        # activity_data = await oura.get_activity_data()
        # readiness_data = await oura.get_readiness_data()

        print("Oura integration ready!")


if __name__ == "__main__":
    asyncio.run(example_usage())
