-- Migration script to add numeric salary columns to jobs table
-- Run this with: psql -U joeythe33rd -d job_scraper_db -f add_numeric_salary_columns_fixed.sql

-- Add numeric salary columns
ALTER TABLE jobs 
ADD COLUMN IF NOT EXISTS salary_min_numeric INTEGER,
ADD COLUMN IF NOT EXISTS salary_max_numeric INTEGER,
ADD COLUMN IF NOT EXISTS salary_currency VARCHAR(3);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_salary_min ON jobs(salary_min_numeric);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_max ON jobs(salary_max_numeric);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_range ON jobs(salary_min_numeric, salary_max_numeric);

-- Function to parse salary string and extract numeric values
CREATE OR REPLACE FUNCTION parse_salary(salary_text VARCHAR) 
RETURNS TABLE (min_salary INTEGER, max_salary INTEGER, currency VARCHAR) AS $$
DECLARE
    matches TEXT[];
    clean_text TEXT;
    amount TEXT;
    multiplier INTEGER;
BEGIN
    -- Handle empty or null salary text
    IF salary_text IS NULL OR salary_text = '' THEN
        min_salary := NULL;
        max_salary := NULL;
        currency := NULL;
        RETURN NEXT;
        RETURN;
    END IF;

    -- Default currency detection
    currency := NULL;
    IF salary_text LIKE '%$%' THEN
        currency := 'USD';
    ELSIF salary_text LIKE '%€%' THEN
        currency := 'EUR';
    ELSIF salary_text LIKE '%£%' THEN
        currency := 'GBP';
    END IF;

    -- Clean the text for parsing (preserve k/K and m/M for multipliers)
    clean_text := REGEXP_REPLACE(salary_text, '[^\d\-\+\.,kKmM]', '', 'g');
    -- Normalize separators
    clean_text := REPLACE(clean_text, ',', '');
    
    -- Pattern 1: Range format (e.g., "100k-150k", "1M-1.5M", "80k-120000", "1.2m-1.8m")
    IF clean_text ~ '^(\d+(?:\.\d+)?)([kKmM]?)-(\d+(?:\.\d+)?)([kKmM]?)$' THEN
        matches := REGEXP_MATCHES(clean_text, '^(\d+(?:\.\d+)?)([kKmM]?)-(\d+(?:\.\d+)?)([kKmM]?)$');
        IF array_length(matches, 1) = 4 THEN
            -- Parse min value
            amount := matches[1];
            multiplier := CASE 
                WHEN matches[2] IN ('m','M') THEN 1000000
                WHEN matches[2] IN ('k','K') THEN 1000
                ELSE 1 
            END;
            min_salary := ROUND(CAST(amount AS NUMERIC) * multiplier)::INTEGER;
            
            -- Parse max value
            amount := matches[3];
            multiplier := CASE 
                WHEN matches[4] IN ('m','M') THEN 1000000
                WHEN matches[4] IN ('k','K') THEN 1000
                ELSE 1 
            END;
            max_salary := ROUND(CAST(amount AS NUMERIC) * multiplier)::INTEGER;
            
            RETURN NEXT;
            RETURN;
        END IF;
    
    -- Pattern 2: Minimum format (e.g., "100k+", "1M+", "100000+")
    ELSIF clean_text ~ '^(\d+(?:\.\d+)?)([kKmM]?)\+$' THEN
        matches := REGEXP_MATCHES(clean_text, '^(\d+(?:\.\d+)?)([kKmM]?)\+$');
        IF array_length(matches, 1) = 2 THEN
            amount := matches[1];
            multiplier := CASE 
                WHEN matches[2] IN ('m','M') THEN 1000000
                WHEN matches[2] IN ('k','K') THEN 1000
                ELSE 1 
            END;
            min_salary := ROUND(CAST(amount AS NUMERIC) * multiplier)::INTEGER;
            max_salary := NULL;
            
            RETURN NEXT;
            RETURN;
        END IF;
    
    -- Pattern 3: Single value (e.g., "100k", "1M", "100000", "1.5m")
    ELSIF clean_text ~ '^(\d+(?:\.\d+)?)([kKmM]?)$' THEN
        matches := REGEXP_MATCHES(clean_text, '^(\d+(?:\.\d+)?)([kKmM]?)$');
        IF array_length(matches, 1) = 2 THEN
            amount := matches[1];
            multiplier := CASE 
                WHEN matches[2] IN ('m','M') THEN 1000000
                WHEN matches[2] IN ('k','K') THEN 1000
                ELSE 1 
            END;
            min_salary := ROUND(CAST(amount AS NUMERIC) * multiplier)::INTEGER;
            max_salary := ROUND(CAST(amount AS NUMERIC) * multiplier)::INTEGER;
            
            RETURN NEXT;
            RETURN;
        END IF;
    END IF;

    -- If no patterns matched, return NULL values
    min_salary := NULL;
    max_salary := NULL;
    currency := NULL;
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Update existing records with parsed salary values
UPDATE jobs 
SET 
    salary_min_numeric = parsed.min_salary,
    salary_max_numeric = parsed.max_salary,
    salary_currency = parsed.currency
FROM (
    SELECT id, (parse_salary(salary)).*
    FROM jobs
) AS parsed
WHERE jobs.id = parsed.id;

-- Create a trigger to automatically parse salary on insert/update
CREATE OR REPLACE FUNCTION update_salary_numeric()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT * INTO NEW.salary_min_numeric, NEW.salary_max_numeric, NEW.salary_currency
        FROM parse_salary(NEW.salary);
    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.salary IS DISTINCT FROM OLD.salary THEN
            SELECT * INTO NEW.salary_min_numeric, NEW.salary_max_numeric, NEW.salary_currency
            FROM parse_salary(NEW.salary);
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_salary_numeric ON jobs;
CREATE TRIGGER trigger_update_salary_numeric
    BEFORE INSERT OR UPDATE OF salary ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_salary_numeric();

-- Verify the migration
SELECT 'Migration completed successfully' as status;
SELECT COUNT(*) as total_jobs,
       COUNT(salary_min_numeric) as jobs_with_min_salary,
       COUNT(salary_max_numeric) as jobs_with_max_salary,
       COUNT(salary_currency) as jobs_with_currency
FROM jobs;
