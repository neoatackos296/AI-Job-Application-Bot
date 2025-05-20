from flask import Flask, render_template, request, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from apscheduler.schedulers.background import BackgroundScheduler

from ..job_bot import JobBot
from ..models import Job, SessionLocal
from ..config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

scheduler = BackgroundScheduler()
scheduler.start()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    resume_path = db.Column(db.String(256))
    preferences = db.Column(db.JSON)
    daily_limit = db.Column(db.Integer, default=20)
    is_active = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Save and process resume
        pass
    
    return jsonify({'message': 'Resume uploaded successfully'})

@app.route('/update_preferences', methods=['POST'])
@login_required
def update_preferences():
    data = request.get_json()
    user = User.query.get(current_user.id)
    user.preferences = data
    db.session.commit()
    return jsonify({'message': 'Preferences updated successfully'})

@app.route('/start_bot', methods=['POST'])
@login_required
def start_bot():
    user = User.query.get(current_user.id)
    if not user.preferences:
        return jsonify({'error': 'Please set job preferences first'}), 400
    
    scheduler.add_job(
        func=run_job_bot,
        trigger='cron',
        hour='9-18',
        id=f'job_bot_{user.id}',
        replace_existing=True,
        args=[user.id]
    )
    return jsonify({'message': 'Bot started successfully'})

@app.route('/stop_bot', methods=['POST'])
@login_required
def stop_bot():
    user = User.query.get(current_user.id)
    scheduler.remove_job(f'job_bot_{user.id}')
    return jsonify({'message': 'Bot stopped successfully'})

def run_job_bot(user_id):
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return
    
    bot = JobBot()
    try:
        jobs = bot.search_jobs(
            keywords=[user.preferences.get('job_role')],
            locations=user.preferences.get('locations', ['Remote'])
        )
        # Process and apply to jobs
    finally:
        bot.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}
