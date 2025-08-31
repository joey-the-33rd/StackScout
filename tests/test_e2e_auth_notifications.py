import pytest
import uuid
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from stackscout_web import app

client = TestClient(app)

def test_register_login_logout_flow():
    # Register a new user
    unique_id = str(uuid.uuid4())

    response = client.post("/auth/register", json={
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "TestPass123",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"].startswith("testuser_")
    assert data["email"].endswith("@example.com")

    # Login with the new user
    response = client.post("/auth/login", json={
        "username": f"testuser_{unique_id}",
        "password": "TestPass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Access protected route /auth/me
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"].startswith("testuser_")

def test_notification_endpoints():
    # Register and login a user
    unique_id = str(uuid.uuid4())

    client.post("/auth/register", json={
        "username": f"notifyuser_{unique_id}",
        "email": f"notifyuser_{unique_id}@example.com",
        "password": "NotifyPass123",
        "full_name": "Notify User"
    })
    login_resp = client.post("/auth/login", json={
        "username": f"notifyuser_{unique_id}",
        "password": "NotifyPass123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get notifications (should be empty initially)
    response = client.get("/notifications", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Create a notification (simulate)
    user_data = client.get("/auth/me", headers=headers).json()
    notification_data = {
        "title": "Test Notification",
        "message": "This is a test notification",
        "user_id": user_data["id"]
    }
    response = client.post("/notifications", json=notification_data, headers=headers)
    assert response.status_code == 200 or response.status_code == 201

    # Get notifications again, should include the new one
    response = client.get("/notifications", headers=headers)
    assert response.status_code == 200
    notifications = response.json()
    assert any(n["title"] == "Test Notification" for n in notifications)
