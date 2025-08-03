import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import multi_platform_scraper_playwright as scraper

@pytest.mark.asyncio
async def test_scrape_remoteok():
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_context.new_page.return_value = mock_page
    html_content = """
    <table>
        <tr class="job" data-position="Dev" data-company="CompanyA" data-href="/job1">
            <div class="tag">Python</div>
            <div class="tag">Django</div>
        </tr>
        <tr class="job" data-position="Engineer" data-company="CompanyB" data-href="/job2">
            <div class="tag">JavaScript</div>
            <div class="tag">React</div>
        </tr>
    </table>
    """
    mock_page.content.return_value = html_content
    mock_page.close = AsyncMock()

    jobs = await scraper.scrape_remoteok(mock_context)
    assert len(jobs) == 2
    assert jobs[0]["Company"] == "CompanyA"
    assert "Python" in jobs[0]["Tech Stack"]
    mock_page.close.assert_awaited_once()

