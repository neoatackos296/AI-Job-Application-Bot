import logging
from pathlib import Path
import asyncio
import os
import traceback
from typing import List
import random
import time
from datetime import datetime
import subprocess
from contextlib import suppress  # Import suppress

# Configure detailed logging
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

log_file = logs_dir / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler(log_file)
stream_handler = logging.StreamHandler()

# Create formatters and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Define job titles to search for
JOB_TITLES = [
    "Data Engineer"  # Focus on Data Engineer jobs
]

# Resume and cover letter templates
RESUME_PATH = Path("data/resume.pdf")
COVER_LETTER_TEMPLATE = """
Dear Hiring Manager,

I am excited to apply for the {job_title} position at {company}. 
{custom_content}

Best regards,
Your Name
"""

async def cleanup() -> None:
    """Clean up Chrome processes and cache."""
    try:
        from src.browser import Browser  # Import Browser here
        Browser.cleanup_all()
        
        logger.info("Cleaning up Chrome processes...")
        processes = ['chrome.exe', 'chromedriver.exe']
        for proc in processes:
            with suppress(subprocess.SubprocessError):
                subprocess.run(
                    ['taskkill', '/F', '/IM', proc], 
                    capture_output=True, 
                    text=True,
                    check=False
                )
        
        cache_dir = Path(os.getenv('LOCALAPPDATA', '')) / 'undetected_chromedriver'
        if cache_dir.exists():
            for item in cache_dir.iterdir():
                with suppress(Exception):
                    item.unlink()
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")

async def test_browser() -> bool:
    """Test browser initialization and LinkedIn job applications."""
    logger.info("Starting automated job application process...")
    browser = None
    total_jobs_found = 0
    applications_submitted = 0
    
    try:
        from src.browser import Browser
        browser = Browser()
        
        # Login to LinkedIn
        if not browser.login_linkedin():
            logger.error("LinkedIn login failed")
            return False
        
        logger.info("LinkedIn login successful")
        time.sleep(2)
        
        # Navigate to jobs page
        if not browser.navigate("https://www.linkedin.com/jobs"):
            logger.error("Failed to navigate to jobs page")
            return False
        
        logger.info("Navigated to jobs page")
        time.sleep(2)
        
        # Search for jobs
        if not browser.search_jobs("Data Engineer", "Remote"):
            logger.error("Job search failed")
            return False
        
        logger.info("Job search completed")
        time.sleep(2)
        
        # Get job listings
        jobs = browser.get_recent_jobs(limit=5)
        if not jobs:
            logger.error("No jobs found")
            return False
        
        total_jobs_found = len(jobs)
        logger.info(f"Found {total_jobs_found} jobs")
        
        # Apply to jobs
        for index, job in enumerate(jobs, 1):
            logger.info(f"Processing job {index}/{total_jobs_found}")
            
            if browser.apply_to_job(job):
                applications_submitted += 1
                logger.info(f"Successfully applied to {job['title']}")
            else:
                logger.error(f"Failed to apply to {job['title']}")
            
            # Wait between applications
            if index < total_jobs_found:
                wait_time = random.uniform(30, 45)
                logger.info(f"Waiting {wait_time:.1f} seconds before next application...")
                time.sleep(wait_time)
        
        logger.info(f"\nFinal Summary:")
        logger.info(f"Total jobs found: {total_jobs_found}")
        logger.info(f"Applications submitted: {applications_submitted}")
        return applications_submitted > 0
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if browser:
            browser.close()

async def main() -> None:
    """Main test runner."""
    try:
        await cleanup()
        logger.info("Starting test suite...")
        success = await test_browser()
        logger.info(f"Browser test {'passed' if success else 'failed'}")
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        traceback.print_exc()
    finally:
        await cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        traceback.print_exc()