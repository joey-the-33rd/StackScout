"""Notification service for sending notifications."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from src.notifications.database import NotificationsDatabase
from job_search_storage import DB_CONFIG
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending and managing notifications."""
    
    def __init__(self):
        self.db = NotificationsDatabase(DB_CONFIG)
        self.db.connect()
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if not self.sendgrid_api_key:
            logger.warning("SENDGRID_API_KEY not set in environment variables")
        else:
            self.sg_client = SendGridAPIClient(self.sendgrid_api_key)
    
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
        """Send email notification using SendGrid."""
        if not self.sendgrid_api_key:
            logger.error("SendGrid API key not configured. Cannot send email.")
            return False
        
        try:
            # Fetch user email from auth database or user service
            # For now, assume a method self._get_user_email(user_id) exists
            user_email = self._get_user_email(user_id)
            if not user_email:
                logger.error(f"User email not found for user_id {user_id}")
                return False
            
            from_email = Email("no-reply@stackscout.com", "StackScout Notifications")
            to_email = To(user_email)
            subject = title
            content = Content("text/plain", message)
            mail = Mail(from_email, to_email, subject, content)
            
            response = self.sg_client.send(mail)
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"📧 Email notification sent to {user_email}: {title}")
                return True
            else:
                logger.error(f"Failed to send email notification: {response.status_code} {response.body}")
                return False
        except Exception as e:
            logger.error(f"Exception sending email notification: {e}")
            return False
    
    def _get_user_email(self, user_id: int) -> str:
        """Fetch user email from auth database."""
        # This is a placeholder; actual implementation should query user service or database
        # For now, return a placeholder email for testing
        return f"user{user_id}@example.com"
    
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
