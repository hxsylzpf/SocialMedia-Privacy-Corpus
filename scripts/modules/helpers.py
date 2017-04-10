"""
    helpers.py
    Responsible for miscellenous helper functions
"""
import json
import random
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

# Randomly shuffle a list
def random_shuffle(slist):
    return random.sample(slist, len(slist))

# Get a random sample from a list
def random_sample(slist):
    return random.choice(slist)

# Filters out puncutation that may break the NLP processing
def remove_bad_puncutation(text):
    return text.replace('‘', '\'').replace('’', '\'').replace('“', '\"').replace('”', '\"')

# Attempts to filter out related articles from the text
def remove_related_articles(text):
    # Related articles appear after a bullet point at the end of the text
    # Look for the last period in the article, remove all text after if bullet
    index = text.rfind('.') + 1
    if text[index:].strip()[0] == '•':
        return text[:index]
    return text

# Santizes text for our application
def sanitize(text):
    text = remove_bad_puncutation(text)
    text = remove_related_articles(text)
    return text

# Splits a list into N equal parts:
def split(a, n):
    k, m = divmod(len(a), n)
    return list((a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)))

# Compute the average of a list
def average(alist):
    return sum(alist) / len(alist)

# Sets the random seed
def set_random_seed(seed):
    random.seed(seed)
