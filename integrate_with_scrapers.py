"""
Integration script to connect existing scrapers with database storage
"""

from enhanced_job_storage import JobSearchIntegrator
import json

def integrate_scrapers_with_storage():
    """Integrate all scrapers with database storage"""
    
    integrator = JobSearchIntegrator()
    
    # Define search queries
    search_queries = [
        {
            "keywords": ["python", "django", "flask"],
            "location": "remote",
            "job_type": "full-time"
        },
        {
            "keywords": ["javascript", "react", "node"],
            "location": "remote",
            "job_type": "full-time"
        },
        {
            "keywords": ["data", "python", "machine learning"],
            "location": "remote",
            "job_type": "full-time"
        }
    ]
    
    total_stored = 0
    
    for query in search_queries:
        try:
            # Use existing scraper function
            from multi_platform_scraper_playwright import scrape_jobs
            stored_count = integrator.search_and_store(query, scrape_jobs)
            total_stored += stored_count
        except Exception as e:
            print(f"❌ Error processing query {query}: {e}")
    
    print(f"🎉 Total jobs stored: {total_stored}")
    
    # Get analytics
    analytics = integrator.get_search_analytics()
    print("📊 Search Analytics:")
    print(json.dumps(analytics, indent=2, default=str))
    
    # Cleanup
    integrator.storage.close()

if __name__ == "__main__":
    integrate_scrapers_with_storage()
