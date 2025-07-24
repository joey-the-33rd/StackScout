from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def test_chromedriver():
    options = Options()
    options.add_argument("--headless=new")
    service = Service('/usr/local/bin/chromedriver')
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        print(f"ChromeDriver test successful, page title: {title}")
    except Exception as e:
        print(f"ChromeDriver test failed: {e}")

if __name__ == "__main__":
    test_chromedriver()
