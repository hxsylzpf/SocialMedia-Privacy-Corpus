"""
    get_training_data.py
    Sources the data IDs and moves them into folders

    Use optional parameter "update" to re-retrieve all API, no reuse.
"""
import os
import sys
from modules import config, data, helpers, training_data

# If optional parameter "clean" provided, do not reuse existing files
if len(sys.argv) == 2 and sys.argv[1] == "update":
    shouldReuse = False
else:
    shouldReuse = True

# Data folders
(DATA_FOLDER_PATH, YES_FOLDER_PATH, NO_FOLDER_PATH) = config.get_training_data_folder_paths()

# Form data directory structure
print("Verifying directory structure...")
for folder in (DATA_FOLDER_PATH, YES_FOLDER_PATH, NO_FOLDER_PATH):
    data.create_data_folder(folder)

# ID files containing IDs of data to retreieve
(TRAINING_DATA_PATH, YES_ID_FILE, NO_ID_FILE) = config.get_training_data_id_file_paths()

# Verify ID files exist
print("Reading ID files...")
if not os.path.exists(YES_ID_FILE) or not os.path.exists(NO_ID_FILE):
    print("Missing ID files! yes.ids and no.ids")
    sys.exit()

# Read ID files
with open(YES_ID_FILE, 'r') as f:
    yes_ids = [x.strip() for x in f.readlines()]
with open(NO_ID_FILE, 'r') as f:
    no_ids = [x.strip() for x in f.readlines()]

# Generate MD5 hashes of each ID. The MD5 hashes are used as the filename.
yes_hashes = [helpers.md5_hash(i) for i in yes_ids]
no_hashes = [helpers.md5_hash(i) for i in no_ids]

# Delete files that are not in the ID lists
print("Cleaning out data folders...")
for f in os.listdir(YES_FOLDER_PATH):
    if f not in yes_hashes:
        data.delete_file(os.path.join(YES_FOLDER_PATH, f))
for f in os.listdir(NO_FOLDER_PATH):
    if f not in no_hashes:
        data.delete_file(os.path.join(NO_FOLDER_PATH, f))

# Retrieve the content for each ID and write it out to file
print("Retrieving data...")
(yesRetrieved, yesCached) = training_data.get_training_data_files_for_ids(yes_ids, yes_hashes, YES_FOLDER_PATH, True, shouldReuse)
(noRetrieved, noCached) = training_data.get_training_data_files_for_ids(no_ids, no_hashes, NO_FOLDER_PATH, False, shouldReuse)

# Print out statistics
print("Done!")
print("  Retrieved {} files from API".format(yesRetrieved + noRetrieved))
print("  Reused {} existing files".format(yesCached + noCached))
