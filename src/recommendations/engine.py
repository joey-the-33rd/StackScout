"""Job recommendation engine for StackScout."""

import logging
from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from src.recommendations.models import JobRecommendation, RecommendationConfig
from src.recommendations.database import RecommendationDatabase
from job_search_storage import DB_CONFIG

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Main recommendation engine for job matching."""
    
    def __init__(self, config: Optional[RecommendationConfig] = None):
        self.config = config or RecommendationConfig()
        self.db = RecommendationDatabase(DB_CONFIG)
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
        self.skill_keywords = self._load_skill_keywords()
    
    def _load_skill_keywords(self) -> List[str]:
        """Load common tech skill keywords for matching."""
        return [
            'python', 'javascript', 'java', 'typescript', 'react', 'angular', 'vue',
            'node', 'express', 'django', 'flask', 'fastapi', 'spring', 'laravel',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'data science', 'deep learning', 'nlp', 'cv',
            'devops', 'ci/cd', 'jenkins', 'git', 'github', 'gitlab', 'agile', 'scrum',
            'frontend', 'backend', 'fullstack', 'mobile', 'ios', 'android', 'flutter',
            'react native', 'web', 'cloud', 'microservices', 'api', 'rest', 'graphql',
            'security', 'cybersecurity', 'blockchain', 'iot', 'ar', 'vr'
        ]
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                found_skills.append(skill)
        
        return found_skills
    
    def _calculate_similarity(self, job_description: str, user_skills: List[str]) -> float:
        """Calculate similarity between job description and user skills."""
        if not job_description or not user_skills:
            return 0.0
        
        # Combine user skills into a single string
        user_skills_text = ' '.join(user_skills)
        
        try:
            # Vectorize both texts
            vectors = self.vectorizer.fit_transform([job_description, user_skills_text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _calculate_match_score(self, job: Dict[str, Any], user_data: Dict[str, Any]) -> float:
        """Calculate overall match score for a job."""
        if not job or not user_data:
            return 0.0
        
        # Extract skills from job description
        job_description = f"{job.get('description', '')} {job.get('requirements', '')}"
        job_skills = self._extract_skills_from_text(job_description)
        
        # Get user skills from interactions and preferences
        user_skills = set()
        
        # Add skills from saved searches
        saved_searches = user_data.get('preferences', {}).get('saved_searches', [])
        for search in saved_searches:
            if isinstance(search, dict):
                keywords = search.get('keywords', [])
                if isinstance(keywords, list):
                    user_skills.update([kw.lower() for kw in keywords if isinstance(kw, str)])
        
        # Add skills from job interactions
        interactions = user_data.get('interactions', [])
        for interaction in interactions:
            # In a real implementation, we'd analyze the jobs the user interacted with
            pass
        
        skill_similarity = self._calculate_similarity(job_description, list(user_skills))
        
        # Calculate location preference (simplified)
        location_score = 0.5  # Default neutral score
        
        # Calculate salary preference (simplified)
        salary_score = 0.5  # Default neutral score
        
        # Calculate company preference based on interactions
        company_score = 0.5  # Default neutral score
        
        # Calculate experience level match (simplified)
        experience_score = 0.5  # Default neutral score
        
        # Weighted average of all scores
        total_score = (
            self.config.skill_weight * skill_similarity +
            self.config.location_weight * location_score +
            self.config.salary_weight * salary_score +
            self.config.company_weight * company_score +
            self.config.experience_weight * experience_score
        )
        
        return total_score
    
    def generate_recommendations(self, user_id: int, limit: int = 10) -> List[JobRecommendation]:
        """Generate job recommendations for a user."""
        try:
            # Get user data
            user_data = self.db.get_user_profile_data(user_id)
            if not user_data:
                logger.warning(f"No user data found for user_id: {user_id}")
                return []
            
            # Get recent jobs
            recent_jobs = self.db.get_recent_jobs(days=30, limit=self.config.max_recommendations)
            if not recent_jobs:
                logger.warning("No recent jobs found for recommendations")
                return []
            
            # Get user's saved jobs
            saved_jobs = self.db.get_user_saved_jobs(user_id)
            
            # Calculate scores for each job
            scored_jobs = []
            for job in recent_jobs:
                match_score = self._calculate_match_score(job, user_data)
                
                if match_score >= self.config.min_match_score:
                    # Generate match reasons
                    match_reasons = self._generate_match_reasons(job, user_data, match_score)
                    
                    scored_jobs.append(JobRecommendation(
                        job_id=job['id'],
                        company=job.get('company', 'Unknown'),
                        role=job.get('role', 'Unknown'),
                        tech_stack=job.get('tech_stack', []),
                        job_type=job.get('job_type', ''),
                        salary=job.get('salary'),
                        location=job.get('location', ''),
                        source_platform=job.get('source_platform', ''),
                        source_url=job.get('source_url', ''),
                        posted_date=job.get('posted_date', ''),
                        match_score=round(match_score, 2),
                        match_reasons=match_reasons,
                        is_saved=job['id'] in saved_jobs
                    ))
            
            # Sort by match score (highest first)
            scored_jobs.sort(key=lambda x: x.match_score, reverse=True)
            
            # Return top recommendations
            return scored_jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _generate_match_reasons(self, job: Dict[str, Any], user_data: Dict[str, Any], score: float) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []
        
        if score >= 0.8:
            reasons.append("Excellent match based on your skills and preferences")
        elif score >= 0.6:
            reasons.append("Strong match with your profile")
        elif score >= 0.4:
            reasons.append("Good potential match")
        else:
            reasons.append("Relevant opportunity based on your search history")
        
        # Add specific reasons based on job features
        job_description = f"{job.get('description', '')} {job.get('requirements', '')}".lower()
        
        # Check for technology matches
        tech_matches = []
        for skill in self.skill_keywords:
            if skill in job_description:
                tech_matches.append(skill)
        
        if tech_matches:
            reasons.append(f"Matches your skills in: {', '.join(tech_matches[:3])}")
        
        # Check if it's from a preferred platform
        saved_searches = user_data.get('preferences', {}).get('saved_searches', [])
        platform = job.get('source_platform', '').lower()
        
        for search in saved_searches:
            if isinstance(search, dict):
                search_platform = search.get('platform', '').lower()
                if search_platform and search_platform in platform:
                    reasons.append(f"From your preferred platform: {platform}")
                    break
        
        return reasons
    
    def record_user_interaction(self, user_id: int, job_id: int, interaction_type: str, duration: Optional[int] = None) -> bool:
        """Record user interaction with a job for future recommendations."""
        return self.db.record_job_interaction(user_id, job_id, interaction_type, duration)
    
    def get_user_recommendation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics about user recommendations and interactions."""
        stats = self.db.get_job_interaction_stats(user_id)
        
        # Add recommendation-specific stats
        stats['total_recommendations_viewed'] = stats.get('view', {}).get('count', 0)
        stats['total_jobs_saved'] = stats.get('save', {}).get('count', 0)
        stats['total_jobs_applied'] = stats.get('apply', {}).get('count', 0)
        
        return stats
    
    def close(self):
        """Close database connection."""
        self.db.close()
