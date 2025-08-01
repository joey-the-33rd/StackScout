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

@pytest.mark.asyncio
async def test_scrape_weworkremotely():
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_context.new_page.return_value = mock_page
    html_content = """
    <section class="jobs">
        <li class="feature">
            <span class="title">Developer</span>
            <span class="company">CompanyX</span>
            <a href="/job1"></a>
        </li>
        <li class="feature">
            <span class="title">Engineer</span>
            <span class="company">CompanyY</span>
            <a href="/job2"></a>
        </li>
    </section>
    """
    mock_page.content.return_value = html_content
    mock_page.close = AsyncMock()

    jobs = await scraper.scrape_weworkremotely(mock_context)
    assert len(jobs) == 2
    assert jobs[0]["Company"] == "CompanyX"
    assert jobs[0]["Role"] == "Developer"
    mock_page.close.assert_awaited_once()

@pytest.mark.asyncio
@patch("multi_platform_scraper_playwright.LINKEDIN_EMAIL", "test@example.com")
@patch("multi_platform_scraper_playwright.LINKEDIN_PASSWORD", "password123")
async def test_scrape_linkedin_success(monkeypatch):
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_context.new_page.return_value = mock_page

    # Mock page methods
    mock_page.goto = AsyncMock()
    mock_page.fill = AsyncMock()
    mock_page.click = AsyncMock()
    mock_page.wait_for_url = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()
    mock_page.content.return_value = """
    <div class="base-card">
        <h3>Python Developer</h3>
        <h4>CompanyZ</h4>
        <a href="https://linkedin.com/job1"></a>
    </div>
    """
    mock_page.close = AsyncMock()

    jobs = await scraper.scrape_linkedin(mock_context)
    assert len(jobs) == 1
    assert jobs[0]["Company"] == "CompanyZ"
    assert jobs[0]["Role"] == "Python Developer"
    mock_page.close.assert_awaited_once()

@pytest.mark.asyncio
@patch("multi_platform_scraper_playwright.LINKEDIN_EMAIL", None)
@patch("multi_platform_scraper_playwright.LINKEDIN_PASSWORD", None)
async def test_scrape_linkedin_no_credentials():
    mock_context = AsyncMock()
    jobs = await scraper.scrape_linkedin(mock_context)
    assert jobs == []
