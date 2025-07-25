import os
import time
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import multi_platform_scraper_playwright as multi_platform_scraper
import traceback
import asyncio

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scraper_results = {}

async def run_scraper(email, password):
    try:
        results = await multi_platform_scraper.main()
        return results
    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        logger.error(traceback.format_exc())
        return []

async def run_scraper_async(email, password, task_id):
    try:
        results = await run_scraper(email, password)
        scraper_results[task_id] = results
    except Exception as e:
        scraper_results[task_id] = []
        logger.error(f"Background scraper task failed: {e}")
        logger.error(traceback.format_exc())

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run", response_class=HTMLResponse)
async def run_job_search(request: Request, background_tasks: BackgroundTasks):
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    task_id = str(id(request))
    background_tasks.add_task(run_scraper_async, email, password, task_id)
    # Immediately return a page indicating the job search is running
    return templates.TemplateResponse("results.html", {"request": request, "results": [], "message": "Job search started. Please refresh this page after a while to see results."})

@app.get("/results/{task_id}", response_class=HTMLResponse)
def get_results(request: Request, task_id: str):
    results = scraper_results.get(task_id, [])
    return templates.TemplateResponse("results.html", {"request": request, "results": results})
