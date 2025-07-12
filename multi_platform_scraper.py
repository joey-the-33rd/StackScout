from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import time
import requests

def get_driver():
    options = Options()
    options.add_argument("--headless=new")  # Updated headless mode for newer Chrome versions
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as e:
        print(f"Error initializing Chrome driver: {e}")
        driver = None
    return driver

def scrape_google_jobs(driver):
    print("Google Jobs scraping is currently a placeholder due to dynamic content and page structure limitations.")
    print("This scraper does not return job listings at this time.")
    return []

import time

def scrape_remoteok():
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
                print(f"Received 429 Too Many Requests, retrying after delay... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(10 * (attempt + 1))  # Exponential backoff
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
def scrape_indeed(driver):
    print("Scraping Indeed jobs...")
    jobs = []
    if not driver:
        print("No Selenium driver available, skipping Indeed scraping.")
        return jobs

    try:
        # Navigate to Indeed remote developer jobs page
        url = "https://www.indeed.com/jobs?q=remote+developer&l="
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.find_all("a", class_="tapItem")[:5]  # Limit to top 5 jobs

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
        print(f"Error scraping Indeed: {e}")

    return jobs

def scrape_weworkremotely(driver):
    print("Scraping We Work Remotely placeholder... (not implemented)")
    return []

def scrape_ziprecruiter(driver):
    print("Scraping ZipRecruiter placeholder... (not implemented)")
    return []

def scrape_arc_dev(driver):
    print("Scraping Arc.dev placeholder... (not implemented)")
    return []

def scrape_linkedin(driver):
    print("Scraping LinkedIn placeholder... (not implemented)")
    return []

def main():
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
