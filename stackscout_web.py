from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file at the very beginning
# Use find_dotenv() to locate the .env file robustly, and override=True to ensure environment variables are set
load_dotenv(find_dotenv(), override=True)

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
from pydantic import BaseModel, Field
  
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

# Import analytics
from src.analytics.engine import get_all_analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include authentication router
app.include_router(auth_router)

# Include recommendations router
app.include_router(recommendations_router)

# Include notifications router
from src.notifications.endpoints import router as notifications_router
app.include_router(notifications_router)

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("enhanced_index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Serve the login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    """Serve the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})

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
    job_type: str = Field(default="", description="Type of job (e.g., full-time, part-time)")
    salary_range: str = Field(default="", description="Salary range (e.g., $50k-$70k)")

def serialize_for_json(obj):
    """Convert non-JSON serializable objects to JSON serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    from datetime import date as _date  # local import to avoid top-level conflicts
    if isinstance(obj, _date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

@app.post("/api/search")
async def api_search(request: SearchRequest):
    """API endpoint for job search with enhanced filtering"""
    storage = None
    try:
        # First try to get filtered results from database
        storage = JobSearchStorage(DB_CONFIG)
        filtered_jobs = storage.get_jobs_filtered(
            limit=100,
            offset=0,
            search=request.keywords,
            job_type=request.job_type,
            salary_range=request.salary_range,
        )
        
        # If we have filtered results, return them
        if filtered_jobs:
            return JSONResponse(content={"results": filtered_jobs})
        
        # If no filtered results but we have specific filters, don't scrape
        if request.job_type or request.salary_range:
            return JSONResponse(content={"results": []})
        
        # If no filters specified, scrape new jobs
        scraper = EnhancedJobScraper()
        results = await scraper.scrape_all_platforms(request.keywords)
        
        # Convert datetime and dict fields to JSON serializable format
        serialized_results = [serialize_for_json(job) for job in results]
        
        # Store results in database
        search_query = {
            "keywords": request.keywords,
            "location": request.location,
            "job_type": request.job_type,
            "salary_range": request.salary_range,
        }
        storage.store_search_results(search_query, serialized_results)
        
        return JSONResponse(content={"results": serialized_results})
    except Exception as e:
        logger.error(f"API search failed: {e}")
        return JSONResponse(content={"results": [], "error": str(e)}, status_code=500)
    finally:
        if storage:
            try:
                storage.close()
            except Exception:
                logger.warning("Failed to close storage in api_search", exc_info=True)


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
    status: str = "",
    job_type: str = "",
    salary_range: str = ""
):
    """Get jobs with filtering and pagination"""
    try:
        storage = JobSearchStorage(DB_CONFIG)
        jobs = storage.get_jobs_filtered(
            limit=limit,
            offset=offset,
            search=search,
            platform=platform,
            status=status,
            job_type=job_type,
            salary_range=salary_range
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
                "description": request.company_info.get("description", "") if request.company_info else ""
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

@app.get("/api/analytics")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    """Get all analytics data for the dashboard."""
    try:
        analytics_data = get_all_analytics()
        logger.info(
            "Analytics retrieved: jobs_total=%s users_total=%s",
            analytics_data.get("overall", {}).get("jobs", {}).get("total", 0),
            analytics_data.get("overall", {}).get("users", {}).get("total", 0)
        )
        serialized_data = serialize_for_json(analytics_data)
        return JSONResponse(content=serialized_data)
    except Exception as e:
        logger.error(f"Analytics data retrieval failed: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/analytics", response_class=HTMLResponse)
def analytics_dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    """Serve the analytics dashboard page."""
    return templates.TemplateResponse("analytics_dashboard.html", {"request": request})

@app.get("/ai-tools", response_class=HTMLResponse)
def ai_tools_page(request: Request):
    """Serve the AI tools page."""
    return templates.TemplateResponse("ai_tools.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
