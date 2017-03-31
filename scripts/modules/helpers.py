"""
    helpers.py
    Responsible for miscellenous helper functions
"""
import json
import hashlib

# Pretty print a JSON object
def json_print(obj):
    print(json.dumps(obj, indent=2))

# Convert json object to string
def json_object_to_string(obj, pretty=True):
    if pretty:
        return json.dumps(obj, indent=2)
    else:
        return json.dumps(obj)

# Convert json string to object
def json_string_to_object(string):
    return json.loads(string)

# Get MD5 hash
def md5_hash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()
