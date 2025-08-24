"""Recommendation models for StackScout."""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class JobRecommendation(BaseModel):
    """Model for job recommendations."""
    job_id: int
    company: str
    role: str
    tech_stack: List[str]
    job_type: str
    salary: Optional[str] = None
    location: str
    source_platform: str
    source_url: str
    posted_date: str
    match_score: float
    match_reasons: List[str]
    is_saved: bool = False

    @validator('posted_date', pre=True)
    def convert_datetime_to_string(cls, v):
        """Convert datetime objects to ISO format strings."""
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v) if v is not None else ""

class RecommendationRequest(BaseModel):
    """Request model for job recommendations."""
    user_id: int
    limit: int = 10
    include_saved: bool = False
    filters: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    """Response model for job recommendations."""
    recommendations: List[JobRecommendation]
    total_count: int
    user_preferences: Optional[Dict[str, Any]] = None

class UserSearchHistory(BaseModel):
    """Model for user search history."""
    search_query: Dict[str, Any]
    search_date: datetime
    job_count: int

class UserJobInteraction(BaseModel):
    """Model for user-job interactions."""
    job_id: int
    user_id: int
    interaction_type: str  # 'view', 'save', 'apply', 'ignore'
    interaction_date: datetime
    duration: Optional[int] = None  # seconds spent viewing

class RecommendationConfig(BaseModel):
    """Configuration for recommendation algorithm."""
    skill_weight: float = 0.4
    experience_weight: float = 0.3
    location_weight: float = 0.1
    salary_weight: float = 0.1
    company_weight: float = 0.1
    min_match_score: float = 0.3
    max_recommendations: int = 50
