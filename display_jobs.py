#!/usr/bin/env python3
"""
Script to display all jobs saved in the database with detailed information
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class JobDisplay:
    def __init__(self):
        """Initialize database connection"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'job_scraper_db'),
            'user': os.getenv('DB_USER', 'joeythe33rd'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 5432))
        }
    
    def get_all_jobs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all jobs from the database"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = """
                        SELECT 
                            id,
                            company,
                            role,
                            tech_stack,
                            job_type,
                            salary,
                            location,
                            description,
                            requirements,
                            benefits,
                            source_platform,
                            source_url,
                            posted_date,
                            keywords,
                            is_active,
                            scraped_date
                        FROM jobs
                        ORDER BY scraped_date DESC
                    """
                    
                    if limit is not None:
                        query += f" LIMIT {limit}"
                    
                    cursor.execute(query)
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            print(f"❌ Error retrieving jobs: {e}")
            return []
    
    def format_tech_stack(self, tech_stack) -> str:
        """Format tech stack array into readable string"""
        if not tech_stack:
            return "N/A"
        
        if isinstance(tech_stack, str):
            try:
                tech_stack = json.loads(tech_stack)
            except:
                return tech_stack
        
        if isinstance(tech_stack, list):
            return ", ".join(tech_stack)
        
        return str(tech_stack)
    
    def format_keywords(self, keywords) -> str:
        """Format keywords array into readable string"""
        if not keywords:
            return "N/A"
        
        if isinstance(keywords, str):
            try:
                keywords = json.loads(keywords)
            except:
                return keywords
        
        if isinstance(keywords, list):
            return ", ".join(keywords)
        
        return str(keywords)
    
    def display_job_details(self, job: Dict[str, Any]) -> None:
        """Display detailed information for a single job"""
        print("\n" + "="*80)
        print(f"🏢 {job['company']} - {job['role']}")
        print("="*80)
        
        print(f"📍 Location: {job['location']}")
        print(f"💰 Salary: {job['salary']}")
        print(f"📝 Job Type: {job['job_type']}")
        print(f"🔧 Tech Stack: {self.format_tech_stack(job['tech_stack'])}")
        print(f"🔑 Keywords: {self.format_keywords(job['keywords'])}")
        print(f"🌐 Source: {job['source_platform']}")
        print(f"🔗 URL: {job['source_url']}")
        print(f"📅 Posted: {job['posted_date']}")
        print(f"📊 Scraped: {job['scraped_date']}")
        print(f"✅ Active: {'Yes' if job['is_active'] else 'No'}")
        
        if job['description'] and job['description'] != 'N/A':
            print(f"\n📝 Description:")
            description = job['description'][:500] + "..." if len(job['description']) > 500 else job['description']
            print(description)
        
        if job['requirements']:
            print(f"\n📋 Requirements:")
            if isinstance(job['requirements'], dict):
                for key, value in job['requirements'].items():
                    print(f"  • {key}: {value}")
            else:
                print(job['requirements'])
        
        if job['benefits']:
            print(f"\n🎁 Benefits:")
            if isinstance(job['benefits'], dict):
                for key, value in job['benefits'].items():
                    print(f"  • {key}: {value}")
            else:
                print(job['benefits'])
    
    def display_summary(self, jobs: List[Dict[str, Any]]) -> None:
        """Display summary statistics"""
        if not jobs:
            print("❌ No jobs found in the database")
            return
        
        total_jobs = len(jobs)
        active_jobs = sum(1 for job in jobs if job['is_active'])
        
        # Count by platform
        platform_counts = {}
        for job in jobs:
            platform = job['source_platform']
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Count by location
        location_counts = {}
        for job in jobs:
            location = job['location']
            location_counts[location] = location_counts.get(location, 0) + 1
        
        print("\n" + "="*50)
        print("📊 DATABASE SUMMARY")
        print("="*50)
        print(f"Total Jobs: {total_jobs}")
        print(f"Active Jobs: {active_jobs}")
        print(f"Inactive Jobs: {total_jobs - active_jobs}")
        
        print("\n📱 Jobs by Platform:")
        for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {platform}: {count}")
        
        print("\n📍 Top Locations:")
        top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for location, count in top_locations:
            print(f"  {location}: {count}")
    
    def display_jobs_table(self, jobs: List[Dict[str, Any]]) -> None:
        """Display jobs in a table format"""
        if not jobs:
            print("❌ No jobs found")
            return
        
        print("\n" + "="*120)
        print(f"{'Company':<20} {'Role':<30} {'Location':<15} {'Type':<12} {'Source':<15} {'Active'}")
        print("="*120)
        
        for job in jobs:
            company = job['company'][:18] + ".." if len(job['company']) > 20 else job['company']
            role = job['role'][:28] + ".." if len(job['role']) > 30 else job['role']
            location = job['location'][:13] + ".." if len(job['location']) > 15 else job['location']
            job_type = job['job_type'][:10] + ".." if len(job['job_type']) > 12 else job['job_type']
            source = job['source_platform'][:13] + ".." if len(job['source_platform']) > 15 else job['source_platform']
            active = "✅" if job['is_active'] else "❌"
            
            print(f"{company:<20} {role:<30} {location:<15} {job_type:<12} {source:<15} {active}")

def main():
    """Main function to display jobs"""
    display = JobDisplay()
    
    print("🔍 Displaying jobs saved in the database...")
    
    # Get all jobs
    jobs = display.get_all_jobs()
    
    if not jobs:
        print("❌ No jobs found in the database")
        return
    
    # Display summary
    display.display_summary(jobs)
    
    # Ask user how they want to view the jobs
    print("\n" + "="*50)
    print("📋 VIEW OPTIONS:")
    print("1. Summary table")
    print("2. Detailed view (all jobs)")
    print("3. Detailed view (first 5 jobs)")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            display.display_jobs_table(jobs)
        elif choice == '2':
            for job in jobs:
                display.display_job_details(job)
        elif choice == '3':
            for job in jobs[:5]:
                display.display_job_details(job)
        elif choice == '4':
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")
    
    print(f"\n✅ Displayed {len(jobs)} jobs from the database")

if __name__ == "__main__":
    main()
