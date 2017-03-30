import os
import sys
import json

# Import theguardian from the above folder
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
from theguardian import theguardian_tag

# Command line argument is the tag
if len(sys.argv) != 2:
    print("Usage: find_tags.py [query string]")
    sys.exit()

with open('api_key', 'r') as f:
    api_key = f.readline().strip()

header = {
    "q": sys.argv[1]
}

tags = theguardian_tag.Tag(api=api_key, **header)
page_num = 1
while True:
    try:
        tag_results = tags.get_references_in_page(page_num)
        for r in tag_results:
            if "sectionId" in r:
                print("id={}, sectionId={}".format(r["id"], r["sectionId"]))
            else:
                print("id={}, sectionId=".format(r["id"]))
        page_num = page_num + 1
    except ValueError:
        break
