import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
import time
import random
import os
from config import Config

class Browser:
    def __init__(self):
        try:
            print("Initializing Chrome browser...")
            options = uc.ChromeOptions()
            if Config.HEADLESS_MODE:
                options.add_argument('--headless')
            if Config.STEALTH_MODE:
                options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Add additional options for stability
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            try:
                # Try undetected-chromedriver first
                print("Attempting to start Chrome with undetected-chromedriver...")
                self.driver = uc.Chrome(version_main=127, options=options)
            except Exception as e:
                print(f"Falling back to regular ChromeDriver: {str(e)}")
                # Fallback to regular ChromeDriver with webdriver-manager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            print("Chrome started successfully")
            # Increase the default wait timeout to 60 seconds
            self.wait = WebDriverWait(self.driver, 60)
            # Also create a shorter wait for regular operations
            self.short_wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            print(f"Error initializing Chrome: {str(e)}")
            raise
    
    def random_delay(self):
        """Add random delay between actions to mimic human behavior"""
        time.sleep(random.uniform(Config.MIN_DELAY, Config.MAX_DELAY))
    
    def safe_click(self, element):
        """Safely click an element with random delay"""
        self.random_delay()
        try:
            element.click()
        except:
            # Fallback to PyAutoGUI if Selenium click fails
            bounds = element.rect
            pyautogui.click(bounds['x'] + bounds['width']/2, 
                          bounds['y'] + bounds['height']/2)
    
    def navigate(self, url):
        """Safely navigate to a URL"""
        print(f"Navigating to: {url}")
        self.driver.get(url)
        self.random_delay()
    
    def wait_for_user_input(self, message: str, timeout: int = 120):
        """Wait for user to complete an action"""
        print(f"\n{message}")
        print(f"You have {timeout} seconds to complete this action...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(1)
            remaining = int(timeout - (time.time() - start_time))
            if remaining % 10 == 0:  # Print remaining time every 10 seconds
                print(f"{remaining} seconds remaining...")
        print("Timeout completed, continuing...")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            print("Closing Chrome browser...")
            try:
                self.driver.quit()
                print("Browser closed successfully")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")
