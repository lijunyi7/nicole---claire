"""
Run the Flask web application for Educational Slides Resource Collector
"""

from backend.app import app, db

if __name__ == '__main__':
    print("=" * 60)
    print("Educational Slides Resource Collector")
    print("=" * 60)
    print("Initializing database...")
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
    print("Starting web server...")
    print("Access the application at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)
