"""
Flask web application for Educational Script Generator
Provides web interface for generating and managing educational scripts
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import datetime
import json
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from core.generate_script import ScriptGenerator
# Note: OpenAI API key is handled by the ScriptGenerator class

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///edu_gen.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scripts = db.relationship('Script', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # JSON content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('signup.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception:
            db.session.rollback()
            flash('Error creating account. Please try again.', 'error')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    scripts = Script.query.filter_by(user_id=user.id).order_by(Script.created_at.desc()).all()
    
    return render_template('dashboard.html', user=user, scripts=scripts)

@app.route('/generate', methods=['GET', 'POST'])
def generate_script():
    if 'user_id' not in session:
        flash('Please log in to generate scripts', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        topic = request.form['topic']
        
        try:
            # Load prompt template
            template_path = Path(__file__).parent / "prompts" / "prompt_template_math.txt"
            with open(template_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            # Generate script
            generator = ScriptGenerator()
            script_data = generator.generate_script(topic, prompt_template)
            
            # Save to database
            script = Script(
                title=script_data.get('metadata', {}).get('topic', topic),
                topic=topic,
                content=json.dumps(script_data, ensure_ascii=False),
                user_id=session['user_id']
            )
            
            db.session.add(script)
            db.session.commit()
            
            flash('Script generated successfully!', 'success')
            return redirect(url_for('view_script', script_id=script.id))
            
        except Exception as e:
            flash(f'Error generating script: {str(e)}', 'error')
    
    return render_template('generate.html')

@app.route('/script/<int:script_id>')
def view_script(script_id):
    if 'user_id' not in session:
        flash('Please log in to view scripts', 'error')
        return redirect(url_for('login'))
    
    script = Script.query.get_or_404(script_id)
    
    # Check if user owns this script
    if script.user_id != session['user_id']:
        flash('You do not have permission to view this script', 'error')
        return redirect(url_for('dashboard'))
    
    script_content = json.loads(script.content)
    return render_template('view_script.html', script=script, content=script_content)

@app.route('/delete_script/<int:script_id>', methods=['POST'])
def delete_script(script_id):
    if 'user_id' not in session:
        flash('Please log in to delete scripts', 'error')
        return redirect(url_for('login'))
    
    script = Script.query.get_or_404(script_id)
    
    # Check if user owns this script
    if script.user_id != session['user_id']:
        flash('You do not have permission to delete this script', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(script)
    db.session.commit()
    flash('Script deleted successfully', 'success')
    return redirect(url_for('dashboard'))

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
