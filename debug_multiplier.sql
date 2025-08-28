-- Debug script to test the multiplier logic
SELECT 'Debugging multiplier logic' as test_description;

-- Test the multiplier CASE statement
SELECT 'Testing multiplier for M suffix:' as test_case;
SELECT 
    'M' as suffix,
    CASE 
        WHEN 'M' IN ('m','M') THEN 1000000
        WHEN 'M' IN ('k','K') THEN 1000
        ELSE 1 
    END as multiplier;

SELECT 'Testing multiplier for k suffix:' as test_case;
SELECT 
    'k' as suffix,
    CASE 
        WHEN 'k' IN ('m','M') THEN 1000000
        WHEN 'k' IN ('k','K') THEN 1000
        ELSE 1 
    END as multiplier;

-- Test the full calculation
SELECT 'Testing full calculation for 1M:' as test_case;
SELECT 
    '1' as amount,
    'M' as suffix,
    CASE 
        WHEN 'M' IN ('m','M') THEN 1000000
        WHEN 'M' IN ('k','K') THEN 1000
        ELSE 1 
    END as multiplier,
    ROUND(CAST('1' AS NUMERIC) * 
        CASE 
            WHEN 'M' IN ('m','M') THEN 1000000
            WHEN 'M' IN ('k','K') THEN 1000
            ELSE 1 
        END)::INTEGER as result;

-- Test the full calculation for 1.5M
SELECT 'Testing full calculation for 1.5M:' as test_case;
SELECT 
    '1.5' as amount,
    'M' as suffix,
    CASE 
        WHEN 'M' IN ('m','M') THEN 1000000
        WHEN 'M' IN ('k','K') THEN 1000
        ELSE 1 
    END as multiplier,
    ROUND(CAST('1.5' AS NUMERIC) * 
        CASE 
            WHEN 'M' IN ('m','M') THEN 1000000
            WHEN 'M' IN ('k','K') THEN 1000
            ELSE 1 
        END)::INTEGER as result;
