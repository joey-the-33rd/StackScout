import sys
import os
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load .env file explicitly for tests
load_dotenv()

# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth.endpoints import router as auth_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(auth_router)

client = TestClient(app)

def test_register_and_login():
    # Test user registration with unique username
    import uuid
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": unique_username,
        "email": f"{unique_username}@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200, f"Registration failed: {response.text}"
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data

    # Test login with correct credentials
    login_data = {
        "username": unique_username,
        "password": "testpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Test login with incorrect password
    login_data_wrong = {
        "username": unique_username,
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data_wrong)
    assert response.status_code == 401

def test_get_me_without_token():
    response = client.get("/auth/me")
    # HTTPBearer returns 403 Forbidden when no credentials are provided
    assert response.status_code == 403

def test_get_me_with_token():
    # Register and login to get token
    import uuid
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": unique_username,
        "email": f"{unique_username}@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200, f"Registration failed: {response.text}"
    
    login_data = {
        "username": unique_username,
        "password": "testpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json().get("access_token")
    assert token is not None, "No access token received"

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200, f"Get me failed: {response.text}"
    data = response.json()
    assert data["username"] == unique_username
