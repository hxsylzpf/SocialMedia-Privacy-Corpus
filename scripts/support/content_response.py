# Include the modules from parent directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules import api, helpers

# Command line argument is the tag
if len(sys.argv) != 2:
    print("Usage: content_response.py [query string]")
    sys.exit(1)

helpers.json_print(api.get_content_response_for_query(sys.argv[1]))
