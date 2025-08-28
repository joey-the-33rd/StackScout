import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_arkdev():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, timeout=10000)
        context = await browser.new_context()
        page = await context.new_page()
        
        logger.info("Navigating to ark.dev...")
        await page.goto("https://ark.dev", timeout=10000)
        
        # Wait for page to load
        await page.wait_for_timeout(5000)
        
        # Take a screenshot
        await page.screenshot(path="arkdev_actual.png", full_page=True)
        logger.info("Screenshot saved as arkdev_actual.png")
        
        # Get page content
        content = await page.content()
        
        # Save HTML content
        with open("arkdev_actual.html", "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("HTML content saved as arkdev_actual.html")
        
        # Try to find job elements
        try:
            await page.wait_for_selector("div.job-card, div.job-listing, article", timeout=10000)
            logger.info("Found job elements with selectors: div.job-card, div.job-listing, article")
        except Exception as e:
            logger.error(f"Timeout waiting for job elements: {e}")
            
            # Try to find any elements that might be job-related
            elements = await page.query_selector_all("div, article, section")
            logger.info(f"Found {len(elements)} div/article/section elements")
            
            # Check first few elements
            for i, elem in enumerate(elements[:10]):
                tag_name = await elem.evaluate("el => el.tagName")
                class_name = await elem.evaluate("el => el.className") or ""
                logger.info(f"Element {i}: {tag_name} with class: {class_name}")
        
        await page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_arkdev())
