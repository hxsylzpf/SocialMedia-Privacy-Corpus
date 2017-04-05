"""
    helpers.py
    Responsible for miscellenous helper functions
"""
import json
import hashlib
import random

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

# Randomly shuffle a list
def random_shuffle(slist):
    return random.sample(slist, len(slist))

# Get a random sample from a list
def random_sample(slist):
    return random.choice(slist)

# Filters out puncutation that may break the NLP processing
def remove_bad_puncutation(text):
    return text.replace('‘', '\'').replace('’', '\'').replace('“', '\"').replace('”', '\"')

# Santizes text for our application
def sanitize(text):
    return remove_bad_puncutation(text)
