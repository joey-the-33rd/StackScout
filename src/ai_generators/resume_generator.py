"""Resume generator for creating professional resumes."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from .base_generator import BaseAIGenerator

class ResumeSection(BaseModel):
    """Represents a section in a resume."""
    title: str
    content: str
    order: int

class ResumeGenerator(BaseAIGenerator):
    """AI-powered resume generator."""
    
    def __init__(self):
        super().__init__()
    
    def generate_resume(self, user_profile: Dict[str, Any], template: str = "ats_friendly") -> Dict[str, Any]:
        """Generate a complete resume based on user profile."""
        sections = {
            "summary": self._generate_summary(user_profile),
            "experience": self._generate_experience(user_profile),
            "education": self._generate_education(user_profile),
            "skills": self._generate_skills(user_profile),
            "projects": self._generate_projects(user_profile)
        }
        
        return {
            "template": template,
            "sections": sections,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "template_type": template
            }
        }
    
    def _generate_summary(self, profile: Dict[str, Any]) -> str:
        """Generate professional summary."""
        prompt = f"""
        Create a compelling 2-3 sentence professional summary for a {profile.get('title', 'professional')} 
        with {profile.get('years_experience', 0)} years of experience in {profile.get('industry', 'technology')}.
        
        Skills: {', '.join(profile.get('skills', [])[:5])}
        Key achievements: {profile.get('achievements', 'various successful projects')}
        """
        return self.generate_content(prompt, profile, max_tokens=150)
    
    def _generate_experience(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate work experience section."""
        experiences = []
        for job in profile.get('experience', []):
            prompt = f"""
            Create a concise bullet-point description for this role:
            Position: {job.get('title')}
            Company: {job.get('company')}
            Duration: {job.get('duration')}
            Responsibilities: {job.get('responsibilities', '')}
            Achievements: {job.get('achievements', '')}
            """
            description = self.generate_content(prompt, job, max_tokens=200)
            experiences.append({
                "title": job.get('title'),
                "company": job.get('company'),
                "duration": job.get('duration'),
                "description": description
            })
        return experiences
    
    def _generate_education(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate education section."""
        education = []
        for edu in profile.get('education', []):
            education.append({
                "degree": edu.get('degree'),
                "institution": edu.get('institution'),
                "year": edu.get('year'),
                "description": edu.get('description', '')
            })
        return education
    
    def _generate_skills(self, profile: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate skills section organized by category."""
        skills = profile.get('skills', [])
        categories = {
            "Technical": [s for s in skills if any(keyword in s.lower() for keyword in ['python', 'javascript', 'java', 'react', 'node'])],
            "Soft Skills": [s for s in skills if any(keyword in s.lower() for keyword in ['leadership', 'communication', 'teamwork'])],
            "Tools": [s for s in skills if any(keyword in s.lower() for keyword in ['git', 'docker', 'aws', 'azure'])]
        }
        return categories
    
    def _generate_projects(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate projects section."""
        projects = []
        for project in profile.get('projects', []):
            prompt = f"""
            Create a concise project description highlighting impact and technologies used:
            Project: {project.get('name')}
            Technologies: {', '.join(project.get('technologies', []))}
            Description: {project.get('description', '')}
            Impact: {project.get('impact', '')}
            """
            description = self.generate_content(prompt, project, max_tokens=150)
            projects.append({
                "name": project.get('name'),
                "technologies": project.get('technologies', []),
                "description": description,
                "url": project.get('url', '')
            })
        return projects
    
    def tailor_resume_for_job(self, resume: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Tailor existing resume for specific job posting."""
        prompt = f"""
        Tailor this resume for the following job posting. Focus on relevant skills and experience:
        
        Job Description: {job_description}
        
        Current Resume: {str(resume)}
        
        Return a JSON object with the tailored resume sections.
        """
        
        tailored_content = self.generate_content(prompt, {"resume": resume, "job": job_description}, max_tokens=2000)
        
        # Parse the response and return structured data
        return {
            "original_resume": resume,
            "tailored_resume": self._parse_tailored_response(tailored_content),
            "job_description": job_description
        }
    
    def _parse_tailored_response(self, content: str) -> Dict[str, Any]:
        """Parse the AI response into structured resume data."""
        # This would be implemented to parse the AI response
        # For now, return a placeholder
        return {"sections": {"summary": content, "experience": [], "skills": []}}
