"""FastAPI endpoints for job recommendations."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging

from src.recommendations.models import (
    JobRecommendation, 
    RecommendationRequest, 
    RecommendationResponse,
    RecommendationConfig
)
from src.recommendations.engine import RecommendationEngine
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
logger = logging.getLogger(__name__)

# Global recommendation engine instance
_recommendation_engine = None

def get_recommendation_engine() -> RecommendationEngine:
    """Get or create recommendation engine instance."""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine

@router.post("/jobs", response_model=RecommendationResponse)
async def get_job_recommendations(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user),
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Get personalized job recommendations for the current user."""
    try:
        # Verify the requesting user matches the authenticated user
        if current_user["id"] != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access recommendations for other users"
            )
        
        recommendations = engine.generate_recommendations(
            user_id=request.user_id,
            limit=request.limit
        )
        
        # Get user preferences for response
        user_prefs = {}
        try:
            from src.recommendations.database import RecommendationDatabase
            from job_search_storage import DB_CONFIG
            db = RecommendationDatabase(DB_CONFIG)
            user_data = db.get_user_profile_data(request.user_id)
            if user_data:
                user_prefs = user_data.get('preferences', {})
            db.close()
        except Exception as e:
            logger.warning(f"Could not fetch user preferences: {e}")
        
        return RecommendationResponse(
            recommendations=recommendations,
            total_count=len(recommendations),
            user_preferences=user_prefs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )

@router.post("/interaction", status_code=status.HTTP_200_OK)
async def record_job_interaction(
    job_id: int,
    interaction_type: str,
    duration: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Record user interaction with a job for recommendation improvement."""
    try:
        valid_interactions = ['view', 'save', 'apply', 'ignore']
        if interaction_type not in valid_interactions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interaction type. Must be one of: {valid_interactions}"
            )
        
        success = engine.record_user_interaction(
            user_id=current_user["id"],
            job_id=job_id,
            interaction_type=interaction_type,
            duration=duration
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record interaction"
            )
        
        return {"success": True, "message": "Interaction recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording job interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record interaction"
        )

@router.get("/stats")
async def get_recommendation_stats(
    current_user: dict = Depends(get_current_user),
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Get statistics about user recommendations and interactions."""
    try:
        stats = engine.get_user_recommendation_stats(current_user["id"])
        return stats
        
    except Exception as e:
        logger.error(f"Error getting recommendation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendation statistics"
        )

@router.get("/config", response_model=RecommendationConfig)
async def get_recommendation_config(
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Get the current recommendation algorithm configuration."""
    return engine.config

@router.put("/config", response_model=RecommendationConfig)
async def update_recommendation_config(
    config: RecommendationConfig,
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Update the recommendation algorithm configuration."""
    # In a real implementation, you might want to add authentication/authorization
    # for this endpoint since it affects the recommendation algorithm
    
    engine.config = config
    return engine.config

@router.get("/health")
async def health_check(
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    """Health check for the recommendation service."""
    try:
        # Simple check to see if the engine can connect to database
        test_user_id = 1  # Assuming user 1 exists for testing
        recommendations = engine.generate_recommendations(test_user_id, limit=1)
        
        return {
            "status": "healthy",
            "database_connected": True,
            "recommendations_available": len(recommendations) > 0
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database_connected": False,
            "error": str(e)
        }
