"""Notification service for sending notifications."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from src.notifications.database import NotificationsDatabase
from job_search_storage import DB_CONFIG

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending and managing notifications."""
    
    def __init__(self):
        self.db = NotificationsDatabase(DB_CONFIG)
        self.db.connect()
    
    def send_notification(self, user_id: int, title: str, message: str) -> bool:
        """Send a notification to a user."""
        try:
            # Get user preferences
            prefs = self.db.get_notification_preferences(user_id)
            if not prefs:
                logger.warning(f"User {user_id} preferences not found")
                return False
            
            # Create in-app notification
            if prefs.get("in_app_notifications", True):
                notification_id = self.db.create_notification(user_id, title, message)
                if notification_id:
                    logger.info(f"✅ In-app notification sent to user {user_id}: {title}")
            
            # Send email notification if enabled
            if prefs.get("email_notifications", True):
                self._send_email_notification(user_id, title, message)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
            return False
    
    def _send_email_notification(self, user_id: int, title: str, message: str) -> bool:
        """Send email notification (placeholder implementation)."""
        # In a real implementation, this would integrate with an email service
        # like SendGrid, Mailgun, or AWS SES
        logger.info(f"📧 Email notification would be sent to user {user_id}: {title} - {message}")
        # TODO: Implement actual email sending logic
        return True
    
    def send_job_alert(self, user_id: int, job_data: Dict[str, Any]) -> bool:
        """Send a job alert notification."""
        title = "New Job Alert!"
        message = f"New job matching your search: {job_data.get('role', 'Unknown role')} at {job_data.get('company', 'Unknown company')}"
        
        return self.send_notification(user_id, title, message)
    
    def send_recommendation_alert(self, user_id: int, job_data: Dict[str, Any]) -> bool:
        """Send a job recommendation notification."""
        title = "Recommended Job for You!"
        message = f"We found a job that matches your profile: {job_data.get('role', 'Unknown role')} at {job_data.get('company', 'Unknown company')}"
        
        return self.send_notification(user_id, title, message)
    
    def send_search_complete_notification(self, user_id: int, search_query: str, result_count: int) -> bool:
        """Send a search completion notification."""
        title = "Search Complete!"
        message = f"Your search for '{search_query}' found {result_count} job(s)"
        
        return self.send_notification(user_id, title, message)
    
    def close(self):
        """Close the database connection."""
        self.db.close()
