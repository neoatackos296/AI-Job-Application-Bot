from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from config import Config

Base = declarative_base()

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    company = Column(String(255))
    location = Column(String(255))
    description = Column(Text)
    url = Column(String(500))
    applied = Column(Boolean, default=False)
    application_date = Column(DateTime, nullable=True)
    status = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', status='{self.status}')>"

# Database setup
engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
