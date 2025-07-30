import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import multi_platform_scraper as scraper

@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("LINKEDIN_EMAIL", "test@example.com")
    monkeypatch.setenv("LINKEDIN_PASSWORD", "password123")

from unittest.mock import patch

def test_linkedin_credentials_loaded(monkeypatch):
    monkeypatch.setenv("LINKEDIN_EMAIL", "test@example.com")
    monkeypatch.setenv("LINKEDIN_PASSWORD", "password123")
    import os
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    assert isinstance(email, str) and len(email) > 0
    assert isinstance(password, str) and len(password) > 0

def test_scrape_linkedin_with_credentials(monkeypatch, capsys):
    monkeypatch.setenv("LINKEDIN_EMAIL", "test@example.com")
    monkeypatch.setenv("LINKEDIN_PASSWORD", "password123")
    import multi_platform_scraper as scraper
    # Reload environment variables in scraper module
    scraper.LINKEDIN_EMAIL = "test@example.com"
    scraper.LINKEDIN_PASSWORD = "password123"
    driver = MagicMock()
    result = scraper.scrape_linkedin(driver)
    captured = capsys.readouterr()
    assert "Scraping LinkedIn placeholder... (not implemented)" in captured.out
    assert isinstance(result, list)

def test_scrape_linkedin_without_credentials(monkeypatch, capsys):
    monkeypatch.delenv("LINKEDIN_EMAIL", raising=False)
    monkeypatch.delenv("LINKEDIN_PASSWORD", raising=False)
    import multi_platform_scraper as scraper
    scraper.LINKEDIN_EMAIL = None
    scraper.LINKEDIN_PASSWORD = None
    driver = MagicMock()
    result = scraper.scrape_linkedin(driver)
    captured = capsys.readouterr()
    assert "Scraping LinkedIn placeholder... (not implemented)" in captured.out
    assert result == []

def test_scrape_remoteok_success(monkeypatch):
    class MockResponse:
        def __init__(self, status_code=200, text=""):
            self.status_code = status_code
            self.text = text
        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP error")
    def mock_get(*args, **kwargs):
        html = """
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
        return MockResponse(200, html)
    monkeypatch.setattr(scraper.requests, "get", mock_get)
    jobs = scraper.scrape_remoteok()
    assert len(jobs) == 2
    assert jobs[0]["Company"] == "CompanyA"
    assert "Python" in jobs[0]["Tech Stack"]

def test_scrape_remoteok_429(monkeypatch, capsys):
    call_count = {"count": 0}
    def mock_get(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] < 3:
            return type("Resp", (), {"status_code": 429, "raise_for_status": lambda self=None: None, "text": ""})()
        else:
            return type("Resp", (), {"status_code": 200, "raise_for_status": lambda self=None: None, "text": """
            <table>
                <tr class="job" data-position="Dev" data-company="CompanyA" data-href="/job1">
                    <div class="tag">Python</div>
                </tr>
            </table>
            """})()
    monkeypatch.setattr(scraper.requests, "get", mock_get)
    jobs = scraper.scrape_remoteok()
    captured = capsys.readouterr()
    assert "Received 429 Too Many Requests" in captured.out
    assert len(jobs) == 1

def test_scrape_indeed_no_driver():
    jobs = scraper.scrape_indeed(None)
    assert jobs == []

def test_scrape_indeed_captcha_handling(monkeypatch):
    import time
    # Mock driver with page_source containing 'captcha' initially, then cleared after refresh
    class MockDriver:
        def __init__(self):
            self.page_source = "captcha"
            self.refresh_count = 0
        def get(self, url):
            pass
        def refresh(self):
            self.refresh_count += 1
            if self.refresh_count >= 3:
                self.page_source = "jobs list"
    driver = MockDriver()

    # Patch time.sleep to fast-forward time
    monkeypatch.setattr(time, "sleep", lambda x: None)

    # Run scrape_indeed with mocked driver
    jobs = scraper.scrape_indeed(driver)

    # After 3 refreshes, page_source no longer contains captcha, so scraping proceeds
    assert isinstance(jobs, list)

def test_scrape_arc_dev_placeholder(capsys):
    result = scraper.scrape_arc_dev(None)
    captured = capsys.readouterr()
    assert "Scraping Arc.dev" in captured.out
    assert result == []

def test_scrape_linkedin_placeholder_with_credentials(monkeypatch, capsys):
    monkeypatch.setenv("LINKEDIN_EMAIL", "test@example.com")
    monkeypatch.setenv("LINKEDIN_PASSWORD", "password123")
    # Reload environment variables in scraper module
    scraper.LINKEDIN_EMAIL = "test@example.com"
    scraper.LINKEDIN_PASSWORD = "password123"
    result = scraper.scrape_linkedin(None)
    captured = capsys.readouterr()
    assert "Scraping LinkedIn placeholder... (not implemented)" in captured.out
    assert isinstance(result, list)

def test_scrape_linkedin_placeholder_without_credentials(monkeypatch, capsys):
    monkeypatch.delenv("LINKEDIN_EMAIL", raising=False)
    monkeypatch.delenv("LINKEDIN_PASSWORD", raising=False)
    scraper.LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    scraper.LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    result = scraper.scrape_linkedin(None)
    captured = capsys.readouterr()
    assert "Scraping LinkedIn placeholder... (not implemented)" in captured.out
    assert result == []
