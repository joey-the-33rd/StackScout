"""
Enhanced Web Integration for StackScout
Integrates enhanced_scraper.py with web UI and database storage
"""

import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Import our scraper and storage
from enhanced_scraper import EnhancedJobScraper
from job_search_storage import JobSearchStorage, DB_CONFIG

logger = logging.getLogger(__name__)

app = FastAPI(title="StackScout Enhanced", version="2.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
scraper = EnhancedJobScraper()
storage = JobSearchStorage(DB_CONFIG)

class SearchRequest(BaseModel):
    keywords: str
    location: Optional[str] = ""
    job_type: Optional[str] = ""

class JobSaveRequest(BaseModel):
    job_data: dict

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main page with enhanced search form"""
    return templates.TemplateResponse("enhanced_index.html", {"request": request})

@app.post("/api/search")
async def search_jobs(request: SearchRequest):
    """API endpoint to search jobs using enhanced scraper"""
    try:
        # Run scraper with provided keywords
        results = await scraper.scrape_all_platforms(request.keywords)
        
        # Store results in database
        search_query = {
            "keywords": request.keywords,
            "location": request.location,
            "job_type": request.job_type
        }
        storage.store_search_results(search_query, results)
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
async def get_jobs(
    skip: int = 0,
    limit: int = 20,
    keywords: Optional[str] = None,
    location: Optional[str] = None
):
    """Get stored jobs from database"""
    try:
        if not storage.connection:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        with storage.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT * FROM jobs 
                WHERE is_active = true
            """
            params = []
            
            if keywords:
                query += " AND keywords @> %s"
                params.append([keywords])
            
            if location:
                query += " AND location ILIKE %s"
                params.append(f"%{location}%")
            
            query += " ORDER BY posted_date DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return {"success": True, "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"Failed to get jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/save")
async def save_job(request: JobSaveRequest):
    """Save a job to the database"""
    try:
        success = storage.store_job(request.job_data, {"manual_save": True})
        return {"success": success}
    except Exception as e:
        logger.error(f"Failed to save job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int):
    """Get specific job details"""
    try:
        if not storage.connection:
            raise HTTPException(status_code=500, detail="Database connection not available")
            
        with storage.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="Job not found")
            
            return result
    except Exception as e:
        logger.error(f"Failed to get job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
