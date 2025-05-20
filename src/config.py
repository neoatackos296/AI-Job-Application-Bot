import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./jobs.db')
    
    # Browser Settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
    STEALTH_MODE = os.getenv('STEALTH_MODE', 'True').lower() == 'true'
    MIN_DELAY = float(os.getenv('MIN_DELAY', '2'))
    MAX_DELAY = float(os.getenv('MAX_DELAY', '5'))
      # Job Search Settings
    JOB_KEYWORDS = [
        'AI Engineer', 'Machine Learning Engineer', 'Prompt Engineer',
        'AI Research Scientist', 'Data Engineer', 'Big Data Engineer',
        'Data Analyst', 'AI Software Engineer', 'Software Architect',
        'Full Stack Developer', 'Cloud Software Developer',
        'Cybersecurity Specialist', 'Cloud Engineer', 'NLP Engineer'
    ]
    LOCATIONS = ['Remote', 'United States', 'New York', 'San Francisco', 'Seattle']
      # Resume/Cover Letter Templates
    RESUME_PATH = 'src/Yash B Agarwa1.pdf'
    COVER_LETTER_TEMPLATE_PATH = 'templates/cover_letter_template.txt'
