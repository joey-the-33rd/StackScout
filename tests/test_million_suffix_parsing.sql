-- Test script for million suffix parsing in the parse_salary function
-- Run with: psql -U your_username -d your_database -f test_million_suffix_parsing.sql

-- Test cases for million suffix parsing
SELECT 'Testing million suffix parsing' as test_description;

-- Test 1: Single million values
SELECT 
    '1M' as input,
    (parse_salary('1M')).* as result,
    'Expected: (1000000, 1000000, NULL)' as expected;

SELECT 
    '1.5M' as input,
    (parse_salary('1.5M')).* as result,
    'Expected: (1500000, 1500000, NULL)' as expected;

SELECT 
    '$1M' as input,
    (parse_salary('$1M')).* as result,
    'Expected: (1000000, 1000000, USD)' as expected;

-- Test 2: Million range values
SELECT 
    '1M-2M' as input,
    (parse_salary('1M-2M')).* as result,
    'Expected: (1000000, 2000000, NULL)' as expected;

SELECT 
    '1.2M-1.8M' as input,
    (parse_salary('1.2M-1.8M')).* as result,
    'Expected: (1200000, 1800000, NULL)' as expected;

-- Test 3: Million minimum values
SELECT 
    '1M+' as input,
    (parse_salary('1M+')).* as result,
    'Expected: (1000000, NULL, NULL)' as expected;

-- Test 4: Mixed thousand and million (edge case)
SELECT 
    '100k-1M' as input,
    (parse_salary('100k-1M')).* as result,
    'Expected: (100000, 1000000, NULL)' as expected;

-- Test 5: Ensure thousand parsing still works
SELECT 
    '100k' as input,
    (parse_salary('100k')).* as result,
    'Expected: (100000, 100000, NULL)' as expected;

SELECT 
    '100k-200k' as input,
    (parse_salary('100k-200k')).* as result,
    'Expected: (100000, 200000, NULL)' as expected;

-- Test 6: Invalid inputs
SELECT 
    'invalid' as input,
    (parse_salary('invalid')).* as result,
    'Expected: (NULL, NULL, NULL)' as expected;

SELECT 
    '' as input,
    (parse_salary('')).* as result,
    'Expected: (NULL, NULL, NULL)' as expected;

SELECT 
    NULL as input,
    (parse_salary(NULL)).* as result,
    'Expected: (NULL, NULL, NULL)' as expected;
