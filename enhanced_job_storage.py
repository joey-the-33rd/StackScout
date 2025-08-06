"""
Enhanced Job Search Storage System
Automatically stores job search results in the database with improved error handling
"""

import psycopg2
from psycopg2.extras import Json, RealDictCursor
from psycopg2 import pool as psycopg2_pool
from datetime import datetime
import hashlib
import json
import os
from typing import List, Dict, Any

class EnhancedJobStorage:
    def __init__(self):
        """Initialize database connection with secure environment variables"""
        self._validate_environment()
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'sslmode': os.getenv('DB_SSL_MODE', 'prefer'),
            'connect_timeout': int(os.getenv('DB_CONNECTION_TIMEOUT', 30))
        }
        self.connection_pool = None
        self._setup_connection_pool()
    
    def _validate_environment(self):
        """Validate required environment variables are set with security checks"""
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Additional security validation
        password = os.getenv('DB_PASSWORD')
        if password and len(password) < 8:
            raise ValueError("Database password must be at least 8 characters long")
        
        # Validate host format
        host = os.getenv('DB_HOST')
        if host and not (host.startswith('localhost') or '.' in host or host.startswith('127.0.0.1')):
            raise ValueError("Invalid database host format")
        
        # Validate port
        port = os.getenv('DB_PORT', '5432')
        try:
            port_int = int(port)
            if not (1 <= port_int <= 65535):
                raise ValueError("Database port must be between 1 and 65535")
        except ValueError:
            raise ValueError("Database port must be a valid integer")
        
        # Validate SSL mode
        ssl_mode = os.getenv('DB_SSL_MODE', 'prefer')
        valid_ssl_modes = ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']
        if ssl_mode not in valid_ssl_modes:
            raise ValueError(f"Invalid SSL mode. Must be one of: {', '.join(valid_ssl_modes)}")
    
    def _setup_connection_pool(self):
        """Setup connection pool for better resource management"""
        try:
            self.connection_pool = psycopg2_pool.SimpleConnectionPool(
                minconn=int(os.getenv('DB_MIN_CONNECTIONS', 5)),
                maxconn=int(os.getenv('DB_MAX_CONNECTIONS', 20)),
                **self.db_config
            )
            print("✅ Database connection pool established successfully")
        except Exception as e:
            print(f"❌ Failed to establish connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool with context manager support"""
        if not self.connection_pool:
            raise Exception("Connection pool not initialized")
        return self.connection_pool.getconn()
    
    def return_connection(self, connection):
        """Return connection to pool"""
        if self.connection_pool and connection:
            self.connection_pool.putconn(connection)
    
    def connection_context(self):
        """Context manager for database connections to prevent resource leaks"""
        class ConnectionContext:
            def __init__(self, pool):
                self.pool = pool
                self.conn = None
            
            def __enter__(self):
                if not self.pool:
                    raise Exception("Connection pool not initialized")
                self.conn = self.pool.getconn()
                return self.conn
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.conn:
                    if exc_type is not None:
                        # Rollback on exception
                        try:
                            self.conn.rollback()
                        except:
                            pass
                    self.pool.putconn(self.conn)
        
        return ConnectionContext(self.connection_pool)
    
    def close(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ Database connection pool closed")
    
    def store_search_results(self, search_query: Dict[str, Any], search_results: List[Dict[str, Any]]) -> int:
        """
        Store job search results in database with proper connection management
        
        Args:
            search_query: Search parameters used
            search_results: List of job dictionaries
            
        Returns:
            int: Number of jobs successfully stored
        """
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
        Store individual job with deduplication and proper connection management
        
        Returns:
            str: "stored", "updated", or "skipped"
        """
        connection = None
        try:
            connection = self.get_connection()
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
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
                
                connection.commit()
                return action
                
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"❌ Error storing job: {e}")
            return "skipped"
        finally:
            if connection:
                self.return_connection(connection)
    
    def store_search_context(self, source_url: str, search_query: Dict[str, Any]):
        """Store search context for analytics with proper connection management"""
        connection = None
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO search_history (source_url, search_query, search_date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (source_url, search_query) DO UPDATE SET
                        search_date = EXCLUDED.search_date
                """, (source_url, json.dumps(search_query), datetime.now()))
                connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"❌ Error storing search context: {e}")
        finally:
            if connection:
                self.return_connection(connection)
    
    def get_recent_searches(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent search history with proper connection management"""
        connection = None
        try:
            connection = self.get_connection()
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
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
        finally:
            if connection:
                self.return_connection(connection)
    
    def get_jobs_by_search(self, search_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get jobs that match a specific search query with proper connection management"""
        connection = None
        try:
            connection = self.get_connection()
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
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
        finally:
            if connection:
                self.return_connection(connection)
    
    def close(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ Database connection pool closed")

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
