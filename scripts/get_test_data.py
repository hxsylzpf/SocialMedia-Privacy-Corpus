"""
    get_test_data.py
    Sources the test data IDs and moves them into the test data folder

    Use optional parameter "update" to re-retrieve all API, no reuse.
"""
import os
import sys
from modules import config, data, helpers, test_data

# If optional parameter "update" provided, do not reuse existing files
if len(sys.argv) == 2 and sys.argv[1] == "update":
    shouldReuse = False
else:
    shouldReuse = True

# Data folders
DATA_FOLDER_PATH = config.get_test_data_folder_path()

# Form data directory structure
print("Verifying directory structure...")
data.create_data_folder(DATA_FOLDER_PATH)

# ID file containing IDs of data to retrieve
(TEST_ID_DATA_PATH, ID_FILE) = config.get_test_data_id_file_paths()

# Copy pre-downloaded test data to the directory
if shouldReuse:
    print("Copying pre-downloaded data...")
    predownloaded_dir = os.path.join(TEST_ID_DATA_PATH, "downloaded_data")
    data.copy_between_folders(predownloaded_dir, DATA_FOLDER_PATH)

# Verify ID file exists
print("Reading ID files...")
if not os.path.exists(ID_FILE):
    print("ERROR: Missing ID file! {}".format(ID_FILE))
    sys.exit(1)

# Read ID file
with open(ID_FILE, 'r') as f:
    ids = [x.strip() for x in f.readlines()]

# Generate MD5 hashes of each ID. The MD5 hashes are used as the filename.
hashes = [helpers.md5_hash(i) for i in ids]

# Delete files that are not in the ID lists
print("Cleaning out data folders...")
for f in os.listdir(DATA_FOLDER_PATH):
    if f not in hashes:
        data.delete_file(os.path.join(DATA_FOLDER_PATH, f))

# Retrieve the content for each ID and write it out to file
try:
    print("Retrieving data...")
    (retrieved, cached) = test_data.get_test_data_files_for_ids(ids, hashes, DATA_FOLDER_PATH, shouldReuse, True)
except:
    raise
    print("\nERROR: Possibly invalid id in ID file - see above index. Perhaps the ID leads to a video or image?")
    print("\nERROR: Possibly hit API limit?")
    sys.exit(1)

# Print out statistics
print("Done!")
print("  Retrieved {} files from API".format(retrieved))
print("  Reused {} existing files".format(cached))
