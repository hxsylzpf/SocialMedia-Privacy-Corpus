import os
import sys
import json

# Import theguardian from the above folder
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from theguardian import theguardian_tag
from theguardian import theguardian_content

# Command line argument is the tag
if len(sys.argv) != 2:
    print("Usage: content_response.py [query string]")
    sys.exit()

with open('api_key', 'r') as f:
    api_key = f.readline().strip()

def json_print(str):
    print(json.dumps(str, indent=2))

headers = {
    "q": sys.argv[1]
}
tag = theguardian_tag.Tag(api=api_key, **headers)

# get the results
tag_content = tag.get_content_response()
results = tag.get_results(tag_content)

# get results for specific tag
first_tag_apiUrl = results[0]["apiUrl"]

# use this api url to content
content = theguardian_content.Content(api=api_key, url=first_tag_apiUrl)

# get content response
content_response = content.get_content_response()
json_print(content_response)
