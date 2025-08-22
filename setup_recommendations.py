#!/usr/bin/env python3
"""Setup script for recommendation system."""

import psycopg2
import sys
import logging
from job_search_storage import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_recommendation_database():
    """Set up the recommendation database schema."""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Read and execute the schema
            with open('create_recommendations_schema.sql', 'r') as f:
                schema_sql = f.read()
                cursor.execute(schema_sql)
                
            logger.info("✅ Recommendation database schema created successfully")
            
    except Exception as e:
        logger.error(f"❌ Error setting up recommendation database: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

def install_dependencies():
    """Install required dependencies for recommendations."""
    import subprocess
    
    try:
        logger.info("Installing recommendation dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "scikit-learn", "numpy", "scipy"
        ])
        logger.info("✅ Recommendation dependencies installed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error installing dependencies: {e}")
        return False

def test_recommendation_engine():
    """Test the recommendation engine setup."""
    try:
        from src.recommendations.engine import RecommendationEngine
        from src.recommendations.database import RecommendationDatabase
        
        # Test database connection
        db = RecommendationDatabase(DB_CONFIG)
        db.connect()
        logger.info("✅ Recommendation database connection test passed")
        db.close()
        
        # Test engine initialization
        engine = RecommendationEngine()
        logger.info("✅ Recommendation engine initialization test passed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Recommendation system test failed: {e}")
        return False

if __name__ == "__main__":
    print("StackScout Recommendation System Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup database
    if not setup_recommendation_database():
        sys.exit(1)
    
    # Test the system
    if not test_recommendation_engine():
        sys.exit(1)
    
    print("\n✅ Recommendation system setup complete!")
    print("\nNext steps:")
    print("1. Start the server: python stackscout_web.py")
    print("2. Test recommendations: python test_recommendations.py")
    print("3. Access recommendations at: http://localhost:8000/recommendations/jobs")
    print("4. View recommendation stats at: http://localhost:8000/recommendations/stats")
