"""
Pydantic schemas for notifications
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class NotificationPriority(str, Enum):
    """Notification priority levels"""

    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class NotificationType(str, Enum):
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


class DevicePlatform(str, Enum):
    """Device platforms"""

    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class RegisterDeviceRequest(BaseModel):
    """Request to register a device for push notifications"""

    token: str = Field(..., description="FCM device token")
    platform: DevicePlatform = Field(..., description="Device platform")
    device_name: Optional[str] = Field(None, description="Optional device name")


class RegisterDeviceResponse(BaseModel):
    """Response for device registration"""

    success: bool
    message: str
    device_id: Optional[str] = None


class SendNotificationRequest(BaseModel):
    """Request to send a notification"""

    user_id: str = Field(..., description="Target user ID")
    notification_type: NotificationType = Field(..., description="Type of notification")
    data: Dict[str, Any] = Field(..., description="Template data")
    priority: Optional[NotificationPriority] = Field(
        None, description="Override priority"
    )
    custom_sound: Optional[str] = Field(None, description="Custom sound file")
    badge_count: Optional[int] = Field(None, description="iOS badge count")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Extra data")


class BulkNotificationRequest(BaseModel):
    """Request to send notifications to multiple users"""

    user_ids: List[str] = Field(..., description="List of user IDs")
    notification_type: NotificationType = Field(..., description="Type of notification")
    data: Dict[str, Any] = Field(..., description="Template data")
    priority: Optional[NotificationPriority] = Field(
        None, description="Override priority"
    )


class NotificationResult(BaseModel):
    """Result of a notification send operation"""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime


class NotificationResponse(BaseModel):
    """Response for notification send request"""

    user_id: str
    results: List[NotificationResult]
    total_sent: int
    total_failed: int


class BulkNotificationResponse(BaseModel):
    """Response for bulk notification request"""

    total_users: int
    total_sent: int
    total_failed: int
    results: Dict[str, List[NotificationResult]]


class ScheduleNotificationRequest(BaseModel):
    """Request to schedule a notification"""

    user_id: str = Field(..., description="Target user ID")
    notification_type: NotificationType = Field(..., description="Type of notification")
    schedule_time: datetime = Field(..., description="When to send")
    data: Dict[str, Any] = Field(..., description="Template data")
    recurring: bool = Field(False, description="Is this recurring")
    recurrence_rule: Optional[str] = Field(
        None, description="Cron expression for recurrence"
    )

    @validator("schedule_time")
    def validate_future_time(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("Schedule time must be in the future")
        return v


class ScheduleNotificationResponse(BaseModel):
    """Response for scheduled notification"""

    success: bool
    notification_id: str
    schedule_time: datetime
    message: str


class CancelScheduledNotificationRequest(BaseModel):
    """Request to cancel a scheduled notification"""

    notification_id: str = Field(..., description="ID of scheduled notification")


class NotificationPreferences(BaseModel):
    """User notification preferences"""

    enabled: bool = Field(True, description="Global notification toggle")
    quiet_hours: Dict[str, Any] = Field(
        default_factory=lambda: {"enabled": True, "start": "22:00", "end": "08:00"},
        description="Quiet hours configuration",
    )
    notification_types: Dict[NotificationType, bool] = Field(
        default_factory=lambda: {
            NotificationType.WORKOUT_REMINDER: True,
            NotificationType.MEAL_REMINDER: True,
            NotificationType.HYDRATION_REMINDER: True,
            NotificationType.SLEEP_REMINDER: True,
            NotificationType.PROGRESS_UPDATE: True,
            NotificationType.ACHIEVEMENT: True,
            NotificationType.COACH_MESSAGE: True,
            NotificationType.RECOVERY_SUGGESTION: True,
            NotificationType.BIOMETRIC_ALERT: True,
            NotificationType.SYSTEM_ALERT: True,
        },
        description="Enable/disable specific notification types",
    )
    frequency: Dict[str, str] = Field(
        default_factory=lambda: {
            "workout_reminders": "daily",
            "meal_reminders": "all",
            "hydration_reminders": "hourly",
            "progress_updates": "weekly",
        },
        description="Frequency settings for different notification types",
    )


class UpdatePreferencesRequest(BaseModel):
    """Request to update notification preferences"""

    preferences: NotificationPreferences


class NotificationTemplate(BaseModel):
    """Notification template information"""

    type: NotificationType
    title_template: str
    body_template: str
    required_fields: List[str]
    default_priority: NotificationPriority


class NotificationTypesResponse(BaseModel):
    """Response with available notification types"""

    notification_types: List[NotificationTemplate]


class NotificationHistory(BaseModel):
    """Notification history entry"""

    notification_id: str
    user_id: str
    type: NotificationType
    title: str
    body: str
    sent_at: datetime
    read_at: Optional[datetime] = None
    status: str
    platform: Optional[DevicePlatform] = None


class NotificationHistoryResponse(BaseModel):
    """Response with notification history"""

    notifications: List[NotificationHistory]
    total: int
    page: int
    per_page: int


class NotificationStats(BaseModel):
    """Notification statistics"""

    total_sent: int
    total_delivered: int
    total_failed: int
    total_opened: int
    open_rate: float
    by_type: Dict[NotificationType, Dict[str, int]]
    by_platform: Dict[DevicePlatform, Dict[str, int]]
    period_start: datetime
    period_end: datetime


class TestNotificationRequest(BaseModel):
    """Request to send a test notification"""

    notification_type: NotificationType = Field(
        NotificationType.SYSTEM_ALERT, description="Type of test notification"
    )
    custom_title: Optional[str] = Field(None, description="Custom title for test")
    custom_body: Optional[str] = Field(None, description="Custom body for test")
