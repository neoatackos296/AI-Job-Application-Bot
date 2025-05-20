from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time

from browser import Browser
from models import Job, SessionLocal
from ai_service import AIService
from config import Config

class JobBot:
    def __init__(self):
        self.browser = Browser()
        self.ai_service = AIService()
        self.db = SessionLocal()
        self._ensure_logged_in()
    
    def _ensure_logged_in(self):
        """Ensure user is logged into LinkedIn"""
        try:
            # First try to access jobs page to check if already logged in
            print("\nChecking LinkedIn login status...")
            self.browser.navigate("https://www.linkedin.com/jobs/")
            
            try:
                # Check if we can find the jobs-search box (indicates we're logged in)
                self.browser.short_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-box"))
                )
                print("Already logged into LinkedIn!")
                return
            except Exception:
                print("Not logged in, starting login process...")
            
            # If not logged in, proceed with login
            self.browser.navigate("https://www.linkedin.com/login")
            self.browser.random_delay()
            
            # Fill in email
            print("Entering email...")
            email_input = self.browser.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.send_keys(os.getenv('LINKEDIN_EMAIL'))
            
            # Fill in password
            print("Entering password...")
            password_input = self.browser.driver.find_element(By.ID, "password")
            password_input.send_keys(os.getenv('LINKEDIN_PASSWORD'))
            
            # Click login button
            print("Clicking login button...")
            login_button = self.browser.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.browser.safe_click(login_button)
              # Check if verification is needed
            # First wait a short time to see if the jobs-search box appears (indicating successful login)
            try:
                self.browser.short_wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-box"))
                )
                print("Login successful without verification!")
                return
            except Exception:
                pass

            # Check for different types of verification
            verification_selectors = [
                "input[name='pin']",  # PIN input
                "input[name='verification']",  # Code input
                "#input__email_verification_pin",  # Email verification
                "#email-pin-input" # Alternative email pin input
            ]
            
            for selector in verification_selectors:
                try:
                    # Look for verification field with a very short timeout
                    self.browser.driver.find_element(By.CSS_SELECTOR, selector)
                    # If we find any verification input, handle verification process
                    print("\n=== VERIFICATION CODE REQUIRED ===")
                    print("1. Check your email/phone for the verification code")
                    print("2. Enter the code in the browser window")
                    print("3. Complete any additional security checks")
                    print("4. Click any 'Submit' or 'Verify' buttons")
                    
                    # Give user 2 minutes to complete verification
                    self.browser.wait_for_user_input("Please complete the verification process...", timeout=120)
                    
                    # After verification, check if we're successfully logged in
                    try:
                        self.browser.navigate("https://www.linkedin.com/jobs/")
                        self.browser.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search-box"))
                        )
                        print("Verification completed successfully!")
                        return
                    except Exception:
                        print("Login still not successful after verification. Continuing with retry logic...")
                    break  # Exit the loop if we found and handled any verification field
                except Exception:
                    continue  # Try next selector if this one wasn't found
            
            print("No verification prompts detected, continuing with login check...")
              # Wait for successful login with improved retry logic
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # First check if we're already on the jobs page
                    current_url = self.browser.driver.current_url
                    if "linkedin.com/jobs" not in current_url:
                        print(f"Navigating to jobs page (attempt {retry_count + 1})")
                        self.browser.navigate("https://www.linkedin.com/jobs/")
                    
                    # Try to find common elements that indicate successful login
                    login_indicators = [
                        ".jobs-search-box",  # Jobs search box
                        ".global-nav",  # Global navigation bar
                        ".search-global-typeahead"  # Global search bar
                    ]
                    
                    for indicator in login_indicators:
                        try:
                            self.browser.short_wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                            )
                            print(f"\nSuccessfully logged into LinkedIn! (Found indicator: {indicator})")
                            return
                        except Exception:
                            continue
                    
                    # If we get here, none of the indicators were found
                    raise Exception("No login indicators found")
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Login check attempt {retry_count} failed: {str(e)}")
                        print(f"Waiting {5 * retry_count} seconds before retry...")
                        time.sleep(5 * retry_count)  # Increase wait time with each retry
                    else:
                        print("\nCould not verify successful login after multiple attempts.")
                        print("Please check:")
                        print("1. Your LinkedIn credentials")
                        print("2. Your internet connection")
                        print("3. If LinkedIn's website is accessible")
                        print("4. If there are any security challenges pending")
                        raise Exception("Login verification failed after maximum retries")
            
        except Exception as e:
            print(f"Error during LinkedIn login process: {str(e)}")
            raise

    def search_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Search for jobs matching keywords and locations"""
        jobs = []
        total_jobs = 0
        
        for keyword in keywords:
            for location in locations:
                try:
                    # Format URL for LinkedIn search
                    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}"
                    print(f"\nSearching: {keyword} in {location}")
                    self.browser.navigate(search_url)
                    self.browser.random_delay()
                    
                    # Wait for job listings to load
                    print("Waiting for job listings to load...")
                    self.browser.wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "jobs-search__results-list"))
                    )
                    
                    # Scroll to load more jobs
                    print("Loading more jobs...")
                    for _ in range(3):  # Scroll 3 times to load more jobs
                        self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                    
                    # Extract job listings
                    print("Extracting job listings...")
                    job_cards = self.browser.driver.find_elements(By.CLASS_NAME, "job-card-container")
                    
                    for card in job_cards:
                        try:
                            # Updated selectors for latest LinkedIn UI
                            title = card.find_element(By.CSS_SELECTOR, "h3.job-card-list__title").text.strip()
                            company = card.find_element(By.CSS_SELECTOR, "h4.job-card-container__company-name").text.strip()
                            location = card.find_element(By.CSS_SELECTOR, ".job-card-container__metadata-item").text.strip()
                            url = card.find_element(By.CSS_SELECTOR, "a.job-card-list__title").get_attribute("href")
                            
                            job_data = {
                                "title": title,
                                "company": company,
                                "location": location,
                                "url": url,
                            }
                            
                            print(f"\nFound job: {title}")
                            print(f"Company: {company}")
                            print(f"Location: {location}")
                            jobs.append(job_data)
                            total_jobs += 1
                            
                        except Exception as e:
                            print(f"Error extracting job card data: {str(e)}")
                            continue
                    
                    print(f"\nTotal jobs found in this search: {total_jobs}")
                    self.browser.random_delay()
                    
                except Exception as e:
                    print(f"Error searching {keyword} in {location}: {str(e)}")
                    continue
        
        return jobs

    def apply_to_job(self, job_data: Dict, user_data: Dict) -> bool:
        """Apply to a job with customized resume and cover letter"""
        try:
            print(f"\nApplying to: {job_data['title']} at {job_data['company']}")
            self.browser.navigate(job_data['url'])
            self.browser.random_delay()
            
            # Wait for the apply button
            apply_button = self.browser.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    "button[data-control-name='jobdetails_topcard_inapply']"
                ))
            )
            self.browser.safe_click(apply_button)
            self.browser.random_delay()
            
            # Check if already applied
            try:
                already_applied = self.browser.driver.find_element(
                    By.CSS_SELECTOR, 
                    ".jobs-apply-button--applied"
                )
                if already_applied:
                    print("Already applied to this job")
                    return False
            except Exception:
                pass
            
            # Handle the application form
            try:
                # Upload resume if requested
                resume_upload = self.browser.driver.find_element(
                    By.CSS_SELECTOR, 
                    "input[name='resume']"
                )
                if resume_upload:
                    resume_upload.send_keys(user_data['resume_path'])
                    self.browser.random_delay()
            except Exception:
                print("No resume upload field found")
            
            # Fill in any additional fields
            input_fields = self.browser.driver.find_elements(
                By.CSS_SELECTOR, 
                "input[type='text'], textarea"
            )
            
            for field in input_fields:
                try:
                    label = field.get_attribute('aria-label').lower()
                    if 'years of experience' in label:
                        field.send_keys(str(user_data['experience_years']))
                    elif 'name' in label:
                        field.send_keys(user_data['name'])
                    elif 'email' in label:
                        field.send_keys(user_data['email'])
                    elif 'phone' in label:
                        field.send_keys(user_data['phone'])
                except Exception:
                    continue
            
            # Handle any screening questions
            questions = self.browser.driver.find_elements(
                By.CSS_SELECTOR, 
                ".jobs-easy-apply-form-section__custom-fields"
            )
            
            for question in questions:
                try:
                    question_text = question.find_element(
                        By.CSS_SELECTOR, 
                        "label"
                    ).text
                    
                    # Use AI to generate appropriate response
                    answer = self.ai_service.answer_application_question(
                        question_text, 
                        user_data['experience']
                    )
                    
                    input_field = question.find_element(
                        By.CSS_SELECTOR, 
                        "input, textarea, select"
                    )
                    input_field.send_keys(answer)
                except Exception as e:
                    print(f"Error handling question: {str(e)}")
                    continue
            
            # Submit application
            submit_button = self.browser.driver.find_element(
                By.CSS_SELECTOR, 
                "button[aria-label='Submit application']"
            )
            self.browser.safe_click(submit_button)
            
            # Wait for confirmation
            success = self.browser.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    ".artdeco-inline-feedback--success"
                ))
            )
            
            print("Application submitted successfully!")
            return True
            
        except Exception as e:
            print(f"Error applying to job: {str(e)}")
            return False

    def close(self):
        """Clean up resources"""
        self.browser.close()
        self.db.close()
