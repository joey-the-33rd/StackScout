-- Detailed debug script to see what's happening in the parsing
SELECT 'Detailed debugging' as test_description;

-- Test the cleaning process
SELECT 
    '1M' as original,
    REGEXP_REPLACE('1M', '[^\d\-\+\.,kKmM]', '', 'g') as cleaned,
    REPLACE(REGEXP_REPLACE('1M', '[^\d\-\+\.,kKmM]', '', 'g'), ',', '') as final_clean;

-- Test what the regex captures for each pattern
SELECT 'Pattern 1 (range) test:' as test_type;
SELECT 
    '1M-2M' as input,
    REGEXP_MATCHES('1M-2M', '^(\d+(?:\.\d+)?)([kKmM]?)-(\d+(?:\.\d+)?)([kKmM]?)$') as matches;

SELECT 'Pattern 2 (minimum) test:' as test_type;
SELECT 
    '1M+' as input,
    REGEXP_MATCHES('1M+', '^(\d+(?:\.\d+)?)([kKmM]?)\+$') as matches;

SELECT 'Pattern 3 (single) test:' as test_type;
SELECT 
    '1M' as input,
    REGEXP_MATCHES('1M', '^(\d+(?:\.\d+)?)([kKmM]?)$') as matches;

-- Test with thousand suffix for comparison
SELECT 'Thousand suffix test:' as test_type;
SELECT 
    '100k' as input,
    REGEXP_MATCHES('100k', '^(\d+(?:\.\d+)?)([kKmM]?)$') as matches;
