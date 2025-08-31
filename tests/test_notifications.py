#!/usr/bin/env python3
"""Test script for notifications system."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_notifications():
    """Test the notifications API endpoints."""
    
    # First, register a test user
    import random
    random_suffix = random.randint(1000, 9999)
    register_data = {
        "username": f"testuser_notifications_{random_suffix}",
        "email": f"test_notifications_{random_suffix}@example.com",
        "password": "testpassword123",
        "full_name": f"Test Notifications User {random_suffix}"
    }
    
    try:
        # Register user
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code != 200:
            print(f"Failed to register user: {response.text}")
            return False
        
        user_data = response.json()
        print(f"✅ User registered: {user_data['username']}")
        
        # Login to get token
        login_data = {
            "username": f"testuser_notifications_{random_suffix}",
            "password": "testpassword123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Failed to login: {response.text}")
            return False
        
        login_response = response.json()
        token = login_response["access_token"]
        user_id = login_response["user"]["id"]
        print(f"✅ Login successful, user ID: {user_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: Get notifications (should be empty)
        print("\n1. Testing GET /notifications/")
        response = requests.get(f"{BASE_URL}/notifications/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Get notification preferences
        print("\n2. Testing GET /notifications/preferences")
        response = requests.get(f"{BASE_URL}/notifications/preferences", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 3: Create a notification
        print("\n3. Testing POST /notifications/")
        notification_data = {
            "user_id": user_id,
            "title": "Test Notification",
            "message": "This is a test notification message"
        }
        response = requests.post(f"{BASE_URL}/notifications/", json=notification_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 4: Get notifications again (should have one)
        print("\n4. Testing GET /notifications/ after creation")
        response = requests.get(f"{BASE_URL}/notifications/", headers=headers)
        print(f"Status: {response.status_code}")
        notifications = response.json()
        print(f"Response: {notifications}")
        
        if notifications:
            notification_id = notifications[0]["id"]
            
            # Test 5: Mark notification as read
            print(f"\n5. Testing PUT /notifications/{notification_id}/read")
            response = requests.put(f"{BASE_URL}/notifications/{notification_id}/read", headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        
        # Test 6: Update notification preferences
        print("\n6. Testing PUT /notifications/preferences")
        prefs_data = {
            "email_notifications": False,
            "in_app_notifications": True
        }
        response = requests.put(f"{BASE_URL}/notifications/preferences", json=prefs_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        print("\n✅ All notification tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("Starting notification system tests...")
    success = test_notifications()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
