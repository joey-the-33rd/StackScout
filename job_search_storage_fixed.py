"""
Job Search Storage System - Fixed Version
Automatically stores job search results in the database for future reference
Fixed: Proper PostgreSQL array handling and keywords field selection
"""

import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import hashlib
import json
import logging

class JobSearchStorageFixed:
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
    
    def parse_postgres_array(self, array_str):
        """Properly parse PostgreSQL array strings to Python lists"""
        if not array_str or array_str == '{}':
            return []
        
        # Handle PostgreSQL array format properly
        if isinstance(array_str, str):
            # Remove curly braces
            array_str = array_str.strip('{}')
            if not array_str:
                return []
            
            # Use psycopg2's array parser
            try:
                # Simple CSV-like parsing with quote handling
                import csv
                from io import StringIO
                
                # Handle PostgreSQL array format
                array_str = array_str.replace('\\"', '"')
                
                # Use CSV parser for proper quote handling
                f = StringIO(array_str)
                reader = csv.reader(f, delimiter=',', quotechar='"')
                items = next(reader, [])
                
                # Clean up items
                items = [item.strip() for item in items if item.strip()]
                return items
            except Exception as e:
                logging.warning(f"Failed to parse PostgreSQL array format: {e}. Falling back to simple split.", exc_info=True)
                # Fallback to simple split if CSV parsing fails
                return [item.strip().strip('"') for item in array_str.split(',') if item.strip()]
        
        elif isinstance(array_str, list):
            return array_str
        
        return []
    
    def store_job(self, job_data, search_query):
        """Store individual job with search context"""
        try:
            with self.connection.cursor() as cursor:
                # Generate unique hash for deduplication
                job_hash = hashlib.md5(
                    f"{job_data.get('company', '')}{job_data.get('role', '')}{job_data.get('source_url', '')}".encode()
                ).hexdigest()
                
                # Parse array fields properly
                tech_stack = self.parse_postgres_array(job_data.get('tech_stack', []))
                keywords = self.parse_postgres_array(job_data.get('keywords', []))
                
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
                """, job_record)
                
                return True
                
        except psycopg2.Error as e:
            logging.error(f"❌ PostgreSQL error storing job for company={job_data.get('company', 'unknown')}, role={job_data.get('role', 'unknown')}: {e}", exc_info=True)
            return False
        except Exception as e:
            logging.error(f"❌ Unexpected error storing job for company={job_data.get('company', 'unknown')}, role={job_data.get('role', 'unknown')}: {e}", exc_info=True)
            return False
    
    def get_jobs_filtered(self, limit=100, offset=0, search="", platform="", status=""):
        """Get jobs with filtering and pagination - fixed version"""
        try:
            with self.connection.cursor() as cursor:
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
                    # Convert arrays properly
                    job['tech_stack'] = self.parse_postgres_array(job.get('tech_stack', []))
                    job['keywords'] = self.parse_postgres_array(job.get('keywords', []))
                    results.append(job)
                
                return results
        except psycopg2.Error as e:
            logging.error(f"❌ PostgreSQL error getting filtered jobs with params limit={limit}, offset={offset}, search='{search}', platform='{platform}', status='{status}': {e}", exc_info=True)
            return []
        except Exception as e:
            logging.error(f"❌ Unexpected error getting filtered jobs with params limit={limit}, offset={offset}, search='{search}', platform='{platform}', status='{status}': {e}", exc_info=True)
            return []

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'job_scraper_db',
    'user': 'joeythe33rd',
    'password': '',
    'port': 5432
}

if __name__ == "__main__":
    storage = JobSearchStorageFixed(DB_CONFIG)
    logging.basicConfig(level=logging.INFO)
    logging.info("✅ Job Search Storage Fixed initialized successfully")
<environment_details>
# VSCode Visible Files
job_search_storage_fixed.py

# VSCode Open Tabs
enhanced_web_integration.py
static/js/security_utils.js
tailwind.config.js
postcss.config.js
src/styles/input.css
templates/enhanced_index.html
templates/index.html
package.json
static/js/db_manager.js
stackscout_web.py
display_jobs.py
templates/database_manager_clean.html
static/js/database_manager_fixed.js
.gitignore
job_search_storage.py
job_search_storage_fixed.py
job_search_storage_secure.py
database_config_specs.md
</environment_details>
