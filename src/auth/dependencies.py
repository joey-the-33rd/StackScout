"""FastAPI dependencies for authentication."""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Generator
from src.auth.security import verify_token
from src.auth.database import AuthDatabase
from job_search_storage import DB_CONFIG

logger = logging.getLogger(__name__)

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

def get_auth_db() -> Generator[AuthDatabase, None, None]:
    """Get authentication database instance."""
    db = AuthDatabase(DB_CONFIG)
    db.connect()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AuthDatabase = Depends(get_auth_db)
) -> dict:
    """Get current authenticated user."""
    token = credentials.credentials
    try:
        payload = verify_token(token)
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get_user_by_id(payload["user_id"])
    if user is None:
        logger.error(f"User not found for user_id: {payload['user_id']}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user["is_active"]:
        logger.error(f"Inactive user: {payload['user_id']}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    logger.info(f"Authenticated user: {user['username']} (ID: {user['id']})")
    return user

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current active user."""
    return current_user

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AuthDatabase = Depends(get_auth_db)
) -> Optional[dict]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None
    try:
        payload = verify_token(credentials.credentials)
        user = db.get_user_by_id(payload["user_id"])
        if user and user["is_active"]:
            return user
    except Exception:
        return None
    return None
