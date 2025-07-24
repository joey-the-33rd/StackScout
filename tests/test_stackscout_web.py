import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from stackscout_web import app

client = TestClient(app)

def test_read_form():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<form" in response.text or "Job Search" in response.text

def test_run_job_search_success(monkeypatch):
    # Mock run_scraper to return sample data
    sample_results = [
        {"Company": "TestCo", "Role": "Developer", "Link": "http://example.com", "Tech Stack": "Python", "Type": "Remote", "Salary": "N/A", "Contact Person": "N/A", "Email": "N/A"}
    ]
    def mock_run_scraper(email, password):
        return sample_results
    monkeypatch.setattr("stackscout_web.run_scraper", mock_run_scraper)
    os.environ["LINKEDIN_EMAIL"] = "test@example.com"
    os.environ["LINKEDIN_PASSWORD"] = "password123"
    response = client.post("/run")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Job search started" in response.text

def test_run_job_search_failure(monkeypatch):
    def mock_run_scraper(email, password):
        raise Exception("Scraper error")
    monkeypatch.setattr("stackscout_web.run_scraper", mock_run_scraper)
    response = client.post("/run")
    assert response.status_code == 200
    # The error message is logged but the template shows "No job results found."
    assert "No job results found" in response.text or "Job search failed" in response.text
