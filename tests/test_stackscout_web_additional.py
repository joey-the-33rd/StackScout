import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import stackscout_web
from selenium.common.exceptions import TimeoutException

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    return driver

def test_google_jobs_scraping_retries(mock_driver):
    # Patch WebDriverWait to raise TimeoutException twice then succeed
    wait_calls = []

    class MockWait:
        def __init__(self, driver, timeout):
            pass
        def until(self, method):
            wait_calls.append(1)
            if len(wait_calls) < 3:
                raise TimeoutException("Timeout")
            return True

    with patch('stackscout_web.WebDriverWait', MockWait), \
         patch('stackscout_web.get_driver', return_value=mock_driver):
        mock_driver.page_source = '''
        <div jscontroller="test">
            <div role="heading">Test Job</div>
            <a href="http://example.com/job1">Link</a>
        </div>
        '''
        results = stackscout_web.run_scraper(email=None, password=None)
        # Google Jobs scraping should succeed after retries
        google_jobs = [job for job in results if job["Company"] == "Unknown (Google Jobs)"]
        assert len(google_jobs) > 0
        assert google_jobs[0]["Role"] == "Test Job"

def test_linkedin_login_retry_success(mock_driver):
    # This test is replaced by direct testing of login_linkedin retry logic
    pass

def test_login_linkedin_retry_logic():
    driver = MagicMock()
    call_count = {"count": 0}

    def side_effect_get(url):
        call_count["count"] += 1
        return None

    driver.get = side_effect_get
    driver.find_element.return_value = MagicMock()

    # Change current_url dynamically based on call_count
    def current_url_side_effect(self):
        if call_count["count"] < 3:
            return "https://www.linkedin.com/login"
        else:
            return "https://www.linkedin.com/feed"

    type(driver).current_url = property(current_url_side_effect)

    # Simulate captcha detection on first two attempts, success on third
    def side_effect_find_elements(by, value):
        if call_count["count"] < 3:
            return [MagicMock()]  # captcha detected
        else:
            return []

    driver.find_elements.side_effect = side_effect_find_elements

    with patch('time.sleep', return_value=None):
        result = stackscout_web.login_linkedin(driver, "email", "password")
        assert result is True
        assert call_count["count"] == 3

def test_indeed_scraping_error_handling(mock_driver):
    # Patch WebDriverWait.until to raise TimeoutException to simulate slow page load
    class MockWait:
        def __init__(self, driver, timeout):
            pass
        def until(self, method):
            raise TimeoutException("Timeout")

    with patch('stackscout_web.WebDriverWait', MockWait):
        mock_driver.page_source = '''
        <div class="job_seen_beacon">
            <h2>Test Job</h2>
            <span class="companyName">Test Company</span>
            <a href="/job1">Link</a>
        </div>
        '''
        # The scrape_indeed function should return empty list on timeout
        jobs = stackscout_web.scrape_indeed(mock_driver)
        assert jobs == []
