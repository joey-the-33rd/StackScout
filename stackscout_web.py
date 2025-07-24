import os
import time
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import multi_platform_scraper
import traceback
import asyncio

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scraper_results = {}

def run_scraper(email, password):
    driver = multi_platform_scraper.get_driver()
    if driver is None:
        logger.error("Web driver could not be initialized. Aborting scraping.")
        return []

    login_success = False
    max_login_attempts = 3
    for attempt in range(max_login_attempts):
        try:
            login_success = multi_platform_scraper.login_linkedin(driver, email, password)
            if login_success:
                break
            else:
                logger.warning(f"LinkedIn login attempt {attempt + 1} failed.")
                time.sleep(5)
        except Exception as e:
            logger.error(f"LinkedIn login exception on attempt {attempt + 1}: {e}")
            logger.error(traceback.format_exc())
            time.sleep(5)

    if not login_success:
        logger.warning("LinkedIn login failed or credentials missing. Continuing without login.")

    results = []

    try:
        google_jobs = multi_platform_scraper.scrape_google_jobs(driver)
        if google_jobs:
            results += google_jobs
    except Exception as e:
        logger.error(f"Google Jobs scraping failed: {e}")
        logger.error(traceback.format_exc())

    try:
        remoteok_jobs = multi_platform_scraper.scrape_remoteok()
        if remoteok_jobs:
            results += remoteok_jobs
    except Exception as e:
        logger.error(f"Remote OK scraping failed: {e}")
        logger.error(traceback.format_exc())

    try:
        indeed_jobs = multi_platform_scraper.scrape_indeed(driver)
        if indeed_jobs:
            results += indeed_jobs
    except Exception as e:
        logger.error(f"Indeed scraping failed: {e}")
        logger.error(traceback.format_exc())

    try:
        arc_dev_jobs = multi_platform_scraper.scrape_arc_dev(driver)
        if arc_dev_jobs:
            results += arc_dev_jobs
    except Exception as e:
        logger.error(f"Arc.dev scraping failed: {e}")
        logger.error(traceback.format_exc())

    try:
        linkedin_jobs = multi_platform_scraper.scrape_linkedin(driver)
        if linkedin_jobs:
            results += linkedin_jobs
    except Exception as e:
        logger.error(f"LinkedIn scraping failed: {e}")
        logger.error(traceback.format_exc())

    driver.quit()
    return results

async def run_scraper_async(email, password, task_id):
    loop = asyncio.get_event_loop()
    try:
        results = await loop.run_in_executor(None, run_scraper, email, password)
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
