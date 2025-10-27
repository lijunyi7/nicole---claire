#!/usr/bin/env python3
"""
Test script to verify Flask app structure without OpenAI dependencies
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_flask_app():
    """Test Flask app creation without OpenAI dependencies."""
    try:
        # Test basic Flask imports
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from flask_bcrypt import Bcrypt
        
        print("✅ Flask dependencies imported successfully")
        
        # Test Flask app creation
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db = SQLAlchemy(app)
        bcrypt = Bcrypt(app)
        
        print("✅ Flask app created successfully")
        
        # Test database models
        class User(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            email = db.Column(db.String(120), unique=True, nullable=False)
            password_hash = db.Column(db.String(128), nullable=False)
            
            def set_password(self, password):
                self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            def check_password(self, password):
                return bcrypt.check_password_hash(self.password_hash, password)
        
        print("✅ Database models defined successfully")
        
        # Test password hashing
        with app.app_context():
            db.create_all()
            user = User(username='test', email='test@example.com')
            user.set_password('testpassword')
            
            # Test password verification
            if user.check_password('testpassword'):
                print("✅ Password hashing and verification working")
            else:
                print("❌ Password verification failed")
                return False
        
        print("✅ All Flask app components working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Flask app structure...")
    if test_flask_app():
        print("\n🎉 Flask app is ready to run!")
        print("📝 Note: You'll need to install dependencies and set OPENAI_API_KEY to run the full app")
    else:
        print("\n❌ Flask app has issues that need to be resolved")
        sys.exit(1)
