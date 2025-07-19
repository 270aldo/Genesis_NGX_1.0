"""
Firebase Cloud Messaging Service for NGX Agents

This module implements push notifications using Firebase Cloud Messaging (FCM).
It provides functionality for sending notifications to users' devices.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum

import aiohttp
from google.oauth2 import service_account
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Notification priority levels"""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class NotificationType(Enum):
    """Types of notifications"""

    WORKOUT_REMINDER = "workout_reminder"
    MEAL_REMINDER = "meal_reminder"
    HYDRATION_REMINDER = "hydration_reminder"
    SLEEP_REMINDER = "sleep_reminder"
    PROGRESS_UPDATE = "progress_update"
    ACHIEVEMENT = "achievement"
    COACH_MESSAGE = "coach_message"
    SYSTEM_ALERT = "system_alert"
    RECOVERY_SUGGESTION = "recovery_suggestion"
    BIOMETRIC_ALERT = "biometric_alert"


@dataclass
class NotificationTemplate:
    """Template for notification content"""

    type: NotificationType
    title_template: str
    body_template: str
    data_fields: List[str] = field(default_factory=list)
    default_priority: NotificationPriority = NotificationPriority.NORMAL
    sound: Optional[str] = "default"
    badge: Optional[int] = None
    icon: Optional[str] = "ngx_icon"
    color: Optional[str] = "#4CAF50"  # NGX brand color

    def render(self, **kwargs) -> Dict[str, str]:
        """Render the template with provided data"""
        return {
            "title": self.title_template.format(**kwargs),
            "body": self.body_template.format(**kwargs),
        }


@dataclass
class DeviceToken:
    """User device token for push notifications"""

    user_id: str
    token: str
    platform: str  # 'ios', 'android', 'web'
    device_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    last_used: Optional[datetime] = None


@dataclass
class NotificationResult:
    """Result of a notification send operation"""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScheduledNotification:
    """Scheduled notification configuration"""

    id: str
    user_id: str
    type: NotificationType
    schedule_time: datetime
    data: Dict[str, Any]
    recurring: bool = False
    recurrence_rule: Optional[str] = None  # cron-like expression
    enabled: bool = True
    last_sent: Optional[datetime] = None
    next_send: Optional[datetime] = None


class FirebaseNotificationService:
    """
    Service for managing push notifications via Firebase Cloud Messaging
    """

    # Default notification templates
    DEFAULT_TEMPLATES = {
        NotificationType.WORKOUT_REMINDER: NotificationTemplate(
            type=NotificationType.WORKOUT_REMINDER,
            title_template="Time for your {workout_type} workout! 💪",
            body_template="Your {duration}-minute {workout_type} session is scheduled now. Ready to crush it?",
            data_fields=["workout_type", "duration", "workout_id"],
            default_priority=NotificationPriority.HIGH,
        ),
        NotificationType.MEAL_REMINDER: NotificationTemplate(
            type=NotificationType.MEAL_REMINDER,
            title_template="{meal_type} time! 🍽️",
            body_template="Don't forget your {meal_type}. {calories} calories of nutritious fuel awaits!",
            data_fields=["meal_type", "calories", "meal_id"],
            default_priority=NotificationPriority.NORMAL,
        ),
        NotificationType.HYDRATION_REMINDER: NotificationTemplate(
            type=NotificationType.HYDRATION_REMINDER,
            title_template="Stay hydrated! 💧",
            body_template="Time to drink water. You've had {current_intake}ml today, aim for {target_intake}ml.",
            data_fields=["current_intake", "target_intake"],
            default_priority=NotificationPriority.LOW,
        ),
        NotificationType.SLEEP_REMINDER: NotificationTemplate(
            type=NotificationType.SLEEP_REMINDER,
            title_template="Time to wind down 😴",
            body_template="Your optimal bedtime is in {minutes} minutes. Start your evening routine for better recovery.",
            data_fields=["minutes", "bedtime"],
            default_priority=NotificationPriority.NORMAL,
        ),
        NotificationType.PROGRESS_UPDATE: NotificationTemplate(
            type=NotificationType.PROGRESS_UPDATE,
            title_template="Weekly Progress Report 📊",
            body_template="You've completed {workouts_completed} workouts and burned {calories_burned} calories this week!",
            data_fields=["workouts_completed", "calories_burned", "week_number"],
            default_priority=NotificationPriority.NORMAL,
        ),
        NotificationType.ACHIEVEMENT: NotificationTemplate(
            type=NotificationType.ACHIEVEMENT,
            title_template="Achievement Unlocked! 🏆",
            body_template="Congratulations! You've {achievement_description}",
            data_fields=["achievement_name", "achievement_description"],
            default_priority=NotificationPriority.HIGH,
            badge=1,
        ),
        NotificationType.COACH_MESSAGE: NotificationTemplate(
            type=NotificationType.COACH_MESSAGE,
            title_template="Message from your coach 👨‍🏫",
            body_template="{message_preview}",
            data_fields=["coach_name", "message_preview", "message_id"],
            default_priority=NotificationPriority.HIGH,
        ),
        NotificationType.RECOVERY_SUGGESTION: NotificationTemplate(
            type=NotificationType.RECOVERY_SUGGESTION,
            title_template="Recovery recommendation 🔄",
            body_template="Based on your {metric}, consider {suggestion} for optimal recovery.",
            data_fields=["metric", "suggestion", "recovery_score"],
            default_priority=NotificationPriority.NORMAL,
        ),
        NotificationType.BIOMETRIC_ALERT: NotificationTemplate(
            type=NotificationType.BIOMETRIC_ALERT,
            title_template="Health metric alert ⚠️",
            body_template="Your {metric_name} is {status}. Current: {current_value}, Normal: {normal_range}",
            data_fields=["metric_name", "status", "current_value", "normal_range"],
            default_priority=NotificationPriority.HIGH,
        ),
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Firebase notification service

        Args:
            config: Configuration containing:
                - service_account_key: Path to Firebase service account JSON
                - project_id: Firebase project ID
                - custom_templates: Optional custom notification templates
        """
        self.config = config
        self.project_id = config.get("project_id")
        self.credentials = None
        self.access_token = None
        self.token_expiry = None
        self.session: Optional[aiohttp.ClientSession] = None

        # Initialize templates
        self.templates = self.DEFAULT_TEMPLATES.copy()
        if "custom_templates" in config:
            self._load_custom_templates(config["custom_templates"])

        # Initialize credentials
        self._initialize_credentials()

        # Storage for device tokens (in production, use database)
        self.device_tokens: Dict[str, List[DeviceToken]] = {}

        # Storage for scheduled notifications (in production, use database)
        self.scheduled_notifications: List[ScheduledNotification] = []

    def _initialize_credentials(self):
        """Initialize Google service account credentials"""
        service_account_path = self.config.get("service_account_key")
        if service_account_path:
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_path,
                scopes=["https://www.googleapis.com/auth/firebase.messaging"],
            )

    def _load_custom_templates(self, custom_templates: Dict[str, Dict[str, Any]]):
        """Load custom notification templates"""
        for type_str, template_data in custom_templates.items():
            try:
                notification_type = NotificationType(type_str)
                self.templates[notification_type] = NotificationTemplate(
                    type=notification_type,
                    title_template=template_data["title"],
                    body_template=template_data["body"],
                    data_fields=template_data.get("data_fields", []),
                    default_priority=NotificationPriority(
                        template_data.get("priority", "normal")
                    ),
                    sound=template_data.get("sound", "default"),
                    badge=template_data.get("badge"),
                    icon=template_data.get("icon", "ngx_icon"),
                    color=template_data.get("color", "#4CAF50"),
                )
            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to load custom template {type_str}: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _get_access_token(self) -> str:
        """Get valid access token, refreshing if necessary"""
        if not self.credentials:
            raise ValueError("Firebase credentials not configured")

        if (
            not self.access_token
            or not self.token_expiry
            or datetime.utcnow() >= self.token_expiry - timedelta(minutes=5)
        ):
            # Refresh the token
            self.credentials.refresh(Request())
            self.access_token = self.credentials.token
            self.token_expiry = self.credentials.expiry

        return self.access_token

    async def register_device_token(self, device_token: DeviceToken) -> bool:
        """
        Register a device token for a user

        Args:
            device_token: Device token information

        Returns:
            Success status
        """
        if device_token.user_id not in self.device_tokens:
            self.device_tokens[device_token.user_id] = []

        # Remove existing token for the same device if present
        self.device_tokens[device_token.user_id] = [
            token
            for token in self.device_tokens[device_token.user_id]
            if token.token != device_token.token
        ]

        # Add new token
        self.device_tokens[device_token.user_id].append(device_token)
        logger.info(f"Registered device token for user {device_token.user_id}")

        return True

    async def unregister_device_token(self, user_id: str, token: str) -> bool:
        """
        Unregister a device token

        Args:
            user_id: User ID
            token: Device token to remove

        Returns:
            Success status
        """
        if user_id in self.device_tokens:
            self.device_tokens[user_id] = [
                t for t in self.device_tokens[user_id] if t.token != token
            ]
            logger.info(f"Unregistered device token for user {user_id}")
            return True
        return False

    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        data: Dict[str, Any],
        priority: Optional[NotificationPriority] = None,
        custom_sound: Optional[str] = None,
        badge_count: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None,
    ) -> List[NotificationResult]:
        """
        Send a notification to a user

        Args:
            user_id: Target user ID
            notification_type: Type of notification
            data: Data to populate the template
            priority: Override default priority
            custom_sound: Custom notification sound
            badge_count: iOS badge count
            additional_data: Additional data to send with notification

        Returns:
            List of notification results (one per device)
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        # Get user's device tokens
        user_tokens = self.device_tokens.get(user_id, [])
        if not user_tokens:
            logger.warning(f"No device tokens found for user {user_id}")
            return [NotificationResult(success=False, error="No device tokens")]

        # Get template
        template = self.templates.get(notification_type)
        if not template:
            logger.error(f"Unknown notification type: {notification_type}")
            return [
                NotificationResult(success=False, error="Unknown notification type")
            ]

        # Render notification content
        try:
            content = template.render(**data)
        except KeyError as e:
            logger.error(f"Missing template data field: {e}")
            return [NotificationResult(success=False, error=f"Missing data: {e}")]

        # Prepare notification payload
        notification_priority = priority or template.default_priority

        # Send to each device
        results = []
        for device_token in user_tokens:
            if device_token.is_active:
                result = await self._send_to_device(
                    device_token,
                    content,
                    notification_type,
                    notification_priority,
                    custom_sound or template.sound,
                    badge_count or template.badge,
                    template.icon,
                    template.color,
                    additional_data,
                )
                results.append(result)

        return results

    async def _send_to_device(
        self,
        device_token: DeviceToken,
        content: Dict[str, str],
        notification_type: NotificationType,
        priority: NotificationPriority,
        sound: Optional[str],
        badge: Optional[int],
        icon: Optional[str],
        color: Optional[str],
        additional_data: Optional[Dict[str, Any]],
    ) -> NotificationResult:
        """Send notification to a specific device"""
        try:
            access_token = await self._get_access_token()

            # Build FCM message
            message = {
                "message": {
                    "token": device_token.token,
                    "notification": {
                        "title": content["title"],
                        "body": content["body"],
                    },
                    "data": {
                        "type": notification_type.value,
                        "timestamp": datetime.utcnow().isoformat(),
                        **(additional_data or {}),
                    },
                    "android": {
                        "priority": priority.value.upper(),
                        "notification": {"icon": icon, "color": color, "sound": sound},
                    },
                    "apns": {"payload": {"aps": {"sound": sound, "badge": badge}}},
                }
            }

            # Send via FCM API
            url = f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            async with self.session.post(
                url, headers=headers, json=message
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    message_id = data.get("name")

                    # Update last used timestamp
                    device_token.last_used = datetime.utcnow()

                    logger.info(f"Notification sent successfully: {message_id}")
                    return NotificationResult(success=True, message_id=message_id)
                else:
                    error_data = await response.text()
                    logger.error(f"Failed to send notification: {error_data}")

                    # Handle invalid token
                    if response.status == 404 or "UNREGISTERED" in error_data:
                        device_token.is_active = False

                    return NotificationResult(
                        success=False,
                        error=f"FCM error: {response.status} - {error_data}",
                    )

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return NotificationResult(success=False, error=str(e))

    async def send_bulk_notification(
        self,
        user_ids: List[str],
        notification_type: NotificationType,
        data: Dict[str, Any],
        priority: Optional[NotificationPriority] = None,
    ) -> Dict[str, List[NotificationResult]]:
        """
        Send notification to multiple users

        Args:
            user_ids: List of user IDs
            notification_type: Type of notification
            data: Template data
            priority: Notification priority

        Returns:
            Dictionary mapping user_id to notification results
        """
        results = {}

        # Send notifications concurrently
        tasks = []
        for user_id in user_ids:
            task = self.send_notification(user_id, notification_type, data, priority)
            tasks.append((user_id, task))

        # Gather results
        for user_id, task in tasks:
            results[user_id] = await task

        return results

    async def schedule_notification(self, notification: ScheduledNotification) -> bool:
        """
        Schedule a notification for future delivery

        Args:
            notification: Scheduled notification configuration

        Returns:
            Success status
        """
        # In production, this would be stored in a database
        # and processed by a scheduler service
        self.scheduled_notifications.append(notification)

        logger.info(
            f"Scheduled {notification.type.value} notification for user "
            f"{notification.user_id} at {notification.schedule_time}"
        )

        return True

    async def cancel_scheduled_notification(self, notification_id: str) -> bool:
        """
        Cancel a scheduled notification

        Args:
            notification_id: ID of notification to cancel

        Returns:
            Success status
        """
        self.scheduled_notifications = [
            n for n in self.scheduled_notifications if n.id != notification_id
        ]

        logger.info(f"Cancelled scheduled notification {notification_id}")
        return True

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user notification preferences

        Args:
            user_id: User ID

        Returns:
            User preferences dictionary
        """
        # In production, this would be retrieved from database
        # Default preferences
        return {
            "enabled": True,
            "quiet_hours": {"enabled": True, "start": "22:00", "end": "08:00"},
            "notification_types": {type.value: True for type in NotificationType},
            "frequency": {
                "workout_reminders": "daily",
                "meal_reminders": "all",
                "hydration_reminders": "hourly",
                "progress_updates": "weekly",
            },
        }

    async def update_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user notification preferences

        Args:
            user_id: User ID
            preferences: Updated preferences

        Returns:
            Success status
        """
        # In production, this would update the database
        logger.info(f"Updated notification preferences for user {user_id}")
        return True

    def get_supported_notification_types(self) -> List[Dict[str, Any]]:
        """
        Get list of supported notification types with descriptions

        Returns:
            List of notification type information
        """
        return [
            {
                "type": notification_type.value,
                "template": {
                    "title": template.title_template,
                    "body": template.body_template,
                    "required_fields": template.data_fields,
                    "default_priority": template.default_priority.value,
                },
            }
            for notification_type, template in self.templates.items()
        ]


# Example usage
def example_notification_usage():
    """Example of how to use the notification service"""

    async def send_example_notifications():
        config = {
            "project_id": "ngx-agents-project",
            "service_account_key": "/path/to/serviceAccountKey.json",
        }

        async with FirebaseNotificationService(config) as service:
            # Register a device token
            device_token = DeviceToken(
                user_id="user123",
                token="device_token_here",
                platform="ios",
                device_name="iPhone 13",
            )
            await service.register_device_token(device_token)

            # Send workout reminder
            results = await service.send_notification(
                user_id="user123",
                notification_type=NotificationType.WORKOUT_REMINDER,
                data={
                    "workout_type": "Strength Training",
                    "duration": 45,
                    "workout_id": "workout_456",
                },
            )

            print(f"Notification results: {results}")

            # Schedule a meal reminder
            scheduled = ScheduledNotification(
                id="sched_123",
                user_id="user123",
                type=NotificationType.MEAL_REMINDER,
                schedule_time=datetime.utcnow() + timedelta(hours=4),
                data={"meal_type": "Lunch", "calories": 650, "meal_id": "meal_789"},
            )
            await service.schedule_notification(scheduled)


if __name__ == "__main__":
    asyncio.run(example_notification_usage())
