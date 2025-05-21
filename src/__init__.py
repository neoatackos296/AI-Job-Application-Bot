"""Initialize the job application bot package"""
from .config import Config
from .database import init_db, Base, SessionLocal, engine
from .models import Job, Application
from .browser import Browser
from .ai_service import AIService
from .job_bot import JobBot