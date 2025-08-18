"""User profile model for AI generators."""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, EmailStr, HttpUrl

class Experience(BaseModel):
    """Work experience model."""
    title: str
    company: str
    duration: str
    description: str
    achievements: Optional[List[str]] = []

class Education(BaseModel):
    """Education model."""
    degree: str
    institution: str
    year: str
    description: Optional[str] = ""

class Project(BaseModel):
    """Project model."""
    name: str
    technologies: List[str]
    description: str
    impact: Optional[str] = ""
    url: Optional[str] = ""

class UserProfile(BaseModel):
    """User profile model."""
    user_id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    summary: Optional[str] = ""
    years_experience: int = 0
    title: str
    industry: str = "technology"
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    achievements: List[str] = []

class DocumentRequest(BaseModel):
    """Base model for document generation requests."""
    user_id: str
    job_id: Optional[str] = None
    template_name: Optional[str] = "default"

class ResumeRequest(DocumentRequest):
    """Resume generation request."""
    template_type: str = "ats_friendly"

class CoverLetterRequest(DocumentRequest):
    """Cover letter generation request."""
    job_title: str
    company_name: str
    job_description: str
    company_info: Optional[Dict[str, Any]] = {}

class CVTailorRequest(DocumentRequest):
    """CV tailoring request."""
    base_resume: Dict[str, Any]
    job_description: str

class EmailRequest(DocumentRequest):
    """Email generation request."""
    email_type: str
    job_title: str
    company_name: str
    context: Optional[Dict[str, Any]] = {}
