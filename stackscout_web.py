# stackscout_web.py
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
        logger.info("Chrome driver initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing Chrome driver: {e}")
        driver = None
    return driver

def login_linkedin(driver, email, password):
    if not email or not password:
        logger.error("LinkedIn credentials are missing.")
        return False
    try:
        driver.get("https://www.linkedin.com/login")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        wait.until(EC.url_contains("feed"))
        return True
    except Exception as e:
        logger.error(f"LinkedIn login failed: {e}")
        return False

from typing import Optional
from bs4.element import Tag

def scrape_linkedin(driver):
    print("Scraping LinkedIn...")
    jobs = []
    driver.get("https://www.linkedin.com/jobs/search/?keywords=remote%20python%20developer")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.base-card")))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.find_all("div", class_="base-card")[:5]
    for job_card in job_cards:
        title: Optional[Tag] = job_card.find("h3")  # type: ignore
        company: Optional[Tag] = job_card.find("h4")  # type: ignore
        link_tag: Optional[Tag] = job_card.find("a")  # type: ignore
        jobs.append({
            "Company": company.get_text(strip=True) if company else "N/A",  # type: ignore
            "Role": title.get_text(strip=True) if title else "N/A",  # type: ignore
            "Link": link_tag.get("href", "N/A") if link_tag else "N/A",  # type: ignore
            "Tech Stack": "Python, Remote",
            "Type": "Remote",
            "Salary": "N/A",
            "Contact Person": "N/A",
            "Email": "N/A"
        })
    return jobs

def scrape_indeed(driver):
    print("Scraping Indeed...")
    jobs = []
    driver.get("https://www.indeed.com/jobs?q=remote+python+developer&l=Worldwide")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job_seen_beacon")))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.select("div.job_seen_beacon")[:5]
    for job_card in job_cards:
        title: Optional[Tag] = job_card.find("h2")  # type: ignore
        company: Optional[Tag] = job_card.find("span", class_="companyName")  # type: ignore
        link_tag: Optional[Tag] = job_card.find("a")  # type: ignore
        link = "https://www.indeed.com" + link_tag.get("href", "N/A") if link_tag else "N/A"  # type: ignore
        jobs.append({
            "Company": company.get_text(strip=True) if company else "N/A",  # type: ignore
            "Role": title.get_text(strip=True) if title else "N/A",  # type: ignore
            "Link": link,
            "Tech Stack": "Python, React, Remote",
            "Type": "Remote",
            "Salary": "N/A",
            "Contact Person": "N/A",
            "Email": "N/A"
        })
    return jobs

def scrape_arc_dev(driver):
    print("Scraping Arc.dev...")
    jobs = []
    driver.get("https://arc.dev/remote-jobs?search=python")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_cards = soup.select("div.job-listing")[:5]
    for card in job_cards:
        title: Optional[Tag] = card.find("h3")  # type: ignore
        company: Optional[Tag] = card.find("div", class_="company-name")  # type: ignore
        link_tag: Optional[Tag] = card.find("a", href=True)  # type: ignore
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

def run_scraper(email, password):
    driver = get_driver()
    if driver is None:
        logger.error("Web driver could not be initialized. Aborting scraping.")
        return []

    login_success = login_linkedin(driver, email, password)
    if not login_success:
        logger.warning("LinkedIn login failed or credentials missing. Continuing without login.")

    results = []

    # Google Jobs placeholder
    try:
        driver.get("https://www.google.com/search?q=remote+developer+jobs+react+python+node+fastapi+docker")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[jscontroller]")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.select("div[jscontroller]")[:5]
        for job_card in job_cards:
            title = job_card.get_text(strip=True)
            results.append({
                "Company": "Unknown (Google Jobs)",
                "Role": title,
                "Link": driver.current_url,
                "Tech Stack": "React, Python, etc.",
                "Contact Person": "N/A",
                "Email": "N/A",
                "Salary": "N/A",
                "Type": "Remote"
            })
    except Exception as e:
        logger.error(f"Google Jobs scraping failed: {e}")

    # Remote OK
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
        logger.error(f"Remote OK scraping failed: {e}")

    try:
        results += scrape_indeed(driver)
    except Exception as e:
        logger.error(f"Indeed scraping failed: {e}")

    try:
        results += scrape_arc_dev(driver)
    except Exception as e:
        logger.error(f"Arc.dev scraping failed: {e}")

    try:
        results += scrape_linkedin(driver)
    except Exception as e:
        logger.error(f"LinkedIn scraping failed: {e}")

    driver.quit()
    return results

@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run", response_class=HTMLResponse)
def run_job_search(request: Request):
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    results = []
    try:
        results = run_scraper(email, password)
    except Exception as e:
        logger.error(f"Job search failed: {e}")
        return templates.TemplateResponse("results.html", {"request": request, "results": [], "error": "Job search failed. Please try again later."})
    return templates.TemplateResponse("results.html", {"request": request, "results": results})
