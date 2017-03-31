"""
    helpers.py
    Responsible for miscellenous helper functions
"""
import json
import hashlib

# Pretty print a JSON string
def json_print(string):
    print(json.dumps(string, indent=2))

# Convert json object to string
def json_string(string, pretty=True):
    if pretty:
        return json.dumps(string, indent=2)
    else:
        return json.dumps(string)

# Get MD5 hash
def md5_hash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()
