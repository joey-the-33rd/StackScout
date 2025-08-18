"""Cover letter generator for creating job-specific cover letters."""
from typing import Dict, Any, Optional
from datetime import datetime
from .base_generator import BaseAIGenerator

class CoverLetterGenerator(BaseAIGenerator):
    """AI-powered cover letter generator."""
    
    def __init__(self):
        super().__init__()
    
    def generate_cover_letter(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a tailored cover letter for a specific job."""
        
        # Extract key information
        job_title = job_details.get('title', '')
        company_name = company_info.get('name', '')
        job_description = job_details.get('description', '')
        
        # Create personalized prompt
        prompt = self._create_cover_letter_prompt(user_profile, job_details, company_info)
        
        # Generate the cover letter
        content = self.generate_content(prompt, {
            "user": user_profile,
            "job": job_details,
            "company": company_info
        }, max_tokens=800)
        
        return {
            "cover_letter": content,
            "job_title": job_title,
            "company_name": company_name,
            "generated_at": datetime.now().isoformat()
        }
    
    def _create_cover_letter_prompt(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], company_info: Dict[str, Any]) -> str:
        """Create a personalized prompt for cover letter generation."""
        
        job_title = job_details.get('title', '')
        company_name = company_info.get('name', '')
        job_description = job_details.get('description', '')
        
        user_name = user_profile.get('full_name', 'Applicant')
        user_title = user_profile.get('title', 'Professional')
        user_experience = user_profile.get('years_experience', 0)
        user_skills = ', '.join(user_profile.get('skills', [])[:5])
        user_achievements = user_profile.get('achievements', 'various successful projects')
        
        return f"""
        Write a compelling cover letter for {user_name} applying for the {job_title} position at {company_name}.
        
        Applicant Profile:
        - Current Role: {user_title}
        - Years of Experience: {user_experience}
        - Key Skills: {user_skills}
        - Notable Achievements: {user_achievements}
        
        Job Description:
        {job_description}
        
        Company Information:
        {company_info.get('description', '')}
        
        Guidelines:
        1. Address the letter to the hiring manager
        2. Show enthusiasm for the role and company
        3. Highlight relevant skills and experience
        4. Connect past achievements to job requirements
        5. Keep it concise (3-4 paragraphs)
        6. End with a call to action
        
        Write in a professional, confident tone.
        """
    
    def tailor_cover_letter(self, base_letter: str, job_details: Dict[str, Any]) -> str:
        """Tailor existing cover letter for specific job."""
        prompt = f"""
        Tailor this cover letter for the following job posting:
        
        Job: {job_details.get('title', '')}
        Description: {job_details.get('description', '')}
        
        Original Letter: {base_letter}
        
        Focus on:
        1. Matching keywords from job description
        2. Highlighting relevant experience
        3. Addressing specific requirements
        4. Maintaining professional tone
        
        Return the tailored cover letter.
        """
        
        return self.generate_content(prompt, {"letter": base_letter, "job": job_details}, max_tokens=600)
    
    def generate_follow_up_email(self, user_profile: Dict[str, Any], job_details: Dict[str, Any], email_type: str = "thank_you") -> str:
        """Generate follow-up email for job applications."""
        
        prompt = f"""
        Generate a {email_type} follow-up email for {user_profile.get('full_name', 'Applicant')} 
        regarding the {job_details.get('title', '')} position at {job_details.get('company', '')}.
        
        User Profile: {str(user_profile)}
        Job Details: {str(job_details)}
        
        Email Type: {email_type}
        
        Guidelines:
        - Keep it brief and professional
        - Express continued interest
        - Include relevant follow-up information
        - End with clear next steps
        """
        
        return self.generate_content(prompt, {
            "user": user_profile,
            "job": job_details,
            "type": email_type
        }, max_tokens=300)
