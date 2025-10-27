# 🚀 Quick Start Guide - Educational Script Generator Web App

## ✅ Issue Fixed!

The `AttributeError: module 'hashlib' has no attribute 'scrypt'` error has been resolved by switching from `werkzeug.security` to `flask-bcrypt` for password hashing.

## 🛠️ Installation Steps

### 1. Install Dependencies

```bash
cd /Users/karyzheng/nicole---claire/edu-gen
pip3 install -r requirements.txt
```

If you encounter architecture issues (like the pydantic error), try:

```bash
# For Apple Silicon Macs
pip3 install --upgrade pip
pip3 install --force-reinstall --no-cache-dir -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export SECRET_KEY="your-secret-key-for-flask-sessions"
```

### 3. Run the Web Application

```bash
python3 run_web_app.py
```

Or directly:

```bash
python3 app.py
```

### 4. Access the Application

Open your browser and go to: **http://localhost:5000**

## 🎯 What You Can Do

1. **Create Account**: Sign up with username, email, and password
2. **Login**: Access your personal dashboard
3. **Generate Scripts**: Create educational scripts using AI
4. **Manage Content**: View, organize, and delete your scripts
5. **Interactive Learning**: Practice with multiple choice questions

## 🔧 Troubleshooting

### If you get import errors:

```bash
# Reinstall dependencies
pip3 uninstall -y flask flask-sqlalchemy flask-bcrypt openai jsonschema python-dotenv
pip3 install -r requirements.txt
```

### If you get database errors:

```bash
# The app will create the database automatically on first run
# If issues persist, delete edu_gen.db and restart
rm edu_gen.db
python3 app.py
```

### If you get OpenAI API errors:

- Make sure your `OPENAI_API_KEY` is set correctly
- Check that you have API credits available
- Verify the API key has the correct permissions

## 📱 Features

- ✅ **User Authentication**: Secure login/signup
- ✅ **Database Storage**: SQLite database for users and scripts
- ✅ **AI Integration**: Uses your existing ScriptGenerator class
- ✅ **Modern UI**: Responsive Bootstrap design
- ✅ **Script Management**: View, delete, and organize scripts
- ✅ **Interactive Practice**: Multiple choice questions with feedback

The web application is now ready to use! 🎉
