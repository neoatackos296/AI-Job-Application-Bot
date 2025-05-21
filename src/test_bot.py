import asyncio
import logging
from pathlib import Path
from .job_bot import JobBot
from .database import init_db
from .config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_bot.log'),
        logging.StreamHandler()
    ]
)

async def test_bot():
    """Test the job application bot functionality"""
    try:
        # Initialize database
        init_db()
        logging.info("Database initialized successfully")

        # Create bot instance
        bot = JobBot()
        logging.info("Bot instance created")

        # Test LinkedIn login
        await bot.login()
        logging.info("Login successful")

        # Search for 1 job as a test
        jobs = await bot.search_jobs(
            title="AI Engineer",
            location="Remote",
            limit=1
        )
        logging.info(f"Found {len(jobs)} jobs")

        return True
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot())
    print("✓ Test completed successfully!" if success else "✗ Test failed!")