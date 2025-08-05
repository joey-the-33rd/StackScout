-- Create the optimal jobs table schema for your job scraping system
-- Run this file with: psql -U joeythe33rd -d job_scraper_db -f create_jobs_schema.sql

-- Create the jobs table with structure matching your scraped data
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    role VARCHAR(500) NOT NULL,
    tech_stack TEXT[],
    job_type VARCHAR(50),
    salary VARCHAR(100),
    location VARCHAR(255),
    description TEXT,
    requirements JSONB,
    benefits JSONB,
    source_platform VARCHAR(100),
    source_url VARCHAR(500) UNIQUE,
    posted_date TIMESTAMP,
    scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    keywords TEXT[],
    is_active BOOLEAN DEFAULT TRUE
);

-- Create essential indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_role ON jobs USING gin(to_tsvector('english', role));
CREATE INDEX IF NOT EXISTS idx_jobs_tech_stack ON jobs USING gin(tech_stack);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON jobs(source_platform);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_date ON jobs(scraped_date DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_keywords ON jobs USING gin(keywords);
CREATE INDEX IF NOT EXISTS idx_jobs_source_url ON jobs(source_url);

-- Insert sample data to test the schema
INSERT INTO jobs (company, role, tech_stack, job_type, salary, source_platform, source_url, keywords) VALUES
('TechCorp', 'Senior Python Developer', ARRAY['Python', 'Django', 'PostgreSQL'], 'Full-time', '$120k-$150k', 'RemoteOK', 'https://remoteok.com/remote-dev-jobs/12345', ARRAY['python', 'remote', 'senior']),
('StartupXYZ', 'Frontend Engineer', ARRAY['React', 'JavaScript', 'TypeScript'], 'Remote', '$90k-$110k', 'JobGether', 'https://jobgether.com/jobs/67890', ARRAY['react', 'frontend', 'remote']);

-- Verify the schema and data
SELECT 'Schema created successfully' as status;
SELECT table_name, column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'jobs' 
ORDER BY ordinal_position;
