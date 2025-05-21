import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./database/jobs.db')
    DATABASE_LOGGING = os.getenv('DATABASE_LOGGING', 'False').lower() == 'true'
    
    # Application Settings
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    STEALTH_MODE = os.getenv('STEALTH_MODE', 'True').lower() == 'true'
    MIN_DELAY = float(os.getenv('MIN_DELAY', '2'))
    MAX_DELAY = float(os.getenv('MAX_DELAY', '5'))
    MAX_DAILY_APPLICATIONS = int(os.getenv('MAX_DAILY_APPLICATIONS', '50'))
