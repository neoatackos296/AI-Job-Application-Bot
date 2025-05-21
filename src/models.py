from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, 
    DateTime, Text, ForeignKey, JSON, Float
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .config import Config

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
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(String)
    url = Column(String, unique=True)
    applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    applications = relationship("Application", back_populates="job")
    
    user = relationship('User', back_populates='jobs')
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', status='{self.status}')>"

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String)  # pending, submitted, rejected, interview
    applied_at = Column(DateTime, default=datetime.utcnow)
    response_received = Column(Boolean, default=False)
    job = relationship("Job", back_populates="applications")

# Database setup
engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
