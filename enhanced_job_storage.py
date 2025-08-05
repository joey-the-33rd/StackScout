"""
Enhanced Job Search Storage System
Automatically stores job search results in the database with improved error handling
"""

import psycopg2
from psycopg2.extras import Json, RealDictCursor
from datetime import datetime
import hashlib
import json
import os
from typing import List, Dict, Any

class EnhancedJobStorage:
    def __init__(self):
        """Initialize database connection with environment variables"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'job_scraper_db'),
            'user': os.getenv('DB_USER', 'joeythe33rd'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 5432))
        }
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.connection = psycopg2.connect(**self.db_config)
                self.connection.autocommit = True
                print("✅ Connected to job_scraper_db successfully")
                return
            except Exception as e:
                print(f"❌ Connection attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
        raise Exception("Failed to connect to database after retries")
    
    def store_search_results(self, search_query: Dict[str, Any], search_results: List[Dict[str, Any]]) -> int:
        """
        Store job search results in database
        
        Args:
            search_query: Search parameters used
            search_results: List of job dictionaries
            
        Returns:
            int: Number of jobs successfully stored
        """
        if not self.connection:
            raise Exception("Database connection not established")
            
        stored_count = 0
        updated_count = 0
        
        for job in search_results:
            try:
                result = self.store_job(job, search_query)
                if result == "stored":
                    stored_count += 1
                elif result == "updated":
                    updated_count += 1
            except Exception as e:
                print(f"❌ Failed to store job {job.get('role', 'Unknown')}: {e}")
        
        print(f"✅ Stored: {stored_count} new, Updated: {updated_count} existing")
        return stored_count + updated_count
    
    def store_job(self, job_data: Dict[str, Any], search_query: Dict[str, Any]) -> str:
        """
        Store individual job with deduplication
        
        Returns:
            str: "stored", "updated", or "skipped"
        """
        if not self.connection:
            raise Exception("Database connection not established")
            
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Prepare job data
                job_record = {
                    'company': job_data.get('company', '').strip(),
                    'role': job_data.get('role', '').strip(),
                    'tech_stack': job_data.get('tech_stack', []),
                    'job_type': job_data.get('job_type', '').strip(),
                    'salary': job_data.get('salary', '').strip(),
                    'location': job_data.get('location', '').strip(),
                    'description': job_data.get('description', '').strip(),
                    'requirements': json.dumps(job_data.get('requirements', {})),
                    'benefits': json.dumps(job_data.get('benefits', {})),
                    'source_platform': job_data.get('source_platform', '').strip(),
                    'source_url': job_data.get('source_url', '').strip(),
                    'posted_date': job_data.get('posted_date'),
                    'keywords': job_data.get('keywords', []),
                    'is_active': True
                }
                
                # Validate required fields
                if not job_record['company'] or not job_record['role']:
                    return "skipped"
                
                # Insert or update job
                cursor.execute("""
                    INSERT INTO jobs (
                        company, role, tech_stack, job_type, salary, location,
                        description, requirements, benefits, source_platform,
                        source_url, posted_date, keywords, is_active
                    ) VALUES (
                        %(company)s, %(role)s, %(tech_stack)s, %(job_type)s,
                        %(salary)s, %(location)s, %(description)s,
                        %(requirements)s::jsonb, %(benefits)s::jsonb, %(source_platform)s,
                        %(source_url)s, %(posted_date)s, %(keywords)s, %(is_active)s
                    )
                    ON CONFLICT (source_url) DO UPDATE SET
                        company = EXCLUDED.company,
                        role = EXCLUDED.role,
                        tech_stack = EXCLUDED.tech_stack,
                        job_type = EXCLUDED.job_type,
                        salary = EXCLUDED.salary,
                        location = EXCLUDED.location,
                        description = EXCLUDED.description,
                        requirements = EXCLUDED.requirements,
                        benefits = EXCLUDED.benefits,
                        source_platform = EXCLUDED.source_platform,
                        posted_date = EXCLUDED.posted_date,
                        keywords = EXCLUDED.keywords,
                        scraped_date = CURRENT_TIMESTAMP,
                        is_active = true
                    RETURNING (xmax = 0) as was_inserted
                """, job_record)
                
                result = cursor.fetchone()
                action = "stored" if result['was_inserted'] else "updated"
                
                # Store search context
                if job_record['source_url']:
                    self.store_search_context(job_record['source_url'], search_query)
                
                return action
                
        except Exception as e:
            print(f"❌ Error storing job: {e}")
            return "skipped"
    
    def store_search_context(self, source_url: str, search_query: Dict[str, Any]):
        """Store search context for analytics"""
        if not self.connection:
            return
            
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO search_history (source_url, search_query, search_date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (source_url, search_query) DO UPDATE SET
                        search_date = EXCLUDED.search_date
                """, (source_url, json.dumps(search_query), datetime.now()))
        except Exception as e:
            print(f"❌ Error storing search context: {e}")
    
    def get_recent_searches(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent search history"""
        if not self.connection:
            return []
            
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        search_query,
                        search_date,
                        COUNT(*) as job_count
                    FROM search_history
                    GROUP BY search_query, search_date
                    ORDER BY search_date DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error retrieving search history: {e}")
            return []
    
    def get_jobs_by_search(self, search_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get jobs that match a specific search query"""
        if not self.connection:
            return []
            
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Build dynamic query based on search parameters
                conditions = []
                params = []
                
                if search_query.get('keywords'):
                    keywords = search_query['keywords']
                    if isinstance(keywords, str):
                        keywords = [keywords]
                    conditions.append("keywords @> %s")
                    params.append(keywords)
                
                if search_query.get('location'):
                    conditions.append("location ILIKE %s")
                    params.append(f"%{search_query['location']}%")
                
                if search_query.get('job_type'):
                    conditions.append("job_type ILIKE %s")
                    params.append(f"%{search_query['job_type']}%")
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                query = f"""
                    SELECT * FROM jobs
                    WHERE {where_clause}
                    ORDER BY scraped_date DESC
                """
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error retrieving jobs by search: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

# Integration with existing scrapers
class JobSearchIntegrator:
    def __init__(self):
        self.storage = EnhancedJobStorage()
    
    def search_and_store(self, search_query: Dict[str, Any], scraper_function) -> int:
        """
        Unified search and storage function
        
        Args:
            search_query: Search parameters
            scraper_function: Function that returns job results
            
        Returns:
            int: Number of jobs stored
        """
        print(f"🔍 Searching for: {search_query}")
        
        # Run scraper
        jobs = scraper_function(search_query)
        
        # Store results
        stored_count = self.storage.store_search_results(search_query, jobs)
        
        print(f"✅ Search complete. Stored {stored_count} jobs")
        return stored_count
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Get search analytics"""
        recent_searches = self.storage.get_recent_searches()
        return {
            "total_searches": len(recent_searches),
            "recent_searches": recent_searches
        }

# Usage example
if __name__ == "__main__":
    # Example usage
    integrator = JobSearchIntegrator()
    
    search_query = {
        "keywords": ["python", "django"],
        "location": "remote",
        "job_type": "full-time"
    }
    
    # Mock scraper function
    def mock_scraper(query):
        return [
            {
                "company": "TechCorp",
                "role": "Senior Python Developer",
                "tech_stack": ["Python", "Django", "PostgreSQL"],
                "job_type": "Full-time",
                "salary": "$120k-$150k",
                "location": "Remote",
                "description": "We are looking for a senior Python developer...",
                "requirements": {"experience": "5+ years", "skills": ["Python", "Django"]},
                "benefits": {"health": "Full coverage", "pto": "Unlimited"},
                "source_platform": "RemoteOK",
                "source_url": "https://remoteok.com/12345",
                "posted_date": "2024-01-15",
                "keywords": ["python", "django", "remote", "senior"]
            }
        ]
    
    # Run search and store
    stored_count = integrator.search_and_store(search_query, mock_scraper)
    print(f"Stored {stored_count} jobs")
    
    # Cleanup
    integrator.storage.close()
