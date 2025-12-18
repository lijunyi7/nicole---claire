#!/bin/bash
# Startup script for Educational Slides Resource Collector

echo "🚀 Starting Educational Slides Resource Collector..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment and start the app
source venv/bin/activate
python3 run_web_app.py
