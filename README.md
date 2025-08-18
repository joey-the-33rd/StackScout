# StackScout - AI-Powered Job Search Platform

## Overview
StackScout is a comprehensive job search platform that leverages AI to help users find remote developer jobs and create compelling application documents.

## Features
- **Job Scraping**: Scrapes remote developer jobs from multiple platforms
- **AI Document Generation**: Generates resumes, cover letters, CVs, and follow-up emails
- **Database Management**: Stores and manages job search data
- **Web Interface**: User-friendly interface for job searching and document generation

## AI Features Added
- **Resume Generator**: Creates professional resumes from user profiles
- **Cover Letter Generator**: Generates job-specific cover letters
- **CV Tailor**: Optimizes CVs for specific job postings
- **Email Generator**: Creates follow-up emails for job applications

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL or SQLite
- OpenAI API key

### Setup
1. Clone the repository:
```bash
git clone https://github.com/joeythe33rd/StackScout.git
cd StackScout
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export OPENAI_API_KEY=your_openai_api_key
```

4. Run the application:
```bash
python main.py
```

## Usage

### Web Interface
Access the web interface at `http://localhost:8000`

### API Endpoints
- **Job Search**: `GET /api/search`
- **Resume Generation**: `POST /api/generate-resume`
- **Cover Letter Generation**: `POST /api/generate-cover-letter`
- **CV Tailoring**: `POST /api/tailor-cv`
- **Email Generation**: `POST /api/generate-email`

## Contributing
Contributions are welcome! Please submit pull requests or open issues for any improvements.

## License
MIT License
