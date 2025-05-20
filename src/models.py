from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, 
    DateTime, Text, ForeignKey, JSON, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from config import Config

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256))
    first_name = Column(String(50))
    last_name = Column(String(50))
    resume_path = Column(String(500))
    preferences = Column(JSON)
    daily_limit = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship('Job', back_populates='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(255))
    company = Column(String(255))
    location = Column(String(255))
    description = Column(Text)
    url = Column(String(500))
    salary_min = Column(Float)
    salary_max = Column(Float)
    applied = Column(Boolean, default=False)
    application_date = Column(DateTime, nullable=True)
    status = Column(String(50))
    resume_version = Column(String(500))
    cover_letter_path = Column(String(500))
    response_received = Column(Boolean, default=False)
    response_date = Column(DateTime, nullable=True)
    interview_date = Column(DateTime, nullable=True)
    rejection_reason = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='jobs')
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', status='{self.status}')>"

# Database setup
engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
