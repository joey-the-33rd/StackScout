#!/usr/bin/env python3
"""
Test suite for salary filtering functionality including million suffix support
"""

import pytest
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from job_search_storage import JobSearchStorage

class TestSalaryFiltering:
    """Test class for salary filtering functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        # Use a mock DB config since we're only testing parsing functionality
        self.storage = JobSearchStorage({
            'host': 'localhost',
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass',
            'port': 5432
        })
    
    def test_million_suffix_parsing(self):
        """Test parsing of million suffixes"""
        test_cases = [
            ("1m", 1000000),
            ("1M", 1000000),
            ("1.5m", 1500000),
            ("2.5M", 2500000),
            ("10m", 10000000),
            ("0m", 0),
            ("0.1m", 100000),
        ]
        
        for input_str, expected in test_cases:
            result = self.storage.parse_salary_amount(input_str)
            assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"
    
    def test_normalization_functionality(self):
        """Test input normalization (whitespace stripping and plus sign removal)"""
        test_cases = [
            (" 100 ", 100),
            ("100+", 100),
            (" 1k ", 1000),
            ("1k+", 1000),
            (" 1m ", 1000000),
            ("1m+", 1000000),
            (" $100 ", 100),
            ("€1k+", 1000),
            (" £1m ", 1000000),
        ]
        
        for input_str, expected in test_cases:
            result = self.storage.parse_salary_amount(input_str)
            assert result == expected, f"Failed for '{input_str}': got {result}, expected {expected}"
    
    def test_backward_compatibility(self):
        """Test that existing functionality still works"""
        test_cases = [
            ("100", 100),
            ("1k", 1000),
            ("1K", 1000),
            ("10k", 10000),
            ("100k", 100000),
            ("$100", 100),
            ("€1k", 1000),
            ("£100", 100),
            ("1,000", 1000),
            ("10,000", 10000),
        ]
        
        for input_str, expected in test_cases:
            result = self.storage.parse_salary_amount(input_str)
            assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"
    
    def test_salary_range_parsing(self):
        """Test salary range parsing with million suffixes"""
        test_cases = [
            ("1m-2m", (1000000, 2000000)),
            ("500k-1m", (500000, 1000000)),
            ("1.5m-2.5m", (1500000, 2500000)),
            ("1m+", (1000000, None)),
            ("500k+", (500000, None)),
        ]
        
        for input_str, expected in test_cases:
            result = self.storage.parse_salary_range_for_query(input_str)
            assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"
    
    def test_error_handling(self):
        """Test error cases"""
        invalid_cases = [
            None,
            "",
            " ",
            "invalid",
            "1x",  # Unknown suffix
            "abc123",
        ]
        
        for invalid_input in invalid_cases:
            with pytest.raises(ValueError):
                self.storage.parse_salary_amount(invalid_input)
    
    def test_mixed_suffix_ranges(self):
        """Test ranges with mixed suffixes (k and m)"""
        test_cases = [
            ("500k-1m", (500000, 1000000)),
            ("1m-1500k", (1000000, 1500000)),
            ("800k-1.2m", (800000, 1200000)),
        ]
        
        for input_str, expected in test_cases:
            result = self.storage.parse_salary_range_for_query(input_str)
            assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"
    
    def test_currency_with_million_suffix(self):
        """Test currency symbols with million suffixes"""
        test_cases = [
            ("$1m", 1000000),
            ("€1.5m", 1500000),
            ("£2m", 2000000),
            ("$1m+", 1000000),
            ("€1.5m+", 1500000),
        ]
        
        for input_str, expected in test_cases:
            result = self.storage.parse_salary_amount(input_str)
            assert result == expected, f"Failed for {input_str}: got {result}, expected {expected}"

if __name__ == "__main__":
    # Run the tests directly
    test_instance = TestSalaryFiltering()
    test_instance.setup_method()
    
    print("Running salary filtering tests...")
    print("=" * 50)
    
    # Run each test method
    test_methods = [
        test_instance.test_million_suffix_parsing,
        test_instance.test_normalization_functionality,
        test_instance.test_backward_compatibility,
        test_instance.test_salary_range_parsing,
        test_instance.test_error_handling,
        test_instance.test_mixed_suffix_ranges,
        test_instance.test_currency_with_million_suffix,
    ]
    
    all_passed = True
    for method in test_methods:
        try:
            method()
            print(f"✓ {method.__name__}")
        except Exception as e:
            print(f"✗ {method.__name__}: {e}")
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("All tests passed! ✅")
    else:
        print("Some tests failed! ❌")
