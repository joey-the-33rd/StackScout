"""FastAPI endpoints for notifications."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.notifications.models import (
    NotificationCreate, NotificationResponse, NotificationUpdate, NotificationPreferences
)
from src.notifications.database import NotificationsDatabase
from src.notifications.dependencies import get_notifications_db
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    db: NotificationsDatabase = Depends(get_notifications_db)
):
    """Create a new notification."""
    notification_id = db.create_notification(
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message
    )
    if notification_id is None:
        raise HTTPException(status_code=500, detail="Failed to create notification")
    return db.get_user_notifications(notification.user_id, limit=1)[0]

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    db: NotificationsDatabase = Depends(get_notifications_db),
    limit: int = 50,
    offset: int = 0
):
    """Get notifications for the current user."""
    notifications = db.get_user_notifications(current_user["id"], limit=limit, offset=offset)
    return notifications

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: NotificationsDatabase = Depends(get_notifications_db)
):
    """Mark a notification as read."""
    success = db.mark_as_read(notification_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found or not authorized")
    notifications = db.get_user_notifications(current_user["id"], limit=1, offset=0)
    for notification in notifications:
        if notification["id"] == notification_id:
            return notification
    raise HTTPException(status_code=404, detail="Notification not found")

@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user),
    db: NotificationsDatabase = Depends(get_notifications_db)
):
    """Get notification preferences for the current user."""
    prefs = db.get_notification_preferences(current_user["id"])
    if prefs is None:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return NotificationPreferences(**prefs)

@router.put("/preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user),
    db: NotificationsDatabase = Depends(get_notifications_db)
):
    """Update notification preferences for the current user."""
    success = db.update_notification_preferences(current_user["id"], preferences.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update preferences")
    return preferences
