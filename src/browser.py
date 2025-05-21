from pathlib import Path
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
import logging
import time
import random
from typing import Optional, Generator, List
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement  # Add this import
from selenium.common.exceptions import TimeoutException, WebDriverException
from contextlib import contextmanager, suppress
import atexit
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException
import openai

# Configure logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)  # Ensure the logs directory exists

log_file = logs_dir / f"job_application_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Write logs to a file
        logging.StreamHandler()         # Also output logs to the console
    ]
)

load_dotenv()

class Browser:
    """Browser automation class with stealth and human-like behavior."""
    
    _instances: List['Browser'] = []
    
    def __init__(self) -> None:
        """Initialize browser with proper logging and error handling."""
        self.logger = logging.getLogger(__name__)
        self.driver: Optional[uc.Chrome] = None
        self._setup_instance()

    def _setup_instance(self) -> None:
        """Setup browser instance and register cleanup."""
        Browser._instances.append(self)
        atexit.register(self._cleanup)
        self._initialize_browser()

    def _initialize_browser(self) -> None:
        """Initialize Chrome browser with stealth settings."""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-logging')
            options.add_argument('--log-level=3')
            
            self.logger.info("Initializing Chrome browser...")
            self.driver = uc.Chrome(
                options=options,
                version_main=None,
                use_subprocess=True,
                suppress_welcome=True
            )
            
            self.wait = WebDriverWait(self.driver, 60)
            self.short_wait = WebDriverWait(self.driver, 10)
            
            self.logger.info("Browser initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Browser initialization failed: {str(e)}")
            self._cleanup()
            raise

    def navigate(self, url: str) -> bool:
        """Navigate to URL with retry logic."""
        try:
            self.logger.info(f"Navigating to {url}")
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))  # Wait for page load
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {str(e)}")
            return False

    def login_linkedin(self) -> bool:
        """Login to LinkedIn with credentials from environment variables."""
        try:
            self.logger.info("Attempting LinkedIn login...")
            
            # Navigate to LinkedIn login page
            self.navigate("https://www.linkedin.com/login")
            
            # Wait for login form
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            
            # Get credentials from environment variables
            email = os.getenv("LINKEDIN_EMAIL")
            password = os.getenv("LINKEDIN_PASSWORD")
            
            if not email or not password:
                self.logger.error("LinkedIn credentials not found in environment variables")
                return False
            
            # Type credentials with human-like behavior
            self._type_like_human(email_field, email)
            time.sleep(random.uniform(0.5, 1.5))
            self._type_like_human(password_field, password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click sign in
            password_field.send_keys(Keys.RETURN)
            
            # Wait for successful login
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".global-nav"))
                )
                self.logger.info("LinkedIn login successful")
                return True
            except TimeoutException:
                self.logger.error("Login verification failed - possible CAPTCHA or security check")
                return False
                
        except Exception as e:
            self.logger.error(f"LinkedIn login failed: {str(e)}")
            return False

    def search_jobs(self, title: str, location: str = "Remote") -> bool:
        """Search for jobs and load job cards."""
        try:
            self.logger.info(f"Searching for {title} jobs in {location}")
            
            # Wait for the search interface to load
            time.sleep(3)
            
            # Find and fill the job title input
            title_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.jobs-search-box__text-input[id*='jobs-search-box-keyword']"))
            )
            self.logger.info("Found job title input field")
            title_input.clear()
            title_input.send_keys(title)
            time.sleep(1)
            
            # Find and fill the location input
            location_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.jobs-search-box__text-input[id*='jobs-search-box-location']"))
            )
            self.logger.info("Found location input field")
            location_input.clear()
            location_input.send_keys(location)
            time.sleep(1)
            
            # Submit the search
            location_input.send_keys(Keys.RETURN)
            self.logger.info("Search submitted")
            time.sleep(3)
            
            # Wait for search results to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
            self.logger.info("Search results loaded")
            
            # Verify job cards are present
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")
            if job_cards:
                self.logger.info(f"Found {len(job_cards)} job cards")
                return True
            else:
                self.logger.error("No job cards found")
                return False
                
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return False

    def _check_search_results(self) -> bool:
        """Check if search results are present."""
        try:
            return bool(self.short_wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            ))
        except:
            return False

    def _verify_and_filter_results(self) -> bool:
        """Verify search results and apply Easy Apply filter."""
        try:
            # Wait for search results
            jobs_list = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
            
            # Click Easy Apply filter if available
            try:
                filters = self.wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button.search-reusables__filter-binary-toggle"))
                )
                for filter_btn in filters:
                    if "Easy Apply" in filter_btn.text:
                        filter_btn.click()
                        time.sleep(2)
                        break
            except:
                self.logger.warning("Could not find Easy Apply filter")
            
            # Verify results exist
            return bool(jobs_list.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item"))
            
        except Exception as e:
            self.logger.error(f"Failed to verify search results: {str(e)}")
            return False

    def _type_like_human(self, element: WebElement, text: str) -> None:
        """Type text with random delays between keystrokes."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

    def _cleanup(self) -> None:
        """Clean up browser resources safely."""
        if self.driver:
            try:
                driver = self.driver
                self.driver = None
                
                with suppress(Exception):
                    for handle in driver.window_handles[:]:
                        with suppress(Exception):
                            driver.switch_to.window(handle)
                            driver.close()
                
                with suppress(Exception):
                    driver.quit()
                
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Browser cleanup error: {str(e)}")

    @classmethod
    def cleanup_all(cls) -> None:
        """Clean up all browser instances."""
        for instance in cls._instances[:]:
            with suppress(Exception):
                instance._cleanup()
        cls._instances.clear()

    def close(self) -> None:
        """Public method to safely close the browser."""
        self._cleanup()
        if self in Browser._instances:
            Browser._instances.remove(self)

    @contextmanager
    def suppress_quit_warning(self) -> Generator[None, None, None]:
        """Context manager to suppress quit warnings."""
        with suppress(Exception) as exc_info:
            yield
            if exc_info is not None and "invalid handle" not in str(exc_info.value):
                self.logger.error(f"Browser error: {str(exc_info.value)}")
                raise

    def get_job_listings(self, limit: int = 5) -> List[dict]:
        """Extract job listings from current search results."""
        try:
            jobs = []
            job_cards = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".jobs-search-results__list-item")
                )
            )
            
            for card in job_cards[:limit]:
                try:
                    # Click the card to load details
                    card.click()
                    time.sleep(random.uniform(1.5, 2.5))
                    
                    # Extract job information
                    job_info = {
                        'title': self._get_text(".jobs-unified-top-card__job-title"),
                        'company': self._get_text(".jobs-unified-top-card__company-name"),
                        'location': self._get_text(".jobs-unified-top-card__workplace-type"),
                        'description': self._get_text(".jobs-description__content"),
                        'url': self.driver.current_url
                    }
                    
                    jobs.append(job_info)
                    self.logger.info(f"Extracted job: {job_info['title']} at {job_info['company']}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to extract job details: {str(e)}")
                    continue
                    
            return jobs
            
        except Exception as e:
            self.logger.error(f"Failed to get job listings: {str(e)}")
            return []

    def _get_text(self, selector: str) -> str:
        """Helper method to safely get text content."""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text.strip()
        except:
            return ""

    def get_recent_jobs(self, limit: int = 5) -> List[dict]:
        """Get recent Easy Apply jobs from search results."""
        try:
            self.logger.info("Getting recent Easy Apply jobs...")
            jobs = []
            
            # Wait for job list to load
            job_list = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
            
            # Get all job cards
            job_cards = job_list.find_elements(By.CSS_SELECTOR, ".jobs-search-results__list-item")
            self.logger.info(f"Found {len(job_cards)} total job cards")
            
            processed = 0
            for card in job_cards:
                if processed >= limit:
                    break
                    
                try:
                    # Scroll card into view
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                        card
                    )
                    time.sleep(1)
                    
                    # Click the card
                    card.click()
                    time.sleep(2)
                    
                    # Check for Easy Apply button
                    try:
                        easy_apply_button = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 
                                "button.jobs-apply-button[aria-label*='Easy Apply']"))
                        )
                        
                        if "Easy Apply" in easy_apply_button.text:
                            job_info = {
                                'title': self._get_text(".jobs-unified-top-card__job-title"),
                                'company': self._get_text(".jobs-unified-top-card__company-name"),
                                'location': self._get_text(".jobs-unified-top-card__workplace-type"),
                                'element': card,
                                'apply_button': easy_apply_button
                            }
                            jobs.append(job_info)
                            processed += 1
                            self.logger.info(f"Found Easy Apply job: {job_info['title']}")
                            
                    except TimeoutException:
                        self.logger.warning("Easy Apply button not found for this job")
                        continue
                        
                except Exception as e:
                    self.logger.error(f"Failed to process job card: {str(e)}")
                    continue
                
            return jobs
            
        except Exception as e:
            self.logger.error(f"Failed to get job listings: {str(e)}")
            return []

    def apply_to_job(self, job: dict) -> bool:
        """Apply to a job using Easy Apply."""
        try:
            self.logger.info(f"Applying to: {job['title']} at {job['company']}")
            
            # Click the job card to ensure it's active
            if 'element' in job:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                    job['element']
                )
                time.sleep(1)
                job['element'].click()
                time.sleep(2)
        
            # Click the Easy Apply button
            apply_button = job.get('apply_button')
            if not apply_button:
                self.logger.error("Easy Apply button not found")
                return False
            
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                apply_button
            )
            time.sleep(1)
            try:
                apply_button.click()
            except Exception as e:
                self.logger.warning(f"Failed to click Easy Apply button normally: {str(e)}")
                self.driver.execute_script("arguments[0].click();", apply_button)
        
            self.logger.info("Clicked Easy Apply button")
            time.sleep(2)
            
            # Complete the application flow
            return self._complete_application_flow()
        
        except Exception as e:
            self.logger.error(f"Failed to start application: {str(e)}")
            return False

    def _complete_application_flow(self) -> bool:
        """Complete the multi-step application process."""
        try:
            step_count = 0
            max_steps = 10

            while step_count < max_steps:
                try:
                    # Wait for the application modal
                    modal = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-easy-apply-modal"))
                    )
                except TimeoutException:
                    self.logger.error("Application modal not found")
                    return False

                # Check for success message
                if self._check_success_message():
                    self.logger.info("Application submitted successfully")
                    return True

                # Find the next/submit button
                button = None
                button_selectors = [
                    "button[aria-label*='Submit application']",
                    "button[aria-label*='Next']",
                    "button[aria-label*='Review']",
                    "footer button"
                ]

                for selector in button_selectors:
                    try:
                        buttons = modal.find_elements(By.CSS_SELECTOR, selector)
                        for btn in buttons:
                            if btn.is_displayed() and any(text in btn.text.lower()
                               for text in ['submit', 'next', 'review', 'apply']):
                                button = btn
                                break
                        if button:
                            break
                    except Exception:
                        continue

                if not button:
                    self.logger.error("No next/submit button found")
                    return False

                # Click the button
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    button
                )
                time.sleep(1)

                try:
                    button.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", button)

                time.sleep(2)
                step_count += 1

            return False

        except Exception as e:
            self.logger.error(f"Application flow failed: {str(e)}")
            return False

    def _check_success_message(self) -> bool:
        """Check for application success message."""
        try:
            success_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                ".artdeco-toast-item--success, .artdeco-inline-feedback--success"
            )
            
            for element in success_elements:
                if any(msg in element.text.lower() for msg in 
                       ['application submitted', 'applied', 'success']):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking success message: {str(e)}")
            return False

    def get_posted_date(self, selector: str) -> str:
        """Extract and return the posted date of the job."""
        try:
            date_text = self._get_text(selector)
            if not date_text:
                return ""
            
            # Parse and return the date
            return self._parse_date(date_text)
            
        except Exception as e:
            self.logger.error(f"Failed to get posted date: {str(e)}")
            return ""

    def _parse_date(self, date_text: str) -> str:
        """Parse the date text and return a standardized date string."""
        try:
            # Example parsing logic (to be customized)
            date_format = "%B %d, %Y"  # Example: January 1, 2022
            parsed_date = datetime.strptime(date_text, date_format)
            return parsed_date.strftime("%Y-%m-%d")
            
        except Exception as e:
            self.logger.error(f"Date parsing error: {str(e)}")
            return ""

    def _is_within_timeframe(self, date_str: str, days: int) -> bool:
        """Check if the given date is within the specified timeframe."""
        try:
            if not date_str:
                return False
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            cutoff_date = datetime.now() - timedelta(days=days)
            return date_obj >= cutoff_date
            
        except Exception as e:
            self.logger.error(f"Timeframe check error: {str(e)}")
            return False

