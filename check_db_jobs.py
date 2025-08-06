#!/usr/bin/env python3
"""
Script to check if jobs have been stored in the database
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Dict, Any

class JobChecker:
    def __init__(self):
        """Initialize database connection"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'job_scraper_db'),
            'user': os.getenv('DB_USER', 'joeythe33rd'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 5432))
        }
    
    def check_jobs_count(self) -> Dict[str, Any]:
        """Check total number of jobs in the database"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get total job count
                    cursor.execute("SELECT COUNT(*) as total_jobs FROM jobs")
                    total_jobs = cursor.fetchone()['total_jobs']
                    
                    # Get active job count
                    cursor.execute("SELECT COUNT(*) as active_jobs FROM jobs WHERE is_active = true")
                    active_jobs = cursor.fetchone()['active_jobs']
                    
                    # Get jobs by source platform
                    cursor.execute("""
                        SELECT source_platform, COUNT(*) as count 
                        FROM jobs 
                        GROUP BY source_platform 
                        ORDER BY count DESC
                    """)
                    platform_counts = [dict(row) for row in cursor.fetchall()]
                    
                    # Get most recent jobs
                    cursor.execute("""
                        SELECT company, role, source_platform, scraped_date 
                        FROM jobs 
                        ORDER BY scraped_date DESC 
                        LIMIT 10
                    """)
                    recent_jobs = [dict(row) for row in cursor.fetchall()]
                    
                    return {
                        'total_jobs': total_jobs,
                        'active_jobs': active_jobs,
                        'platform_counts': platform_counts,
                        'recent_jobs': recent_jobs
                    }
                    
        except Exception as e:
            print(f"❌ Error checking jobs: {e}")
            return None
    
    def check_search_history(self) -> List[Dict[str, Any]]:
        """Check search history to see if searches have been performed"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            search_query,
                            search_date,
                            COUNT(*) as job_count
                        FROM search_history
                        GROUP BY search_query, search_date
                        ORDER BY search_date DESC
                        LIMIT 10
                    """)
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            print(f"❌ Error checking search history: {e}")
            return []

def main():
    """Main function to check jobs in database"""
    print("🔍 Checking jobs in database...")
    
    checker = JobChecker()
    
    # Check if jobs exist
    job_stats = checker.check_jobs_count()
    
    if job_stats is None:
        print("❌ Could not connect to database or jobs table doesn't exist")
        return
    
    print(f"\n📊 Database Statistics:")
    print(f"Total jobs: {job_stats['total_jobs']}")
    print(f"Active jobs: {job_stats['active_jobs']}")
    
    if job_stats['platform_counts']:
        print("\n📱 Jobs by platform:")
        for platform in job_stats['platform_counts']:
            print(f"  {platform['source_platform']}: {platform['count']} jobs")
    
    if job_stats['recent_jobs']:
        print("\n🆕 Most recent jobs:")
        for job in job_stats['recent_jobs'][:5]:
            print(f"  {job['company']} - {job['role']} ({job['source_platform']}) - {job['scraped_date']}")
    
    # Check search history
    search_history = checker.check_search_history()
    
    if search_history:
        print(f"\n🔎 Recent searches ({len(search_history)} total):")
        for search in search_history[:3]:
            print(f"  Query: {search['search_query']}")
            print(f"  Date: {search['search_date']} - Jobs: {search['job_count']}")
    
    if job_stats['total_jobs'] == 0:
        print("\n⚠️  No jobs found in the database")
    else:
        print(f"\n✅ Found {job_stats['total_jobs']} jobs in the database")

if __name__ == "__main__":
    main()
