-- Debug script to see what the regex patterns are capturing
SELECT 'Debugging regex patterns' as test_description;

-- Test what the regex captures for "1M"
SELECT 
    '1M' as input,
    REGEXP_MATCHES('1M', '^(\d+(?:\.\d+)?)([kKmM]?)$') as matches;

-- Test what the regex captures for "1.5M"  
SELECT 
    '1.5M' as input,
    REGEXP_MATCHES('1.5M', '^(\d+(?:\.\d+)?)([kKmM]?)$') as matches;

-- Test what the regex captures for "1M-2M"
SELECT 
    '1M-2M' as input,
    REGEXP_MATCHES('1M-2M', '^(\d+(?:\.\d+)?)([kKmM]?)-(\d+(?:\.\d+)?)([kKmM]?)$') as matches;

-- Test what the regex captures for "100k"
SELECT 
    '100k' as input,
    REGEXP_MATCHES('100k', '^(\d+(?:\.\d+)?)([kKmM]?)$') as matches;
