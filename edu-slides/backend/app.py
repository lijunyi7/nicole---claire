"""
Flask web application for Educational Slides Resource Collector
Provides web interface for collecting, filtering, and ranking educational resources
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import Person 1 and Person 2 modules
from backend.slides_generator import generate_slide_deck

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# Ensure database directory exists
db_dir = Path(__file__).parent.parent / 'instance'
db_dir.mkdir(exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_dir}/edu_slides.db')
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
    slides = db.relationship('Slide', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Slide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    slides_content = db.Column(db.Text, nullable=False)  # JSON content
    resource_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route('/')
def index():
    """Homepage"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
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
    """Sign up page"""
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
    """Logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard - shows user's saved slides"""
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user is None:
        session.pop('user_id', None)
        flash('Session expired. Please log in again.', 'error')
        return redirect(url_for('login'))
    
    slides = Slide.query.filter_by(user_id=user.id).order_by(Slide.created_at.desc()).all()
    return render_template('dashboard.html', user=user, slides=slides)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search page - displays form and handles search requests"""
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        grade = request.form.get('grade', 'elementary')
        
        if not topic:
            flash('Please enter a topic', 'error')
            return render_template('search.html')
        
        try:
            # Step 1: Generate a full slide deck using a single LLM prompt
            deck, _raw_text = generate_slide_deck(topic, grade)
            slides = deck.get("slides", [])

            # Step 2: Persist deck JSON (source of truth for frontend)
            data_dir = Path(__file__).parent.parent / "data" / "generated"
            data_dir.mkdir(parents=True, exist_ok=True)
            slug_topic = topic.replace(" ", "_").lower()
            slug_grade = grade.replace(" ", "_").lower()
            deck_path = data_dir / f"{slug_topic}_{slug_grade}_slides.json"
            with open(deck_path, "w", encoding="utf-8") as f_deck:
                json.dump(deck, f_deck, indent=2, ensure_ascii=False)
            print(f"Saved slide deck to {deck_path}")

            if not slides:
                flash('No slides were generated. Please try again.', 'error')
                return render_template('search.html')

            # Step 3: Save slides to database if user is logged in
            slide_id = None
            if 'user_id' in session:
                try:
                    source_count = sum(len(s.get("sources", [])) for s in slides)
                    slide = Slide(
                        title=f"{topic} - {grade.title()}",
                        topic=topic,
                        grade=grade,
                        slides_content=json.dumps(slides, ensure_ascii=False),
                        resource_count=source_count,
                        user_id=session['user_id']
                    )
                    db.session.add(slide)
                    db.session.commit()
                    slide_id = slide.id
                    flash('Slides generated and saved!', 'success')
                except Exception as e:
                    print(f"Error saving slide: {e}")
                    db.session.rollback()
                    flash('Slides generated, but failed to save. You can still view them.', 'warning')

            # Render slides
            return render_template('slides.html',
                                 slides=slides,
                                 topic=topic,
                                 grade=grade,
                                 generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                 resource_count=source_count if slides else 0,
                                 slide_id=slide_id)
            
        except Exception as e:
            flash(f'Error generating slides: {str(e)}', 'error')
            import traceback
            print(f"Error: {traceback.format_exc()}")
            return render_template('search.html', error=str(e))
    
    # GET request - show search form
    return render_template('search.html')

@app.route('/slide/<int:slide_id>')
def view_slide(slide_id):
    """View a saved slide"""
    if 'user_id' not in session:
        flash('Please log in to view slides', 'error')
        return redirect(url_for('login'))
    
    slide = Slide.query.get_or_404(slide_id)
    
    # Check if user owns this slide
    if slide.user_id != session['user_id']:
        flash('You do not have permission to view this slide', 'error')
        return redirect(url_for('dashboard'))
    
    slides_content = json.loads(slide.slides_content)
    return render_template('slides.html', 
                         slides=slides_content, 
                         topic=slide.topic, 
                         grade=slide.grade,
                         generated_at=slide.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                         resource_count=slide.resource_count,
                         slide_id=slide.id)

@app.route('/delete_slide/<int:slide_id>', methods=['POST'])
def delete_slide(slide_id):
    """Delete a saved slide"""
    if 'user_id' not in session:
        flash('Please log in to delete slides', 'error')
        return redirect(url_for('login'))
    
    slide = Slide.query.get_or_404(slide_id)
    
    # Check if user owns this slide
    if slide.user_id != session['user_id']:
        flash('You do not have permission to delete this slide', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(slide)
    db.session.commit()
    flash('Slide deleted successfully', 'success')
    return redirect(url_for('dashboard'))

# Initialize database
def create_tables():
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("Database tables initialized!")

# Safety check: ensure tables exist (idempotent - won't recreate existing tables)
# This runs once when the app starts
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Note: Database initialization: {e}")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5001)
