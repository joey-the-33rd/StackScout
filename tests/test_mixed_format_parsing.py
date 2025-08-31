 #!/usr/bin/env python3
"""
Test script to verify mixed format salary parsing (e.g., "80k-120000")
This tests the per-side 'k' suffix handling fix in the SQL function.
"""

import psycopg2
import sys
import os

# Add the parent directory to the path to import DB_CONFIG
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import DB_CONFIG from job_search_storage
try:
    from job_search_storage import DB_CONFIG
except ImportError:
    # Fallback if DB_CONFIG is not available
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'job_scraper_db',
        'user': 'joeythe33rd',
        'password': '',  # Add your password if needed
        'port': 5432
    }

def test_mixed_format_parsing():
    """Test the mixed format parsing functionality"""
    print("🧪 Testing Mixed Format Salary Parsing...")
    print("=" * 60)
    
    test_cases = [
        # Mixed formats (the main issue being fixed)
        ("80k-120000", "Mixed format: 80k-120000", 80000, 120000),
        ("100000-150k", "Mixed format: 100000-150k", 100000, 150000),
        ("75K-90000", "Mixed format: 75K-90000", 75000, 90000),
        
        # Consistent formats (should still work)
        ("100k-150k", "Consistent k format: 100k-150k", 100000, 150000),
        ("100000-150000", "Consistent numeric: 100000-150000", 100000, 150000),
        ("80K-120K", "Consistent K format: 80K-120K", 80000, 120000),
        
        # Edge cases
        ("1k-2000", "Small mixed: 1k-2000", 1000, 2000),
        ("50000-100k", "Mixed: 50000-100k", 50000, 100000),
    ]
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Testing parse_salary function with mixed formats:")
        print("-" * 50)
        
        for salary_text, description, expected_min, expected_max in test_cases:
            try:
                # Test the parse_salary function directly
                cursor.execute("SELECT * FROM parse_salary(%s)", (salary_text,))
                result = cursor.fetchone()
                
                if result:
                    min_salary, max_salary, currency = result
                    status = "✅ PASS" if min_salary == expected_min and max_salary == expected_max else "❌ FAIL"
                    
                    print(f"{status} {description}")
                    print(f"   Input: '{salary_text}'")
                    print(f"   Expected: Min={expected_min}, Max={expected_max}")
                    print(f"   Actual:   Min={min_salary}, Max={max_salary}")
                    
                    if min_salary != expected_min or max_salary != expected_max:
                        print(f"   ❌ MISMATCH!")
                else:
                    print(f"❌ NO RESULT: {description} - '{salary_text}'")
                    
            except Exception as e:
                print(f"❌ ERROR testing '{salary_text}': {e}")
            
            print()
        
        # Test database trigger functionality
        print("\n🧪 Testing Database Trigger with Mixed Formats:")
        print("-" * 50)
        
        trigger_test_cases = [
            ("TestMixed1", "80k-120000"),
            ("TestMixed2", "100000-150k"),
            ("TestMixed3", "75K-90000"),
        ]
        
        for company, salary in trigger_test_cases:
            try:
                # Insert test record (should trigger automatic parsing)
                cursor.execute("""
                    INSERT INTO jobs (company, role, salary, source_platform, source_url, is_active)
                    VALUES (%s, %s, %s, %s, %s, true)
                    RETURNING id, salary_min_numeric, salary_max_numeric, salary_currency
                """, (company, 'Test Role', salary, 'test', f'test-mixed-{company.lower()}'))
                
                result = cursor.fetchone()
                if result:
                    job_id, min_sal, max_sal, currency = result
                    print(f"✅ Trigger parsed '{salary}' -> Min: {min_sal}, Max: {max_sal}")
                else:
                    print(f"❌ Trigger failed for '{salary}'")
                    
            except Exception as e:
                print(f"❌ Trigger test error for '{salary}': {e}")
        
        # Clean up test data
        cursor.execute("DELETE FROM jobs WHERE source_platform = 'test'")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 Mixed format parsing tests completed!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure PostgreSQL is running and the database is accessible")

if __name__ == "__main__":
    test_mixed_format_parsing()
