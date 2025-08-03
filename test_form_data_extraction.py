import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from stackscout_web import app

client = TestClient(app)

def test_form_data_extraction_basic():
    """Test basic form data extraction with valid inputs"""
    response = client.post("/run", data={
        "keywords": "python developer",
        "location": "remote",
        "job_type": "full-time"
    })
    assert response.status_code == 200

def test_form_data_extraction_default_keywords():
    """Test that default keywords are used when not provided"""
    response = client.post("/run", data={
        "location": "remote",
        "job_type": "full-time"
    })
    assert response.status_code == 200

def test_form_data_extraction_empty_fields():
    """Test with empty form fields"""
    response = client.post("/run", data={
        "keywords": "",
        "location": "",
        "job_type": ""
    })
    assert response.status_code == 200

def test_form_data_extraction_special_characters():
    """Test with special characters in keywords"""
    response = client.post("/run", data={
        "keywords": "python & java",
        "location": "New York, NY",
        "job_type": "full-time"
    })
    assert response.status_code == 200

def test_form_data_extraction_long_strings():
    """Test with very long input strings"""
    long_string = "a" * 1000
    response = client.post("/run", data={
        "keywords": long_string,
        "location": long_string,
        "job_type": "remote"
    })
    assert response.status_code == 200

def test_form_data_extraction_numeric_values():
    """Test with numeric values in text fields"""
    response = client.post("/run", data={
        "keywords": "123",
        "location": "123",
        "job_type": "full-time"
    })
    assert response.status_code == 200

def test_form_data_extraction_partial_fields():
    """Test with only some fields provided"""
    response = client.post("/run", data={
        "keywords": "python"
        # location and job_type are omitted
    })
    assert response.status_code == 200

def test_form_data_extraction_no_data():
    """Test with no form data provided"""
    response = client.post("/run", data={})
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
