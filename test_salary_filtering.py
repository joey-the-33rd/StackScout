#!/usr/bin/env python3
"""
Test script to verify that the numeric salary filtering is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_search_storage import JobSearchStorage, DB_CONFIG

def test_salary_filtering():
    """Test the salary filtering functionality"""
    print("🧪 Testing salary filtering with numeric fields...")
    
    # Initialize the storage
    storage = JobSearchStorage(DB_CONFIG)
    
    # Test cases for salary filtering
    test_cases = [
        ("100k+", "Minimum salary filter"),
        ("80k-120k", "Salary range filter"),
        ("150000+", "Minimum salary (no k suffix)"),
        ("80000-120000", "Salary range (no k suffix)"),
    ]
    
    for salary_range, description in test_cases:
        print(f"\n📋 Testing: {description} - '{salary_range}'")
        try:
            jobs = storage.get_jobs_filtered(salary_range=salary_range, limit=10)
            print(f"   ✅ Found {len(jobs)} jobs matching the salary range")
            
            if jobs:
                for job in jobs[:3]:  # Show first 3 results
                    print(f"      - {job.get('company', 'N/A')}: {job.get('role', 'N/A')}")
                    print(f"        Salary: {job.get('salary', 'N/A')}")
                    print(f"        Min: {job.get('salary_min_numeric')}, Max: {job.get('salary_max_numeric')}, Currency: {job.get('salary_currency')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test invalid salary format
    print(f"\n📋 Testing invalid salary format: 'invalid'")
    try:
        jobs = storage.get_jobs_filtered(salary_range="invalid", limit=10)
        print(f"   ✅ Gracefully handled invalid format, found {len(jobs)} jobs")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    storage.close()
    print("\n🎉 Salary filtering test completed!")

if __name__ == "__main__":
    test_salary_filtering()
