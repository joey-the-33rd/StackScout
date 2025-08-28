import unittest
from job_search_storage import JobSearchStorage

class TestSalaryFilterValidationNoDB(unittest.TestCase):
    def setUp(self):
        # Create a minimal storage instance without database connection
        self.storage = JobSearchStorage.__new__(JobSearchStorage)
        
        # Mock the parse_salary_amount method
        def parse_salary_amount(amount_str):
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
        
        self.storage.parse_salary_amount = parse_salary_amount

    def test_empty_salary_filter(self):
        with self.assertRaises(ValueError) as context:
            self.storage.parse_salary_range_for_query("")
        self.assertEqual(str(context.exception), "Empty salary filter")

    def test_missing_minimum_amount(self):
        with self.assertRaises(ValueError) as context:
            self.storage.parse_salary_range_for_query("+")
        self.assertEqual(str(context.exception), "Missing minimum amount before '+'")

    def test_incomplete_salary_range(self):
        with self.assertRaises(ValueError) as context:
            self.storage.parse_salary_range_for_query("100k-")
        self.assertEqual(str(context.exception), "Incomplete salary range")

    def test_valid_salary_range(self):
        min_val, max_val = self.storage.parse_salary_range_for_query("100k-200k")
        self.assertEqual(min_val, 100000)
        self.assertEqual(max_val, 200000)

    def test_valid_exact_salary(self):
        min_val, max_val = self.storage.parse_salary_range_for_query("100k")
        self.assertEqual(min_val, 100000)
        self.assertEqual(max_val, 100000)

if __name__ == '__main__':
    unittest.main()
