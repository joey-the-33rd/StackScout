#!/usr/bin/env python3
"""Setup script for notifications system."""

import psycopg2
import logging
from job_search_storage import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_notifications_database():
    """Create notifications database tables."""
    try:
        # Read the schema file
        with open('create_notifications_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Execute schema creation
        cursor.execute(schema_sql)
        logger.info("✅ Notifications database schema created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Error setting up notifications database: {e}")
        raise

if __name__ == "__main__":
    print("Setting up notifications database...")
    setup_notifications_database()
    print("✅ Notifications setup complete!")
