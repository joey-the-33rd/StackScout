"""
Job Search Storage System
Automatically stores job search results in the database for future reference
"""

import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import hashlib
import json

class JobSearchStorage:
    def __init__(self, db_config):
        """Initialize database connection"""
        self.db_config = db_config
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            print("✅ Connected to job_scraper_db successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def store_search_results(self, search_query, search_results):
        """
        Store job search results in database
        
        Args:
            search_query (dict): Search parameters used
            search_results (list): List of job dictionaries
        """
        stored_count = 0
        for job in search_results:
            try:
                if self.store_job(job, search_query):
                    stored_count += 1
            except Exception as e:
                print(f"❌ Failed to store job: {e}")
        
        print(f"✅ Stored {stored_count} jobs from search query: {search_query}")
        return stored_count
    
    def store_job(self, job_data, search_query):
        """
        Store individual job with search context
        
        Args:
            job_data (dict): Job information
            search_query (dict): Original search parameters
        
        Returns:
            bool: Success status
        """
        try:
            with self.connection.cursor() as cursor:
                # Generate unique hash for deduplication
                job_hash = self.generate_job_hash(job_data)
                
                # Prepare job data for insertion
                job_record = {
                    'company': job_data.get('company', ''),
                    'role': job_data.get('role', ''),
                    'tech_stack': job_data.get('tech_stack', []),
                    'job_type': job_data.get('job_type', ''),
                    'salary': job_data.get('salary', ''),
                    'location': job_data.get('location', ''),
                    'description': job_data.get('description', ''),
                    'requirements': job_data.get('requirements', {}),
                    'benefits': job_data.get('benefits', {}),
                    'source_platform': job_data.get('source_platform', ''),
                    'source_url': job_data.get('source_url', ''),
                    'posted_date': job_data.get('posted_date'),
                    'keywords': job_data.get('keywords', []),
                    'is_active': True
                }
                
                # Insert or update job
                cursor.execute("""
                    INSERT INTO jobs (
                        company, role, tech_stack, job_type, salary, location,
                        description, requirements, benefits, source_platform,
                        source_url, posted_date, keywords, is_active
                    ) VALUES (
                        %(company)s, %(role)s, %(tech_stack)s, %(job_type)s,
                        %(salary)s, %(location)s, %(description)s,
                        %(requirements)s, %(benefits)s, %(source_platform)s,
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
                    WHERE jobs.source_url = EXCLUDED.source_url
                """, job_record)
                
                # Store search context
                self.store_search_context(job_data.get('source_url', ''), search_query)
                
                return True
                
        except Exception as e:
            print(f"❌ Error storing job: {e}")
            return False
    
    def generate_job_hash(self, job_data):
        """Generate unique hash for job deduplication"""
        hash_input = f"{job_data.get('company', '')}{job_data.get('role', '')}{job_data.get('source_url', '')}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def store_search_context(self, source_url, search_query):
        """Store search context for analytics"""
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
    
    def get_search_history(self, limit=100):
        """Retrieve recent search history"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT search_query, search_date, COUNT(*) as job_count
                    FROM search_history
                    GROUP BY search_query, search_date
                    ORDER BY search_date DESC
                    LIMIT %s
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error retrieving search history: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'job_scraper_db',
    'user': 'joeythe33rd',
    'password': '',  # Add your password if needed
    'port': 5432
}

# Usage example
if __name__ == "__main__":
    storage = JobSearchStorage(DB_CONFIG)
    
    # Example search query
    search_query = {
        "keywords": ["python", "remote"],
        "location": "remote",
        "job_type": "full-time"
    }
    
    # Example job results
    sample_jobs = [
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
            "keywords": ["python", "remote", "senior"]
        }
    ]
    
    # Store results
    storage.store_search_results(search_query, sample_jobs)
    storage.close()
