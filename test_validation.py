import unittest
from job_search_storage import JobSearchStorage

class TestSalaryFilterValidation(unittest.TestCase):
    def setUp(self):
        db_config = {
            'host': 'localhost',
            'database': 'job_scraper_db',
            'user': 'joeythe33rd',
            'password': '',  # Add your password if needed
            'port': 5432
        }
        self.storage = JobSearchStorage(db_config)

    def test_empty_salary_filter(self):
        with self.assertRaises(ValueError) as context:
            self.storage.parse_salary_range_for_query("")
        self.assertEqual(str(context.exception), "Empty salary filter")

    def test_missing_minimum_amount(self):
        with self.assertRaises(ValueError) as context:
            self.storage.parse_salary_range_for_query("100k+")
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
