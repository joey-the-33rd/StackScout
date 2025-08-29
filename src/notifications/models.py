"""Notification models for StackScout."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NotificationCreate(BaseModel):
    """Model for creating a notification."""
    user_id: int = Field(..., description="User ID to send notification to")
    title: str = Field(..., max_length=255, description="Notification title")
    message: str = Field(..., description="Notification message")

class NotificationResponse(BaseModel):
    """Model for notification response."""
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationPreferences(BaseModel):
    """Model for notification preferences."""
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    in_app_notifications: bool = Field(default=True, description="Enable in-app notifications")

class NotificationUpdate(BaseModel):
    """Model for updating notification status."""
    is_read: bool = Field(default=True, description="Mark notification as read")

class NotificationBatchUpdate(BaseModel):
    """Model for batch updating notifications."""
    notification_ids: List[int] = Field(..., description="List of notification IDs to update")
    is_read: bool = Field(default=True, description="Mark notifications as read")
