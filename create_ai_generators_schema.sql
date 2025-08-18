-- Database schema additions for AI generators
-- Add tables for user profiles and generated documents

-- User profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    summary TEXT,
    years_experience INTEGER DEFAULT 0,
    skills TEXT,
    experience TEXT,
    education TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated documents table
CREATE TABLE IF NOT EXISTS generated_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    job_id TEXT,
    document_content TEXT NOT NULL,
    template_name TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

-- Document templates table
CREATE TABLE IF NOT EXISTS document_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT NOT NULL,
    template_type TEXT NOT NULL,
    template_content TEXT NOT NULL,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search history table
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    search_query TEXT NOT NULL,
    search_results JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_documents_user_id ON generated_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_documents_job_id ON generated_documents(job_id);
CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);
