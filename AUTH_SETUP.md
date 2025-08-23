# StackScout Authentication System Setup Guide

## Overview

This guide provides step-by-step instructions for setting up the user authentication system for StackScout.

## Features Implemented

- ✅ User registration with email validation
- ✅ Secure password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ User login/logout
- ✅ Protected API endpoints
- ✅ User profile management
- ✅ User preferences system

## Quick Start

### 1. Install Dependencies

```bash
python setup_auth.py
```

### 2. Manual Setup (Alternative)

```bash
# Install authentication dependencies
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# Set up database schema
psql -d job_scraper_db -f create_users_schema.sql
```

### 3. Set Environment Variables

- **SECRET_KEY**: A strong secret key must be set in the environment. This key is used for signing JWT tokens and must not be hardcoded in the application.

### 4. Start the Server

```bash
python stackscout_web.py
```

## API Endpoints

### Authentication Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info (protected)

### Example Usage

#### Register a new user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

#### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

#### Get current user

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Database Schema

### Users Table

- `id` (SERIAL PRIMARY KEY)
- `username` (VARCHAR UNIQUE)
- `email` (VARCHAR UNIQUE)
- `password_hash` (VARCHAR)
- `full_name` (VARCHAR)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `is_active` (BOOLEAN)
- `last_login` (TIMESTAMP)

### User Preferences Table

- `id` (SERIAL PRIMARY KEY)
- `user_id` (FOREIGN KEY)
- `notification_enabled` (BOOLEAN)
- `email_notifications` (BOOLEAN)
- `saved_searches` (JSONB)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

## Security Features

- Password hashing with bcrypt
- JWT tokens with 30-minute expiration
- Secure token validation
- SQL injection prevention
- Input validation with Pydantic

## Testing

Run the test script:

```bash
python test_auth.py
```

## Integration with Existing Features

The authentication system is now integrated with:

- Job search functionality
- AI generators
- Database management
- User preferences

## Next Steps

1. Implement Phase 2: Job Recommendations Engine
2. Add user-specific job storage
3. Implement saved searches
4. Add notification preferences
