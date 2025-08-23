"""Authentication models for StackScout."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Model for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password must be at least 6 characters")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name (optional)")

class UserLogin(BaseModel):
    """Model for user login."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")

class UserResponse(BaseModel):
    """Model for user response."""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes

class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None
    user_id: Optional[int] = None

class UserPreferences(BaseModel):
    """User preferences model."""
    notification_enabled: bool = True
    email_notifications: bool = True
    saved_searches: list = []

class UserUpdate(BaseModel):
    """Model for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
