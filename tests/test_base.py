import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# URL where the Flet app runs (ensure it's running before testing)
FLET_APP_URL = "http://localhost:5000"

@pytest.fixture(scope="module")
def driver():
    """Set up Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run browser in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(FLET_APP_URL)
    time.sleep(2)  # Allow time for the app to load
    yield driver
    driver.quit()

def test_toolbar_exists(driver):
    """Check if the toolbar is present."""
    toolbar = driver.find_element(By.XPATH, "//div[contains(text(),'TOOLBAR')]")
    assert toolbar is not None, "Toolbar not found!"

def test_tabs_exist(driver):
    """Check if tabs are rendered."""
    tab_1 = driver.find_element(By.XPATH, "//div[contains(text(),'1')]")
    tab_2 = driver.find_element(By.XPATH, "//div[contains(text(),'2')]")
    assert tab_1 is not None, "Tab 1 not found!"
    assert tab_2 is not None, "Tab 2 not found!"

def test_tab_click(driver):
    """Check if clicking tabs changes the selection."""
    tab_2 = driver.find_element(By.XPATH, "//div[contains(text(),'2')]")
    tab_2.click()
    time.sleep(1)
    # Verify tab 2 is selected (customize based on UI feedback)
    selected_tab = driver.find_element(By.XPATH, "//div[contains(text(),'2') and @class='selected']")
    assert selected_tab is not None, "Tab 2 is not selected after click!"
