# Include the modules from parent directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules import api, helpers, config

# Command line arguments
if len(sys.argv) != 4:
    print("Usage: find_test_data.py [type] [search_string] [printToFile (true or false)]")
    sys.exit(1)

# Max number of pages we want to retrieve
MAX_PAGES = 100

search_type = sys.argv[1]
search_string = sys.argv[2]
print_to_file = sys.argv[3]

if ( (print_to_file != "true") and (print_to_file != "false")):
    print("Usage: printToFile must be 'true' or 'false'")
    sys.exit(1)

folder_path, id_path = config.get_test_data_id_file_paths()
with open(id_path, "r") as f:
    # bring in existing ids from test_data/ids
    existing_id_set = set([x.strip() for x in f.readlines()])

# Searching by tag
if (search_type == "tag"):
    # get the first page of results and the number of pages
    numPages, results = api.get_ids_for_query(tags=search_string)
    results_id_set = set(results)

    numPages = MAX_PAGES if numPages > MAX_PAGES else numPages
    # get the rest of the results
    for i in range( 2, numPages + 1):
        p, results = api.get_ids_for_query(tags=search_string, pageNum=i)
        results_id_set.update(results)

    print("{} ids retrieved".format(len(results_id_set)))

# Searching by keyword
elif (search_type == "content"):
    # get the first page of results and te number of pages
    numPages, results = api.get_ids_for_query(keywords=search_string)
    results_id_set = set(results)

    numPages = MAX_PAGES if numPages > MAX_PAGES else numPages
    # get the rest of the results
    for i in range( 2, numPages + 1):
        p, results = api.get_ids_for_query(keywords=search_string, pageNum=i)
        results_id_set.update(results)

    print("{} ids retrieved".format(len(results_id_set)))

else:
    # only have support for a search by tag or content
    print("Usage: type is either 'tag' or 'content' ")
    sys.exit(1)

# add new ids to id file
ids_to_be_added = results_id_set - existing_id_set
print("{} ids added".format(len(ids_to_be_added)))

if (print_to_file == "true") :
    with open(id_path, "a") as f:
        to_append = "\n".join(ids_to_be_added)
        f.write(to_append)
        f.write('\n')
elif (print_to_file == "false"):
    to_print = "\n".join(ids_to_be_added)
    print(to_print)
