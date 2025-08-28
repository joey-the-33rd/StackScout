-- Debug script to understand regex group capturing
SELECT 'Debugging regex group capturing' as test_description;

-- Test individual regex patterns with explicit group capturing
SELECT 'Testing pattern: ^(\\d+(?:\\.\\d+)?)([kKmM]?)$' as pattern_test;
SELECT 
    '1M' as input,
    (REGEXP_MATCHES('1M', '^(\d+(?:\.\d+)?)([kKmM]?)$'))[1] as group1,
    (REGEXP_MATCHES('1M', '^(\d+(?:\.\d+)?)([kKmM]?)$'))[2] as group2;

SELECT 
    '100k' as input,
    (REGEXP_MATCHES('100k', '^(\d+(?:\.\d+)?)([kKmM]?)$'))[1] as group1,
    (REGEXP_MATCHES('100k', '^(\d+(?:\.\d+)?)([kKmM]?)$'))[2] as group2;

SELECT 
    '1.5M' as input,
    (REGEXP_MATCHES('1.5M', '^(\d+(?:\.\d+)?)([kKmM]?)$'))[1] as group1,
    (REGEXP_MATCHES('1.5M', '^(\d+(?:\.\d+)?)([kKmM]?)$'))[2] as group2;

-- Test range pattern
SELECT 'Testing pattern: ^(\\d+(?:\\.\\d+)?)([kKmM]?)-(\\d+(?:\\.\\d+)?)([kKmM]?)$' as pattern_test;
SELECT 
    '1M-2M' as input,
    (REGEXP_MATCHES('1M-2M', '^(\d+(?:\.\d+)?)([kKmM]?)-(\d+(?:\.\d+)?)([kKmM]?)$'))[1] as group1,
    (REGEXP_MATCHES('1M-2M', '^(\d+(?:\.\d+)?)([kKmM]?)-(\d+(?:\.\d+)?)([kKmM]?)$'))[2] as group2,
    (REGEXP_MATCHES('1M-2M', '^(\d+(?:\.\d+)?)([kKmM]?)-(\d+(?:\.\d+)?)([kKmM]?)$'))[3] as group3,
    (REGEXP_MATCHES('1M-2M', '^(\d+(?:\.\d+)?)([kKmM]?)-(\d+(?:\.\d+)?)([kKmM]?)$'))[4] as group4;
