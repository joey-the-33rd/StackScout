#!/usr/bin/env python3
"""
Test script for enhanced search filters functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_search_storage import JobSearchStorage, DB_CONFIG
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_enhanced_filters():
    """Test the enhanced filtering functionality"""
    try:
        storage = JobSearchStorage(DB_CONFIG)
        print("✅ Connected to database successfully")
        
        # Test job type filtering
        print("\n🧪 Testing job type filtering...")
        jobs = storage.get_jobs_filtered(job_type="full-time", limit=5)
        print(f"Found {len(jobs)} full-time jobs")
        
        # Test salary range filtering
        print("\n🧪 Testing salary range filtering...")
        jobs = storage.get_jobs_filtered(salary_range="$50k-$70k", limit=5)
        print(f"Found {len(jobs)} jobs in $50k-$70k range")
        
        # Test combined filtering
        print("\n🧪 Testing combined filtering...")
        jobs = storage.get_jobs_filtered(job_type="full-time", salary_range="$70k-$90k", limit=5)
        print(f"Found {len(jobs)} full-time jobs in $70k-$90k range")
        
        # Test $150k+ filtering
        print("\n🧪 Testing $150k+ filtering...")
        jobs = storage.get_jobs_filtered(salary_range="$150k+", limit=5)
        print(f"Found {len(jobs)} jobs with $150k+ salary")
        
        storage.close()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_filters()
