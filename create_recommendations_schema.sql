-- User Job Interactions Table
-- Tracks user interactions with jobs for recommendation algorithms
CREATE TABLE IF NOT EXISTS user_job_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20) NOT NULL CHECK (interaction_type IN ('view', 'save', 'apply', 'ignore')),
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER, -- seconds spent viewing/interacting
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure we don't duplicate the same interaction type for same user/job
    UNIQUE(user_id, job_id, interaction_type)
);

-- User Search History Table (if not already exists)
-- Tracks user search queries for recommendation personalization
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    search_query JSONB NOT NULL, -- Stores the search parameters
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job Recommendation Cache Table
-- Stores pre-computed recommendations for faster retrieval
CREATE TABLE IF NOT EXISTS job_recommendation_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    match_score DECIMAL(4, 3) NOT NULL CHECK (match_score >= 0 AND match_score <= 1),
    match_reasons JSONB DEFAULT '[]',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Index for faster retrieval
    UNIQUE(user_id, job_id)
);

-- User Recommendation Preferences Table
-- Stores user-specific recommendation preferences and settings
CREATE TABLE IF NOT EXISTS user_recommendation_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    preferred_technologies JSONB DEFAULT '[]',
    preferred_locations JSONB DEFAULT '[]',
    preferred_companies JSONB DEFAULT '[]',
    salary_range JSONB DEFAULT '{"min": null, "max": null}',
    experience_level VARCHAR(50) DEFAULT 'any',
    job_types JSONB DEFAULT '[]',
    notification_frequency VARCHAR(20) DEFAULT 'daily',
    last_recommendation_sent TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_user_id ON user_job_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_job_id ON user_job_interactions(job_id);
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_type ON user_job_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_date ON user_job_interactions(interaction_date);

CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_date ON search_history(search_date);

CREATE INDEX IF NOT EXISTS idx_recommendation_cache_user_id ON job_recommendation_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_cache_score ON job_recommendation_cache(match_score);
CREATE INDEX IF NOT EXISTS idx_recommendation_cache_expires ON job_recommendation_cache(expires_at);

CREATE INDEX IF NOT EXISTS idx_recommendation_prefs_user_id ON user_recommendation_preferences(user_id);

-- Update existing tables if needed
ALTER TABLE user_preferences 
ADD COLUMN IF NOT EXISTS recommendation_settings JSONB DEFAULT '{"enabled": true, "frequency": "daily"}';

ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS tech_stack VARCHAR[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50),
ADD COLUMN IF NOT EXISTS remote_ok BOOLEAN DEFAULT FALSE;

-- Insert sample data for testing (optional)
INSERT INTO user_recommendation_preferences (user_id, preferred_technologies, preferred_locations)
SELECT 
    id, 
    '["python", "javascript", "react", "aws"]'::JSONB,
    '["San Francisco", "Remote", "New York"]'::JSONB
FROM users 
WHERE id = 1
ON CONFLICT (user_id) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE user_job_interactions IS 'Tracks user interactions with jobs for recommendation algorithms';
COMMENT ON TABLE search_history IS 'Stores user search history for personalization';
COMMENT ON TABLE job_recommendation_cache IS 'Caches pre-computed job recommendations for faster retrieval';
COMMENT ON TABLE user_recommendation_preferences IS 'Stores user-specific recommendation preferences and settings';
