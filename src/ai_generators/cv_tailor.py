"""CV tailor for optimizing resumes for specific job postings."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_generator import BaseAIGenerator

class CVTailor(BaseAIGenerator):
    """AI-powered CV tailoring service."""
    
    def __init__(self):
        super().__init__()
    
    def tailor_cv(self, base_resume: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Tailor a CV for a specific job posting."""
        
        # Analyze job description
        job_keywords = self._extract_keywords(job_description)
        job_requirements = self._extract_requirements(job_description)
        
        # Tailor each section
        tailored_resume = {
            "summary": self._tailor_summary(base_resume.get("summary", ""), job_keywords, job_requirements),
            "experience": self._tailor_experience(base_resume.get("experience", []), job_keywords),
            "skills": self._tailor_skills(base_resume.get("skills", {}), job_keywords),
            "projects": self._tailor_projects(base_resume.get("projects", []), job_keywords),
            "keywords_matched": job_keywords,
            "tailoring_score": self._calculate_tailoring_score(base_resume, job_keywords)
        }
        
        return {
            "original_resume": base_resume,
            "tailored_resume": tailored_resume,
            "job_keywords": job_keywords,
            "generated_at": datetime.now().isoformat()
        }
    
    def _extract_keywords(self, job_description: str) -> List[str]:
        """Extract relevant keywords from job description."""
        prompt = f"""
        Extract the top 15 most important keywords from this job description.
        Focus on:
        - Technical skills
        - Soft skills
        - Industry terms
        - Tools and technologies
        - Required qualifications
        
        Job Description: {job_description}
        
        Return as a comma-separated list of keywords.
        """
        
        keywords_str = self.generate_content(prompt, {"description": job_description}, max_tokens=200)
        return [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
    
    def _extract_requirements(self, job_description: str) -> List[str]:
        """Extract key requirements from job description."""
        prompt = f"""
        Extract the main requirements from this job description.
        Focus on:
        - Years of experience
        - Specific skills
        - Education requirements
        - Certifications
        - Soft skills
        
        Job Description: {job_description}
        
        Return as a bulleted list.
        """
        
        requirements = self.generate_content(prompt, {"description": job_description}, max_tokens=300)
        return [req.strip() for req in requirements.split('\n') if req.strip()]
    
    def _tailor_summary(self, summary: str, keywords: List[str], requirements: List[str]) -> str:
        """Tailor the summary section with job-specific keywords."""
        prompt = f"""
        Rewrite this professional summary to include these keywords and address these requirements:
        
        Original Summary: {summary}
        Keywords to include: {', '.join(keywords[:8])}
        Requirements to address: {', '.join(requirements[:3])}
        
        Keep it concise (2-3 sentences) and natural.
        """
        
        return self.generate_content(prompt, {"summary": summary, "keywords": keywords}, max_tokens=150)
    
    def _tailor_experience(self, experience: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """Tailor experience descriptions with job-specific keywords."""
        tailored_experience = []
        
        for job in experience:
            prompt = f"""
            Rewrite this job description to emphasize these keywords:
            
            Job: {job.get('title')} at {job.get('company')}
            Original Description: {job.get('description', '')}
            Keywords to emphasize: {', '.join(keywords[:5])}
            
            Keep it concise and impactful.
            """
            
            tailored_description = self.generate_content(prompt, {"job": job, "keywords": keywords}, max_tokens=200)
            
            tailored_experience.append({
                **job,
                "description": tailored_description,
                "keywords_used": [kw for kw in keywords if kw.lower() in tailored_description.lower()]
            })
        
        return tailored_experience
    
    def _tailor_skills(self, skills: Dict[str, List[str]], keywords: List[str]) -> Dict[str, List[str]]:
        """Prioritize skills based on job keywords."""
        all_skills = []
        for category, skill_list in skills.items():
            all_skills.extend(skill_list)
        
        # Prioritize skills that match keywords
        prioritized_skills = []
        for keyword in keywords:
            for skill in all_skills:
                if keyword.lower() in skill.lower() or skill.lower() in keyword.lower():
                    prioritized_skills.append(skill)
        
        # Add remaining skills
        remaining_skills = [s for s in all_skills if s not in prioritized_skills]
        prioritized_skills.extend(remaining_skills[:10])  # Limit total skills
        
        return {
            "Prioritized": prioritized_skills[:5],
            "Technical": [s for s in prioritized_skills if s in skills.get("Technical", [])],
            "Soft Skills": [s for s in prioritized_skills if s in skills.get("Soft Skills", [])]
        }
    
    def _tailor_projects(self, projects: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """Tailor project descriptions with job-specific keywords."""
        tailored_projects = []
        
        for project in projects:
            prompt = f"""
            Rewrite this project description to emphasize these keywords:
            
            Project: {project.get('name')}
            Technologies: {', '.join(project.get('technologies', []))}
            Original Description: {project.get('description', '')}
            Keywords to emphasize: {', '.join(keywords[:5])}
            
            Focus on impact and relevance to the job.
            """
            
            tailored_description = self.generate_content(prompt, {"project": project, "keywords": keywords}, max_tokens=150)
            
            tailored_projects.append({
                **project,
                "description": tailored_description,
                "relevance_score": len([kw for kw in keywords if kw.lower() in tailored_description.lower()])
            })
        
        return sorted(tailored_projects, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    def _calculate_tailoring_score(self, resume: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
        """Calculate how well the resume matches the job keywords."""
        resume_text = str(resume).lower()
        matched_keywords = [kw for kw in keywords if kw.lower() in resume_text]
        
        return {
            "total_keywords": len(keywords),
            "matched_keywords": len(matched_keywords),
            "match_percentage": round((len(matched_keywords) / len(keywords)) * 100, 2),
            "missing_keywords": [kw for kw in keywords if kw.lower() not in resume_text]
        }
    
    def generate_keyword_suggestions(self, resume: Dict[str, Any], job_description: str) -> List[str]:
        """Suggest keywords to add to the resume."""
        prompt = f"""
        Based on this job description, suggest 5-7 specific keywords or phrases 
        that should be added to this resume to improve ATS matching:
        
        Resume: {str(resume)}
        Job Description: {job_description}
        
        Return as a comma-separated list of actionable suggestions.
        """
        
        suggestions = self.generate_content(prompt, {"resume": resume, "job": job_description}, max_tokens=200)
        return [s.strip() for s in suggestions.split(',') if s.strip()]
