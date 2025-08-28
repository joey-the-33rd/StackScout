#!/usr/bin/env python3
"""Test script for authentication system."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration."""
    print("Testing user registration...")
    
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login():
    """Test user login."""
    print("\nTesting user login...")
    
    data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_me_endpoint(token):
    """Test getting current user info."""
    print("\nTesting /auth/me endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Authentication System Test")
    print("=" * 50)
    
    # Start the server first with: python stackscout_web.py
    
    # Test registration
    user = test_registration()
    
    # Test login
    login_response = test_login()
    
    if login_response and "access_token" in login_response:
        token = login_response["access_token"]
        test_me_endpoint(token)
    
    print("\n" + "=" * 50)
    print("Test completed!")
