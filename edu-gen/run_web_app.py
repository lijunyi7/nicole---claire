#!/usr/bin/env python3
"""
Startup script for Educational Script Generator Web Application
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def check_environment():
    """Check if required environment variables are set."""
    try:
        from config.env_config import get_openai_api_key
        get_openai_api_key()  # This will load .env and check for API key
        print("✅ Environment configuration loaded successfully")
        return True
    except ValueError as e:
        print(f"❌ Environment configuration issue: {e}")
        return False

def create_database():
    """Create database tables if they don't exist."""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main startup function."""
    print("🚀 Starting Educational Script Generator Web Application...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create database
    if not create_database():
        sys.exit(1)
    
    # Start the application
    try:
        from app import app
        print("✅ Application ready!")
        print("🌐 Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5001")
        print("⏹️  Press Ctrl+C to stop the server")
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
