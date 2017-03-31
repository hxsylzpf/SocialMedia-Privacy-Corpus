import sys
from modules import api, helpers

# Command line argument is the tag
if len(sys.argv) != 2:
    print("Usage: content_response.py [query string]")
    sys.exit()

helpers.json_print(api.get_content_response_for_query(sys.argv[1]))
