"""
Tests for Garmin Connect Integration
"""

import pytest
from datetime import datetime, timedelta, date
from unittest.mock import AsyncMock, MagicMock, patch

from integrations.wearables.adapters.garmin import (
    GarminAdapter,
    GarminConfig,
    GarminUserProfile,
    GarminSleepData,
    GarminActivityData,
    GarminBodyComposition,
    GarminDailyStats,
)
from integrations.wearables.normalizer import WearableDevice, WearableDataNormalizer
from integrations.wearables.service import WearableIntegrationService


@pytest.fixture
def garmin_config():
    """Create test Garmin configuration"""
    return GarminConfig(
        consumer_key="test_consumer_key",
        consumer_secret="test_consumer_secret",
        redirect_uri="http://localhost:8000/wearables/auth/garmin/callback",
    )


@pytest.fixture
def mock_garmin_user_profile():
    """Create mock Garmin user profile"""
    return GarminUserProfile(
        user_id="garmin_test_user_123",
        display_name="Test User",
        first_name="Test",
        last_name="User",
        profile_image_url="https://garmin.com/profile/123.jpg",
        gender="male",
        birth_date=date(1990, 1, 1),
        height_cm=180.0,
        weight_kg=75.0,
        email="test@example.com",
    )


@pytest.fixture
def mock_garmin_sleep_data():
    """Create mock Garmin sleep data"""
    return GarminSleepData(
        sleep_id="sleep_123",
        calendar_date=date(2025, 1, 26),
        sleep_start_time=datetime(2025, 1, 26, 23, 0, 0),
        sleep_end_time=datetime(2025, 1, 27, 7, 0, 0),
        sleep_duration_seconds=28800,  # 8 hours
        unmeasurable_sleep_seconds=300,
        deep_sleep_seconds=5400,  # 90 minutes
        light_sleep_seconds=14400,  # 240 minutes
        rem_sleep_seconds=5400,  # 90 minutes
        awake_seconds=1800,  # 30 minutes
        sleep_quality_score=82.0,
        average_sp_o2=96.5,
        lowest_sp_o2=94.0,
        average_respiration=14.5,
        average_stress=25.0,
        rest_heart_rate=52,
        sleep_feedback="Good recovery sleep",
    )


@pytest.fixture
def mock_garmin_activity_data():
    """Create mock Garmin activity data"""
    return GarminActivityData(
        activity_id="activity_123",
        activity_name="Morning Run",
        activity_type="running",
        start_time=datetime(2025, 1, 26, 7, 0, 0),
        duration_seconds=3600,  # 1 hour
        distance_meters=10000.0,  # 10 km
        calories=650,
        active_calories=580,
        average_heart_rate=145,
        max_heart_rate=172,
        steps=12000,
        elevation_gain_meters=120.0,
        average_speed_mps=2.78,  # 10 km/h
        max_speed_mps=3.33,  # 12 km/h
        average_power_watts=250.0,
        max_power_watts=320.0,
        training_effect=3.5,
        aerobic_training_effect=3.2,
        anaerobic_training_effect=2.1,
        activity_training_load=85.0,
    )


@pytest.fixture
def mock_garmin_body_composition():
    """Create mock Garmin body composition data"""
    return GarminBodyComposition(
        measurement_date=date(2025, 1, 26),
        weight_kg=75.5,
        bmi=23.5,
        body_fat_percentage=15.5,
        body_water_percentage=62.0,
        muscle_mass_kg=60.0,
        bone_mass_kg=3.5,
        metabolic_age=28,
        visceral_fat_rating=5,
        physique_rating=7,
    )


@pytest.fixture
def mock_garmin_daily_stats():
    """Create mock Garmin daily stats"""
    return GarminDailyStats(
        calendar_date=date(2025, 1, 26),
        total_steps=15000,
        total_distance_meters=12000.0,
        highly_active_minutes=45,
        active_calories=650,
        resting_calories=1800,
        total_calories=2450,
        floors_climbed=10,
        min_heart_rate=48,
        max_heart_rate=172,
        average_heart_rate=72,
        resting_heart_rate=52,
        stress_duration_seconds=14400,  # 4 hours
        average_stress_level=35,
        max_stress_level=75,
        body_battery_charged_value=45,
        body_battery_drained_value=55,
        body_battery_highest_value=85,
        body_battery_lowest_value=25,
    )


class TestGarminAdapter:
    """Test Garmin adapter functionality"""

    @pytest.mark.asyncio
    async def test_get_auth_url(self, garmin_config):
        """Test OAuth URL generation"""
        adapter = GarminAdapter(garmin_config)
        auth_url = adapter.get_auth_url(state="test_state_123")

        assert "oauthConfirm" in auth_url
        assert "oauth_consumer_key=test_consumer_key" in auth_url
        assert "oauth_callback=" in auth_url
        assert "state=test_state_123" in auth_url

    @pytest.mark.asyncio
    async def test_get_user_profile(self, garmin_config, mock_garmin_user_profile):
        """Test getting user profile"""
        mock_response = {
            "userId": "garmin_test_user_123",
            "displayName": "Test User",
            "firstName": "Test",
            "lastName": "User",
            "profileImageUrl": "https://garmin.com/profile/123.jpg",
            "gender": "male",
            "birthDate": "1990-01-01",
            "height": 180.0,
            "weight": 75.0,
            "email": "test@example.com",
        }

        with patch.object(
            GarminAdapter, "_make_request", new=AsyncMock(return_value=mock_response)
        ):
            async with GarminAdapter(garmin_config) as adapter:
                adapter.access_token = "test_token"
                user_profile = await adapter.get_user_profile()

                assert user_profile.user_id == mock_garmin_user_profile.user_id
                assert (
                    user_profile.display_name == mock_garmin_user_profile.display_name
                )
                assert user_profile.weight_kg == mock_garmin_user_profile.weight_kg

    @pytest.mark.asyncio
    async def test_get_sleep_data(self, garmin_config, mock_garmin_sleep_data):
        """Test getting sleep data"""
        mock_response = {
            "sleeps": [
                {
                    "id": "sleep_123",
                    "calendarDate": "2025-01-26",
                    "sleepStartTime": "2025-01-26T23:00:00Z",
                    "sleepEndTime": "2025-01-27T07:00:00Z",
                    "sleepDurationSeconds": 28800,
                    "unmeasurableSleepSeconds": 300,
                    "deepSleepSeconds": 5400,
                    "lightSleepSeconds": 14400,
                    "remSleepSeconds": 5400,
                    "awakeSeconds": 1800,
                    "sleepQualityScore": 82.0,
                    "averageSpO2": 96.5,
                    "lowestSpO2": 94.0,
                    "averageRespiration": 14.5,
                    "averageStress": 25.0,
                    "restHeartRate": 52,
                    "sleepFeedback": "Good recovery sleep",
                }
            ]
        }

        with patch.object(
            GarminAdapter, "_make_request", new=AsyncMock(return_value=mock_response)
        ):
            async with GarminAdapter(garmin_config) as adapter:
                adapter.access_token = "test_token"
                sleep_data = await adapter.get_sleep_data(
                    start_date=date(2025, 1, 25), end_date=date(2025, 1, 27)
                )

                assert len(sleep_data) == 1
                assert sleep_data[0].sleep_id == mock_garmin_sleep_data.sleep_id
                assert (
                    sleep_data[0].sleep_quality_score
                    == mock_garmin_sleep_data.sleep_quality_score
                )
                assert (
                    sleep_data[0].sleep_duration_seconds
                    == mock_garmin_sleep_data.sleep_duration_seconds
                )

    @pytest.mark.asyncio
    async def test_get_activities(self, garmin_config, mock_garmin_activity_data):
        """Test getting activity data"""
        mock_response = {
            "activities": [
                {
                    "activityId": "activity_123",
                    "activityName": "Morning Run",
                    "activityType": "running",
                    "startTime": "2025-01-26T07:00:00Z",
                    "durationSeconds": 3600,
                    "distanceMeters": 10000.0,
                    "calories": 650,
                    "activeCalories": 580,
                    "averageHeartRate": 145,
                    "maxHeartRate": 172,
                    "steps": 12000,
                    "elevationGainMeters": 120.0,
                    "averageSpeedMps": 2.78,
                    "maxSpeedMps": 3.33,
                    "averagePowerWatts": 250.0,
                    "maxPowerWatts": 320.0,
                    "trainingEffect": 3.5,
                    "aerobicTrainingEffect": 3.2,
                    "anaerobicTrainingEffect": 2.1,
                    "activityTrainingLoad": 85.0,
                }
            ]
        }

        with patch.object(
            GarminAdapter, "_make_request", new=AsyncMock(return_value=mock_response)
        ):
            async with GarminAdapter(garmin_config) as adapter:
                adapter.access_token = "test_token"
                activities = await adapter.get_activities(
                    start_date=date(2025, 1, 25), end_date=date(2025, 1, 27)
                )

                assert len(activities) == 1
                assert (
                    activities[0].activity_id == mock_garmin_activity_data.activity_id
                )
                assert (
                    activities[0].distance_meters
                    == mock_garmin_activity_data.distance_meters
                )
                assert activities[0].calories == mock_garmin_activity_data.calories


class TestGarminNormalizer:
    """Test Garmin data normalization"""

    def test_normalize_recovery_data(self, mock_garmin_daily_stats):
        """Test normalizing Garmin daily stats to recovery data"""
        normalizer = WearableDataNormalizer()
        normalized = normalizer.normalize_recovery_data(
            WearableDevice.GARMIN, mock_garmin_daily_stats
        )

        assert normalized.recovery_score == 85.0  # body_battery_highest_value
        assert normalized.resting_heart_rate == 52.0
        assert normalized.device == WearableDevice.GARMIN
        assert normalized.timestamp.date() == mock_garmin_daily_stats.calendar_date

    def test_normalize_sleep_data(self, mock_garmin_sleep_data):
        """Test normalizing Garmin sleep data"""
        normalizer = WearableDataNormalizer()
        normalized = normalizer.normalize_sleep_data(
            WearableDevice.GARMIN, mock_garmin_sleep_data
        )

        assert normalized.sleep_score == 82.0  # sleep_quality_score
        assert normalized.total_duration_minutes == 480.0  # 28800 seconds / 60
        assert normalized.deep_sleep_minutes == 90.0  # 5400 seconds / 60
        assert normalized.rem_sleep_minutes == 90.0  # 5400 seconds / 60
        assert normalized.light_sleep_minutes == 240.0  # 14400 seconds / 60
        assert normalized.awake_minutes == 30.0  # 1800 seconds / 60
        assert normalized.device == WearableDevice.GARMIN

    def test_normalize_workout_data(self, mock_garmin_activity_data):
        """Test normalizing Garmin activity data"""
        normalizer = WearableDataNormalizer()
        normalized = normalizer.normalize_workout_data(
            WearableDevice.GARMIN, mock_garmin_activity_data
        )

        assert normalized.activity_type == "running"
        assert normalized.duration_minutes == 60.0  # 3600 seconds / 60
        assert normalized.distance_km == 10.0  # 10000 meters / 1000
        assert normalized.calories_burned == 650.0
        assert normalized.avg_heart_rate == 145.0
        assert normalized.strain_score == 3.5  # training_effect
        assert normalized.device == WearableDevice.GARMIN

    def test_normalize_body_composition(self, mock_garmin_body_composition):
        """Test normalizing Garmin body composition data"""
        normalizer = WearableDataNormalizer()
        metrics = normalizer._normalize_garmin_body_composition(
            mock_garmin_body_composition
        )

        # Should have metrics for weight, body fat, and muscle mass
        assert len(metrics) == 3

        # Check weight metric
        weight_metric = next(
            (m for m in metrics if m.metric_type.value == "weight"), None
        )
        assert weight_metric is not None
        assert weight_metric.value == 75.5
        assert weight_metric.unit == "kg"

        # Check body fat metric
        body_fat_metric = next(
            (m for m in metrics if m.metric_type.value == "body_fat_percentage"), None
        )
        assert body_fat_metric is not None
        assert body_fat_metric.value == 15.5
        assert body_fat_metric.unit == "%"


class TestGarminIntegrationService:
    """Test Garmin integration with the wearable service"""

    @pytest.mark.asyncio
    async def test_garmin_in_supported_devices(self):
        """Test that Garmin is listed in supported devices"""
        config = {
            "garmin": {
                "consumer_key": "test_consumer_key",
                "consumer_secret": "test_consumer_secret",
                "redirect_uri": "http://localhost:8000/callback",
            }
        }
        service = WearableIntegrationService(config)
        supported_devices = service.get_supported_devices()

        assert WearableDevice.GARMIN in supported_devices

    @pytest.mark.asyncio
    async def test_garmin_authorization_url(self):
        """Test getting Garmin authorization URL through service"""
        config = {
            "garmin": {
                "consumer_key": "test_consumer_key",
                "consumer_secret": "test_consumer_secret",
                "redirect_uri": "http://localhost:8000/callback",
            }
        }
        service = WearableIntegrationService(config)

        auth_url = await service.get_authorization_url(
            WearableDevice.GARMIN, "test_user_123", "test_state"
        )

        assert "oauthConfirm" in auth_url
        assert "oauth_consumer_key=test_consumer_key" in auth_url
        assert "test_user_123:test_state" in auth_url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
