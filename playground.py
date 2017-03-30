import json
from theguardian import theguardian_tag

def json_print(str):
    print(json.dumps(str, indent=2))

with open('api_key', 'r') as f:
    api_key = f.readline().strip()

header = {
    "q": "apple"
}

t = theguardian_tag.Tag(api=api_key, **header)
json_print(t.get_references_in_page())
