import os
import time
import requests
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Ensure ssl module is loaded early to avoid missing module error in restricted environments
try:
    import ssl
except ImportError as e:
    raise ImportError("SSL support is required but missing. Please ensure your Python environment includes the 'ssl' module.")

from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join("templates", ".env"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add debug log to confirm environment variables are loaded
logger.info(f"Loaded LINKEDIN_EMAIL: {os.getenv('LINKEDIN_EMAIL')}")
logger.info(f"Loaded LINKEDIN_PASSWORD: {'***' if os.getenv('LINKEDIN_PASSWORD') else None}")

# Import the Playwright scrapers
import multi_platform_scraper_playwright as playwright_scraper

async def run_scraper_async(keywords: str = "python"):
    """Run the Playwright-based scrapers asynchronously"""
    async with async_playwright() as p:
        # Set a user agent to avoid bot detection
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        results = []
        
        # Run all the Playwright scrapers
        try:
            results += await playwright_scraper.scrape_remoteok(context, keywords)
        except Exception as e:
            logger.error(f"❌ RemoteOK scraping failed: {e}")
            
        try:
            # Skip LinkedIn scraping for now as it requires credentials and is prone to errors
            logger.info("⏭️ Skipping LinkedIn scraping (requires credentials and prone to errors)")
        except Exception as e:
            logger.error(f"❌ LinkedIn scraping failed: {e}")
            
        try:
            results += await playwright_scraper.scrape_jobgether(context, keywords)
        except Exception as e:
            logger.error(f"❌ JobGether scraping failed: {e}")
            
            
        try:
            results += await playwright_scraper.scrape_nodesk(context, keywords)
        except Exception as e:
            logger.error(f"❌ NoDesk scraping failed: {e}")
            
        try:
            results += await playwright_scraper.scrape_arkdev(context, keywords)
        except Exception as e:
            logger.error(f"❌ ArkDev scraping failed: {e}")
            
        await browser.close()
        logger.info(f"ℹ️ Total jobs found: {len(results)}")
        return results

def run_scraper(email, password):
    """Synchronous wrapper for the async scraper"""
    try:
        # Run the async function in a new event loop
        return asyncio.run(run_scraper_async())
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        return []

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run", response_class=HTMLResponse)
async def run_job_search(request: Request):
    results = []
    try:
        # Extract form data from the request
        form_data = await request.form()
        keywords = str(form_data.get("keywords", "python"))
        location = str(form_data.get("location")) if form_data.get("location") else None
        job_type = str(form_data.get("job_type")) if form_data.get("job_type") else None
        
        # Pass the keywords to the scraper
        results = await run_scraper_async(keywords)
        if not results:
            logger.warning("⚠️ No jobs found during scraping.")
    except Exception as e:
        logger.error(f"❌ Job search failed: {e}")
        return templates.TemplateResponse("results.html", {"request": request, "results": [], "error": "Job search failed. Please try again later."})
    return templates.TemplateResponse("results.html", {"request": request, "results": results})

from fastapi.responses import Response
import base64

@app.get("/apple-touch-icon.png")
def apple_touch_icon():
    # 16x16 transparent PNG base64
    transparent_png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAKklEQVR4AWP4//8/AyUYTFhY+P//"
        "P4MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMA"
        "AABJRU5ErkJggg=="
    )
    png_bytes = base64.b64decode(transparent_png_base64)
    return Response(content=png_bytes, media_type="image/png")
