"""FastAPI dependencies for notifications."""

from typing import Generator
from src.notifications.database import NotificationsDatabase
from job_search_storage import DB_CONFIG

def get_notifications_db() -> Generator[NotificationsDatabase, None, None]:
    """Get notifications database instance."""
    db = NotificationsDatabase(DB_CONFIG)
    db.connect()
    try:
        yield db
    finally:
        db.close()
