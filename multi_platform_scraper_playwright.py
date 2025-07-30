import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

async def get_page_content(url, context):
    page = await context.new_page()
    await page.goto(url)
    content = await page.content()
    await page.close()
    return content

async def scrape_remoteok(context):
    url = "https://remoteok.com/remote-dev-jobs"
    content = await get_page_content(url, context)
    soup = BeautifulSoup(content, "html.parser")
    jobs = []
    job_list = soup.find_all("tr", class_="job")[:5]
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
    return jobs

async def scrape_weworkremotely(context):
    url = "https://weworkremotely.com/remote-jobs/search?term=python"
    content = await get_page_content(url, context)
    soup = BeautifulSoup(content, "html.parser")
    jobs = []
    job_sections = soup.find_all("section", class_="jobs")[:1]
    for section in job_sections:
        job_listings = section.find_all("li", class_="feature")[:5]
        for job in job_listings:
            title = job.find("span", attrs={"class": "title"})
            company = job.find("span", attrs={"class": "company"})
            link_tag = job.find("a", href=True)
            jobs.append({
                "Company": company.get_text(strip=True) if company else "N/A",
                "Role": title.get_text(strip=True) if title else "N/A",
                "Link": "https://weworkremotely.com" + link_tag.attrs["href"] if link_tag else "N/A",
                "Tech Stack": "Python, Remote",
                "Type": "Remote",
                "Salary": "N/A",
                "Contact Person": "N/A",
                "Email": "N/A"
            })
    return jobs

async def scrape_linkedin(context):
    import logging
    logger = logging.getLogger("stackscout_web")
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        logger.warning("LinkedIn credentials missing. Skipping LinkedIn scraping.")
        return []
    # Removed logging of LinkedIn email to avoid credential exposure
    page = await context.new_page()
    await page.goto("https://www.linkedin.com/login")
    await page.fill("#username", LINKEDIN_EMAIL)
    await page.fill("#password", LINKEDIN_PASSWORD)
    await page.click("button[type='submit']")
    try:
        # Wait for URL starting with https://www.linkedin.com/feed with 30s timeout
        await page.wait_for_url(lambda url: url.startswith("https://www.linkedin.com/feed"), timeout=30000)
        logger.info("Successfully logged in and navigated to LinkedIn feed.")
    except Exception as e:
        logger.error("Timeout or error waiting for LinkedIn feed URL.")
        # Retry login once
        await page.goto("https://www.linkedin.com/login")
        await page.fill("#username", "")  # Clear field first
        await page.fill("#username", LINKEDIN_EMAIL)
        await page.fill("#password", "")  # Clear field first
        await page.fill("#password", LINKEDIN_PASSWORD)
        await page.click("button[type='submit']")
        try:
            await page.wait_for_url(lambda url: url.startswith("https://www.linkedin.com/feed"), timeout=30000)
            logger.info("Retry successful: logged in and navigated to LinkedIn feed.")
        except Exception:
            logger.error("Retry failed waiting for LinkedIn feed URL.")
            await page.close()
            return []
    # Proceed to jobs page
    await page.goto("https://www.linkedin.com/jobs/search/?keywords=remote%20python%20developer")
    await page.wait_for_selector("div.base-card")
    content = await page.content()
    await page.close()
    soup = BeautifulSoup(content, "html.parser")
    jobs = []
    job_cards = soup.find_all("div", class_="base-card")[:5]
    for job_card in job_cards:
        title = job_card.find("h3")
        company = job_card.find("h4")
        link_tag = job_card.find("a")
        jobs.append({
            "Company": company.get_text(strip=True) if company else "N/A",
            "Role": title.get_text(strip=True) if title else "N/A",
            "Link": link_tag.attrs.get("href", "N/A") if link_tag else "N/A",
            "Tech Stack": "Python, Remote",
            "Type": "Remote",
            "Salary": "N/A",
            "Contact Person": "N/A",
            "Email": "N/A"
        })
    return jobs

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        results = []
        results += await scrape_remoteok(context)
        results += await scrape_weworkremotely(context)
        results += await scrape_linkedin(context)
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
