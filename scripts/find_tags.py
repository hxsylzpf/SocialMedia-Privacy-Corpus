import sys
from modules import api

# Command line argument is the tag
if len(sys.argv) != 2:
    print("Usage: find_tags.py [query string]")
    sys.exit()

print(api.get_tag_ids_for_query(sys.argv[1]))
