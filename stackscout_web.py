import os
import time
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Ensure ssl module is loaded early to avoid missing module error in restricted environments
try:
    import ssl
except ImportError as e:
    raise ImportError("SSL support is required but missing. Please ensure your Python environment includes the 'ssl' module.")

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("✅ Chrome driver initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Error initializing Chrome driver: {e}")
        driver = None
    return driver

def scrape_arc_dev(driver):
    print("🔍 Scraping Arc.dev...")
    jobs = []
    driver.get("https://arc.dev/remote-jobs?search=python")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.select("div.job-listing")[:5]
    if not job_cards:
        logger.warning("⚠️ No job cards found in Arc.dev scraper.")
    for card in job_cards:
        title = card.find("h3")  # type: ignore
        company = card.find("div", class_="company-name")  # type: ignore
        link_tag = card.find("a", href=True)  # type: ignore
        jobs.append({
            "Company": company.get_text(strip=True) if company else "N/A",  # type: ignore
            "Role": title.get_text(strip=True) if title else "N/A",  # type: ignore
            "Link": "https://arc.dev" + link_tag["href"] if link_tag else "N/A",  # type: ignore
            "Tech Stack": "Python, Remote",
            "Type": "Remote",
            "Salary": "N/A",
            "Contact Person": "N/A",
            "Email": "N/A"
        })
    return jobs

def scrape_remote_ok():
    print("🔍 Scraping Remote OK...")
    results = []
    try:
        res = requests.get("https://remoteok.com/remote-dev-jobs")
        soup = BeautifulSoup(res.text, "html.parser")
        job_list = soup.find_all("tr", class_="job")[:5]
        for job in job_list:
            title_text = job.get("data-position")  # type: ignore
            company_text = job.get("data-company")  # type: ignore
            link = "https://remoteok.com" + job.get("data-href", "")  # type: ignore
            tags = [t.text for t in job.find_all("div", class_="tag")]  # type: ignore
            results.append({
                "Company": company_text,
                "Role": title_text,
                "Tech Stack": ", ".join(tags),
                "Type": "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A",
                "Link": link
            })
    except Exception as e:
        logger.error(f"❌ Remote OK scraping failed: {e}")
    return results

def scrape_we_work_remotely(driver):
    print("🔍 Scraping We Work Remotely...")
    jobs = []
    driver.get("https://weworkremotely.com/remote-jobs/search?term=python")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_sections = soup.select("section.jobs")[:1]
    if not job_sections:
        logger.warning("⚠️ No job sections found in We Work Remotely scraper.")
    for section in job_sections:
        job_posts = section.select("li.feature") + section.select("li:not(.feature)")
        for post in job_posts[:5]:
            title = post.find("span", class_="title")
            company = post.find("span", class_="company")
            link_tag = post.find("a", href=True)
            link = "https://weworkremotely.com" + link_tag["href"] if link_tag else "N/A"
            jobs.append({
                "Company": company.get_text(strip=True) if company else "N/A",
                "Role": title.get_text(strip=True) if title else "N/A",
                "Link": link,
                "Tech Stack": "Python, Remote",
                "Type": "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A"
            })
    return jobs

def run_scraper(email, password):
    driver = get_driver()
    if driver is None:
        logger.error("❌ Web driver could not be initialized. Aborting scraping.")
        return []

    results = []

    results += scrape_remote_ok()

    try:
        results += scrape_job_together(driver)
    except Exception as e:
        logger.error(f"❌ Job Together scraping failed: {e}")

    try:
        results += scrape_ziprecruiter(driver)
    except Exception as e:
        logger.error(f"❌ Ziprecruiter scraping failed: {e}")

    try:
        results += scrape_no_desk(driver)
    except Exception as e:
        logger.error(f"❌ No Desk scraping failed: {e}")

    try:
        results += scrape_turing(driver)
    except Exception as e:
        logger.error(f"❌ Turing scraping failed: {e}")

    try:
        results += scrape_arc_dev(driver)
    except Exception as e:
        logger.error(f"❌ Arc.dev scraping failed: {e}")

    try:
        results += scrape_we_work_remotely(driver)
    except Exception as e:
        logger.error(f"❌ We Work Remotely scraping failed: {e}")

    driver.quit()
    logger.info(f"ℹ️ Total jobs found: {len(results)}")
    return results

def scrape_google_jobs(driver):
    print("🔍 Placeholder for Google Jobs scraper...")
    # Placeholder function for Google Jobs scraper
    return []

def scrape_job_together(driver):
    print("🔍 Scraping Job Together...")
    jobs = []
    driver.get("https://jobtogether.com/jobs?search=remote+python+developer")
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job-listing")))
        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job-listing")[:5]
        if not job_cards:
            logger.warning("⚠️ No job cards found in Job Together scraper.")
        for card in job_cards:
            title = card.find_element(By.TAG_NAME, "h2")
            company = card.find_element(By.CLASS_NAME, "company")
            link_tag = card.find_element(By.TAG_NAME, "a")
            jobs.append({
                "Company": company.text if company else "N/A",
                "Role": title.text if title else "N/A",
                "Link": link_tag.get_attribute("href") if link_tag else "N/A",
                "Tech Stack": "Python, Remote",
                "Type": "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A"
            })
    except Exception as e:
        logger.error(f"❌ Job Together scraping failed: {e}")
    return jobs

def scrape_ziprecruiter(driver):
    print("🔍 Scraping Ziprecruiter...")
    jobs = []
    try:
        print("Loading Ziprecruiter page...")
        driver.get("https://www.ziprecruiter.com/candidate/search?search=remote+python+developer")
        print("Waiting for page to load...")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.job_result")))
        print("Page loaded. Parsing HTML...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.select("article.job_result")[:5]
        if not job_cards:
            logger.warning("⚠️ No job cards found in Ziprecruiter scraper.")
        for card in job_cards:
            print(f"Processing job card: {card}")
            title = card.find("a", class_="job_link")
            company = card.find("a", class_="t_org_link")
            location = card.find("span", class_="job_result_location")
            link_tag = title
            jobs.append({
                "Company": company.get_text(strip=True) if company else "N/A",
                "Role": title.get_text(strip=True) if title else "N/A",
                "Link": "https://www.ziprecruiter.com" + link_tag["href"] if link_tag else "N/A",
                "Tech Stack": "Python, Remote",
                "Type": location.get_text(strip=True) if location else "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A"
            })
    except Exception as e:
        logger.error(f"❌ Error scraping Ziprecruiter: {e}")
    return jobs

def scrape_no_desk(driver):
    print("🔍 Scraping No Desk...")
    jobs = []
    driver.get("https://nodesk.co/remote-jobs/search?term=python")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.select("div.job-listing")[:5]
    if not job_cards:
        logger.warning("⚠️ No job cards found in No Desk scraper.")
    for card in job_cards:
        title = card.find("h3")
        company = card.find("div.company")
        link_tag = card.find("a", href=True)
        jobs.append({
            "Company": company.get_text(strip=True) if company else "N/A",
            "Role": title.get_text(strip=True) if title else "N/A",
            "Link": link_tag["href"] if link_tag else "N/A",
            "Tech Stack": "Python, Remote",
            "Type": "Remote",
            "Salary": "N/A",
            "Contact Person": "N/A",
            "Email": "N/A"
        })
    return jobs

def scrape_turing(driver):
    print("🔍 Scraping Turing...")
    jobs = []
    driver.get("https://www.turing.com/jobs?search=python")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.select("div.job-card")[:5]
    for card in job_cards:
        title = card.find("h3")
        company = card.find("div.company-name")
        link_tag = card.find("a", href=True)
        jobs.append({
            "Company": company.get_text(strip=True) if company else "N/A",
            "Role": title.get_text(strip=True) if title else "N/A",
            "Link": link_tag["href"] if link_tag else "N/A",
            "Tech Stack": "Python, Remote",
            "Type": "Remote",
            "Salary": "N/A",
            "Contact Person": "N/A",
            "Email": "N/A"
        })
    return jobs

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run", response_class=HTMLResponse)
def run_job_search(request: Request):
    results = []
    try:
        results = run_scraper(None, None)
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
