"""Database operations for notifications."""

import psycopg2
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class NotificationsDatabase:
    """Database operations for notifications."""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.connection: Optional[psycopg2.extensions.connection] = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            logger.info("✅ Connected to notifications database successfully")
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def create_notification(self, user_id: int, title: str, message: str) -> Optional[int]:
        """Create a new notification."""
        try:
            self.connect()  # Always connect first
            if not self.connection:
                raise Exception("Database connection failed")
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO notifications (user_id, title, message)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (user_id, title, message))
                
                notification_id = cursor.fetchone()[0]
                logger.info(f"✅ Notification created successfully for user {user_id}")
                return notification_id
                
        except Exception as e:
            logger.error(f"❌ Error creating notification: {e}")
            return None
    
    def get_user_notifications(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        try:
            self.connect()  # Always connect first
            if not self.connection:
                raise Exception("Database connection failed")
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_id, title, message, is_read, created_at
                    FROM notifications
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, (user_id, limit, offset))
                
                notifications = []
                for row in cursor.fetchall():
                    notifications.append({
                        "id": row[0],
                        "user_id": row[1],
                        "title": row[2],
                        "message": row[3],
                        "is_read": row[4],
                        "created_at": row[5]
                    })
                return notifications
                
        except Exception as e:
            logger.error(f"❌ Error getting user notifications: {e}")
            return []
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        try:
            self.connect()  # Always connect first
            if not self.connection:
                raise Exception("Database connection failed")
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM notifications
                    WHERE user_id = %s AND is_read = FALSE
                """, (user_id,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"❌ Error getting unread count: {e}")
            return 0
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        try:
            self.connect()  # Always connect first
            if not self.connection:
                raise Exception("Database connection failed")
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE notifications
                    SET is_read = TRUE
                    WHERE id = %s AND user_id = %s
                """, (notification_id, user_id))
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Error marking notification as read: {e}")
            return False
    
    def mark_all_as_read(self, user_id: int) -> bool:
        """Mark all notifications as read for a user."""
        try:
            self.connect()  # Always connect first
            if not self.connection:
                raise Exception("Database connection failed")
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE notifications
                    SET is_read = TRUE
                    WHERE user_id = %s AND is_read = FALSE
                """, (user_id,))
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Error marking all notifications as read: {e}")
            return False
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        try:
            self.connect()  # Always connect first
            if not self.connection:
                raise Exception("Database connection failed")
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM notifications
                    WHERE id = %s AND user_id = %s
                """, (notification_id, user_id))
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Error deleting notification: {e}")
            return False
    
    def get_notification_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get notification preferences for a user."""
        try:
            self.connect()  # Always connect first
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT email_notifications, in_app_notifications
                    FROM notification_preferences
                    WHERE user_id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "email_notifications": result[0],
                        "in_app_notifications": result[1]
                    }
                
                # Create default preferences if they don't exist
                cursor.execute("""
                    INSERT INTO notification_preferences (user_id)
                    VALUES (%s)
                    RETURNING email_notifications, in_app_notifications
                """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "email_notifications": result[0],
                        "in_app_notifications": result[1]
                    }
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting notification preferences: {e}")
            return None
    
    def update_notification_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Update notification preferences for a user."""
        try:
            self.connect()  # Always connect first
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE notification_preferences
                    SET email_notifications = %s,
                        in_app_notifications = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (
                    preferences.get("email_notifications", True),
                    preferences.get("in_app_notifications", True),
                    user_id
                ))
                
                if cursor.rowcount == 0:
                    # Insert if preferences don't exist
                    cursor.execute("""
                        INSERT INTO notification_preferences (user_id, email_notifications, in_app_notifications)
                        VALUES (%s, %s, %s)
                    """, (
                        user_id,
                        preferences.get("email_notifications", True),
                        preferences.get("in_app_notifications", True)
                    ))
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Error updating notification preferences: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                logger.info("✅ Notifications database connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing notifications database connection: {e}")
