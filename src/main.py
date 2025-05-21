import logging
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

from job_bot import JobBot
from config import Config
from models import SessionLocal, Job, User, Base, engine
from resume_parser import ResumeParser
from web.forms import LoginForm, RegistrationForm, JobPreferencesForm
from database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app with template and static folders
app = Flask(__name__,
    template_folder=Path(__file__).parent / 'templates',
    static_folder=Path(__file__).parent / 'static'
)
app.config.from_object(Config)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    try:
        return db.query(User).get(int(user_id))
    finally:
        db.close()

def run_job_search(user_id: int):
    """Background job to search and apply to jobs"""
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if not user or not user.is_active:
            return
        
        job_bot = JobBot()
        try:
            preferences = user.preferences or {}
            keywords = preferences.get('job_role', ['Software Engineer'])
            locations = preferences.get('locations', ['Remote'])
            
            logger.info(f"Starting job search for {keywords} in {locations}")
            jobs = job_bot.search_jobs(keywords, locations)
            
            new_jobs = 0
            for job_data in jobs:
                if db.query(Job).filter(Job.url == job_data["url"]).first():
                    continue
                    
                job = Job(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    url=job_data["url"],
                    status="new",
                    user_id=user_id,
                    created_at=datetime.utcnow()
                )
                db.add(job)
                new_jobs += 1
                logger.info(f"New job found: {job.title} at {job.company}")
            
            db.commit()
            logger.info(f"Added {new_jobs} new jobs to the database")
            
        finally:
            job_bot.close()
            
    except Exception as e:
        logger.error(f"Error in job search: {str(e)}", exc_info=True)
    finally:
        db.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        db = SessionLocal()
        try:
            if db.query(User).filter_by(email=form.email.data).first():
                flash('Email already registered')
                return redirect(url_for('register'))
            
            user = User(
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password.data)
            db.add(user)
            db.commit()
            
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        finally:
            db.close()
    
    return render_template('register.html', title='Register', form=form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = JobPreferencesForm()
    if form.validate_on_submit():
        db = SessionLocal()
        try:
            user = db.query(User).get(current_user.id)
            user.preferences = {
                'job_role': form.job_role.data,
                'experience_level': form.experience_level.data,
                'min_salary': form.min_salary.data,
                'max_salary': form.max_salary.data,
                'locations': [loc.strip() for loc in form.locations.data.split(',') if loc.strip()],
                'daily_limit': form.daily_limit.data
            }
            db.commit()
            flash('Preferences updated successfully!')
            return redirect(url_for('dashboard'))
        finally:
            db.close()
    
    return render_template('settings.html', title='Settings', form=form)

@app.route('/bot_status')
@login_required
def bot_status():
    job_id = f'job_bot_{current_user.id}'
    is_running = scheduler.get_job(job_id) is not None
    return jsonify({'running': is_running})

@app.route('/logout')
@login_required
def logout():
    # Stop the bot if it's running
    job_id = f'job_bot_{current_user.id}'
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    logout_user()
    return redirect(url_for('login'))

@app.route('/application/<int:job_id>')
@login_required
def view_application(job_id):
    db = SessionLocal()
    try:
        job = db.query(Job).filter_by(id=job_id, user_id=current_user.id).first_or_404()
        return jsonify({
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'status': job.status,
            'application_date': job.application_date.isoformat() if job.application_date else None,
            'resume_url': url_for('static', filename=job.resume_version) if job.resume_version else None,
            'cover_letter_url': url_for('static', filename=job.cover_letter_path) if job.cover_letter_path else None
        })
    finally:
        db.close()

async def main():
    """Main entry point for the job application bot"""
    try:
        init_db()
        bot = JobBot()
        await bot.start_application_process()
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Start the Flask app
    app.run(debug=Config.DEBUG_MODE, use_reloader=False)
    asyncio.run(main())
