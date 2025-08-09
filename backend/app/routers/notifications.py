"""
API router for push notifications
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query, Request
from fastapi.responses import JSONResponse

from core.auth import get_current_user
from app.schemas.notifications import (
    RegisterDeviceRequest,
    RegisterDeviceResponse,
    SendNotificationRequest,
    BulkNotificationRequest,
    NotificationResponse,
    BulkNotificationResponse,
    ScheduleNotificationRequest,
    ScheduleNotificationResponse,
    CancelScheduledNotificationRequest,
    NotificationPreferences,
    UpdatePreferencesRequest,
    NotificationTypesResponse,
    NotificationTemplate,
    NotificationHistoryResponse,
    NotificationHistory,
    NotificationStats,
    TestNotificationRequest,
    NotificationType,
    NotificationPriority,
    DevicePlatform,
)
from integrations.notifications.firebase_service import (
    FirebaseNotificationService,
    DeviceToken,
    ScheduledNotification,
)
from core.telemetry import get_tracer
from app.schemas.pagination import PaginationParams, PaginatedResponse
from core.pagination_helpers import apply_pagination_to_dict_list

logger = logging.getLogger(__name__)
tracer = get_tracer("ngx_agents.api.notifications")

router = APIRouter(prefix="/notifications", tags=["notifications"])


# In production, this would be initialized with proper config
# and use dependency injection
notification_service_config = {
    "project_id": "ngx-agents",
    "service_account_key": "/path/to/serviceAccountKey.json",  # Set via environment
}


@router.post("/device/register", response_model=RegisterDeviceResponse)
async def register_device(
    request: RegisterDeviceRequest,
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Register a device for push notifications

    This endpoint registers a device token (FCM token) for the authenticated user.
    The token will be used to send push notifications to the device.
    """
    with tracer.start_as_current_span("register_device") as span:
        span.set_attribute("user_id", current_user["id"])
        span.set_attribute("platform", request.platform.value)

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                device_token = DeviceToken(
                    user_id=current_user["id"],
                    token=request.token,
                    platform=request.platform.value,
                    device_name=request.device_name,
                )

                success = await service.register_device_token(device_token)

                if success:
                    device_id = f"device_{uuid4().hex[:8]}"

                    # Log registration in background
                    background_tasks.add_task(
                        log_device_registration,
                        current_user["id"],
                        device_id,
                        request.platform.value,
                    )

                    return RegisterDeviceResponse(
                        success=True,
                        message="Device registered successfully",
                        device_id=device_id,
                    )
                else:
                    return RegisterDeviceResponse(
                        success=False, message="Failed to register device"
                    )

        except Exception as e:
            logger.error(f"Error registering device: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register device",
            )


@router.post("/device/unregister")
async def unregister_device(token: str, current_user: Dict = Depends(get_current_user)):
    """
    Unregister a device token

    This removes the device token from the user's registered devices.
    """
    with tracer.start_as_current_span("unregister_device") as span:
        span.set_attribute("user_id", current_user["id"])

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                success = await service.unregister_device_token(
                    current_user["id"], token
                )

                if success:
                    return {"success": True, "message": "Device unregistered"}
                else:
                    return {"success": False, "message": "Device not found"}

        except Exception as e:
            logger.error(f"Error unregistering device: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to unregister device",
            )


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Send a notification to a user

    This endpoint sends a push notification to all registered devices of the specified user.
    Only admins and coaches can send notifications to other users.
    """
    with tracer.start_as_current_span("send_notification") as span:
        span.set_attribute("sender_id", current_user["id"])
        span.set_attribute("target_user_id", request.user_id)
        span.set_attribute("notification_type", request.notification_type.value)

        # Check permissions
        if request.user_id != current_user["id"]:
            # Only admins and coaches can send to other users
            if current_user.get("role") not in ["admin", "coach"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to send notifications to other users",
                )

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                results = await service.send_notification(
                    user_id=request.user_id,
                    notification_type=request.notification_type,
                    data=request.data,
                    priority=request.priority,
                    custom_sound=request.custom_sound,
                    badge_count=request.badge_count,
                    additional_data=request.additional_data,
                )

                # Count successes and failures
                total_sent = sum(1 for r in results if r.success)
                total_failed = len(results) - total_sent

                # Log notification in background
                background_tasks.add_task(
                    log_notification_sent,
                    request.user_id,
                    request.notification_type.value,
                    total_sent,
                    total_failed,
                )

                return NotificationResponse(
                    user_id=request.user_id,
                    results=results,
                    total_sent=total_sent,
                    total_failed=total_failed,
                )

        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send notification",
            )


@router.post("/send/bulk", response_model=BulkNotificationResponse)
async def send_bulk_notification(
    request: BulkNotificationRequest,
    current_user: Dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Send notifications to multiple users

    This endpoint sends the same notification to multiple users.
    Only admins can send bulk notifications.
    """
    with tracer.start_as_current_span("send_bulk_notification") as span:
        span.set_attribute("sender_id", current_user["id"])
        span.set_attribute("target_count", len(request.user_ids))
        span.set_attribute("notification_type", request.notification_type.value)

        # Check permissions - only admins can send bulk
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can send bulk notifications",
            )

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                results = await service.send_bulk_notification(
                    user_ids=request.user_ids,
                    notification_type=request.notification_type,
                    data=request.data,
                    priority=request.priority,
                )

                # Calculate totals
                total_sent = 0
                total_failed = 0
                for user_results in results.values():
                    for result in user_results:
                        if result.success:
                            total_sent += 1
                        else:
                            total_failed += 1

                # Log bulk send in background
                background_tasks.add_task(
                    log_bulk_notification,
                    current_user["id"],
                    len(request.user_ids),
                    request.notification_type.value,
                    total_sent,
                    total_failed,
                )

                return BulkNotificationResponse(
                    total_users=len(request.user_ids),
                    total_sent=total_sent,
                    total_failed=total_failed,
                    results=results,
                )

        except Exception as e:
            logger.error(f"Error sending bulk notification: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send bulk notification",
            )


@router.post("/schedule", response_model=ScheduleNotificationResponse)
async def schedule_notification(
    request: ScheduleNotificationRequest, current_user: Dict = Depends(get_current_user)
):
    """
    Schedule a notification for future delivery

    This endpoint schedules a notification to be sent at a specific time.
    Notifications can be one-time or recurring.
    """
    with tracer.start_as_current_span("schedule_notification") as span:
        span.set_attribute("user_id", request.user_id)
        span.set_attribute("notification_type", request.notification_type.value)
        span.set_attribute("schedule_time", request.schedule_time.isoformat())
        span.set_attribute("recurring", request.recurring)

        # Check permissions
        if request.user_id != current_user["id"]:
            if current_user.get("role") not in ["admin", "coach"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to schedule notifications for other users",
                )

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                notification_id = f"sched_{uuid4().hex}"

                scheduled = ScheduledNotification(
                    id=notification_id,
                    user_id=request.user_id,
                    type=request.notification_type,
                    schedule_time=request.schedule_time,
                    data=request.data,
                    recurring=request.recurring,
                    recurrence_rule=request.recurrence_rule,
                )

                success = await service.schedule_notification(scheduled)

                if success:
                    return ScheduleNotificationResponse(
                        success=True,
                        notification_id=notification_id,
                        schedule_time=request.schedule_time,
                        message="Notification scheduled successfully",
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to schedule notification",
                    )

        except Exception as e:
            logger.error(f"Error scheduling notification: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to schedule notification",
            )


@router.delete("/schedule/{notification_id}")
async def cancel_scheduled_notification(
    notification_id: str, current_user: Dict = Depends(get_current_user)
):
    """
    Cancel a scheduled notification

    This endpoint cancels a previously scheduled notification.
    """
    with tracer.start_as_current_span("cancel_scheduled_notification") as span:
        span.set_attribute("notification_id", notification_id)
        span.set_attribute("user_id", current_user["id"])

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                success = await service.cancel_scheduled_notification(notification_id)

                if success:
                    return {
                        "success": True,
                        "message": "Scheduled notification cancelled",
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Scheduled notification not found",
                    )

        except Exception as e:
            logger.error(f"Error cancelling notification: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel notification",
            )


@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(current_user: Dict = Depends(get_current_user)):
    """
    Get user notification preferences

    Returns the user's notification preferences including enabled types,
    quiet hours, and frequency settings.
    """
    with tracer.start_as_current_span("get_notification_preferences") as span:
        span.set_attribute("user_id", current_user["id"])

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                preferences = await service.get_user_preferences(current_user["id"])
                return NotificationPreferences(**preferences)

        except Exception as e:
            logger.error(f"Error getting preferences: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get preferences",
            )


@router.put("/preferences")
async def update_notification_preferences(
    request: UpdatePreferencesRequest, current_user: Dict = Depends(get_current_user)
):
    """
    Update user notification preferences

    Updates the user's notification preferences.
    """
    with tracer.start_as_current_span("update_notification_preferences") as span:
        span.set_attribute("user_id", current_user["id"])

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                success = await service.update_user_preferences(
                    current_user["id"], request.preferences.dict()
                )

                if success:
                    return {
                        "success": True,
                        "message": "Preferences updated successfully",
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update preferences",
                    )

        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences",
            )


@router.get("/types", response_model=NotificationTypesResponse)
async def get_notification_types():
    """
    Get available notification types

    Returns a list of all available notification types with their templates
    and required fields.
    """
    with tracer.start_as_current_span("get_notification_types"):
        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                types_data = service.get_supported_notification_types()

                templates = []
                for type_info in types_data:
                    templates.append(
                        NotificationTemplate(
                            type=type_info["type"],
                            title_template=type_info["template"]["title"],
                            body_template=type_info["template"]["body"],
                            required_fields=type_info["template"]["required_fields"],
                            default_priority=type_info["template"]["default_priority"],
                        )
                    )

                return NotificationTypesResponse(notification_types=templates)

        except Exception as e:
            logger.error(f"Error getting notification types: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get notification types",
            )


@router.get("/history", response_model=PaginatedResponse[NotificationHistory])
async def get_notification_history(
    request: Request,
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items por página"),
    sort_by: str = Query(default="sent_at", description="Campo para ordenar"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$", description="Orden"),
    notification_type: Optional[NotificationType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: Dict = Depends(get_current_user),
):
    """
    Get notification history

    Returns the user's notification history with pagination and filtering options.
    """
    with tracer.start_as_current_span("get_notification_history") as span:
        span.set_attribute("user_id", current_user["id"])
        span.set_attribute("page", page)
        span.set_attribute("page_size", page_size)

        # Crear parámetros de paginación
        pagination_params = PaginationParams(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )

        # Mock implementation - in production, this would query the database
        all_notifications = []

        # Generate mock data (simular 50 notificaciones)
        for i in range(50):
            notification = NotificationHistory(
                notification_id=f"notif_{uuid4().hex[:8]}",
                user_id=current_user["id"],
                type=NotificationType.WORKOUT_REMINDER if i % 3 == 0 else NotificationType.NUTRITION_REMINDER,
                title="Time for your workout!" if i % 3 == 0 else "Log your meal",
                body="Your strength training session starts in 15 minutes" if i % 3 == 0 else "Don't forget to log your lunch",
                sent_at=datetime.utcnow() - timedelta(days=i),
                read_at=(
                    datetime.utcnow() - timedelta(days=i, hours=1)
                    if i > 0
                    else None
                ),
                status="delivered",
                platform=DevicePlatform.IOS if i % 2 == 0 else DevicePlatform.ANDROID,
            )
            
            # Aplicar filtros
            if notification_type and notification.type != notification_type:
                continue
            if start_date and notification.sent_at < start_date:
                continue
            if end_date and notification.sent_at > end_date:
                continue
                
            all_notifications.append(notification)

        # Convertir a diccionarios para paginación
        notification_dicts = [
            {
                "notification_id": n.notification_id,
                "user_id": n.user_id,
                "type": n.type.value,
                "title": n.title,
                "body": n.body,
                "sent_at": n.sent_at.isoformat(),
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "status": n.status,
                "platform": n.platform.value,
            }
            for n in all_notifications
        ]

        # Aplicar paginación
        base_url = str(request.url).split('?')[0]
        paginated_response = apply_pagination_to_dict_list(
            items=notification_dicts,
            params=pagination_params,
            base_url=base_url,
            sort_key=sort_by
        )

        logger.info(
            f"Historial de notificaciones obtenido para usuario {current_user['id']} "
            f"(página {page}, tamaño {page_size})"
        )

        return paginated_response


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: Dict = Depends(get_current_user),
):
    """
    Get notification statistics

    Returns statistics about notifications sent to the user.
    Only admins can see global statistics.
    """
    with tracer.start_as_current_span("get_notification_stats") as span:
        span.set_attribute("user_id", current_user["id"])

        # Default date range - last 30 days
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Mock implementation
        return NotificationStats(
            total_sent=150,
            total_delivered=145,
            total_failed=5,
            total_opened=120,
            open_rate=0.827,
            by_type={
                NotificationType.WORKOUT_REMINDER: {
                    "sent": 50,
                    "delivered": 48,
                    "opened": 45,
                },
                NotificationType.MEAL_REMINDER: {
                    "sent": 60,
                    "delivered": 59,
                    "opened": 50,
                },
                NotificationType.PROGRESS_UPDATE: {
                    "sent": 10,
                    "delivered": 10,
                    "opened": 8,
                },
            },
            by_platform={
                DevicePlatform.IOS: {"sent": 80, "delivered": 78, "opened": 70},
                DevicePlatform.ANDROID: {"sent": 70, "delivered": 67, "opened": 50},
            },
            period_start=start_date,
            period_end=end_date,
        )


@router.post("/test")
async def send_test_notification(
    request: TestNotificationRequest, current_user: Dict = Depends(get_current_user)
):
    """
    Send a test notification

    Sends a test notification to the user's devices to verify setup.
    """
    with tracer.start_as_current_span("send_test_notification") as span:
        span.set_attribute("user_id", current_user["id"])

        try:
            async with FirebaseNotificationService(
                notification_service_config
            ) as service:
                # Use custom title/body or defaults
                title = request.custom_title or "NGX Test Notification 🧪"
                body = (
                    request.custom_body
                    or "This is a test notification from NGX Agents. If you see this, notifications are working!"
                )

                results = await service.send_notification(
                    user_id=current_user["id"],
                    notification_type=request.notification_type,
                    data={"title": title, "body": body, "test": True},
                    priority=NotificationPriority.HIGH,
                )

                success_count = sum(1 for r in results if r.success)

                return {
                    "success": success_count > 0,
                    "message": f"Test notification sent to {success_count} device(s)",
                    "results": results,
                }

        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
            span.record_exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send test notification",
            )


# Background task functions
async def log_device_registration(user_id: str, device_id: str, platform: str):
    """Log device registration event"""
    logger.info(
        f"Device registered: user={user_id}, device={device_id}, platform={platform}"
    )


async def log_notification_sent(
    user_id: str, notification_type: str, sent_count: int, failed_count: int
):
    """Log notification send event"""
    logger.info(
        f"Notification sent: user={user_id}, type={notification_type}, "
        f"sent={sent_count}, failed={failed_count}"
    )


async def log_bulk_notification(
    sender_id: str,
    user_count: int,
    notification_type: str,
    sent_count: int,
    failed_count: int,
):
    """Log bulk notification event"""
    logger.info(
        f"Bulk notification: sender={sender_id}, users={user_count}, "
        f"type={notification_type}, sent={sent_count}, failed={failed_count}"
    )
