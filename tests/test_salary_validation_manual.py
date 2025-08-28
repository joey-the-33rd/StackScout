#!/usr/bin/env python3
"""
Manual test script to verify the parse_salary_range_for_query method behavior
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from job_search_storage import JobSearchStorage

# Create a minimal storage instance without database connection
class TestStorage:
    def __init__(self):
        pass
    
    def parse_salary_amount(self, amount_str):
        """Parse a single salary amount string and return numeric value"""
        if not amount_str:
            return None
        
        # Remove currency symbols and commas
        clean_str = amount_str.replace('$', '').replace('€', '').replace('£', '').replace(',', '')
        
        # Handle 'k' suffix (thousands)
        if clean_str.lower().endswith('k'):
            clean_str = clean_str[:-1]
            multiplier = 1000
        else:
            multiplier = 1
        
        try:
            return int(float(clean_str) * multiplier)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid salary amount: {amount_str}")
    
    def parse_salary_range_for_query(self, salary_range):
        """Parse salary range string and return numeric min and max values"""
        if salary_range is None or str(salary_range).strip() == "":
            raise ValueError("Empty salary filter")

        sr = str(salary_range).strip().replace(' ', '')

        try:
            if sr.endswith('+'):
                # Handle minimum salary filter (e.g., "100k+")
                min_str = sr[:-1]
                if min_str == "":
                    raise ValueError("Missing minimum amount before '+'")
                min_val = self.parse_salary_amount(min_str)
                return min_val, None

            elif '-' in sr:
                # Handle range filter (e.g., "100k-200k")
                min_str, max_str = sr.split('-', 1)
                if min_str == "" or max_str == "":
                    raise ValueError("Incomplete salary range")
                min_val = self.parse_salary_amount(min_str)
                max_val = self.parse_salary_amount(max_str)
                return min_val, max_val

            else:
                # Handle exact match filter
                exact_val = self.parse_salary_amount(sr)
                return exact_val, exact_val

        except (ValueError, AttributeError) as e:
            # Re-raise ValueError as-is to preserve specific messages
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid salary range format: {salary_range}")

def test_cases():
    """Test various salary range parsing scenarios"""
    storage = TestStorage()
    
    test_cases = [
        # Valid cases
        ("100k+", "Valid minimum salary"),
        ("80k-120k", "Valid range"),
        ("100000", "Valid exact amount"),
        ("$100k", "Valid with currency"),
        
        # Invalid cases that should raise ValueError
        ("", "Empty string"),
        (None, "None input"),
        ("+", "Missing minimum before +"),
        ("100k-", "Incomplete range (missing max)"),
        ("-200k", "Incomplete range (missing min)"),
        ("invalid", "Invalid format"),
    ]
    
    print("🧪 Testing salary range parsing...")
    print("=" * 50)
    
    for salary_range, description in test_cases:
        print(f"\n📋 {description}: '{salary_range}'")
        try:
            result = storage.parse_salary_range_for_query(salary_range)
            print(f"   ✅ SUCCESS: {result}")
        except ValueError as e:
            print(f"   ❌ ERROR: {e}")
        except Exception as e:
            print(f"   💥 UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_cases()
