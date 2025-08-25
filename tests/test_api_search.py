import pytest
from fastapi.testclient import TestClient
from stackscout_web import app

client = TestClient(app)

def test_api_search_valid_request():
    response = client.post("/api/search", json={
        "keywords": "python",
        "location": "remote",
        "job_type": "full-time",
        "salary_range": "$50k-$70k"
    })
    assert response.status_code == 200
    assert "results" in response.json()

def test_api_search_missing_keywords():
    response = client.post("/api/search", json={
        "location": "remote",
        "job_type": "full-time",
        "salary_range": "$50k-$70k"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_api_search_empty_request():
    response = client.post("/api/search", json={})
    assert response.status_code == 422  # Unprocessable Entity

def test_api_search_invalid_job_type():
    response = client.post("/api/search", json={
        "keywords": "python",
        "location": "remote",
        "job_type": "invalid_type",
        "salary_range": "$50k-$70k"
    })
    assert response.status_code == 200
    assert "results" in response.json()

# Add more tests as needed for edge cases and other scenarios
