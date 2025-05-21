from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, login_required
from models import User, Job
from job_bot import JobBot

app = Flask(__name__)
login_manager = LoginManager()

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')