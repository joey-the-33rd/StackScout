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
import time
import requests
import random
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

def get_driver():
    options = Options()
    # Use headful mode (non-headless) to better simulate user behavior
    # Comment out headless argument
    # options.add_argument("--headless=new")  # Updated headless mode for newer Chrome versions

    # Randomize user agent
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')

    # Additional options for stealth
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    try:
        driver = webdriver.Chrome(options=options)

        # Apply selenium-stealth
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        # Additional stealth: modify navigator.webdriver property
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })

        driver.set_page_load_timeout(60)  # Increased page load timeout to 60 seconds
    except WebDriverException as e:
        print(f"Error initializing Chrome driver: {e}")
        driver = None
    return driver

def scrape_google_jobs(driver):
    """
    Attempts to scrape job listings from Google Jobs using a Selenium driver.
    
    Note:
    - This function is currently a placeholder due to the limitations imposed by the dynamic nature of Google's job listings page and its complex structure.
    - No job listings are returned by this scraper at this time.

    Args:
    - driver (selenium.webdriver.Chrome): Selenium WebDriver instance used to interact with web pages.

    Returns:
    - list: An empty list as no scraping is performed.
    """

    print("Google Jobs scraping is currently a placeholder due to dynamic content and page structure limitations.")
    print("This scraper does not return job listings at this time.")
    return []

import time

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
    max_retries = 5
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 429:
                print(f"Received 429 Too Many Requests, retrying after delay... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(15 * (attempt + 1))  # Increased exponential backoff
                # Rotate user agent on retry
                ua = UserAgent()
                headers["User-Agent"] = ua.random
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
            print(f"Error scraping Remote OK: {e}")
            if attempt == max_retries - 1:
                print("Max retries reached, skipping Remote OK scraping.")
    return jobs

# Placeholder functions for platforms to be implemented
import random

def scrape_indeed(driver=None, proxies=None):
    """
    Scrapes the top 5 job listings from Indeed's remote developer jobs page using Selenium with stealth and session handling.

    Args:
    - driver (selenium.webdriver.Chrome): Selenium WebDriver instance used to interact with web pages.
    - proxies: Ignored in this implementation.

    Returns:
    - list: A list of dictionaries containing job information with the following keys:
        - Company
        - Role
        - Tech Stack (job summary)
        - Type (location)
        - Salary
        - Contact Person (always "N/A")
        - Email (always "N/A")
        - Link
    """
    print("Scraping Indeed jobs using Selenium with stealth...")
    jobs = []
    if not driver:
        print("No Selenium driver available, skipping Indeed scraping.")
        return jobs

    try:
        url = "https://www.indeed.com/jobs?q=remote+developer&l="
        driver.get(url)

        # Check for CAPTCHA or login page
        if "captcha" in driver.page_source.lower() or "verify" in driver.page_source.lower():
            print("CAPTCHA or verification page detected. Attempting to wait for manual solve for up to 3 minutes...")
            for i in range(18):
                time.sleep(10)
                driver.refresh()
                if "captcha" not in driver.page_source.lower() and "verify" not in driver.page_source.lower():
                    print("CAPTCHA solved, continuing scraping.")
                    break
            else:
                print("CAPTCHA not solved within timeout, skipping Indeed scraping.")
                return []
        wait = WebDriverWait(driver, 30)
        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.tapItem")))
        except Exception as e:
            print(f"Timeout waiting for job cards: {e}")
            print("Page source snippet for debugging:")
            print(driver.page_source[:1000])  # Print first 1000 chars of page source for debugging
            return []

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.find_all("a", class_="tapItem")[:5]

        for job_card in job_cards:
            title_elem = job_card.find("h2", class_="jobTitle")
            company_elem = job_card.find("span", class_="companyName")
            location_elem = job_card.find("div", class_="companyLocation")
            salary_elem = job_card.find("div", class_="salary-snippet")
            summary_elem = job_card.find("div", class_="job-snippet")

            title = title_elem.text.strip() if title_elem else "N/A"
            company = company_elem.text.strip() if company_elem else "N/A"
            location = location_elem.text.strip() if location_elem else "N/A"
            salary = salary_elem.text.strip() if salary_elem else "N/A"
            summary = summary_elem.text.strip().replace("\n", " ") if summary_elem else "N/A"

            job_link = "https://www.indeed.com" + job_card.get("href", "")

            jobs.append({
                "Company": company,
                "Role": title,
                "Tech Stack": summary,
                "Type": location,
                "Salary": salary,
                "Contact Person": "N/A",
                "Email": "N/A",
                "Link": job_link
            })
    except Exception as e:
        import traceback
        print(f"Error scraping Indeed: {e}")
        traceback.print_exc()

    return jobs

def scrape_weworkremotely(driver):
    print("Scraping We Work Remotely...")
    jobs = []
    if not driver:
        print("No Selenium driver available, skipping We Work Remotely scraping.")
        return jobs
    try:
        driver.get("https://weworkremotely.com/remote-jobs/search?term=python")
        time.sleep(5)  # Wait for page to load
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_sections = soup.find_all("section", class_="jobs")[:1]  # Limit to first section
        for section in job_sections:
            job_listings = section.find_all("li", class_="feature")[:5]
            for job in job_listings:
                title = job.find("span", class_="title")
                company = job.find("span", class_="company")
                link_tag = job.find("a", href=True)
                jobs.append({
                    "Company": company.get_text(strip=True) if company else "N/A",
                    "Role": title.get_text(strip=True) if title else "N/A",
                    "Link": "https://weworkremotely.com" + link_tag["href"] if link_tag else "N/A",
                    "Tech Stack": "Python, Remote",
                    "Type": "Remote",
                    "Salary": "N/A",
                    "Contact Person": "N/A",
                    "Email": "N/A"
                })
    except Exception as e:
        print(f"We Work Remotely scraping failed: {e}")
    return jobs

def scrape_ziprecruiter(driver):
    print("Scraping ZipRecruiter placeholder... (not implemented)")
    return []

def scrape_arc_dev(driver):
    print("Scraping Arc.dev...")
    jobs = []
    if not driver:
        print("No Selenium driver available, skipping Arc.dev scraping.")
        return jobs
    try:
        driver.get("https://arc.dev/remote-jobs?search=python")
        time.sleep(5)  # Wait for page to load
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.select("div.job-listing")[:5]
        for card in job_cards:
            title = card.find("h3")
            company = card.find("div", class_="company-name")
            link_tag = card.find("a", href=True)
            jobs.append({
                "Company": company.get_text(strip=True) if company else "N/A",
                "Role": title.get_text(strip=True) if title else "N/A",
                "Link": "https://arc.dev" + link_tag["href"] if link_tag else "N/A",
                "Tech Stack": "Python, Remote",
                "Type": "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A"
            })
    except Exception as e:
        print(f"Arc.dev scraping failed: {e}")
    return jobs

def login_linkedin(driver, email, password):
    if not email or not password:
        print("LinkedIn credentials missing.")
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
        print(f"LinkedIn login failed: {e}")
        return False

def scrape_linkedin(driver):
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        print("LinkedIn credentials missing. Skipping LinkedIn scraping.")
        return []
    print(f"Using LinkedIn credentials for {LINKEDIN_EMAIL} to scrape jobs.")
    jobs = []
    try:
        driver.get("https://www.linkedin.com/jobs/search/?keywords=remote%20python%20developer")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.base-card")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.find_all("div", class_="base-card")[:5]
        for job_card in job_cards:
            title = job_card.find("h3")
            company = job_card.find("h4")
            link_tag = job_card.find("a")
            jobs.append({
                "Company": company.get_text(strip=True) if company else "N/A",
                "Role": title.get_text(strip=True) if title else "N/A",
                "Link": link_tag.get("href", "N/A") if link_tag else "N/A",
                "Tech Stack": "Python, Remote",
                "Type": "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A"
            })
    except Exception as e:
        print(f"LinkedIn scraping failed: {e}")
    return jobs

def main() -> None:
    driver = get_driver()
    results = []

    print("Scraping Google Jobs...")
    results += scrape_google_jobs(driver)

    print("Scraping Remote OK...")
    results += scrape_remoteok()

    results += scrape_indeed(driver)
    results += scrape_weworkremotely(driver)
    results += scrape_ziprecruiter(driver)
    results += scrape_arc_dev(driver)
    results += scrape_linkedin(driver)

    if driver:
        driver.quit()

    try:
        with open("multi_platform_jobs.md", "w", encoding="utf-8") as f:
            for job in results:
                tech_stack = " ".join(job['Tech Stack'].split())
                f.write(
                    f"- **Company:** {job['Company']}\n"
                    f"- **Role:** {job['Role']}\n"
                    f"- **Tech Stack:** {tech_stack}\n"
                    f"- **Type:** {job['Type']}\n"
                    f"- **Salary:** {job['Salary']}\n"
                    f"- **Contact Person:** {job['Contact Person']}\n"
                    f"- **Email/Contact:** {job['Email']}\n"
                    f"- **Link:** {job['Link']}\n\n"
                    "---\n"
                )
        print(f"Saved {len(results)} jobs to multi_platform_jobs.md")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    main()
