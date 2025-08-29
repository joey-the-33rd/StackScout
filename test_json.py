import json

# Test data
test_data = {
    "key1": "value1",
    "key2": "value2",
    "key3": {
        "nested_key1": "nested_value1",
        "nested_key2": "nested_value2"
    },
    "key4": [1, 2, 3, 4, 5]
}

# Test JSON formatting
print("Testing JSON formatting:")
json_str = json.dumps(test_data)
print("Default formatting:")
print(json_str)
print()

print("Compact formatting:")
json_str_compact = json.dumps(test_data, separators=(',', ':'))
print(json_str_compact)
print()

print("Pretty formatting:")
json_str_pretty = json.dumps(test_data, indent=2)
print(json_str_pretty)
