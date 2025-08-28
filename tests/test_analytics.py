"""Tests for the analytics API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stackscout_web import app
from src.analytics.engine import get_all_analytics

client = TestClient(app)

def test_analytics_endpoint_success():
    """Test successful retrieval of analytics data."""
    # Mock the get_all_analytics function to return sample data
    sample_data = {
        "overall": {
            "jobs": {"total": 100, "active": 80, "this_week": 20, "growth_rate": 5.0, "by_platform": {"RemoteOK": 60, "JobGether": 40}},
            "users": {"total": 50, "new_this_week": 5, "active_this_week": 30},
            "interactions": {"total": 200}
        },
        "user_interactions": {
            "interaction_types": {"view": 150, "save": 30, "apply": 20},
            "daily_trend": [{"date": "2023-01-01", "count": 10}, {"date": "2023-01-02", "count": 15}],
            "top_users": [{"username": "user1", "interaction_count": 50}, {"username": "user2", "interaction_count": 40}],
            "average_per_user": 4.0
        },
        "search_patterns": {
            "top_keywords": [{"keywords": "python", "search_count": 30}, {"keywords": "javascript", "search_count": 25}],
            "day_of_week": [{"day": "Monday", "search_count": 20}, {"day": "Tuesday", "search_count": 15}],
            "search_trend": [{"date": "2023-01-01", "search_count": 10}, {"date": "2023-01-02", "search_count": 15}],
            "job_type_preferences": [{"job_type": "Full-time", "search_count": 40}, {"job_type": "Remote", "search_count": 35}]
        },
        "recommendations": {
            "effectiveness": [
                {"interaction_type": "view", "count": 100, "avg_match_score": 0.85},
                {"interaction_type": "save", "count": 20, "avg_match_score": 0.90}
            ],
            "top_recommended": [
                {"company": "TechCorp", "role": "Senior Python Developer", "interaction_count": 15, "avg_match_score": 0.92},
                {"company": "StartupXYZ", "role": "Frontend Engineer", "interaction_count": 12, "avg_match_score": 0.88}
            ],
            "score_distribution": [
                {"score_range": "90-100%", "count": 20},
                {"score_range": "80-89%", "count": 30}
            ]
        }
    }
    
    with patch('src.analytics.engine.get_all_analytics', return_value=sample_data):
        response = client.get("/api/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "overall" in data
        assert "user_interactions" in data
        assert "search_patterns" in data
        assert "recommendations" in data

def test_analytics_endpoint_failure():
    """Test handling of analytics data retrieval failure."""
    # Mock the get_all_analytics function to raise an exception
    with patch('src.analytics.engine.get_all_analytics', side_effect=Exception("Database error")):
        response = client.get("/api/analytics")
        assert response.status_code == 500
        data = response.json()
        assert "error" in data

def test_analytics_dashboard_page():
    """Test that the analytics dashboard page loads."""
    response = client.get("/analytics")
    # This will fail because we don't have authentication in the test client
    # but we can at least check that the endpoint exists
    assert response.status_code in [200, 401]  # 200 if no auth required, 401 if auth required

if __name__ == "__main__":
    pytest.main([__file__])
