"""Database operations for authentication."""

import psycopg2
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuthDatabase:
    """Database operations for user authentication."""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            logger.info("✅ Connected to auth database successfully")
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def create_user(self, username: str, email: str, password_hash: str, full_name: Optional[str] = None) -> Optional[int]:
        """Create a new user."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, full_name)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (username, email, password_hash, full_name))
                
                user_id = cursor.fetchone()[0]
                logger.info(f"✅ User created successfully: {username} (ID: {user_id})")
                
                # Create default user preferences
                cursor.execute("""
                    INSERT INTO user_preferences (user_id)
                    VALUES (%s)
                """, (user_id,))
                
                return user_id
                
        except psycopg2.IntegrityError as e:
            if "username" in str(e):
                logger.warning(f"⚠️ Username already exists: {username}")
                return None
            elif "email" in str(e):
                logger.warning(f"⚠️ Email already exists: {email}")
                return None
            else:
                logger.error(f"❌ Database integrity error: {e}")
                return None
        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username or email."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, password_hash, full_name, 
                           created_at, is_active, last_login
                    FROM users
                    WHERE username = %s OR email = %s
                """, (username, username))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "username": result[1],
                        "email": result[2],
                        "password_hash": result[3],
                        "full_name": result[4],
                        "created_at": result[5],
                        "is_active": result[6],
                        "last_login": result[7]
                    }
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, password_hash, full_name, 
                           created_at, is_active, last_login
                    FROM users
                    WHERE id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "username": result[1],
                        "email": result[2],
                        "password_hash": result[3],
                        "full_name": result[4],
                        "created_at": result[5],
                        "is_active": result[6],
                        "last_login": result[7]
                    }
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting user by ID: {e}")
            return None
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (user_id,))
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Error updating last login: {e}")
            return False
    
    def update_user(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user profile."""
        try:
            with self.connection.cursor() as cursor:
                set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
                values = list(updates.values()) + [user_id]
                
                cursor.execute(f"""
                    UPDATE users
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, values)
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Error updating user: {e}")
            return False
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user preferences."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT notification_enabled, email_notifications, saved_searches
                    FROM user_preferences
                    WHERE user_id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "notification_enabled": result[0],
                        "email_notifications": result[1],
                        "saved_searches": result[2] or []
                    }
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting user preferences: {e}")
            return None
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Update user preferences."""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE user_preferences
                    SET notification_enabled = %s,
                        email_notifications = %s,
                        saved_searches = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (
                    preferences.get("notification_enabled", True),
                    preferences.get("email_notifications", True),
                    preferences.get("saved_searches", []),
                    user_id
                ))
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Error updating user preferences: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                logger.info("✅ Auth database connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing auth database connection: {e}")
