import os
import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
from pydantic import BaseModel

from enhanced_scraper import EnhancedJobScraper
from job_search_storage import JobSearchStorage, DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    """Serve favicon"""
    from fastapi.responses import FileResponse
    import os
    
    favicon_path = os.path.join("static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    else:
        # Return a simple 404 if favicon doesn't exist
        from fastapi.responses import Response
        return Response(status_code=404)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
