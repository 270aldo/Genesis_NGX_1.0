"""
Tests for Oura Ring Integration
"""

import pytest
from datetime import datetime, timedelta, date
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from integrations.wearables.adapters.oura import (
    OuraAdapter,
    OuraConfig,
    OuraPersonalInfo,
    OuraSleepData,
    OuraActivityData,
    OuraReadinessData,
    OuraHeartRateData,
)
from integrations.wearables.normalizer import WearableDevice, WearableDataNormalizer
from integrations.wearables.service import WearableIntegrationService


@pytest.fixture
def oura_config():
    """Create test Oura configuration"""
    return OuraConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8000/wearables/auth/oura/callback",
    )


@pytest.fixture
def mock_oura_personal_info():
    """Create mock Oura personal info"""
    return OuraPersonalInfo(
        user_id="oura_test_user_123",
        age=35,
        weight=75.5,
        height=180.0,
        biological_sex="male",
        email="test@example.com",
    )


@pytest.fixture
def mock_oura_sleep_data():
    """Create mock Oura sleep data"""
    return OuraSleepData(
        sleep_id="sleep_123",
        day=date(2025, 1, 26),
        bedtime_start=datetime(2025, 1, 26, 23, 0, 0),
        bedtime_end=datetime(2025, 1, 27, 7, 0, 0),
        average_breath=14.5,
        average_heart_rate=52.0,
        average_hrv=45.0,
        awake_time=1800,  # 30 minutes
        deep_sleep_duration=5400,  # 90 minutes
        efficiency=85,
        latency=600,  # 10 minutes
        light_sleep_duration=14400,  # 240 minutes
        low_battery_alert=False,
        lowest_heart_rate=48,
        movement_30_sec="000111000111000",
        period_id=1,
        readiness_score_delta=5.0,
        rem_sleep_duration=5400,  # 90 minutes
        restless_periods=3,
        sleep_phase_5_min="LLRRDDDLLRR",
        sleep_score_delta=3.0,
        sleep_algorithm_version="v2",
        time_in_bed=28800,  # 480 minutes
        total_sleep_duration=25200,  # 420 minutes
        type="long_sleep",
    )


@pytest.fixture
def mock_oura_activity_data():
    """Create mock Oura activity data"""
    return OuraActivityData(
        activity_id="activity_123",
        day=date(2025, 1, 26),
        timestamp=datetime(2025, 1, 26, 12, 0, 0),
        activity_type="daily_movement",
        calories=320,
        distance=5200.0,
        duration=7200,  # 2 hours
        steps=8500,
        active_calories=180,
        average_met_minutes=1.8,
        contributors={
            "meet_daily_targets": 85,
            "move_every_hour": 75,
            "recovery_time": 90,
            "stay_active": 80,
            "training_frequency": 70,
            "training_volume": 65,
        },
        equivalent_walking_distance=5000,
        high_activity_met_minutes=45,
        high_activity_time=900,  # 15 minutes
        inactivity_alerts=2,
        low_activity_met_minutes=120,
        low_activity_time=4800,  # 80 minutes
        medium_activity_met_minutes=90,
        medium_activity_time=1500,  # 25 minutes
        met={"interval": 300, "items": [1.0, 1.2, 1.5, 2.0, 1.8]},
        meters_to_target=-200,
        non_wear_time=0,
        resting_time=7200,  # 2 hours
        sedentary_met_minutes=30,
        sedentary_time=14400,  # 4 hours
        steps_to_target=-500,
        target_calories=350,
        target_meters=5000,
        total_calories=2150,
    )


@pytest.fixture
def mock_oura_readiness_data():
    """Create mock Oura readiness data"""
    return OuraReadinessData(
        readiness_id="readiness_123",
        day=date(2025, 1, 26),
        score=85,
        temperature_deviation=-0.2,
        temperature_trend_deviation=-0.1,
        timestamp=datetime(2025, 1, 26, 6, 0, 0),
        contributors={
            "activity_balance": 85,
            "body_temperature": 90,
            "hrv_balance": 80,
            "previous_day_activity": 75,
            "previous_night": 85,
            "recovery_index": 88,
            "resting_heart_rate": 92,
            "sleep_balance": 83,
        },
    )


@pytest.fixture
def mock_oura_heart_rate_data():
    """Create mock Oura heart rate data"""
    return [
        OuraHeartRateData(
            timestamp=datetime(2025, 1, 26, 0, 0, 0) + timedelta(minutes=i * 5),
            bpm=50 + (i % 10),
            source="ppg",
        )
        for i in range(12)  # 1 hour of data, every 5 minutes
    ]


class TestOuraAdapter:
    """Test Oura adapter functionality"""

    @pytest.mark.asyncio
    async def test_get_auth_url(self, oura_config):
        """Test OAuth URL generation"""
        adapter = OuraAdapter(oura_config)
        auth_url = adapter.get_auth_url(state="test_state_123")

        assert "https://cloud.ouraring.com/oauth/authorize" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert (
            "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fwearables%2Fauth%2Foura%2Fcallback"
            in auth_url
        )
        assert "response_type=code" in auth_url
        assert "scope=personal+daily+heartrate+workout+tag" in auth_url
        assert "state=test_state_123" in auth_url

    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens(self, oura_config):
        """Test OAuth token exchange"""
        mock_response = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 86400,
        }

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 200
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(
                return_value=mock_response
            )

            async with OuraAdapter(oura_config) as adapter:
                token_data = await adapter.exchange_code_for_tokens("test_code")

                assert token_data["access_token"] == "test_access_token"
                assert token_data["refresh_token"] == "test_refresh_token"
                assert adapter.access_token == "test_access_token"
                assert adapter.refresh_token == "test_refresh_token"

    @pytest.mark.asyncio
    async def test_get_personal_info(self, oura_config, mock_oura_personal_info):
        """Test getting personal info"""
        mock_response = {
            "id": "oura_test_user_123",
            "age": 35,
            "weight": 75.5,
            "height": 180.0,
            "biological_sex": "male",
            "email": "test@example.com",
        }

        with patch.object(
            OuraAdapter, "_make_request", new=AsyncMock(return_value=mock_response)
        ):
            async with OuraAdapter(oura_config) as adapter:
                adapter.access_token = "test_token"
                personal_info = await adapter.get_personal_info()

                assert personal_info.user_id == mock_oura_personal_info.user_id
                assert personal_info.age == mock_oura_personal_info.age
                assert personal_info.weight == mock_oura_personal_info.weight

    @pytest.mark.asyncio
    async def test_get_sleep_data(self, oura_config, mock_oura_sleep_data):
        """Test getting sleep data"""
        mock_response = {
            "data": [
                {
                    "id": "sleep_123",
                    "day": "2025-01-26",
                    "bedtime_start": "2025-01-26T23:00:00Z",
                    "bedtime_end": "2025-01-27T07:00:00Z",
                    "average_breath": 14.5,
                    "average_heart_rate": 52.0,
                    "average_hrv": 45.0,
                    "awake_time": 1800,
                    "deep_sleep_duration": 5400,
                    "efficiency": 85,
                    "latency": 600,
                    "light_sleep_duration": 14400,
                    "low_battery_alert": False,
                    "lowest_heart_rate": 48,
                    "movement_30_sec": "000111000111000",
                    "period_id": 1,
                    "readiness_score_delta": 5.0,
                    "rem_sleep_duration": 5400,
                    "restless_periods": 3,
                    "sleep_phase_5_min": "LLRRDDDLLRR",
                    "sleep_score_delta": 3.0,
                    "sleep_algorithm_version": "v2",
                    "time_in_bed": 28800,
                    "total_sleep_duration": 25200,
                    "type": "long_sleep",
                }
            ]
        }

        with patch.object(
            OuraAdapter, "_make_request", new=AsyncMock(return_value=mock_response)
        ):
            async with OuraAdapter(oura_config) as adapter:
                adapter.access_token = "test_token"
                sleep_data = await adapter.get_sleep_data(
                    start_date=date(2025, 1, 25), end_date=date(2025, 1, 27)
                )

                assert len(sleep_data) == 1
                assert sleep_data[0].sleep_id == mock_oura_sleep_data.sleep_id
                assert sleep_data[0].efficiency == mock_oura_sleep_data.efficiency
                assert (
                    sleep_data[0].total_sleep_duration
                    == mock_oura_sleep_data.total_sleep_duration
                )

    @pytest.mark.asyncio
    async def test_get_activity_data(self, oura_config, mock_oura_activity_data):
        """Test getting activity data"""
        mock_response = {
            "data": [
                {
                    "id": "activity_123",
                    "day": "2025-01-26",
                    "timestamp": "2025-01-26T12:00:00Z",
                    "class_5_min": "daily_movement",
                    "calories": 320,
                    "distance": 5200.0,
                    "duration": 7200,
                    "steps": 8500,
                    "active_calories": 180,
                    "average_met_minutes": 1.8,
                    "contributors": mock_oura_activity_data.contributors,
                    "equivalent_walking_distance": 5000,
                    "high_activity_met_minutes": 45,
                    "high_activity_time": 900,
                    "inactivity_alerts": 2,
                    "low_activity_met_minutes": 120,
                    "low_activity_time": 4800,
                    "medium_activity_met_minutes": 90,
                    "medium_activity_time": 1500,
                    "met": {"interval": 300, "items": [1.0, 1.2, 1.5, 2.0, 1.8]},
                    "meters_to_target": -200,
                    "non_wear_time": 0,
                    "resting_time": 7200,
                    "sedentary_met_minutes": 30,
                    "sedentary_time": 14400,
                    "steps_to_target": -500,
                    "target_calories": 350,
                    "target_meters": 5000,
                    "total_calories": 2150,
                }
            ]
        }

        with patch.object(
            OuraAdapter, "_make_request", new=AsyncMock(return_value=mock_response)
        ):
            async with OuraAdapter(oura_config) as adapter:
                adapter.access_token = "test_token"
                activity_data = await adapter.get_activity_data(
                    start_date=date(2025, 1, 25), end_date=date(2025, 1, 27)
                )

                assert len(activity_data) == 1
                assert (
                    activity_data[0].activity_id == mock_oura_activity_data.activity_id
                )
                assert activity_data[0].steps == mock_oura_activity_data.steps
                assert activity_data[0].calories == mock_oura_activity_data.calories

    @pytest.mark.asyncio
    async def test_get_readiness_data(self, oura_config, mock_oura_readiness_data):
        """Test getting readiness data"""
        mock_response = {
            "data": [
                {
                    "id": "readiness_123",
                    "day": "2025-01-26",
                    "score": 85,
                    "temperature_deviation": -0.2,
                    "temperature_trend_deviation": -0.1,
                    "timestamp": "2025-01-26T06:00:00Z",
                    "contributors": mock_oura_readiness_data.contributors,
                }
            ]
        }

        with patch.object(
            OuraAdapter, "_make_request", new=AsyncMock(return_value=mock_response)
        ):
            async with OuraAdapter(oura_config) as adapter:
                adapter.access_token = "test_token"
                readiness_data = await adapter.get_readiness_data(
                    start_date=date(2025, 1, 25), end_date=date(2025, 1, 27)
                )

                assert len(readiness_data) == 1
                assert (
                    readiness_data[0].readiness_id
                    == mock_oura_readiness_data.readiness_id
                )
                assert readiness_data[0].score == mock_oura_readiness_data.score
                assert (
                    readiness_data[0].temperature_deviation
                    == mock_oura_readiness_data.temperature_deviation
                )


class TestOuraNormalizer:
    """Test Oura data normalization"""

    def test_normalize_recovery_data(self, mock_oura_readiness_data):
        """Test normalizing Oura readiness to recovery data"""
        normalizer = WearableDataNormalizer()
        normalized = normalizer.normalize_recovery_data(
            WearableDevice.OURA_RING, mock_oura_readiness_data
        )

        assert normalized.recovery_score == 85.0
        assert normalized.device == WearableDevice.OURA_RING
        assert normalized.device_specific_id == "readiness_123"
        assert normalized.timestamp == mock_oura_readiness_data.timestamp

    def test_normalize_sleep_data(self, mock_oura_sleep_data):
        """Test normalizing Oura sleep data"""
        normalizer = WearableDataNormalizer()
        normalized = normalizer.normalize_sleep_data(
            WearableDevice.OURA_RING, mock_oura_sleep_data
        )

        assert normalized.sleep_score == 85.0  # Uses efficiency as score
        assert normalized.total_duration_minutes == 420.0  # 25200 seconds / 60
        assert normalized.sleep_efficiency_percent == 85.0
        assert normalized.deep_sleep_minutes == 90.0  # 5400 seconds / 60
        assert normalized.rem_sleep_minutes == 90.0  # 5400 seconds / 60
        assert normalized.light_sleep_minutes == 240.0  # 14400 seconds / 60
        assert normalized.awake_minutes == 30.0  # 1800 seconds / 60
        assert normalized.device == WearableDevice.OURA_RING

    def test_normalize_activity_to_metrics(self, mock_oura_activity_data):
        """Test converting Oura activity data to metrics"""
        normalizer = WearableDataNormalizer()
        metrics = normalizer.normalize_to_metrics(
            WearableDevice.OURA_RING, mock_oura_activity_data, "activity"
        )

        # Should have metrics for steps and calories
        assert len(metrics) >= 2

        # Check steps metric
        steps_metric = next(
            (m for m in metrics if m.metric_type.value == "steps"), None
        )
        assert steps_metric is not None
        assert steps_metric.value == 8500.0
        assert steps_metric.unit == "steps"

        # Check calories metric
        calories_metric = next(
            (m for m in metrics if m.metric_type.value == "calories_burned"), None
        )
        assert calories_metric is not None
        assert calories_metric.value == 2150.0
        assert calories_metric.unit == "kcal"


class TestOuraIntegrationService:
    """Test Oura integration with the wearable service"""

    @pytest.mark.asyncio
    async def test_oura_in_supported_devices(self):
        """Test that Oura is listed in supported devices"""
        config = {
            "oura": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "redirect_uri": "http://localhost:8000/callback",
            }
        }
        service = WearableIntegrationService(config)
        supported_devices = service.get_supported_devices()

        assert WearableDevice.OURA_RING in supported_devices

    @pytest.mark.asyncio
    async def test_oura_authorization_url(self):
        """Test getting Oura authorization URL through service"""
        config = {
            "oura": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "redirect_uri": "http://localhost:8000/callback",
            }
        }
        service = WearableIntegrationService(config)

        auth_url = await service.get_authorization_url(
            WearableDevice.OURA_RING, "test_user_123", "test_state"
        )

        assert "https://cloud.ouraring.com/oauth/authorize" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "test_user_123:test_state" in auth_url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
