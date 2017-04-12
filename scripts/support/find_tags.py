# Include the modules from parent directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules import api

# Command line argument is the tag
if len(sys.argv) != 2:
    print("Usage: find_tags.py [query string]")
    sys.exit(1)

print(api.get_tag_ids_for_query(sys.argv[1]))
