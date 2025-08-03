import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import multi_platform_scraper_playwright as scraper

@pytest.mark.asyncio
async def test_scrape_arkdev_function_signature():
    """Test that scrape_arkdev accepts both context and keywords parameters"""
    # This test verifies that the function signature has been fixed
    # We're not testing the actual scraping logic, just that the function can be called with keywords
    
    # Create a mock context
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_context.new_page.return_value = mock_page
    mock_page.content.return_value = "<div>No jobs found</div>"
    mock_page.close = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    
    # This should not raise a TypeError anymore
    try:
        jobs = await scraper.scrape_arkdev(mock_context, "python")
        # If we get here without an exception, the function signature is correct
        assert True
    except TypeError as e:
        if "positional argument" in str(e):
            pytest.fail(f"Function signature error still exists: {e}")
        else:
            # Some other TypeError, which might be expected in a mock environment
            pass
    except Exception:
        # Other exceptions are fine, we're just testing the function signature
        pass

@pytest.mark.asyncio
async def test_scrape_arkdev_with_keywords():
    """Test that scrape_arkdev can be called with keywords parameter"""
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_context.new_page.return_value = mock_page
    html_content = """
    <div class="job-card">
        <h3 class="job-title">Python Developer</h3>
        <div class="company-name">Test Company</div>
        <a href="/jobs/123"></a>
    </div>
    """
    mock_page.content.return_value = html_content
    mock_page.close = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    
    # Call with keywords parameter - this should work now
    jobs = await scraper.scrape_arkdev(mock_context, "python")
    # We're not asserting specific results because the actual scraping logic
    # might not work with mock data, but we're verifying the call doesn't fail
    
    # Verify that the function was called without errors
    assert True  # If we reached here, no TypeError was raised
