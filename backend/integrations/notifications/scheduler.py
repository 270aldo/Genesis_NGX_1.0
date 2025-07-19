"""
Notification Scheduler Service

This module handles scheduled notifications processing using Celery.
It checks for pending notifications and sends them at the appropriate time.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from celery import Celery
from celery.schedules import crontab

from core.celery_app import celery_app
from .firebase_service import (
    FirebaseNotificationService,
    ScheduledNotification,
    NotificationType,
)

logger = logging.getLogger(__name__)


@celery_app.task(name="process_scheduled_notifications")
def process_scheduled_notifications():
    """
    Process scheduled notifications that are due to be sent

    This task runs every minute to check for notifications that need to be sent.
    """
    asyncio.run(_process_scheduled_notifications())


async def _process_scheduled_notifications():
    """Async implementation of scheduled notification processing"""
    try:
        config = {
            "project_id": "ngx-agents",
            "service_account_key": "/path/to/serviceAccountKey.json",
        }

        async with FirebaseNotificationService(config) as service:
            # In production, this would query the database for due notifications
            # For now, we'll process from the in-memory list
            current_time = datetime.utcnow()

            # Get notifications that are due
            due_notifications = [
                n
                for n in service.scheduled_notifications
                if n.enabled and n.schedule_time <= current_time
            ]

            logger.info(f"Found {len(due_notifications)} notifications to process")

            for notification in due_notifications:
                try:
                    # Send the notification
                    results = await service.send_notification(
                        user_id=notification.user_id,
                        notification_type=notification.type,
                        data=notification.data,
                    )

                    # Update last_sent timestamp
                    notification.last_sent = current_time

                    # Handle recurring notifications
                    if notification.recurring and notification.recurrence_rule:
                        # Calculate next send time based on recurrence rule
                        next_time = calculate_next_send_time(
                            notification.recurrence_rule, current_time
                        )
                        notification.next_send = next_time
                        notification.schedule_time = next_time
                    else:
                        # One-time notification, disable it
                        notification.enabled = False

                    logger.info(
                        f"Sent scheduled notification {notification.id} "
                        f"to user {notification.user_id}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to send scheduled notification {notification.id}: {e}"
                    )

    except Exception as e:
        logger.error(f"Error processing scheduled notifications: {e}")


@celery_app.task(name="send_daily_reminders")
def send_daily_reminders():
    """
    Send daily reminder notifications

    This task runs every morning to send daily workout and meal reminders.
    """
    asyncio.run(_send_daily_reminders())


async def _send_daily_reminders():
    """Send daily reminder notifications to users"""
    try:
        config = {
            "project_id": "ngx-agents",
            "service_account_key": "/path/to/serviceAccountKey.json",
        }

        async with FirebaseNotificationService(config) as service:
            # In production, this would query users with daily reminders enabled
            # For demo, we'll use mock data
            users_with_reminders = [
                {
                    "user_id": "user123",
                    "workout_time": "08:00",
                    "meal_times": ["08:30", "13:00", "19:00"],
                }
            ]

            current_hour = datetime.utcnow().hour

            for user in users_with_reminders:
                # Check if it's time for workout reminder
                workout_hour = int(user["workout_time"].split(":")[0])
                if current_hour == workout_hour:
                    await service.send_notification(
                        user_id=user["user_id"],
                        notification_type=NotificationType.WORKOUT_REMINDER,
                        data={
                            "workout_type": "Morning Workout",
                            "duration": 45,
                            "workout_id": "daily_workout",
                        },
                    )

                # Check meal times
                for meal_time in user["meal_times"]:
                    meal_hour = int(meal_time.split(":")[0])
                    if current_hour == meal_hour:
                        meal_type = get_meal_type_by_time(meal_hour)
                        await service.send_notification(
                            user_id=user["user_id"],
                            notification_type=NotificationType.MEAL_REMINDER,
                            data={
                                "meal_type": meal_type,
                                "calories": get_meal_calories(meal_type),
                                "meal_id": f"daily_{meal_type.lower()}",
                            },
                        )

    except Exception as e:
        logger.error(f"Error sending daily reminders: {e}")


@celery_app.task(name="send_weekly_progress_update")
def send_weekly_progress_update():
    """
    Send weekly progress update notifications

    This task runs every Sunday to send weekly progress summaries.
    """
    asyncio.run(_send_weekly_progress_update())


async def _send_weekly_progress_update():
    """Send weekly progress updates to users"""
    try:
        config = {
            "project_id": "ngx-agents",
            "service_account_key": "/path/to/serviceAccountKey.json",
        }

        async with FirebaseNotificationService(config) as service:
            # In production, calculate actual user progress
            # For demo, use mock data
            users_progress = [
                {
                    "user_id": "user123",
                    "workouts_completed": 5,
                    "calories_burned": 2500,
                    "week_number": datetime.utcnow().isocalendar()[1],
                }
            ]

            for progress in users_progress:
                await service.send_notification(
                    user_id=progress["user_id"],
                    notification_type=NotificationType.PROGRESS_UPDATE,
                    data=progress,
                )

    except Exception as e:
        logger.error(f"Error sending weekly progress updates: {e}")


@celery_app.task(name="check_biometric_alerts")
def check_biometric_alerts():
    """
    Check for biometric alerts that need to be sent

    This task runs every hour to check if any biometric values are out of range.
    """
    asyncio.run(_check_biometric_alerts())


async def _check_biometric_alerts():
    """Check and send biometric alerts"""
    try:
        config = {
            "project_id": "ngx-agents",
            "service_account_key": "/path/to/serviceAccountKey.json",
        }

        async with FirebaseNotificationService(config) as service:
            # In production, check actual biometric data
            # For demo, use mock alerts
            alerts = [
                {
                    "user_id": "user123",
                    "metric_name": "Resting Heart Rate",
                    "status": "elevated",
                    "current_value": "75 bpm",
                    "normal_range": "50-70 bpm",
                }
            ]

            for alert in alerts:
                await service.send_notification(
                    user_id=alert["user_id"],
                    notification_type=NotificationType.BIOMETRIC_ALERT,
                    data=alert,
                    priority="high",
                )

    except Exception as e:
        logger.error(f"Error checking biometric alerts: {e}")


# Helper functions
def calculate_next_send_time(recurrence_rule: str, current_time: datetime) -> datetime:
    """
    Calculate next send time based on recurrence rule

    Args:
        recurrence_rule: Cron-like expression or simple rule (daily, weekly, monthly)
        current_time: Current datetime

    Returns:
        Next scheduled datetime
    """
    if recurrence_rule == "daily":
        return current_time + timedelta(days=1)
    elif recurrence_rule == "weekly":
        return current_time + timedelta(weeks=1)
    elif recurrence_rule == "monthly":
        # Approximate - in production use proper date math
        return current_time + timedelta(days=30)
    elif recurrence_rule == "hourly":
        return current_time + timedelta(hours=1)
    else:
        # For cron expressions, use croniter library in production
        # Default to daily
        return current_time + timedelta(days=1)


def get_meal_type_by_time(hour: int) -> str:
    """Get meal type based on hour of day"""
    if 6 <= hour < 11:
        return "Breakfast"
    elif 11 <= hour < 15:
        return "Lunch"
    elif 15 <= hour < 17:
        return "Snack"
    elif 17 <= hour < 21:
        return "Dinner"
    else:
        return "Late Snack"


def get_meal_calories(meal_type: str) -> int:
    """Get typical calories for meal type"""
    calories_map = {
        "Breakfast": 400,
        "Lunch": 600,
        "Snack": 200,
        "Dinner": 700,
        "Late Snack": 150,
    }
    return calories_map.get(meal_type, 500)


# Celery beat schedule
celery_app.conf.beat_schedule.update(
    {
        "process-scheduled-notifications": {
            "task": "process_scheduled_notifications",
            "schedule": 60.0,  # Every minute
        },
        "send-daily-reminders": {
            "task": "send_daily_reminders",
            "schedule": crontab(minute=0),  # Every hour at minute 0
        },
        "send-weekly-progress": {
            "task": "send_weekly_progress_update",
            "schedule": crontab(hour=10, minute=0, day_of_week=0),  # Sunday 10 AM
        },
        "check-biometric-alerts": {
            "task": "check_biometric_alerts",
            "schedule": crontab(minute=0),  # Every hour
        },
    }
)
