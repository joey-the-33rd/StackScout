#!/usr/bin/env python3
"""Test script for recommendation system."""

import requests
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_recommendation_health():
    """Test recommendation system health check."""
    print("Testing recommendation health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/recommendations/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_recommendations(user_id=1, token=None):
    """Test getting job recommendations."""
    print(f"\nTesting job recommendations for user {user_id}...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    data = {
        "user_id": user_id,
        "limit": 5,
        "include_saved": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/recommendations/jobs",
            json=data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Total recommendations: {result['total_count']}")
            print("Recommendations:")
            for rec in result['recommendations']:
                print(f"  - {rec['company']}: {rec['role']} (Score: {rec['match_score']})")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_record_interaction(user_id=1, job_id=1, token=None):
    """Test recording job interaction."""
    print(f"\nTesting job interaction recording...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    params = {
        "job_id": job_id,
        "interaction_type": "view",
        "duration": 30
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/recommendations/interaction",
            params=params,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_stats(user_id=1, token=None):
    """Test getting recommendation statistics."""
    print(f"\nTesting recommendation statistics...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(
            f"{BASE_URL}/recommendations/stats",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Stats: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_config():
    """Test getting recommendation configuration."""
    print(f"\nTesting recommendation configuration...")
    
    try:
        response = requests.get(f"{BASE_URL}/recommendations/config")
        print(f"Status: {response.status_code}")
        print(f"Config: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_auth_token() -> tuple:
    """Get authentication token for testing."""
    print("\nGetting authentication token...")
    
    # First try to register a test user
    register_data = {
        "username": "testuser_recommend",
        "email": "test_recommend@example.com",
        "password": "testpassword123",
        "full_name": "Test Recommendation User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("Registered test user successfully")
        elif response.status_code == 400 and "already exists" in response.text:
            print("Test user already exists")
        else:
            print(f"Registration failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Registration error: {e}")
        return None, None
    
    # Login to get token
    login_data = {
        "username": "testuser_recommend",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            user_id = response.json()["user"]["id"]
            print(f"Login successful - User ID: {user_id}")
            return token, user_id
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"Login error: {e}")
        return None, None

if __name__ == "__main__":
    print("Recommendation System Test")
    print("=" * 50)
    
    # Start the server first with: python stackscout_web.py
    
    # Get authentication token
    token, user_id = get_auth_token()
    
    # Run tests
    tests = []
    
    # Always run these tests (no auth required)
    tests.append(("Health Check", lambda: test_recommendation_health()))
    tests.append(("Get Config", lambda: test_get_config()))
    
    # Only run auth-required tests if we have a token
    if token and user_id:
        tests.append(("Get Recommendations", lambda: test_get_recommendations(user_id, token)))
        tests.append(("Record Interaction", lambda: test_record_interaction(user_id, 1, token)))
        tests.append(("Get Stats", lambda: test_get_stats(user_id, token)))
    else:
        print("\nSkipping auth-required tests (no valid token)")
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        result = test_func()
        results.append((test_name, result))
        print(f"Result: {'PASS' if result else 'FAIL'}")
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for test_name, result in results:
        print(f"{test_name}: {'PASS' if result else 'FAIL'}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
