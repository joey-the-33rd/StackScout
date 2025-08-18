#!/usr/bin/env python3
"""Setup script for AI features."""

import os
import sqlite3
import sys

def setup_database():
    """Initialize the database with AI features schema."""
    print("📊 Setting up database...")
    
    try:
        conn = sqlite3.connect('jobs.db')
        cursor = conn.cursor()
        
        # Read and execute the schema
        with open('create_ai_generators_schema.sql', 'r') as f:
            schema = f.read()
            cursor.executescript(schema)
        
        conn.commit()
        conn.close()
        print("✅ Database setup complete")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'openai',
        'python-docx',
        'reportlab',
        'weasyprint',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements_new.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_environment():
    """Check if required environment variables are set."""
    print("🔐 Checking environment variables...")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        print("Run: export OPENAI_API_KEY=your_key_here")
        return False
    
    print("✅ OPENAI_API_KEY is set")
    return True

def main():
    """Run setup checks."""
    print("🚀 Setting up AI features for StackScout...")
    
    checks = [
        check_dependencies,
        check_environment,
        setup_database
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print(f"\n📊 Setup Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Setup complete! You can now use AI features.")
        print("Run: python stackscout_web.py")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")

if __name__ == "__main__":
    main()
