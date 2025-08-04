import asyncio
from playwright.async_api import async_playwright
import multi_platform_scraper_playwright as scraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_arkdev_simple():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        logger.info("Testing scrape_arkdev...")
        jobs = await scraper.scrape_arkdev(context)
        logger.info(f"Found {len(jobs)} jobs")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_arkdev_simple())
