"""
Tests for Push Notifications System
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from integrations.notifications.firebase_service import (
    FirebaseNotificationService,
    DeviceToken,
    NotificationType,
    NotificationPriority,
    NotificationTemplate,
    ScheduledNotification,
    NotificationResult,
)


@pytest.fixture
def notification_config():
    """Create test notification service configuration"""
    return {
        "project_id": "test-project",
        "service_account_key": "/path/to/test-key.json",
    }


@pytest.fixture
def mock_device_token():
    """Create mock device token"""
    return DeviceToken(
        user_id="test_user_123",
        token="test_device_token_abc123",
        platform="ios",
        device_name="iPhone 13",
    )


@pytest.fixture
def mock_credentials():
    """Mock Google credentials"""
    with patch(
        "integrations.notifications.firebase_service.service_account.Credentials"
    ) as mock:
        creds = MagicMock()
        creds.token = "test_access_token"
        creds.expiry = datetime.utcnow() + timedelta(hours=1)
        mock.from_service_account_file.return_value = creds
        yield creds


class TestFirebaseNotificationService:
    """Test Firebase notification service functionality"""

    @pytest.mark.asyncio
    async def test_device_token_registration(
        self, notification_config, mock_device_token
    ):
        """Test registering a device token"""
        async with FirebaseNotificationService(notification_config) as service:
            # Register device token
            success = await service.register_device_token(mock_device_token)

            assert success is True
            assert mock_device_token.user_id in service.device_tokens
            assert len(service.device_tokens[mock_device_token.user_id]) == 1
            assert (
                service.device_tokens[mock_device_token.user_id][0].token
                == mock_device_token.token
            )

    @pytest.mark.asyncio
    async def test_device_token_unregistration(
        self, notification_config, mock_device_token
    ):
        """Test unregistering a device token"""
        async with FirebaseNotificationService(notification_config) as service:
            # First register
            await service.register_device_token(mock_device_token)

            # Then unregister
            success = await service.unregister_device_token(
                mock_device_token.user_id, mock_device_token.token
            )

            assert success is True
            assert len(service.device_tokens.get(mock_device_token.user_id, [])) == 0

    @pytest.mark.asyncio
    async def test_notification_template_rendering(self, notification_config):
        """Test notification template rendering"""
        template = NotificationTemplate(
            type=NotificationType.WORKOUT_REMINDER,
            title_template="Time for your {workout_type} workout!",
            body_template="Your {duration}-minute session starts now.",
            data_fields=["workout_type", "duration"],
        )

        rendered = template.render(workout_type="Strength Training", duration=45)

        assert rendered["title"] == "Time for your Strength Training workout!"
        assert rendered["body"] == "Your 45-minute session starts now."

    @pytest.mark.asyncio
    async def test_send_notification_no_devices(self, notification_config):
        """Test sending notification when user has no devices"""
        async with FirebaseNotificationService(notification_config) as service:
            results = await service.send_notification(
                user_id="no_devices_user",
                notification_type=NotificationType.WORKOUT_REMINDER,
                data={
                    "workout_type": "Cardio",
                    "duration": 30,
                    "workout_id": "workout_123",
                },
            )

            assert len(results) == 1
            assert results[0].success is False
            assert results[0].error == "No device tokens"

    @pytest.mark.asyncio
    async def test_send_notification_with_mock_fcm(
        self, notification_config, mock_device_token, mock_credentials
    ):
        """Test sending notification with mocked FCM response"""
        async with FirebaseNotificationService(notification_config) as service:
            # Register device
            await service.register_device_token(mock_device_token)

            # Mock FCM response
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"name": "message_id_123"})

            with patch.object(service, "session") as mock_session:
                mock_session.post.return_value.__aenter__.return_value = mock_response

                results = await service.send_notification(
                    user_id=mock_device_token.user_id,
                    notification_type=NotificationType.MEAL_REMINDER,
                    data={"meal_type": "Lunch", "calories": 650, "meal_id": "meal_456"},
                )

                assert len(results) == 1
                assert results[0].success is True
                assert results[0].message_id == "message_id_123"

    @pytest.mark.asyncio
    async def test_send_bulk_notification(self, notification_config, mock_credentials):
        """Test sending bulk notifications"""
        async with FirebaseNotificationService(notification_config) as service:
            # Register multiple users
            users = ["user1", "user2", "user3"]
            for user_id in users:
                token = DeviceToken(
                    user_id=user_id, token=f"token_{user_id}", platform="android"
                )
                await service.register_device_token(token)

            # Mock FCM responses
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"name": "message_id"})

            with patch.object(service, "session") as mock_session:
                mock_session.post.return_value.__aenter__.return_value = mock_response

                results = await service.send_bulk_notification(
                    user_ids=users,
                    notification_type=NotificationType.PROGRESS_UPDATE,
                    data={
                        "workouts_completed": 5,
                        "calories_burned": 2500,
                        "week_number": 10,
                    },
                )

                assert len(results) == 3
                for user_id in users:
                    assert user_id in results
                    assert len(results[user_id]) == 1
                    assert results[user_id][0].success is True

    @pytest.mark.asyncio
    async def test_schedule_notification(self, notification_config):
        """Test scheduling a notification"""
        async with FirebaseNotificationService(notification_config) as service:
            scheduled = ScheduledNotification(
                id="sched_test_123",
                user_id="test_user",
                type=NotificationType.SLEEP_REMINDER,
                schedule_time=datetime.utcnow() + timedelta(hours=2),
                data={"minutes": 30, "bedtime": "22:30"},
            )

            success = await service.schedule_notification(scheduled)

            assert success is True
            assert len(service.scheduled_notifications) == 1
            assert service.scheduled_notifications[0].id == "sched_test_123"

    @pytest.mark.asyncio
    async def test_cancel_scheduled_notification(self, notification_config):
        """Test canceling a scheduled notification"""
        async with FirebaseNotificationService(notification_config) as service:
            # First schedule a notification
            scheduled = ScheduledNotification(
                id="sched_cancel_123",
                user_id="test_user",
                type=NotificationType.HYDRATION_REMINDER,
                schedule_time=datetime.utcnow() + timedelta(hours=1),
                data={"current_intake": 1000, "target_intake": 2500},
            )
            await service.schedule_notification(scheduled)

            # Then cancel it
            success = await service.cancel_scheduled_notification("sched_cancel_123")

            assert success is True
            assert len(service.scheduled_notifications) == 0

    @pytest.mark.asyncio
    async def test_get_user_preferences(self, notification_config):
        """Test getting user notification preferences"""
        async with FirebaseNotificationService(notification_config) as service:
            preferences = await service.get_user_preferences("test_user")

            assert preferences["enabled"] is True
            assert "quiet_hours" in preferences
            assert "notification_types" in preferences
            assert (
                preferences["notification_types"][
                    NotificationType.WORKOUT_REMINDER.value
                ]
                is True
            )

    @pytest.mark.asyncio
    async def test_update_user_preferences(self, notification_config):
        """Test updating user notification preferences"""
        async with FirebaseNotificationService(notification_config) as service:
            new_preferences = {
                "enabled": False,
                "quiet_hours": {"enabled": True, "start": "21:00", "end": "09:00"},
            }

            success = await service.update_user_preferences(
                "test_user", new_preferences
            )

            assert success is True

    def test_get_supported_notification_types(self, notification_config):
        """Test getting supported notification types"""
        service = FirebaseNotificationService(notification_config)
        types = service.get_supported_notification_types()

        assert len(types) > 0

        # Check that all default types are present
        type_values = [t["type"] for t in types]
        assert NotificationType.WORKOUT_REMINDER.value in type_values
        assert NotificationType.MEAL_REMINDER.value in type_values
        assert NotificationType.ACHIEVEMENT.value in type_values

        # Check template structure
        workout_type = next(
            t for t in types if t["type"] == NotificationType.WORKOUT_REMINDER.value
        )
        assert "template" in workout_type
        assert "title" in workout_type["template"]
        assert "body" in workout_type["template"]
        assert "required_fields" in workout_type["template"]

    @pytest.mark.asyncio
    async def test_notification_with_priority(
        self, notification_config, mock_device_token, mock_credentials
    ):
        """Test sending notification with custom priority"""
        async with FirebaseNotificationService(notification_config) as service:
            await service.register_device_token(mock_device_token)

            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"name": "high_priority_msg"})

            with patch.object(service, "session") as mock_session:
                mock_session.post.return_value.__aenter__.return_value = mock_response

                results = await service.send_notification(
                    user_id=mock_device_token.user_id,
                    notification_type=NotificationType.BIOMETRIC_ALERT,
                    data={
                        "metric_name": "Heart Rate",
                        "status": "critical",
                        "current_value": "180 bpm",
                        "normal_range": "60-100 bpm",
                    },
                    priority=NotificationPriority.HIGH,
                )

                # Verify the request was made with high priority
                call_args = mock_session.post.call_args
                message_data = call_args[1]["json"]["message"]
                assert message_data["android"]["priority"] == "HIGH"

    @pytest.mark.asyncio
    async def test_achievement_notification_with_badge(
        self, notification_config, mock_device_token, mock_credentials
    ):
        """Test achievement notification includes badge count"""
        async with FirebaseNotificationService(notification_config) as service:
            mock_device_token.platform = "ios"  # Badge is iOS specific
            await service.register_device_token(mock_device_token)

            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"name": "achievement_msg"})

            with patch.object(service, "session") as mock_session:
                mock_session.post.return_value.__aenter__.return_value = mock_response

                results = await service.send_notification(
                    user_id=mock_device_token.user_id,
                    notification_type=NotificationType.ACHIEVEMENT,
                    data={
                        "achievement_name": "Week Warrior",
                        "achievement_description": "completed 7 workouts in a week!",
                    },
                )

                # Verify badge was included for iOS
                call_args = mock_session.post.call_args
                message_data = call_args[1]["json"]["message"]
                assert message_data["apns"]["payload"]["aps"]["badge"] == 1


class TestSchedulerIntegration:
    """Test notification scheduler functionality"""

    @pytest.mark.asyncio
    async def test_process_due_notifications(self, notification_config):
        """Test processing of due scheduled notifications"""
        from integrations.notifications.scheduler import (
            _process_scheduled_notifications,
        )

        # This would need proper mocking of the service and database
        # For now, just verify the function exists and can be called
        with patch("integrations.notifications.scheduler.FirebaseNotificationService"):
            await _process_scheduled_notifications()

    def test_calculate_next_send_time(self):
        """Test calculation of next send time for recurring notifications"""
        from integrations.notifications.scheduler import calculate_next_send_time

        current = datetime(2025, 1, 26, 10, 0, 0)

        # Test daily recurrence
        next_daily = calculate_next_send_time("daily", current)
        assert next_daily == current + timedelta(days=1)

        # Test weekly recurrence
        next_weekly = calculate_next_send_time("weekly", current)
        assert next_weekly == current + timedelta(weeks=1)

        # Test hourly recurrence
        next_hourly = calculate_next_send_time("hourly", current)
        assert next_hourly == current + timedelta(hours=1)

    def test_get_meal_type_by_time(self):
        """Test meal type determination by hour"""
        from integrations.notifications.scheduler import get_meal_type_by_time

        assert get_meal_type_by_time(7) == "Breakfast"
        assert get_meal_type_by_time(13) == "Lunch"
        assert get_meal_type_by_time(16) == "Snack"
        assert get_meal_type_by_time(19) == "Dinner"
        assert get_meal_type_by_time(22) == "Late Snack"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
