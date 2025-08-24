#!/usr/bin/env python3
"""
StackScout Environment Setup Assistant

This script helps users set up their environment variables for StackScout.
It provides guidance and generates configuration templates.
"""

import os
import sys
from pathlib import Path

def check_current_env():
    """Check if environment variables are already set."""
    print("Checking current environment configuration...")
    
    env_vars = ['SECRET_KEY', 'GEMINI_API_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in env_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            missing_vars.append(var)
    
    return missing_vars

def generate_env_template():
    """Generate a template for the .env file with instructions."""
    template = """# StackScout Environment Configuration
# =============================================

# REQUIRED: Authentication Security
# Generate a strong secret key using: python generate_secret_key.py
SECRET_KEY=your_very_strong_secret_key_here

# REQUIRED: Google Gemini API
# Get your API key from: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration (choose one option)

# Option 1: SQLite (default, recommended for development)
DATABASE_URL=sqlite:///stackscout.db

# Option 2: PostgreSQL (uncomment and configure for production)
# DB_HOST=localhost
# DB_NAME=job_scraper_db
# DB_USER=your_username
# DB_PASSWORD=your_secure_password
# DB_PORT=5432

# Optional: Email configuration
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your_email@gmail.com
# SMTP_PASSWORD=your_app_password

# Optional: Debug settings
DEBUG=True
LOG_LEVEL=INFO
"""
    return template

def main():
    print("StackScout Environment Setup Assistant")
    print("=" * 50)
    
    # Check current environment
    missing_vars = check_current_env()
    
    if missing_vars:
        print(f"\n⚠️  Missing required environment variables: {', '.join(missing_vars)}")
    else:
        print("\n✅ All required environment variables are set!")
        return
    
    print("\n" + "=" * 50)
    print("SETUP INSTRUCTIONS:")
    print("=" * 50)
    
    # Generate and show env template
    env_template = generate_env_template()
    print("\nRecommended .env file content:")
    print("-" * 30)
    print(env_template)
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        print(f"\n📁 .env file already exists at: {env_file.absolute()}")
        print("Please update it with the missing variables above.")
    else:
        print(f"\n📁 No .env file found. You can create one with the content above.")
    
    print("\n" + "=" * 50)
    print("QUICK SETUP COMMANDS:")
    print("=" * 50)
    
    print("""
# Generate a strong SECRET_KEY:
python generate_secret_key.py

# Create .env file (if it doesn't exist):
cp .env.example .env

# Set file permissions (recommended):
chmod 600 .env

# Test your configuration:
python -c "import os; from src.auth.security import SECRET_KEY; print('✅ SECRET_KEY is properly configured')"
""")
    
    print("\nFor detailed instructions, see ENVIRONMENT_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
