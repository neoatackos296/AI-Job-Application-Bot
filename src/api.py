from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models import SessionLocal, Job
from config import Config

app = FastAPI(title="Job Application Bot API")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/jobs/", response_model=List[Job])
def get_jobs(
    status: Optional[str] = None,
    applied: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get list of jobs with optional filters"""
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    if applied is not None:
        query = query.filter(Job.applied == applied)
    return query.all()

@app.post("/jobs/")
def add_job(job: Job, db: Session = Depends(get_db)):
    """Add a new job to the database"""
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@app.put("/jobs/{job_id}")
def update_job(job_id: int, status: str, db: Session = Depends(get_db)):
    """Update job status"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = status
    if status == "applied":
        job.applied = True
        job.application_date = datetime.utcnow()
    db.commit()
    return job

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
