from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import json
import base64
import pickle
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
        self.cookie_file = Path('src/database/session.enc')
        self.key_file = Path('src/database/key.bin')
        self.driver = None
        self._initialize_browser()
    
    def _initialize_browser(self):
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
                print("Attempting to start Chrome with undetected-chromedriver...")
                self.driver = uc.Chrome(version_main=127, options=options)
                # Load saved cookies after browser is initialized
                if self._load_cookies():
                    print("Loaded saved session...")
            except Exception as e:
                print(f"Falling back to regular ChromeDriver: {str(e)}")
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
    
    def _get_encryption_key(self):
        """Get or create encryption key for cookie storage"""
        if not self.key_file.exists():
            key = get_random_bytes(32)
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
        else:
            with open(self.key_file, 'rb') as f:
                key = f.read()
        return key
    
    def _encrypt_data(self, data):
        """Encrypt data for storage"""
        key = self._get_encryption_key()
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(pickle.dumps(data))
        json_data = {
            'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8')
        }
        return json.dumps(json_data)
    
    def _decrypt_data(self, encrypted_str):
        """Decrypt stored data"""
        try:
            key = self._get_encryption_key()
            json_data = json.loads(encrypted_str)
            nonce = base64.b64decode(json_data['nonce'])
            ciphertext = base64.b64decode(json_data['ciphertext'])
            tag = base64.b64decode(json_data['tag'])
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            data = cipher.decrypt_and_verify(ciphertext, tag)
            return pickle.loads(data)
        except Exception as e:
            print(f"Error decrypting data: {str(e)}")
            return None
    
    def save_cookies(self):
        """Save current session cookies"""
        if not self.driver:
            return
        
        try:
            cookies = self.driver.get_cookies()
            encrypted_data = self._encrypt_data(cookies)
            self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cookie_file, 'w') as f:
                f.write(encrypted_data)
            print("Session saved successfully")
        except Exception as e:
            print(f"Error saving session: {str(e)}")
    
    def _load_cookies(self):
        """Load saved session cookies"""
        if not self.cookie_file.exists() or not self.driver:
            return False
        
        try:
            with open(self.cookie_file, 'r') as f:
                encrypted_data = f.read()
            cookies = self._decrypt_data(encrypted_data)
            if cookies:
                self.driver.get("https://www.linkedin.com")  # Load domain before adding cookies
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"Error adding cookie: {str(e)}")
                return True
        except Exception as e:
            print(f"Error loading session: {str(e)}")
        return False
    
    def navigate(self, url):
        """Safely navigate to a URL"""
        print(f"Navigating to: {url}")
        self.driver.get(url)
        self.random_delay()
    
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
    
    def close(self):
        """Close the browser and save session"""
        if self.driver:
            self.save_cookies()
            try:
                self.driver.quit()
                print("Browser closed successfully")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")
