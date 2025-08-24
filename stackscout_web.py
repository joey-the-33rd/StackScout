from dotenv import load_dotenv

# Load environment variables from .env file at the very beginning
load_dotenv()

import os
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import json
from pydantic import BaseModel
  
from enhanced_scraper import EnhancedJobScraper
from job_search_storage import JobSearchStorage, DB_CONFIG

# Import AI generators
from src.ai_generators.resume_generator import ResumeGenerator
from src.ai_generators.cover_letter_generator import CoverLetterGenerator
from src.ai_generators.cv_tailor import CVTailor
from src.ai_generators.email_generator import EmailGenerator
from src.models.user_profile import (
    UserProfile, ResumeRequest, CoverLetterRequest, 
    CVTailorRequest, EmailRequest
)

# Import authentication
from src.auth.endpoints import router as auth_router
from src.auth.dependencies import get_current_user, get_optional_current_user

# Import recommendations
from src.recommendations.endpoints import router as recommendations_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include authentication router
app.include_router(auth_router)

# Include recommendations router
app.include_router(recommendations_router)

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("enhanced_index.html", {"request": request})

@app.post("/run", response_class=HTMLResponse)
async def run_job_search(request: Request):
    results = []
    try:
        form_data = await request.form()
        keywords = str(form_data.get("keywords", "python")) if form_data.get("keywords") else "python"
        location = str(form_data.get("location", "")) if form_data.get("location") else ""
        job_type = str(form_data.get("job_type", "")) if form_data.get("job_type") else ""

        # Use enhanced_scraper
        scraper = EnhancedJobScraper()
        results = await scraper.scrape_all_platforms(keywords)

        # Store results in database
        storage = JobSearchStorage(DB_CONFIG)
        search_query = {
            "keywords": keywords,
            "location": location,
            "job_type": job_type
        }
        storage.store_search_results(search_query, results)
        storage.close()

    except Exception as e:
        logger.error(f"Job search failed: {e}")
        return templates.TemplateResponse("results.html", {"request": request, "results": [], "error": "Job search failed. Please try again later."})

    return templates.TemplateResponse("results.html", {"request": request, "results": results})

class SearchRequest(BaseModel):
    keywords: str
    location: str = ""
    job_type: str = ""

def serialize_for_json(obj):
    """Convert non-JSON serializable objects to JSON serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    return obj

@app.post("/api/search")
async def api_search(request: SearchRequest):
    """API endpoint for job search"""
    try:
        scraper = EnhancedJobScraper()
        results = await scraper.scrape_all_platforms(request.keywords)
        
        # Convert datetime and dict fields to JSON serializable format
        serialized_results = [serialize_for_json(job) for job in results]
        
        # Store results in database
        storage = JobSearchStorage(DB_CONFIG)
        search_query = {
            "keywords": request.keywords,
            "location": request.location,
            "job_type": request.job_type
        }
        storage.store_search_results(search_query, serialized_results)
        storage.close()
        
        return JSONResponse(content={"results": serialized_results})
    except Exception as e:
        logger.error(f"API search failed: {e}")
        return JSONResponse(content={"results": [], "error": str(e)}, status_code=500)

@app.post("/api/jobs/save")
async def api_save_job(request: Request):
    """API endpoint to save a job"""
    try:
        data = await request.json()
        job_data = data.get("job_data")
        
        # Convert datetime and dict fields to JSON serializable format
        serialized_job = serialize_for_json(job_data)
        
        storage = JobSearchStorage(DB_CONFIG)
        success = storage.store_job(serialized_job, {})
        storage.close()
        
        return JSONResponse(content={"success": success})
    except Exception as e:
        logger.error(f"Save job failed: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

@app.get("/favicon.ico")
def favicon():
    """Serve favicon with proper media type and caching"""
    from fastapi.responses import FileResponse
    import os
    
    favicon_path = os.path.join("static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(
            favicon_path, 
            media_type="image/vnd.microsoft.icon",
            headers={
                "Cache-Control": "public, max-age=31536000, immutable"
            }
        )
    else:
        # Return a simple 404 if favicon doesn't exist
        from fastapi.responses import Response
        return Response(status_code=404)

@app.get("/database/manager", response_class=HTMLResponse)
def database_manager(request: Request):
    """Serve the database manager page"""
    return templates.TemplateResponse("database_manager_enhanced.html", {"request": request})

@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics for the manager dashboard"""
    try:
        storage = JobSearchStorage(DB_CONFIG)
        stats = storage.get_database_stats()
        storage.close()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Database stats failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/database/jobs")
async def get_jobs(
    limit: int = 100,
    offset: int = 0,
    search: str = "",
    platform: str = "",
    status: str = ""
):
    """Get jobs with filtering and pagination"""
    try:
        storage = JobSearchStorage(DB_CONFIG)
        jobs = storage.get_jobs_filtered(
            limit=limit,
            offset=offset,
            search=search,
            platform=platform,
            status=status
        )
        storage.close()
        return JSONResponse(content={"jobs": jobs})
    except Exception as e:
        logger.error(f"Get jobs failed: {e}")
        return JSONResponse(content={"jobs": [], "error": str(e)}, status_code=500)

@app.delete("/api/database/jobs/{job_id}")
async def delete_job(job_id: int):
    """Delete a specific job"""
    try:
        storage = JobSearchStorage(DB_CONFIG)
        success = storage.delete_job(job_id)
        storage.close()
        return JSONResponse(content={"success": success})
    except Exception as e:
        logger.error(f"Delete job failed: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

@app.get("/apple-touch-icon.png")
def apple_touch_icon():
    import base64
    transparent_png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAKklEQVR4AWP4//8/AyUYTFhY+P//"
        "P4MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMA"
        "AABJRU5ErkJggg=="
    )
    png_bytes = base64.b64decode(transparent_png_base64)
    return HTMLResponse(content=png_bytes, media_type="image/png")

# AI Generator API Endpoints
@app.post("/api/generate-resume")
async def generate_resume(request: ResumeRequest):
    """Generate a resume based on user profile."""
    try:
        generator = ResumeGenerator()
        
        # In a real implementation, fetch user profile from database
        # For now, use mock data
        user_profile = {
            "full_name": "John Doe",
            "title": "Senior Software Engineer",
            "years_experience": 5,
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2021-2024",
                    "description": "Led development of scalable web applications",
                    "achievements": ["Reduced load time by 40%", "Led team of 5 developers"]
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Computer Science",
                    "institution": "University of Technology",
                    "year": "2019"
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "technologies": ["React", "Node.js", "MongoDB"],
                    "description": "Full-stack e-commerce solution",
                    "impact": "Increased sales by 25%"
                }
            ]
        }
        
        resume = generator.generate_resume(user_profile, request.template_type)
        return JSONResponse(content={"resume": resume})
        
    except Exception as e:
        logger.error(f"Resume generation failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/generate-cover-letter")
async def generate_cover_letter(request: CoverLetterRequest):
    """Generate a cover letter for a specific job."""
    try:
        generator = CoverLetterGenerator()
        
        # Mock user profile
        user_profile = {
            "full_name": "John Doe",
            "title": "Senior Software Engineer",
            "years_experience": 5,
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"]
        }
        
        cover_letter = generator.generate_cover_letter(
            user_profile=user_profile,
            job_details={
                "title": request.job_title,
                "description": request.job_description,
                "company": request.company_name
            },
            company_info={
                "name": request.company_name,
                "description": request.company_info.get("description", "")
            }
        )
        
        return JSONResponse(content={"cover_letter": cover_letter})
        
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/tailor-cv")
async def tailor_cv(request: CVTailorRequest):
    """Tailor a CV for a specific job posting."""
    try:
        tailor = CVTailor()
        
        tailored_cv = tailor.tailor_cv(
            base_resume=request.base_resume,
            job_description=request.job_description
        )
        
        return JSONResponse(content={"tailored_cv": tailored_cv})
        
    except Exception as e:
        logger.error(f"CV tailoring failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/generate-email")
async def generate_email(request: EmailRequest):
    """Generate a follow-up email."""
    try:
        generator = EmailGenerator()
        
        # Mock user profile
        user_profile = {
            "full_name": "John Doe",
            "email": "john.doe@email.com"
        }
        
        email = generator.generate_follow_up_email(
            user_profile=user_profile,
            job_details={
                "title": request.job_title,
                "company": request.company_name
            },
            email_type=request.email_type,
            context=request.context
        )
        
        return JSONResponse(content={"email": email})
        
    except Exception as e:
        logger.error(f"Email generation failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/ai-tools")
async def get_ai_tools():
    """Get available AI tools and their status."""
    return JSONResponse(content={
        "tools": [
            {
                "name": "Resume Generator",
                "endpoint": "/api/generate-resume",
                "description": "Generate professional resumes from user profile"
            },
            {
                "name": "Cover Letter Generator",
                "endpoint": "/api/generate-cover-letter",
                "description": "Generate job-specific cover letters"
            },
            {
                "name": "CV Tailor",
                "endpoint": "/api/tailor-cv",
                "description": "Tailor CV for specific job postings"
            },
            {
                "name": "Email Generator",
                "endpoint": "/api/generate-email",
                "description": "Generate follow-up emails"
            }
        ],
        "status": "active"
    })

@app.get("/ai-tools", response_class=HTMLResponse)
def ai_tools_page(request: Request):
    """Serve the AI tools page."""
    return templates.TemplateResponse("ai_tools.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
