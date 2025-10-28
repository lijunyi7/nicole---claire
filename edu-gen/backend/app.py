"""
Flask web application for Educational Script Generator
Provides web interface for generating and managing educational scripts
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import datetime
import json
import re
from pathlib import Path
import sys
from core.text_to_speech import TextToSpeechGenerator
from core.video_frame_generator import VideoFrameGenerator
from core.video_generator import VideoGenerator
# Add backend directory to path for imports
sys.path.append(str(Path(__file__).parent))

from core.generate_script import ScriptGenerator

app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
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
    if user is None:  # <--- THIS LINE FIXES YOUR ERROR
        session.pop('user_id', None)  # clean bad session
        flash('Session expired. Please log in again.', 'error')
        return redirect(url_for('login'))

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

            # 1) Generate JSON script (no audio here)
            generator = ScriptGenerator()
            script_data = generator.generate_script(topic, prompt_template)

            # 2) Generate MULTIPLE audio files (intro/explanation/question/…)
            #    They will be saved under: outputs/audio/
            #    Create unique identifier based on topic and timestamp
            safe_topic = re.sub(r'[^a-zA-Z0-9_-]', '_', topic)[:50]  # Sanitize topic
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            script_id = f"{safe_topic}_{timestamp}"
            
            tts = TextToSpeechGenerator(voice="nova")
            audio_dir = Path(__file__).parent.parent / "outputs" / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            audio_files = tts.generate_script_audio(script_data, str(audio_dir), script_id=script_id)  # returns full paths

            # 2a) Store only basenames into the script for use with /audio/<filename>
            #    and mark metadata (audio_generated, voice, etc.)
            updated_script = tts.update_script_with_audio(script_data, audio_files)

            # 3) Generate video frames for each narration
            # Use custom background image
            background_path = Path(__file__).parent.parent / "background_edu.jpg"
            frame_generator = VideoFrameGenerator(background_path=str(background_path))
            frames_dir = Path(__file__).parent.parent / "outputs" / "frames"
            frames_dir.mkdir(parents=True, exist_ok=True)

            frame_files = frame_generator.generate_script_frames(script_data, str(frames_dir), script_id=script_id)
            
            # 3a) Update script with frame paths
            updated_script = frame_generator.update_script_with_frames(updated_script, frame_files)

            # 4) Generate videos by combining audio and frames
            video_dir = Path(__file__).parent.parent / "outputs" / "videos"
            video_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                video_generator = VideoGenerator()
                video_files = video_generator.generate_script_videos(
                    script_data,
                    str(audio_dir),
                    str(frames_dir),
                    str(video_dir),
                    script_id=script_id
                )
                
                # 4a) Update script with video paths
                updated_script = video_generator.update_script_with_videos(updated_script, video_files)
            except RuntimeError as e:
                print(f"Warning: Video generation failed: {e}")
                # Continue without videos - they're optional
                updated_script["metadata"]["videos_generated"] = False

            # 5) Save to database (store updated_script with audio, frame, and video paths)
            script = Script(
                title=updated_script.get('metadata', {}).get('topic', topic),
                topic=topic,
                content=json.dumps(updated_script, ensure_ascii=False),
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

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve audio files from the outputs/audio directory."""
    if 'user_id' not in session:
        flash('Please log in to access audio files', 'error')
        return redirect(url_for('login'))
    
    audio_path = Path(__file__).parent.parent / "outputs" / "audio" / filename
    
    if not audio_path.exists():
        flash('Audio file not found', 'error')
        return redirect(url_for('dashboard'))
    
    return send_file(audio_path, mimetype='audio/mpeg')

@app.route('/frames/<path:filename>')
def serve_frames(filename):
    """Serve frame files from the outputs/frames directory."""
    if 'user_id' not in session:
        flash('Please log in to access frames', 'error')
        return redirect(url_for('login'))
    
    frame_path = Path(__file__).parent.parent / "outputs" / "frames" / filename
    
    if not frame_path.exists():
        flash('Frame file not found', 'error')
        return redirect(url_for('dashboard'))
    
    return send_file(frame_path, mimetype='image/png')

@app.route('/videos/<path:filename>')
def serve_videos(filename):
    """Serve video files from the outputs/videos directory."""
    if 'user_id' not in session:
        flash('Please log in to access videos', 'error')
        return redirect(url_for('login'))
    
    video_path = Path(__file__).parent.parent / "outputs" / "videos" / filename
    
    if not video_path.exists():
        flash('Video file not found', 'error')
        return redirect(url_for('dashboard'))
    
    return send_file(video_path, mimetype='video/mp4')

# Initialize database
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
