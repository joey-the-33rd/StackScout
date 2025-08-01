import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from fake_useragent import UserAgent
import os
from dotenv import load_dotenv
from urllib.parse import urljoin

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

async def get_page_content(url, context):
    page = await context.new_page()
    await page.goto(url)
    content = await page.content()
    await page.close()
    return content

import logging

logger = logging.getLogger("stackscout_web")

from typing import List, Union

async def scrape_remoteok(context) -> List[dict]:
    url = "https://remoteok.com/remote-dev-jobs"
    try:
        content = await get_page_content(url, context)
        soup = BeautifulSoup(content, "html.parser")
        jobs: List[dict] = []
        job_list = soup.find_all("tr", class_="job")[:5]
        if not job_list:
            logger.warning("No jobs found on remoteok.com with current selector.")
        for job in job_list:
            if isinstance(job, Tag):
                title = job.get("data-position")
                if not title:
                    title_tag = job.find("h2") or job.find("h3")
                    title = title_tag.get_text(strip=True) if title_tag else "N/A"
                company = job.get("data-company")
                if not company:
                    company_tag = job.find("h3", class_="company") or job.find("div", class_="company")
                    company = company_tag.get_text(strip=True) if company_tag else "N/A"
                data_href = job.get("data-href", "")
                link = "https://remoteok.com" + (str(data_href) if data_href else "")
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
        return jobs
    except Exception as e:
        logger.error(f"Error scraping remoteok.com: {e}")
        return []

from typing import List, Union, Dict

async def scrape_weworkremotely(context) -> List[dict]:
    logger.warning("Skipping scrape_weworkremotely due to persistent Cloudflare anti-bot protection.")
    return []

from typing import List, Optional
from bs4.element import Tag

async def scrape_linkedin(context) -> List[dict]:
    import logging
    logger = logging.getLogger("stackscout_web")
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        logger.warning("LinkedIn credentials missing. Skipping LinkedIn scraping.")
        return []
    page = await context.new_page()
    await page.goto("https://www.linkedin.com/login")
    await page.fill("#username", LINKEDIN_EMAIL)
    await page.fill("#password", LINKEDIN_PASSWORD)
    await page.click("button[type='submit']")
    try:
        await page.wait_for_url(lambda url: url.startswith("https://www.linkedin.com/feed"), timeout=30000)
        logger.info("Successfully logged in and navigated to LinkedIn feed.")
    except Exception as e:
        logger.error("Timeout or error waiting for LinkedIn feed URL.")
        await page.goto("https://www.linkedin.com/login")
    await page.fill("#username", "")
    await page.fill("#username", LINKEDIN_EMAIL)
    await page.fill("#password", LINKEDIN_PASSWORD)
    await page.click("button[type='submit']")
    try:
        await page.wait_for_url(lambda url: url.startswith("https://www.linkedin.com/feed"), timeout=30000)
        logger.info("Retry successful: logged in and navigated to LinkedIn feed.")
    except Exception as e:
        logger.error("Retry failed waiting for LinkedIn feed URL.")
        await page.close()
        return []
    await page.goto("https://www.linkedin.com/jobs/search/?keywords=remote%20python%20developer")
    try:
        await page.wait_for_selector("div.base-card", timeout=10000)
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
    except Exception as e:
        logger.error(f"Error waiting for LinkedIn job cards: {e}")
    try:
        await page.wait_for_selector("ul.jobs-search__results-list", timeout=10000)
    except Exception as e:
        logger.error(f"Error waiting for LinkedIn jobs list container: {e}")
    content = await page.content()
    await page.close()
    soup = BeautifulSoup(content, "html.parser")
    jobs: List[dict] = []
    job_cards = soup.find_all("div", class_="base-card")[:5]
    if not job_cards:
        logger.warning("No LinkedIn job cards found with current selector.")
    for job_card in job_cards:
        if isinstance(job_card, Tag):
            title: Optional[Tag] = job_card.find("h3")
            company: Optional[Tag] = job_card.find("h4")
            link_tag: Optional[Tag] = job_card.find("a")
            link = link_tag.attrs.get("href", "N/A") if link_tag and "href" in link_tag.attrs else "N/A"
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

async def scrape_jobgether(context) -> List[Dict[str, str]]:
    """Scrape job listings from JobGether.com using Playwright page selectors"""
    base_url = "https://jobgether.com"
    search_url = f"{base_url}/remote-jobs"
    jobs: List[Dict[str, str]] = []
    try:
        page = await context.new_page()
        await page.goto(search_url)
        await page.wait_for_selector("div.columns-2", timeout=15000)
        await asyncio.sleep(5)  # Wait for dynamic content to load
        job_elements = await page.query_selector_all("div.new-opportunity")
        if not job_elements:
            logger.warning("No job elements found with 'div.new-opportunity' selector on JobGether")
        for job_element in job_elements[:5]:  # Limit to first 5 results
            title_element = await job_element.query_selector("h2, h3")
            title = await title_element.inner_text() if title_element else "N/A"
            company_element = await job_element.query_selector("span.company-name, div.company")
            company = await company_element.inner_text() if company_element else "N/A"
            link_element = await job_element.query_selector("a[href]")
            href = await link_element.get_attribute("href") if link_element else ""
            full_link = urljoin(base_url, href) if href else "N/A"
            jobs.append({
                "Company": company,
                "Role": title,
                "Link": full_link,
                "Tech Stack": "Python, Remote",
                "Type": "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A"
            })
        await page.screenshot(path="jobgether_debug.png", full_page=True)
        await page.close()
        return jobs
    except Exception as e:
        logger.error(f"Error scraping JobGether with Playwright selectors: {str(e)}", exc_info=True)
        return []

def extract_text(element: Tag, tag_names: List[str], class_keywords: List[str]) -> str:
    """Helper to extract text from elements with flexible selectors"""
    for tag in tag_names:
        for keyword in class_keywords:
            # Try exact class match
            found = element.find(tag, class_=keyword)
            if found:
                return found.get_text(strip=True)
            
            # Try partial class match
            found = element.find(tag, class_=lambda x: x and keyword in x.lower())
            if found:
                return found.get_text(strip=True)
    
    # Fallback to any matching tag
    for tag in tag_names:
        found = element.find(tag)
        if found:
            return found.get_text(strip=True)
    
    return ""

from typing import List, Optional
from bs4.element import Tag



from typing import List, Optional
from bs4.element import Tag

async def scrape_ziprecruiter(context) -> List[dict]:
    logger.warning("Skipping scrape_ziprecruiter due to persistent Cloudflare anti-bot protection.")
    return []

from typing import List, Optional
from bs4.element import Tag

async def scrape_turing(context) -> List[dict]:
    logger.warning("Skipping scrape_turing due to persistent Incapsula anti-bot protection.")
    return []

from typing import List, Optional
from bs4.element import Tag

async def scrape_nodesk(context) -> List[dict]:
    url = "https://nodesk.co/remote-jobs/search?term=python"
    jobs: List[dict] = []
    try:
        page = await context.new_page()
        await page.goto(url)
        try:
            # Wait for job list container
            await page.wait_for_selector("ul.list.mv0.pl0 > li", timeout=10000)
        except Exception:
            logger.warning("Job list container not found, falling back to page content parsing.")
            content = await page.content()
            with open("nodesk_debug.html", "w", encoding="utf-8") as f:
                f.write(content)
            await page.screenshot(path="nodesk_debug.png", full_page=True)
            logger.info("Saved fallback page content and screenshot for analysis.")
            soup = BeautifulSoup(content, "html.parser")
            job_items = soup.select("ul.list.mv0.pl0 > li")[:5]
            if not job_items:
                logger.warning("No job items found on nodesk.co with BeautifulSoup fallback.")
                await page.close()
                return []
            for job in job_items:
                title_tag = job.select_one("h2 a, h3 a")
                company_tag = job.select_one("h3, div.company-name")
                link_tag = job.select_one("a[href]")
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                company = company_tag.get_text(strip=True) if company_tag else "N/A"
                link = link_tag.attrs.get("href", "N/A") if link_tag and "href" in link_tag.attrs else "N/A"
                full_link = "https://nodesk.co" + link if link.startswith("/") else link
                jobs.append({
                    "Company": company,
                    "Role": title,
                    "Link": full_link,
                    "Tech Stack": "Python, Remote",
                    "Type": "Remote",
                    "Salary": "N/A",
                    "Contact Person": "N/A",
                    "Email": "N/A"
                })
            await page.close()
            return jobs
        await asyncio.sleep(5)  # Wait for dynamic content to load
        job_items = await page.query_selector_all("ul.list.mv0.pl0 > li")
        if not job_items:
            logger.warning("No job items found on nodesk.co.")
            await page.close()
            return []
        for job in job_items[:5]:  # Limit to first 5 jobs
            title_element = await job.query_selector("h2 a, h3 a")
            company_element = await job.query_selector("h3, div.company-name")
            link_element = await job.query_selector("a[href]")
            title = await title_element.inner_text() if title_element else "N/A"
            company = await company_element.inner_text() if company_element else "N/A"
            href = await link_element.get_attribute("href") if link_element else ""
            full_link = "https://nodesk.co" + href if href.startswith("/") else href
            jobs.append({
                "Company": company,
                "Role": title,
                "Link": full_link,
                "Tech Stack": "Python, Remote",
                "Type": "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A"
            })
        await page.close()
        return jobs
    except Exception as e:
        logger.error(f"Error scraping nodesk.co: {e}")
        return []

from typing import List, Optional
from bs4.element import Tag

async def scrape_arkdev(context) -> List[dict]:
    url = "https://ark.dev/jobs?search=python+remote"
    try:
        content = await get_page_content(url, context)
        soup = BeautifulSoup(content, "html.parser")
        jobs: List[dict] = []
        job_cards = soup.find_all("div", class_="job-card")[:5]
        if not job_cards:
            logger.warning("No jobs found on ark.dev with current selector.")
        for job in job_cards:
            if isinstance(job, Tag):
                title: Optional[Tag] = job.find("h3", class_="job-title")
                company: Optional[Tag] = job.find("div", class_="company-name")
                link_tag: Optional[Tag] = job.find("a", href=True)
                link = link_tag.attrs.get("href", "N/A") if link_tag and "href" in link_tag.attrs else "N/A"
                full_link = "https://ark.dev" + link if link.startswith("/") else link
                jobs.append({
                    "Company": company.get_text(strip=True) if company else "N/A",
                    "Role": title.get_text(strip=True) if title else "N/A",
                    "Link": full_link,
                    "Tech Stack": "Python, Remote",
                    "Type": "Remote",
                    "Salary": "N/A",
                    "Contact Person": "N/A",
                    "Email": "N/A"
                })
        return jobs
    except Exception as e:
        logger.error(f"Error scraping ark.dev: {e}")
        return []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        results = []
        results += await scrape_remoteok(context)
        results += await scrape_weworkremotely(context)
        results += await scrape_linkedin(context)
        results += await scrape_jobgether(context)
        results += await scrape_ziprecruiter(context)
        results += await scrape_turing(context)
        results += await scrape_nodesk(context)
        results += await scrape_arkdev(context)
        await browser.close()
        # Save results to file
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
    asyncio.run(main())
