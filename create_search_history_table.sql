-- Create search history table for tracking job searches
-- Run this file with: psql -U joeythe33rd -d job_scraper_db -f create_search_history_table.sql

CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    source_url VARCHAR(500) NOT NULL,
    search_query JSONB NOT NULL,
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_url, search_query)
);

-- Create indexes for search history
CREATE INDEX IF NOT EXISTS idx_search_history_date ON search_history(search_date DESC);
CREATE INDEX IF NOT EXISTS idx_search_history_url ON search_history(source_url);
CREATE INDEX IF NOT EXISTS idx_search_history_query ON search_history USING gin(search_query);

-- Create a view for search analytics
CREATE OR REPLACE VIEW search_analytics AS
SELECT 
    search_query->>'keywords' as keywords,
    search_query->>'location' as location,
    search_query->>'job_type' as job_type,
    COUNT(*) as search_count,
    MAX(search_date) as last_searched
FROM search_history
GROUP BY search_query->>'keywords', search_query->>'location', search_query->>'job_type'
ORDER BY search_count DESC;

-- Verify table creation
SELECT 'Search history table created successfully' as status;
