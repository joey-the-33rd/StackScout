"""Analytics engine for StackScout."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import psycopg2
from job_search_storage import DB_CONFIG

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Main analytics engine for job search system."""
    
    def __init__(self):
        self.db_config = DB_CONFIG
        self.connection = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            logger.info("✅ Connected to analytics database successfully")
            return True
        except psycopg2.Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.connection = None
            return False
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        try:
            if not self.connection:
                if not self.connect():
                    return {}
            
            with self.connection.cursor() as cursor:
                # Total jobs count
                cursor.execute("SELECT COUNT(*) FROM jobs")
                total_jobs = cursor.fetchone()[0]
                
                # Active jobs count
                cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = true")
                active_jobs = cursor.fetchone()[0]
                
                # Jobs this week
                cursor.execute("""
                    SELECT COUNT(*) FROM jobs 
                    WHERE scraped_date >= CURRENT_DATE - INTERVAL '7 days'
                """)
                week_jobs = cursor.fetchone()[0]
                
                # Jobs by platform
                cursor.execute("""
                    SELECT source_platform, COUNT(*) 
                    FROM jobs 
                    GROUP BY source_platform 
                    ORDER BY COUNT(*) DESC
                """)
                platform_stats = [
                    {"source_platform": row[0], "count": row[1]}
                    for row in cursor.fetchall()
                ]
                
                # Growth rate (comparing last 7 days to previous 7 days)
                cursor.execute("""
                    SELECT 
                        COALESCE(COUNT(CASE WHEN scraped_date >= NOW() - INTERVAL '7 days' THEN 1 END), 0) AS recent,
                        COALESCE(COUNT(CASE WHEN scraped_date >= NOW() - INTERVAL '14 days'
                                           AND scraped_date < NOW() - INTERVAL '7 days' THEN 1 END), 0) AS previous
                    FROM jobs
                """)
                recent, previous = cursor.fetchone() or (0, 0)
                growth_rate = 0.0
                if previous > 0:
                    growth_rate = ((recent - previous) / previous) * 100.0
                
                # User statistics
                cursor.execute("SELECT COUNT(*) FROM users")
                total_users = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                """)
                new_users = cursor.fetchone()[0]
                
                # Recommendation statistics
                cursor.execute("SELECT COUNT(*) FROM user_job_interactions")
                total_interactions = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM user_job_interactions 
                    WHERE interaction_date >= CURRENT_DATE - INTERVAL '7 days'
                """)
                active_users = cursor.fetchone()[0]
                
                return {
                    "jobs": {
                        "total": total_jobs,
                        "active": active_jobs,
                        "this_week": week_jobs,
                        "growth_rate": round(growth_rate, 2),
                        "by_platform": platform_stats
                    },
                    "users": {
                        "total": total_users,
                        "new_this_week": new_users,
                        "active_this_week": active_users
                    },
                    "interactions": {
                        "total": total_interactions
                    }
                }
        except Exception as e:
            logger.error(f"❌ Error getting overall statistics: {e}")
            return {}
    
    def get_user_interaction_analytics(self) -> Dict[str, Any]:
        """Get user interaction analytics."""
        try:
            if not self.connection:
                if not self.connect():
                    return {}
            
            with self.connection.cursor() as cursor:
                # Interaction type distribution
                cursor.execute("""
                    SELECT interaction_type, COUNT(*) 
                    FROM user_job_interactions 
                    GROUP BY interaction_type
                """)
                interaction_types = dict(cursor.fetchall())
                
                # Daily interaction trend (last 30 days)
                cursor.execute("""
                    SELECT 
                        DATE(interaction_date) as date,
                        COUNT(*) as count
                    FROM user_job_interactions
                    WHERE interaction_date >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE(interaction_date)
                    ORDER BY date
                """)
                rows = cursor.fetchall()
                counts_by_date = {row[0]: row[1] for row in rows}
                from datetime import datetime, timedelta
                end_date = datetime.utcnow().date()
                start_date = end_date - timedelta(days=29)
                daily_trend = []
                d = start_date
                while d <= end_date:
                    daily_trend.append({"date": d.isoformat(), "count": counts_by_date.get(d, 0)})
                    d += timedelta(days=1)
                
                # Top interacting users
                cursor.execute("""
                    SELECT 
                        u.username,
                        COUNT(uji.id) as interaction_count
                    FROM user_job_interactions uji
                    JOIN users u ON uji.user_id = u.id
                    GROUP BY u.id, u.username
                    ORDER BY interaction_count DESC
                    LIMIT 10
                """)
                top_users = []
                for row in cursor.fetchall():
                    top_users.append({
                        "username": row[0],
                        "interaction_count": row[1]
                    })
                
                # Average interactions per user
                cursor.execute("""
                    SELECT 
                        COALESCE(COUNT(uji.id)::numeric / NULLIF(COUNT(DISTINCT uji.user_id), 0), 0) AS avg_interactions
                    FROM user_job_interactions uji
                """)
                result = cursor.fetchone()
                avg_interactions = float(result[0]) if result and result[0] is not None else 0.0
                
                return {
                    "interaction_types": interaction_types,
                    "daily_trend": daily_trend,
                    "top_users": top_users,
                    "average_per_user": round(avg_interactions, 2) if avg_interactions else 0
                }
        except Exception as e:
            logger.error(f"❌ Error getting user interaction analytics: {e}")
            return {}
    
    def get_search_pattern_analytics(self) -> Dict[str, Any]:
        """Get search pattern analytics."""
        try:
            if not self.connection:
                if not self.connect():
                    return {}
            
            with self.connection.cursor() as cursor:
                # Top search keywords
                cursor.execute("""
                    SELECT 
                        search_query->>'keywords' as keywords,
                        COUNT(*) as search_count
                    FROM search_history
                    WHERE search_query->>'keywords' IS NOT NULL
                    AND search_query->>'keywords' != ''
                    GROUP BY search_query->>'keywords'
                    ORDER BY search_count DESC
                    LIMIT 10
                """)
                top_keywords = []
                for row in cursor.fetchall():
                    top_keywords.append({
                        "keywords": row[0],
                        "search_count": row[1]
                    })
                
                # Search frequency by day of week
                cursor.execute("""
                    SELECT 
                        EXTRACT(DOW FROM search_date) as day_of_week,
                        COUNT(*) as search_count
                    FROM search_history
                    GROUP BY EXTRACT(DOW FROM search_date)
                    ORDER BY day_of_week
                """)
                day_counts = {int(row[0]): row[1] for row in cursor.fetchall()}
                day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
                day_of_week = [
                    {"day": day_names[i], "search_count": day_counts.get(i, 0)}
                    for i in range(7)
                ]
                
                # Search trend over time (last 30 days)
                cursor.execute("""
                    SELECT 
                        DATE(search_date) as date,
                        COUNT(*) as search_count
                    FROM search_history
                    WHERE search_date >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE(search_date)
                    ORDER BY date
                """)
                search_trend = []
                for row in cursor.fetchall():
                    search_trend.append({
                        "date": row[0].isoformat(),
                        "search_count": row[1]
                    })
                
                # Job type preferences from searches
                cursor.execute("""
                    SELECT 
                        search_query->>'job_type' as job_type,
                        COUNT(*) as search_count
                    FROM search_history
                    WHERE search_query->>'job_type' IS NOT NULL
                    AND search_query->>'job_type' != ''
                    GROUP BY search_query->>'job_type'
                    ORDER BY search_count DESC
                """)
                job_type_preferences = []
                for row in cursor.fetchall():
                    job_type_preferences.append({
                        "job_type": row[0],
                        "search_count": row[1]
                    })
                
                return {
                    "top_keywords": top_keywords,
                    "day_of_week": day_of_week,
                    "search_trend": search_trend,
                    "job_type_preferences": job_type_preferences
                }
        except Exception as e:
            logger.error(f"❌ Error getting search pattern analytics: {e}")
            return {}
    
    def get_recommendation_performance(self) -> Dict[str, Any]:
        """Get recommendation performance analytics."""
        try:
            if not self.connection:
                if not self.connect():
                    return {}
            
            with self.connection.cursor() as cursor:
                # Recommendation effectiveness by interaction type
                cursor.execute("""
                    SELECT 
                        uji.interaction_type,
                        COUNT(*) as count,
                        COALESCE(AVG(jrc.match_score), 0) as avg_match_score
                    FROM user_job_interactions uji
                    LEFT JOIN job_recommendation_cache jrc ON uji.job_id = jrc.job_id AND uji.user_id = jrc.user_id
                    GROUP BY uji.interaction_type
                """)
                recommendation_effectiveness = []
                for row in cursor.fetchall():
                    recommendation_effectiveness.append({
                        "interaction_type": row[0],
                        "count": row[1],
                        "avg_match_score": round(row[2], 3) if row[2] else 0
                    })
                
                # Top recommended jobs
                cursor.execute("""
                    SELECT 
                        j.company,
                        j.role,
                        COUNT(uji.id) as interaction_count,
                        AVG(jrc.match_score) as avg_match_score
                    FROM job_recommendation_cache jrc
                    JOIN jobs j ON jrc.job_id = j.id
                    LEFT JOIN user_job_interactions uji ON jrc.job_id = uji.job_id AND jrc.user_id = uji.user_id
                    GROUP BY j.id, j.company, j.role
                    ORDER BY interaction_count DESC, avg_match_score DESC
                    LIMIT 10
                """)
                top_recommended = []
                for row in cursor.fetchall():
                    top_recommended.append({
                        "company": row[0],
                        "role": row[1],
                        "interaction_count": row[2] if row[2] else 0,
                        "avg_match_score": round(row[3], 3) if row[3] else 0
                    })
                
                # Recommendation score distribution
                cursor.execute("""
                    SELECT 
                        score_range,
                        COUNT(*) as count
                    FROM (
                        SELECT 
                            CASE 
                                WHEN match_score >= 0.9 THEN '90-100%'
                                WHEN match_score >= 0.8 THEN '80-89%'
                                WHEN match_score >= 0.7 THEN '70-79%'
                                WHEN match_score >= 0.6 THEN '60-69%'
                                WHEN match_score >= 0.5 THEN '50-59%'
                                ELSE '<50%'
                            END as score_range
                        FROM job_recommendation_cache
                    ) as score_groups
                    GROUP BY score_range
                    ORDER BY 
                        CASE 
                            WHEN score_range = '90-100%' THEN 1
                            WHEN score_range = '80-89%' THEN 2
                            WHEN score_range = '70-79%' THEN 3
                            WHEN score_range = '60-69%' THEN 4
                            WHEN score_range = '50-59%' THEN 5
                            ELSE 6
                        END
                """)
                score_distribution = []
                for row in cursor.fetchall():
                    score_distribution.append({
                        "score_range": row[0],
                        "count": row[1]
                    })
                
                return {
                    "effectiveness": recommendation_effectiveness,
                    "top_recommended": top_recommended,
                    "score_distribution": score_distribution
                }
        except Exception as e:
            logger.error(f"❌ Error getting recommendation performance: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                logger.info("✅ Analytics database connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing analytics database connection: {e}")

# Convenience functions for API endpoints
def get_all_analytics() -> Dict[str, Any]:
    """Get all analytics data."""
    logger.info("Retrieving all analytics data...")
    engine = AnalyticsEngine()
    try:
        defaults = {
            "overall": {
                "jobs": {"total": 0, "active": 0, "this_week": 0, "growth_rate": 0.0, "by_platform": {}},
                "users": {"total": 0, "new_this_week": 0, "active_this_week": 0},
                "interactions": {"total": 0}
            },
            "user_interactions": {
                "interaction_types": {},
                "daily_trend": [],
                "top_users": [],
                "average_per_user": 0.0
            },
            "search_patterns": {
                "top_keywords": [],
                "day_of_week": [],
                "search_trend": [],
                "job_type_preferences": []
            },
            "recommendations": {
                "effectiveness": [],
                "top_recommended": [],
                "score_distribution": []
            }
        }

        overall_stats = engine.get_overall_statistics() or {}
        user_analytics = engine.get_user_interaction_analytics() or {}
        search_analytics = engine.get_search_pattern_analytics() or {}
        recommendation_analytics = engine.get_recommendation_performance() or {}

        analytics_data = {
            "overall": overall_stats if overall_stats else defaults["overall"],
            "user_interactions": user_analytics if user_analytics else defaults["user_interactions"],
            "search_patterns": search_analytics if search_analytics else defaults["search_patterns"],
            "recommendations": recommendation_analytics if recommendation_analytics else defaults["recommendations"]
        }
        logger.info(
            "Analytics assembled: jobs_total=%s users_total=%s",
            analytics_data.get("overall", {}).get("jobs", {}).get("total", 0),
            analytics_data.get("overall", {}).get("users", {}).get("total", 0)
        )
        return analytics_data
    finally:
        engine.close()
