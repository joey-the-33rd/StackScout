from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

def test_geckodriver():
    options = Options()
    options.add_argument("--headless")
    # Specify the path to geckodriver executable
    service = Service('/usr/local/bin/geckodriver')
    try:
        driver = webdriver.Firefox(service=service, options=options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        print(f"GeckoDriver test successful, page title: {title}")
    except Exception as e:
        print(f"GeckoDriver test failed: {e}")

if __name__ == "__main__":
    test_geckodriver()

# Note:
# To install geckodriver on macOS, you can use Homebrew:
#   brew install geckodriver
# Make sure the geckodriver executable is in the specified path or update the path accordingly.
# Run this script with: python geckodriver_test.py
