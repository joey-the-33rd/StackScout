"""Database operations for recommendations."""

import psycopg2
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class RecommendationDatabase:
    """Database operations for job recommendations."""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.connection: Optional[psycopg2.extensions.connection] = None
        # Don't connect automatically - connect on first use
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            logger.info("✅ Connected to recommendation database successfully")
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.connection = None
            return False
    
    def get_user_search_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's search history."""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            # Type assertion for Pylance
            assert self.connection is not None
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT search_query, search_date, COUNT(*) as job_count
                    FROM search_history
                    WHERE user_id = %s
                    GROUP BY search_query, search_date
                    ORDER BY search_date DESC
                    LIMIT %s
                """, (user_id, limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        "search_query": row[0],
                        "search_date": row[1],
                        "job_count": row[2]
                    })
                return results
                
        except Exception as e:
            logger.error(f"❌ Error getting user search history: {e}")
            return []
    
    def get_user_saved_jobs(self, user_id: int) -> List[int]:
        """Get IDs of jobs saved by user."""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            # Type assertion for Pylance
            assert self.connection is not None
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT job_id FROM user_job_interactions
                    WHERE user_id = %s AND interaction_type = 'save'
                """, (user_id,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Error getting user saved jobs: {e}")
            return []
    
    def get_user_profile_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile data for recommendations."""
        try:
            if not self.connection:
                if not self.connect():
                    return None
            # Type assertion for Pylance
            assert self.connection is not None
            with self.connection.cursor() as cursor:
                # Get user preferences
                cursor.execute("""
                    SELECT notification_enabled, email_notifications, saved_searches
                    FROM user_preferences
                    WHERE user_id = %s
                """, (user_id,))
                
                preferences = cursor.fetchone()
                if not preferences:
                    return None
                
                # Get user's recent job interactions
                cursor.execute("""
                    SELECT job_id, interaction_type, interaction_date
                    FROM user_job_interactions
                    WHERE user_id = %s
                    ORDER BY interaction_date DESC
                    LIMIT 100
                """, (user_id,))
                
                interactions = []
                for row in cursor.fetchall():
                    interactions.append({
                        "job_id": row[0],
                        "interaction_type": row[1],
                        "interaction_date": row[2]
                    })
                
                return {
                    "preferences": {
                        "notification_enabled": preferences[0],
                        "email_notifications": preferences[1],
                        "saved_searches": preferences[2] or []
                    },
                    "interactions": interactions
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting user profile data: {e}")
            return None
    
    def get_recent_jobs(self, days: int = 30, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get recent jobs for recommendation."""
        try:
            if not self.connection:
                if not self.connect():
                    return []
            # Type assertion for Pylance
            assert self.connection is not None
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, company, role, tech_stack, job_type, salary, location,
                           description, source_platform, source_url, posted_date,
                           scraped_date, keywords
                    FROM jobs
                    WHERE scraped_date >= CURRENT_DATE - INTERVAL '%s days'
                    AND is_active = true
                    ORDER BY scraped_date DESC
                    LIMIT %s
                """, (days, limit))
                
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        job = dict(zip(columns, row))
                        # Convert arrays to lists
                        if isinstance(job.get('tech_stack'), str):
                            job['tech_stack'] = job['tech_stack'].strip('{}').split(',') if job['tech_stack'] else []
                        if isinstance(job.get('keywords'), str):
                            job['keywords'] = job['keywords'].strip('{}').split(',') if job['keywords'] else []
                        results.append(job)
                else:
                    results = []
                
                return results
                
        except Exception as e:
            logger.error(f"❌ Error getting recent jobs: {e}")
            return []
    
    def record_job_interaction(self, user_id: int, job_id: int, interaction_type: str, duration: Optional[int] = None) -> bool:
        """Record user interaction with a job."""
        try:
            if not self.connection:
                if not self.connect():
                    return False
            # Type assertion for Pylance
            assert self.connection is not None
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_job_interactions (user_id, job_id, interaction_type, duration)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id, job_id, interaction_type) DO UPDATE SET
                        interaction_date = CURRENT_TIMESTAMP,
                        duration = EXCLUDED.duration
                """, (user_id, job_id, interaction_type, duration))
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Error recording job interaction: {e}")
            return False
    
    def get_job_interaction_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about user job interactions."""
        try:
            if not self.connection:
                if not self.connect():
                    return {}
            # Type assertion for Pylance
            assert self.connection is not None
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT interaction_type, COUNT(*), MAX(interaction_date)
                    FROM user_job_interactions
                    WHERE user_id = %s
                    GROUP BY interaction_type
                """, (user_id,))
                
                stats = {}
                for row in cursor.fetchall():
                    stats[row[0]] = {
                        "count": row[1],
                        "last_interaction": row[2]
                    }
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ Error getting job interaction stats: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                logger.info("✅ Recommendation database connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing recommendation database connection: {e}")
