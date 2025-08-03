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

async def scrape_remoteok(context, keywords: str = "python") -> List[dict]:
    url = f"https://remoteok.com/remote-dev-jobs?search={keywords}"
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
                # Add keywords to tech stack if not already present
                tech_stack_tags = [tag for tag in tags]
                if keywords and keywords not in ", ".join(tech_stack_tags).lower():
                    tech_stack_tags.append(keywords)
                jobs.append({
                    "Company": company,
                    "Role": title,
                    "Tech Stack": ", ".join(tech_stack_tags),
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

async def scrape_jobgether(context, keywords: str = "python") -> List[Dict[str, str]]:
    """Scrape job listings from JobGether.com using Playwright page selectors"""
    base_url = "https://jobgether.com"
    search_url = f"{base_url}/remote-jobs?search={keywords}"
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
                "Tech Stack": keywords,
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

async def scrape_nodesk(context, keywords: str = "python") -> List[dict]:
    """Scrape jobs from NoDesk with improved data extraction"""
    url = f"https://nodesk.co/remote-jobs/search?term={keywords}"
    jobs: List[dict] = []
    try:
        page = await context.new_page()
        # Set a user agent to avoid bot detection
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        await page.goto(url)
        
        # Wait for job listings to load
        await page.wait_for_selector("ul.list.mv0.pl0 > li, .job-item, .job-card", timeout=15000)
        await asyncio.sleep(3)  # Wait a bit more for dynamic content
        
        # Get page content
        content = await page.content()
        await page.close()
        
        soup = BeautifulSoup(content, "html.parser")
        jobs_list: List[dict] = []
        
        # Try multiple selectors for job items
        job_selectors = [
            "ul.list.mv0.pl0 > li",
            ".job-item",
            ".job-card",
            "article.job",
            "div.job-listing",
            "li.job"
        ]
        
        job_items = []
        for selector in job_selectors:
            job_items = soup.select(selector)
            if job_items:
                logger.info(f"Found {len(job_items)} job items with selector: {selector}")
                break
        
        if not job_items:
            logger.warning("No job items found on nodesk.co with any selector.")
            return []
        
        # Process each job item
        for job in job_items[:10]:  # Process up to 10 jobs
            try:
                # Extract title with multiple fallbacks
                title = "N/A"
                title_selectors = [
                    "h2 a", "h3 a", "h2", "h3", 
                    ".job-title", "[data-title]", 
                    ".position", ".role", "a.job-link"
                ]
                
                for selector in title_selectors:
                    title_elem = job.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        if title:
                            break
                
                # If still no title, try getting text from the job element itself
                if title == "N/A":
                    title = job.get_text(strip=True)[:100]  # Limit to 100 chars
                    if not title:
                        title = "N/A"
                
                # Extract company with multiple fallbacks
                company = "N/A"
                company_selectors = [
                    ".company", ".company-name", 
                    "[data-company]", ".employer",
                    "span.company", "div.company"
                ]
                
                for selector in company_selectors:
                    company_elem = job.select_one(selector)
                    if company_elem:
                        company_text = company_elem.get_text(strip=True)
                        if company_text and company_text != title:
                            company = company_text
                            break
                
                # Extract link
                link = "N/A"
                link_selectors = [
                    "a[href]", "h2 a", "h3 a", "a.job-link"
                ]
                
                for selector in link_selectors:
                    link_elem = job.select_one(selector)
                    if link_elem and link_elem.get("href"):
                        href = link_elem["href"]
                        if href.startswith("http"):
                            link = href
                        elif href.startswith("/"):
                            link = "https://nodesk.co" + href
                        else:
                            link = "https://nodesk.co/" + href
                        break
                
                # Extract tech stack/tags
                tech_stack = keywords  # Default to keywords
                tag_selectors = [
                    ".tags", ".tag", ".skills", 
                    "[data-tags]", "[data-skills]",
                    ".job-tags", ".keyword"
                ]
                
                for selector in tag_selectors:
                    tag_elements = job.select(selector)
                    if tag_elements:
                        # Extract text from all tag elements
                        tags = []
                        for tag_elem in tag_elements:
                            tag_text = tag_elem.get_text(strip=True)
                            if tag_text:
                                tags.append(tag_text)
                        if tags:
                            tech_stack = ", ".join(tags)
                            break
                
                # If no tags found, try to extract from job description or other text
                if tech_stack == keywords:
                    # Look for common tech terms in the job element text
                    job_text = job.get_text(strip=True).lower()
                    common_tech_terms = [
                        "python", "javascript", "react", "node", "java", "c++", 
                        "c#", "ruby", "php", "swift", "kotlin", "go", "rust",
                        "docker", "kubernetes", "aws", "azure", "gcp", "sql",
                        "mongodb", "postgresql", "mysql", "redis", "graphql",
                        "django", "flask", "fastapi", "spring", "express"
                    ]
                    found_terms = [term for term in common_tech_terms if term in job_text]
                    if found_terms:
                        tech_stack = ", ".join(found_terms)
                    elif keywords:
                        tech_stack = keywords
                
                # Only add job if we have at least a title or company
                if title != "N/A" or company != "N/A":
                    jobs_list.append({
                        "Company": company,
                        "Role": title,
                        "Link": link,
                        "Tech Stack": tech_stack,
                        "Type": "Remote",
                        "Salary": "N/A",
                        "Contact Person": "N/A",
                        "Email": "N/A"
                    })
            except Exception as job_error:
                logger.warning(f"Error processing individual job item: {job_error}")
                continue
        
        logger.info(f"Successfully extracted {len(jobs_list)} jobs from NoDesk")
        return jobs_list[:5]  # Return only first 5 jobs
        
    except Exception as e:
        logger.error(f"Error scraping nodesk.co: {e}")
        return []

from typing import List, Optional
from bs4.element import Tag

async def scrape_arkdev(context, keywords: str = "python") -> List[dict]:
    """Scrape jobs from ArkDev - updated to handle website structure changes"""
    # Note: ArkDev doesn't appear to have search functionality, so keywords are not used in URL
    url = "https://ark.dev/jobs"
    try:
        # Use Playwright to get the page content (better for dynamic content)
        page = await context.new_page()
        await page.goto(url)
        # Wait for job listings to load
        await page.wait_for_selector("div.job-card, div.job-listing, article", timeout=10000)
        content = await page.content()
        await page.close()
        
        soup = BeautifulSoup(content, "html.parser")
        jobs: List[dict] = []
        
        # Try multiple selectors to find job cards
        job_cards = (
            soup.find_all("div", class_="job-card") or
            soup.find_all("div", class_="job-listing") or
            soup.find_all("article") or
            soup.find_all("div", class_="job")
        )[:5]
        
        if not job_cards:
            logger.warning("No jobs found on ark.dev with current selectors.")
            # Try a more general approach
            job_cards = soup.find_all("a", href=lambda x: x and "/jobs/" in x)[:5]
            
        if not job_cards:
            logger.warning("No jobs found on ark.dev with fallback selectors.")
            return []
            
        for job in job_cards:
            if isinstance(job, Tag):
                # Extract title
                title = None
                title_selectors = [
                    "h3.job-title", "h2.job-title", "h3", "h2", 
                    ".job-title", "[data-job-title]", "h1"
                ]
                for selector in title_selectors:
                    title_elem = job.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                # Extract company
                company = None
                company_selectors = [
                    "div.company-name", ".company", "[data-company]", 
                    "span.company", "div.employer"
                ]
                for selector in company_selectors:
                    company_elem = job.select_one(selector)
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                        break
                
                # Extract link
                link = "N/A"
                link_tag = job.find("a", href=True)
                if not link_tag:
                    # If job element itself is a link
                    if job.name == "a" and job.get("href"):
                        link_tag = job
                    # Or look for any link in the job element
                    else:
                        link_tag = job.find("a")
                
                if link_tag and link_tag.get("href"):
                    href = link_tag.get("href")
                    if href.startswith("http"):
                        link = href
                    elif href.startswith("/"):
                        link = "https://ark.dev" + href
                    else:
                        link = "https://ark.dev/" + href
                
                jobs.append({
                    "Company": company or "N/A",
                    "Role": title or "N/A",
                    "Link": link,
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
        results += await scrape_jobgether(context)
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
