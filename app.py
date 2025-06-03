'''
This module is a web app for Jiu Jitsu athletes intended to 
provide a centralized location for logging their training sessions.
'''
import os
from datetime import datetime, timedelta
from collections import Counter

from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_bcrypt import Bcrypt
from flask_login import (
    UserMixin, LoginManager, login_user,
    logout_user, login_required, current_user
)
from dotenv import load_dotenv
import sys
import traceback


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('sk')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rolls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirects to 'login' route if @login_required fails
demo_user = os.getenv('demo_username')

class User(db.Model, UserMixin):
    '''
    Creates a User object to identify each unique user accessing the app.
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    logs = db.relationship('TrainingLog', backref='user', lazy = True)


class TrainingLog(db.Model):
    '''
    Creates TrainingLog object to identify each training 
    session to fill the database fields.
    '''
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date, nullable = False)
    partner = db.Column(db.String(100), nullable = False)
    duration = db.Column(db.Integer, nullable = False)   # Minutes
    subs = db.Column(db.String(100))    # eg. RNC, Footlock
    subbed_with = db.Column(db.String(100))
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f'<Roll {self.id} - {self.partner} on {self.date}>'
    
@login_manager.user_loader
def load_user(user_id):
    '''
    Loads the user's unique id.
    '''
    return User.query.get(int(user_id))

@app.route('/')
def index():
    '''
    Loads index/homepage.
    '''
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Loads register page for new users and collects their form submissions.
    Creates a new user.
    '''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        registration_code = request.form.get('registration_code')

        if registration_code != os.getenv('regis_code'):
            flash('Invalid registration code.', 'danger')
            return render_template('register.html')
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template('register.html')
        
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            flash('User already exists', 'warning')
            return render_template('register.html')
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Logs in a valid credentialed user and redirects to dashboard when
    valid.
    '''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(username=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    '''
    Ends user session and redirects to login page.
    '''
    logout_user()
    return redirect(url_for('login'))

@app.route(('/add'), methods=['GET', 'POST'])
@login_required
def add_roll():
    '''
    Collects form filed submissions and creates new TrainingLog 
    object to add to database fields.
    '''
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        partner = request.form['partner']
        duration = request.form['duration']
        subs = request.form['subs']
        subbed_with = request.form['subbed_with']
        notes = request.form['notes']

        if current_user.username == demo_user:
            flash('Demo Mode: Your data has been temporarily saved in your browser.', 'info')
            return redirect(url_for('view_rolls'))

        new_roll = TrainingLog(
            date=date,
            partner=partner,
            duration=duration,
            subs=subs,
            subbed_with=subbed_with,
            notes=notes,
            user_id=current_user.id
        )
        db.session.add(new_roll)
        db.session.commit()

        return redirect(url_for('view_rolls'))
    return render_template('add_roll.html')

@app.route('/rolls')
@login_required
def view_rolls():
    '''
    Displays all rolls for current user ordered by date. Can be 
    filtered/searched on as well.
    '''
    try:
        is_demo = current_user.username == demo_user
        partner = request.args.get('partner', '')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)

        query = TrainingLog.query.filter_by(user_id=current_user.id)

        if partner:
            query = query.filter(TrainingLog.partner.ilike(f'%{partner}%'))
        if start_date:
            query = query.filter(TrainingLog.date >= datetime.strptime(start_date, '%Y-%m-%d')) 
        if end_date:
            query = query.filter(TrainingLog.date <= datetime.strptime(end_date, '%Y-%m-%d'))

        rolls = query.order_by(TrainingLog.date.desc()).paginate(page=page, per_page=5)
        return render_template('rolls.html', rolls=rolls, is_demo=is_demo)
    except Exception:
        print("View rolls error:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return "An error occurred in the view rolls.", 500

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_roll(id):
    '''
    Opens an edit page to edit a previously entered 
    roll/TrainingLog.
    '''
    roll = TrainingLog.query.get_or_404(id)

    if request.method == 'POST':
        roll.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        roll.partner = request.form['partner']
        roll.duration = int(request.form['duration'])
        roll.subs = request.form['subs']
        roll.subbed_with = request.form['subbed_with']
        roll.notes = request.form['notes']

        db.session.commit()
        return redirect(url_for('view_rolls'))
    return render_template('edit_roll.html', roll=roll)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_roll(id):
    '''
    Allows deletion of previous rolls/TrainingLogs.
    '''
    roll = TrainingLog.query.get_or_404(id)
    db.session.delete(roll)
    db.session.commit()
    return redirect(url_for('view_rolls'))

@app.route('/dashboard')
@login_required
def dashboard():
    '''
    Displays a dashboard page for current user with quick
    insights into total rolls, submission distributions, etc.
    '''
    try:
        # Month/year filters
        month = request.args.get('month')
        year = request.args.get('year')

        query = TrainingLog.query.filter_by(user_id=current_user.id)

        if month and year:
            query = query.filter(
                func.strftime('%m', TrainingLog.date) == month.zfill(2),
                func.strftime('%Y', TrainingLog.date) == year
            )

        rolls = query.order_by(TrainingLog.date.desc()).all()

        # Basic stats
        total_sessions = len(rolls)
        total_mins = sum(roll.duration or 0 for roll in rolls)
        avg_duration = round(total_mins / total_sessions, 2) if total_sessions else 0

        # Weekly stats, last 4 weeks
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        weekly_mins = []

        for i in range(4):
            week_start = start_of_week - timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)
            week_logs = [r for r in rolls if r.date and week_start.date() <= r.date <= week_end.date()]

            week_total = sum(r.duration for r in week_logs)
            label = f'{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}'
            weekly_mins.append((label, week_total))
        
        weekly_mins.reverse()

        # Submission stats
        def extract_subs(rolls, attr):
            submissions = []
            for roll in rolls:
                field = getattr(roll, attr)
                if field:
                    submissions += [s.strip().capitalize() for s in field.split(',')]
            return Counter(submissions)
        
        win_data = extract_subs(rolls, 'subs')
        loss_data = extract_subs(rolls, 'subbed_with')

        return render_template(
            'dashboard.html',
            total_sessions=total_sessions,
            total_mins=total_mins,
            avg_duration=avg_duration,
            weekly_mins=weekly_mins,
            win_data=win_data,
            loss_data=loss_data
        )
    except Exception:
        print("Dashboard error:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return "An error occurred in the dashboard.", 500
