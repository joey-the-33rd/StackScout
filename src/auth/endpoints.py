"""FastAPI endpoints for authentication."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from src.auth.models import UserCreate, UserLogin, UserResponse
from src.auth.security import create_access_token, get_password_hash, verify_password
from src.auth.database import AuthDatabase
from src.auth.dependencies import get_auth_db, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AuthDatabase = Depends(get_auth_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    password_hash = get_password_hash(user.password)
    user_id = db.create_user(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        full_name=user.full_name
    )
    
    if user_id is None:
        raise HTTPException(status_code=400, detail="Failed to create user")
    
    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": datetime.utcnow(),
        "is_active": True
    }

@router.post("/login")
async def login(user: UserLogin, db: AuthDatabase = Depends(get_auth_db)):
    """Login user and return JWT token."""
    user_data = db.get_user_by_username(user.username)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user.password, user_data["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user_data["username"], "user_id": user_data["id"]})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 1800,
        "user": user_data
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.put("/me")
async def update_user(user: dict, current_user: dict = Depends(get_current_user)):
    """Update current user information."""
    return current_user
