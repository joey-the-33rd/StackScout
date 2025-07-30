from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def remote_webdriver_test():
    try:
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
        )
        driver.get("https://www.example.com")
        print(f"Page title: {driver.title}")
        driver.quit()
        print("Remote WebDriver test successful.")
    except Exception as e:
        print(f"Remote WebDriver test failed: {e}")

if __name__ == "__main__":
    remote_webdriver_test()
