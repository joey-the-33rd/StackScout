-- Debug script to simulate the full function logic
SELECT 'Debugging full function logic' as test_description;

-- Simulate the function logic for "1M"
SELECT 'Testing "1M":' as test_case;
WITH test_data AS (
    SELECT '1M' as salary_text
),
cleaned AS (
    SELECT 
        salary_text,
        REGEXP_REPLACE(salary_text, '[^\d\-\+\.,kKmM]', '', 'g') as clean_text1,
        REPLACE(REGEXP_REPLACE(salary_text, '[^\d\-\+\.,kKmM]', '', 'g'), ',', '') as clean_text
    FROM test_data
),
pattern_check AS (
    SELECT 
        clean_text,
        clean_text ~ '^(\d+(?:\.\d+)?)([kKmM]?)$' as matches_pattern3
    FROM cleaned
),
regex_matches AS (
    SELECT 
        clean_text,
        REGEXP_MATCHES(clean_text, '^(\d+(?:\.\d+)?)([kKmM]?)$') as matches
    FROM cleaned
    WHERE clean_text ~ '^(\d+(?:\.\d+)?)([kKmM]?)$'
)
SELECT 
    c.salary_text,
    c.clean_text,
    p.matches_pattern3,
    r.matches,
    r.matches[1] as amount,
    r.matches[2] as suffix,
    CASE 
        WHEN r.matches[2] IN ('m','M') THEN 1000000
        WHEN r.matches[2] IN ('k','K') THEN 1000
        ELSE 1 
    END as multiplier,
    ROUND(CAST(r.matches[1] AS NUMERIC) * 
        CASE 
            WHEN r.matches[2] IN ('m','M') THEN 1000000
            WHEN r.matches[2] IN ('k','K') THEN 1000
            ELSE 1 
        END)::INTEGER as result
FROM cleaned c
LEFT JOIN pattern_check p ON true
LEFT JOIN regex_matches r ON true;

-- Simulate the function logic for "100k" (should work)
SELECT 'Testing "100k":' as test_case;
WITH test_data AS (
    SELECT '100k' as salary_text
),
cleaned AS (
    SELECT 
        salary_text,
        REGEXP_REPLACE(salary_text, '[^\d\-\+\.,kKmM]', '', 'g') as clean_text1,
        REPLACE(REGEXP_REPLACE(salary_text, '[^\d\-\+\.,kKmM]', '', 'g'), ',', '') as clean_text
    FROM test_data
),
pattern_check AS (
    SELECT 
        clean_text,
        clean_text ~ '^(\d+(?:\.\d+)?)([kKmM]?)$' as matches_pattern3
    FROM cleaned
),
regex_matches AS (
    SELECT 
        clean_text,
        REGEXP_MATCHES(clean_text, '^(\d+(?:\.\d+)?)([kKmM]?)$') as matches
    FROM cleaned
    WHERE clean_text ~ '^(\d+(?:\.\d+)?)([kKmM]?)$'
)
SELECT 
    c.salary_text,
    c.clean_text,
    p.matches_pattern3,
    r.matches,
    r.matches[1] as amount,
    r.matches[2] as suffix,
    CASE 
        WHEN r.matches[2] IN ('m','M') THEN 1000000
        WHEN r.matches[2] IN ('k','K') THEN 1000
        ELSE 1 
    END as multiplier,
    ROUND(CAST(r.matches[1] AS NUMERIC) * 
        CASE 
            WHEN r.matches[2] IN ('m','M') THEN 1000000
            WHEN r.matches[2] IN ('k','K') THEN 1000
            ELSE 1 
        END)::INTEGER as result
FROM cleaned c
LEFT JOIN pattern_check p ON true
LEFT JOIN regex_matches r ON true;
