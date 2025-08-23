#!/usr/bin/env python3
"""Setup script for authentication system."""

import psycopg2
import sys
import logging
from job_search_storage import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_auth_database():
    """Set up the authentication database schema."""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Read and execute the schema
            with open('create_users_schema.sql', 'r') as f:
                schema_sql = f.read()
                cursor.execute(schema_sql)
                
            logger.info("✅ Authentication database schema created successfully")
            
    except Exception as e:
        logger.error(f"❌ Error setting up authentication database: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

def install_dependencies():
    """Install required dependencies for authentication."""
    import subprocess
    
    try:
        logger.info("Installing authentication dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "python-jose[cryptography]", "passlib[bcrypt]", "python-multipart"
        ])
        logger.info("✅ Authentication dependencies installed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error installing dependencies: {e}")
        return False

if __name__ == "__main__":
    print("StackScout Authentication Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup database
    if not setup_auth_database():
        sys.exit(1)
    
    print("\n✅ Authentication system setup complete!")
    print("\nNext steps:")
    print("1. Start the server: python stackscout_web.py")
    print("2. Test authentication: python test_auth.py")
    print("3. Register at: http://localhost:8000/auth/register")
    print("4. Login at: http://localhost:8000/auth/login")
