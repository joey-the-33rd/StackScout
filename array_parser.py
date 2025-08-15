"""
PostgreSQL Array Parser Utility
Handles proper conversion of PostgreSQL array strings to Python lists
"""

import re
import csv
from io import StringIO
from typing import List, Union

def parse_postgres_array(array_str: Union[str, list]) -> List[str]:
    """
    Properly parse PostgreSQL array strings to Python lists
    
    Args:
        array_str: PostgreSQL array string or Python list
        
    Returns:
        List of strings parsed from the array
        
    Examples:
        >>> parse_postgres_array('{python,django,flask}')
        ['python', 'django', 'flask']
        
        >>> parse_postgres_array('{"python, django","flask, fastapi"}')
        ['python, django', 'flask, fastapi']
        
        >>> parse_postgres_array(['python', 'django'])
        ['python', 'django']
    """
    if not array_str:
        return []
    
    # If already a list, return as-is
    if isinstance(array_str, list):
        return array_str
    
    # Handle empty or null strings
    if not isinstance(array_str, str) or not array_str.strip():
        return []
    
    # Clean the string
    array_str = array_str.strip()
    
    # Handle empty array
    if array_str == '{}' or array_str == '[]':
        return []
    
    # Remove outer braces/brackets
    if array_str.startswith('{') and array_str.endswith('}'):
        content = array_str[1:-1]
    elif array_str.startswith('[') and array_str.endswith(']'):
        content = array_str[1:-1]
    else:
        content = array_str
    
    # Handle empty content
    if not content.strip():
        return []
    
    # Use CSV parser for proper quote handling
    try:
        # Handle PostgreSQL array format with proper escaping
        content = content.replace('\\"', '""')
        
        # Use CSV parser
        f = StringIO(content)
        reader = csv.reader(f, delimiter=',', quotechar='"', skipinitialspace=True)
        items = next(reader, [])
        
        # Clean up items
        items = [item.strip() for item in items if item.strip()]
        
        # Handle edge cases where items might still be quoted
        cleaned_items = []
        for item in items:
            # Remove outer quotes if present
            if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                item = item[1:-1]
            cleaned_items.append(item)
        
        return cleaned_items
    
    except Exception as e:
        # Fallback to regex-based parsing for edge cases
        return _fallback_parse_array(content)

def _fallback_parse_array(content: str) -> List[str]:
    """Fallback parser for edge cases"""
    # Split by comma but respect quotes
    pattern = r'"([^"]*)"|\s*([^,]+)\s*'
    matches = re.findall(pattern, content)
    
    items = []
    for quoted, unquoted in matches:
        item = quoted if quoted else unquoted
        if item.strip():
            items.append(item.strip())
    
    return items

def test_array_parser():
    """Test the array parser with various inputs"""
    test_cases = [
        '{python,django,flask}',
        '{"python, django","flask, fastapi"}',
        "{python,'django, flask',javascript}",
        '["python", "django, flask"]',
        '{single-item}',
        '{}',
        '[]',
        None,
        ['already', 'a', 'list'],
        '{item with "quotes", another "item"}',
        "{item with 'single quotes', another 'item'}",
    ]
    
    print("Testing PostgreSQL array parser:")
    for test in test_cases:
        result = parse_postgres_array(test)
        print(f"Input: {test} -> Output: {result}")

if __name__ == "__main__":
    test_array_parser()
