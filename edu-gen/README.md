# Educational Script Generator

A comprehensive web application for generating educational scripts with AI-powered content creation and voice narration.

## Features

- **AI-Powered Script Generation**: Create engaging educational content using OpenAI's GPT models
- **Voice Narration**: Automatically generate high-quality audio narration for all script sections
- **Interactive Practice Questions**: Include multiple-choice questions with immediate feedback
- **User Management**: Secure authentication and script management
- **Modern Web Interface**: Responsive design with Bootstrap 5

## Project Structure

```
edu-gen/
├── backend/                 # Backend application
│   ├── app.py              # Main Flask application
│   ├── core/               # Core functionality
│   │   ├── generate_script.py
│   │   └── text_to_speech.py
│   ├── config/             # Configuration
│   ├── prompts/            # Prompt templates
│   ├── schema/             # JSON schemas
│   ├── validation/         # Validation utilities
│   └── tools/              # Utility tools
├── frontend/               # Frontend application
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, and assets
│       ├── css/
│       └── js/
├── outputs/                # Generated content
│   ├── scripts/            # JSON script files
│   └── audio/              # MP3 audio files
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── run_web_app.py         # Application startup script
```

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd edu-gen
   ```

2. **Create virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_for_flask_sessions
   ```

## Usage

1. **Start the application**

   ```bash
   python run_web_app.py
   ```

2. **Access the web interface**
   Open your browser and go to: http://localhost:5000

3. **Create an account** and start generating educational scripts!

## API Endpoints

- `GET /` - Home page
- `GET /login` - Login page
- `POST /login` - User authentication
- `GET /signup` - Registration page
- `POST /signup` - User registration
- `GET /dashboard` - User dashboard
- `GET /generate` - Script generation page
- `POST /generate` - Generate new script
- `GET /script/<id>` - View script
- `POST /delete_script/<id>` - Delete script
- `GET /audio/<filename>` - Serve audio files

## Technologies Used

- **Backend**: Flask, SQLAlchemy, OpenAI API
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Audio**: OpenAI Text-to-Speech API
- **Authentication**: Flask-Bcrypt for secure password hashing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
