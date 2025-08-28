import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from stackscout_web import app

client = TestClient(app)

def test_form_data_extraction_basic():
    """Test basic form data extraction with valid inputs"""
    # Mock the scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    
    with patch('stackscout_web.run_scraper_async', return_value=sample_results) as mock_scraper:
        response = client.post("/run", data={
            "keywords": "python developer",
            "location": "remote",
            "job_type": "full-time"
        })
        assert response.status_code == 200
        # Verify that the scraper was called with the correct keywords
        mock_scraper.assert_called_once_with("python developer")

def test_form_data_extraction_default_keywords():
    """Test that default keywords are used when not provided"""
    # Mock the scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    
    with patch('stackscout_web.run_scraper_async', return_value=sample_results) as mock_scraper:
        response = client.post("/run", data={
            "location": "remote",
            "job_type": "full-time"
        })
        assert response.status_code == 200
        # Verify that the scraper was called with the default keywords
        mock_scraper.assert_called_once_with("python")

def test_form_data_extraction_empty_keywords():
    """Test that default keywords are used when empty keywords provided"""
    # Mock the scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    
    with patch('stackscout_web.run_scraper_async', return_value=sample_results) as mock_scraper:
        response = client.post("/run", data={
            "keywords": "",
            "location": "remote",
            "job_type": "full-time"
        })
        assert response.status_code == 200
        # Verify that the scraper was called with the default keywords
        mock_scraper.assert_called_once_with("python")

def test_form_data_extraction_special_characters():
    """Test with special characters in keywords"""
    # Mock the scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    
    with patch('stackscout_web.run_scraper_async', return_value=sample_results) as mock_scraper:
        response = client.post("/run", data={
            "keywords": "python & java",
            "location": "New York, NY",
            "job_type": "full-time"
        })
        assert response.status_code == 200
        # Verify that the scraper was called with the correct keywords
        mock_scraper.assert_called_once_with("python & java")

def test_form_data_extraction_long_strings():
    """Test with very long input strings"""
    # Mock the scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    
    long_string = "a" * 1000
    with patch('stackscout_web.run_scraper_async', return_value=sample_results) as mock_scraper:
        response = client.post("/run", data={
            "keywords": long_string,
            "location": long_string,
            "job_type": "remote"
        })
        assert response.status_code == 200
        # Verify that the scraper was called with the correct keywords
        mock_scraper.assert_called_once_with(long_string)

def test_form_data_extraction_numeric_values():
    """Test with numeric values in text fields"""
    # Mock the scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    
    with patch('stackscout_web.run_scraper_async', return_value=sample_results) as mock_scraper:
        response = client.post("/run", data={
            "keywords": "123",
            "location": "123",
            "job_type": "full-time"
        })
        assert response.status_code == 200
        # Verify that the scraper was called with the correct keywords
        mock_scraper.assert_called_once_with("123")

def test_form_data_extraction_partial_fields():
    """Test with only some fields provided"""
    # Mock the scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    
    with patch('stackscout_web.run_scraper_async', return_value=sample_results) as mock_scraper:
        response = client.post("/run", data={
            "keywords": "python"
            # location and job_type are omitted
        })
        assert response.status_code == 200
        # Verify that the scraper was called with the correct keywords
        mock_scraper.assert_called_once_with("python")

def test_form_data_extraction_no_data():
    """Test with no form data provided"""
    # Mock the scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    
    with patch('stackscout_web.run_scraper_async', return_value=sample_results) as mock_scraper:
        response = client.post("/run", data={})
        assert response.status_code == 200
        # Verify that the scraper was called with the default keywords
        mock_scraper.assert_called_once_with("python")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
