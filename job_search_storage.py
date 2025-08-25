"""
Job Search Storage System
Automatically stores job search results in the database for future reference
"""

import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import hashlib
import json
import logging

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
            logging.info("✅ Connected to job_scraper_db successfully")
        except psycopg2.Error as e:
            logging.error(f"❌ Database connection failed: {e}", exc_info=True)
            raise
        except Exception as e:
            logging.error(f"❌ Unexpected error during database connection: {e}", exc_info=True)
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
                logging.error(f"❌ Failed to store job for company={job.get('company', 'unknown')}: {e}", exc_info=True)
        
        logging.info(f"✅ Stored {stored_count} jobs from search query: {search_query}")
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
                
                # Prepare job data for insertion - handle array types properly
                tech_stack = job_data.get('tech_stack', [])
                keywords = job_data.get('keywords', [])
                
                # Ensure arrays are properly formatted with explicit validation and logging
                if isinstance(tech_stack, str):
                    try:
                        parsed_tech_stack = json.loads(tech_stack)
                        # Validate that parsed data is a list
                        if isinstance(parsed_tech_stack, list):
                            tech_stack = parsed_tech_stack
                        else:
                            logging.warning(f"Invalid tech_stack format: expected list, got {type(parsed_tech_stack)}. Using original string as single item.")
                            tech_stack = [tech_stack]
                    except json.JSONDecodeError as e:
                        logging.warning(f"Failed to parse tech_stack JSON: {e}. Input: {tech_stack}. Using string as single item.")
                        tech_stack = [tech_stack]
                    except Exception as e:
                        logging.error(f"Unexpected error parsing tech_stack: {e}. Input: {tech_stack}. Using string as single item.")
                        tech_stack = [tech_stack]
                
                # Handle keywords JSON parsing with explicit validation and logging
                if isinstance(keywords, str):
                    try:
                        parsed_keywords = json.loads(keywords)
                        if isinstance(parsed_keywords, list):
                            keywords = parsed_keywords
                        else:
                            logging.warning(f"Invalid keywords format: expected list, got {type(parsed_keywords)}. Using original string as single item.")
                            keywords = [keywords]
                    except json.JSONDecodeError as e:
                        logging.warning(f"Failed to parse keywords JSON: {e}. Input: {keywords}. Using string as single item.")
                        keywords = [keywords]
                    except Exception as e:
                        logging.error(f"Unexpected error parsing keywords: {e}. Input: {keywords}. Using string as single item.")
                        keywords = [keywords]
                
                # Ensure final values are lists
                if not isinstance(tech_stack, list):
                    logging.warning(f"tech_stack is not a list after processing: {type(tech_stack)}. Converting to list.")
                    tech_stack = [str(tech_stack)] if tech_stack is not None else []
                
                if not isinstance(keywords, list):
                    logging.warning(f"keywords is not a list after processing: {type(keywords)}. Converting to list.")
                    keywords = [str(keywords)] if keywords is not None else []
                
                job_record = {
                    'company': str(job_data.get('company', '')),
                    'role': str(job_data.get('role', '')),
                    'tech_stack': tech_stack,
                    'job_type': str(job_data.get('job_type', '')),
                    'salary': str(job_data.get('salary', '')),
                    'location': str(job_data.get('location', '')),
                    'description': str(job_data.get('description', '')),
                    'requirements': Json(job_data.get('requirements', {})),
                    'benefits': Json(job_data.get('benefits', {})),
                    'source_platform': str(job_data.get('source_platform', '')),
                    'source_url': str(job_data.get('source_url', '')),
                    'posted_date': str(job_data.get('posted_date', '')),
                    'keywords': keywords,
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
                
        except psycopg2.Error as e:
            logging.error(f"❌ PostgreSQL error storing job for company={job_data.get('company', 'unknown')}, role={job_data.get('role', 'unknown')}: {e}", exc_info=True)
            return False
        except Exception as e:
            logging.error(f"❌ Unexpected error storing job for company={job_data.get('company', 'unknown')}, role={job_data.get('role', 'unknown')}: {e}", exc_info=True)
            return False
    
    def generate_job_hash(self, job_data):
        """Generate unique hash for job deduplication"""
        try:
            hash_input = f"{job_data.get('company', '')}{job_data.get('role', '')}{job_data.get('source_url', '')}"
            return hashlib.md5(hash_input.encode()).hexdigest()
        except Exception as e:
            logging.error(f"❌ Error generating job hash: {e}", exc_info=True)
            return ""
    
    def store_search_context(self, source_url, search_query):
        """Store search context for analytics"""
        try:
            normalized_url = (source_url or "").strip()
            if not normalized_url:
                logging.warning("⚠️ Skipping search context insert: empty source_url")
                return
            
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO search_history (source_url, search_query, search_date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (source_url, search_query) DO UPDATE SET
                        search_date = EXCLUDED.search_date
                """, (normalized_url, json.dumps(search_query), datetime.now()))
        except psycopg2.Error as e:
            logging.error(f"❌ PostgreSQL error storing search context for URL={source_url}: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"❌ Unexpected error storing search context for URL={source_url}: {e}", exc_info=True)
    
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
        except psycopg2.Error as e:
            logging.error(f"❌ PostgreSQL error retrieving search history: {e}", exc_info=True)
            return []
        except Exception as e:
            logging.error(f"❌ Unexpected error retrieving search history: {e}", exc_info=True)
            return []
    
    def get_database_stats(self):
        """Get comprehensive database statistics"""
        try:
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
                platform_stats = cursor.fetchall()
                
                # Growth rate (comparing last 7 days to previous 7 days)
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN scraped_date >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as recent,
                        COUNT(CASE WHEN scraped_date >= CURRENT_DATE - INTERVAL '14 days' 
                                  AND scraped_date < CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as previous
                    FROM jobs
                """)
                recent, previous = cursor.fetchone()
                growth_rate = 0
                if previous > 0:
                    growth_rate = ((recent - previous) / previous) * 100
                
                return {
                    "total_jobs": total_jobs,
                    "active_jobs": active_jobs,
                    "week_jobs": week_jobs,
                    "growth_rate": round(growth_rate, 2),
                    "platform_stats": dict(platform_stats)
                }
        except psycopg2.Error as e:
            logging.error(f"❌ PostgreSQL error getting database stats: {e}", exc_info=True)
            return {
                "total_jobs": 0,
                "active_jobs": 0,
                "week_jobs": 0,
                "growth_rate": 0,
                "platform_stats": {}
            }
        except Exception as e:
            logging.error(f"❌ Unexpected error getting database stats: {e}", exc_info=True)
            return {
                "total_jobs": 0,
                "active_jobs": 0,
                "week_jobs": 0,
                "growth_rate": 0,
                "platform_stats": {}
            }
    
    def get_jobs_filtered(self, limit=100, offset=0, search="", platform="", status="", job_type="", salary_range=""):
        """Get jobs with filtering and pagination"""
        try:
            with self.connection.cursor() as cursor:
                # sanitize pagination inputs
                try:
                    limit = max(1, min(int(limit), 1000))
                    offset = max(0, int(offset))
                except (ValueError, TypeError):
                    limit, offset = 100, 0
                
                query = """
                    SELECT id, company, role, tech_stack, job_type, salary, location,
                           description, source_platform, source_url, posted_date,
                           scraped_date, is_active, keywords
                    FROM jobs
                    WHERE 1=1
                """
                params = []
                
                if search:
                    query += " AND (company ILIKE %s OR role ILIKE %s OR description ILIKE %s)"
                    search_param = f"%{search}%"
                    params.extend([search_param, search_param, search_param])
                
                if platform:
                    query += " AND source_platform = %s"
                    params.append(platform)

                if job_type:
                    query += " AND job_type = %s"
                    params.append(job_type)

                if salary_range and salary_range.strip():
                    try:
                        # Handle URL encoding issues - replace spaces with +
                        salary_range = salary_range.replace(' ', '+')
                        
                        if salary_range.endswith('+'):
                            # Handle ranges like "$150k+"
                            salary_min = salary_range.replace('+', '').strip()
                            query += " AND salary >= %s"
                            params.append(salary_min)
                        else:
                            # Handle ranges like "$50k-$70k"
                            salary_min, salary_max = salary_range.split('-')
                            query += " AND salary BETWEEN %s AND %s"
                            params.extend([salary_min.strip(), salary_max.strip()])
                    except (ValueError, AttributeError):
                        # Handle invalid salary range format
                        logging.warning(f"Invalid salary range format: {salary_range}")
                
                if status == "active":
                    query += " AND is_active = true"
                elif status == "expired":
                    query += " AND is_active = false"
                
                query += " ORDER BY scraped_date DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
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
                
                # Convert datetime fields to string for JSON serialization
                for job in results:
                    if isinstance(job.get('posted_date'), datetime):
                        job['posted_date'] = job['posted_date'].isoformat()
                    if isinstance(job.get('scraped_date'), datetime):
                        job['scraped_date'] = job['scraped_date'].isoformat()
                return results
        except psycopg2.Error as e:
            logging.error(f"❌ PostgreSQL error getting filtered jobs with params limit={limit}, offset={offset}, search='{search}', platform='{platform}', status='{status}': {e}", exc_info=True)
            return []
        except Exception as e:
            logging.error(f"❌ Unexpected error getting filtered jobs with params limit={limit}, offset={offset}, search='{search}', platform='{platform}', status='{status}': {e}", exc_info=True)
            return []
    
    def delete_job(self, job_id):
        """Delete a specific job by ID"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    logging.info(f"✅ Successfully deleted job with ID={job_id}")
                    return True
                else:
                    logging.warning(f"⚠️ No job found with ID={job_id} to delete")
                    return False
        except psycopg2.Error as e:
            logging.error(f"❌ PostgreSQL error deleting job with ID={job_id}: {e}", exc_info=True)
            return False
        except Exception as e:
            logging.error(f"❌ Unexpected error deleting job with ID={job_id}: {e}", exc_info=True)
            return False
    
    def close(self):
        """Close database connection"""
        try:
            if self.connection:
                self.connection.close()
                logging.info("✅ Database connection closed")
        except Exception as e:
            logging.error(f"❌ Error closing database connection: {e}", exc_info=True)

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
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        storage = JobSearchStorage(DB_CONFIG)
        logging.info("✅ Job Search Storage initialized successfully")
    except ValueError as e:
        logging.error(f"❌ Configuration error: {e}", exc_info=True)
    except Exception as e:
        logging.error(f"❌ Initialization failed: {e}", exc_info=True)
