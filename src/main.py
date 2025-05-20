import asyncio
from typing import List
from datetime import datetime
import sys
import logging

from job_bot import JobBot
from config import Config
from models import SessionLocal, Job

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the job application bot"""
    logger.info("Starting job application bot...")
    logger.info(f"Python version: {sys.version}")
    
    try:
        job_bot = JobBot()
        db = SessionLocal()
        
        # Search for jobs (testing with first keyword and location)
        keyword = Config.JOB_KEYWORDS[0]  # "AI Engineer"
        location = Config.LOCATIONS[0]    # "Remote"
        
        logger.info(f"Starting job search for {keyword} in {location}")
        jobs = job_bot.search_jobs([keyword], [location])
        
        # Save jobs to database
        new_jobs = 0
        for job_data in jobs:
            # Check if job already exists
            existing_job = db.query(Job).filter(Job.url == job_data["url"]).first()
            if not existing_job:
                job = Job(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    url=job_data["url"],
                    status="new",
                    created_at=datetime.utcnow()
                )
                db.add(job)
                new_jobs += 1
                logger.info(f"New job found: {job.title} at {job.company}")
        
        db.commit()
        logger.info(f"Added {new_jobs} new jobs to the database")
        
        # For now, let's just print the jobs we found
        logger.info("\nJobs found in this search:")
        all_jobs = db.query(Job).all()
        for job in all_jobs:
            logger.info(f"- {job.title} at {job.company} ({job.location})")
        
        # Ask if user wants to proceed with applications
        logger.info("\nJob search completed. Database updated with new positions.")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}", exc_info=True)
    
    finally:
        job_bot.close()
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
