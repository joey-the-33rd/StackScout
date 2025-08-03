from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
import time
import requests
import random
from dotenv import load_dotenv
import os

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver

def get_firefox_driver(geckodriver_path=None):
    options = FirefoxOptions()
    # Use headful mode (non-headless) to better simulate user behavior
    # options.add_argument("--headless")  # Uncomment to run headless

    # Randomize user agent
    ua = UserAgent()
    user_agent = ua.random
    options.set_preference("general.useragent.override", user_agent)

    try:
        if geckodriver_path:
            service = FirefoxService(executable_path=geckodriver_path)
        else:
            service = FirefoxService()  # Use default geckodriver from PATH or specify path here if needed
        driver = FirefoxDriver(service=service, options=options)
        driver.set_page_load_timeout(120)  # Increased page load timeout to 120 seconds
    except Exception as e:
        import traceback
        print(f"Error initializing Firefox driver: {e}")
        traceback.print_exc()
        driver = None
    return driver

def scrape_google_jobs(driver):
    """
    Placeholder for Google Jobs scraper.
    """
    print("🕵️‍♂️ Google Jobs scraping is currently a placeholder.")
    return []

def scrape_indeed(driver=None, proxies=None):
    """
    Placeholder for Indeed scraper.
    """
    print("🕵️‍♂️ Indeed scraping is currently a placeholder.")
    return []

def scrape_remoteok():
    """
    Scrapes the top 5 job listings from Remote OK using requests and BeautifulSoup.

    Note:
    - This scraper is subject to rate limiting and may not work if you have made too many requests recently.
    - This scraper does not return job listings if the rate limit has been exceeded.

    Returns:
    - list: A list of dictionaries containing job information with the following keys:
        - Company
        - Role
        - Tech Stack
        - Type (always "Remote")
        - Salary (always "N/A")
        - Contact Person (always "N/A")
        - Email (always "N/A")
        - Link
    """
    jobs = []
    url = "https://remoteok.com/remote-dev-jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 429:
                print(f"❌ Received 429 Too Many Requests, retrying after delay... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(10 * (2 ** attempt))  # True exponential backoff
                continue
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            job_list = soup.find_all("tr", class_="job")[:5]  # Limit to top 5
            for job in job_list:
                title = job.get("data-position")
                company = job.get("data-company")
                link = "https://remoteok.com" + job.get("data-href", "")
                tags = [t.text for t in job.find_all("div", class_="tag")]
                jobs.append({
                    "Company": company,
                    "Role": title,
                    "Tech Stack": ", ".join(tags),
                    "Type": "Remote",
                    "Salary": "N/A",
                    "Contact Person": "N/A",
                    "Email": "N/A",
                    "Link": link
                })
            break  # Success, exit retry loop
        except requests.RequestException as e:
            print(f"❌ Error scraping Remote OK: {e}")
            if attempt == max_retries - 1:
                print("❌ Max retries reached, skipping Remote OK scraping.")
    return jobs

def scrape_job_together():
    """
    Scrapes the top 5 job listings from Job Together using requests and BeautifulSoup.
    """
    jobs = []
    url = "https://jobtogether.com/jobs"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 404:
            print("Job Together URL returned 404 Not Found. Skipping scraping Job Together.")
            return jobs
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        job_cards = soup.find_all("div", class_="job-card")[:5]
        for job in job_cards:
            title_elem = job.find("h2", class_="job-title")
            company_elem = job.find("div", class_="company-name")
            location_elem = job.find("div", class_="job-location")
            link_elem = job.find("a", href=True)

            title = title_elem.text.strip() if title_elem else "N/A"
            company = company_elem.text.strip() if company_elem else "N/A"
            location = location_elem.text.strip() if location_elem else "N/A"
            link = link_elem['href'] if link_elem else "N/A"

            jobs.append({
                "Company": company,
                "Role": title,
                "Tech Stack": "N/A",
                "Type": location,
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A",
                "Link": link
            })
    except Exception as e:
        print(f"Error scraping Job Together: {e}")
    return jobs

def scrape_no_desk():
    """
    Scrapes the top 5 job listings from No Desk using requests and BeautifulSoup.
    """
    jobs = []
    url = "https://nodesk.co/remote-jobs"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        job_cards = soup.find_all("div", class_="job")[:5]
        for job in job_cards:
            title_elem = job.find("h3", class_="job-title")
            company_elem = job.find("div", class_="company")
            location_elem = job.find("div", class_="location")
            link_elem = job.find("a", href=True)

            title = title_elem.text.strip() if title_elem else "N/A"
            company = company_elem.text.strip() if company_elem else "N/A"
            location = location_elem.text.strip() if location_elem else "N/A"
            link = link_elem['href'] if link_elem else "N/A"

            jobs.append({
                "Company": company,
                "Role": title,
                "Tech Stack": "N/A",
                "Type": location,
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A",
                "Link": link
            })
    except Exception as e:
        print(f"Error scraping No Desk: {e}")
    return jobs

def scrape_arc_dev(driver=None):
    """
    Scrapes the top 5 job listings from Arc.dev using Selenium.
    """
    jobs = []
    if not driver:
        print("No Selenium driver available, skipping Arc.dev scraping.")
        return jobs
    try:
        url = "https://arc.dev/jobs"
        driver.get(url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.job-card")))
        soup = BeautifulSoup(driver.page_source, "lxml")
        job_cards = soup.find_all("a", class_="job-card")[:5]
        for job in job_cards:
            title_elem = job.find("h3", class_="job-title")
            company_elem = job.find("div", class_="company-name")
            location_elem = job.find("div", class_="job-location")
            link_elem = job

            title = title_elem.text.strip() if title_elem else "N/A"
            company = company_elem.text.strip() if company_elem else "N/A"
            location = location_elem.text.strip() if location_elem else "N/A"
            link = link_elem['href'] if link_elem else "N/A"

            jobs.append({
                "Company": company,
                "Role": title,
                "Tech Stack": "N/A",
                "Type": location,
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A",
                "Link": link
            })
    except Exception as e:
        print(f"Error scraping Arc.dev: {e}")
    return jobs

def main():
    # Use Firefox driver instead of Chrome driver
    driver = get_firefox_driver()
    results = []

    # Google and Indeed replaced with placeholders
    results += scrape_google_jobs(driver)
    results += scrape_indeed(driver)

    # Add scrapers for requested platforms
    results += scrape_job_together()
    results += scrape_remoteok()
    results += scrape_no_desk()
    results += scrape_arc_dev(driver)

    if driver:
        driver.quit()

    try:
        with open("multi_platform_jobs.md", "w", encoding="utf-8") as f:
            for job in results:
                tech_stack = " ".join(job['Tech Stack'].split())
                f.write(f"""
- **Company:** {job['Company']}
- **Role:** {job['Role']}
- **Tech Stack:** {tech_stack}
- **Type:** {job['Type']}
- **Salary:** {job['Salary']}
- **Contact Person:** {job['Contact Person']}
- **Email/Contact:** {job['Email']}
- **Link:** {job['Link']}

---
""")
        print(f"Saved {len(results)} jobs to multi_platform_jobs.md")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()
