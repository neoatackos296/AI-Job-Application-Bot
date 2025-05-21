from .config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import logging

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/database.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create database directory
os.makedirs('database', exist_ok=True)

# Initialize database engine
engine = create_engine(
    Config.DATABASE_URL,
    echo=Config.DATABASE_LOGGING
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize the database and create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise