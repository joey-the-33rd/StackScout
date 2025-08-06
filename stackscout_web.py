import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

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
