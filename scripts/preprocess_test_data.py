"""
    preprocess_test_data.py
    Performs preprocessing on the test data
        - pull core words from summarization

    Use optional parameter "update" to re-do preprocessing
    Use optional parameter "remove" to delete all preprocessing
"""
import sys
import glob
from modules import config, data, helpers, preprocessing

# If optional parameter "clean" provided, do not reuse existing preprocessing
shouldReuse = True
shouldRemove = False
if len(sys.argv) == 2:
    if sys.argv[1] == "update":
        shouldReuse = False
    elif sys.argv[1] == "remove":
        shouldRemove = True
    else:
        print("ERROR: Invalid argument specified")
        sys.exit(1)

# Data folder - should already exist
DATA_FOLDER_PATH = config.get_test_data_folder_path()

# Read in each file in the test set
print("Finding test data...")
test_data = glob.glob(DATA_FOLDER_PATH + "/*")

# If the user specified remove, then we want to remove preprocessing
if shouldRemove:
    print("Removing preprocessing...")
    for td_file in test_data:
        # Convert json string in file to object
        with open(td_file, 'r') as f:
            record_json = f.read().strip()
        record = helpers.json_string_to_object(record_json)

        # Remove the preprocessing
        preprocessing.remove_preprocessing()

        # Write the record back out to its file
        record_json = helpers.json_object_to_string(record)
        data.write_string_to_file(td_file, record_json)
    print("Done!")
    sys.exit(0)

# Perform preprocessing on each file and write it back out to the file
print("Preprocessing...")
totalPreprocessed = 0
totalReused = 0
for i, td_file in enumerate(training_data):
    # Convert json string in file to object
    with open(td_file, 'r') as f:
        record_json = f.read().strip()
    record = helpers.json_string_to_object(record_json)

    # Perform preprocessing
    didPreprocessing = preprocessing.preprocess(record, shouldReuse)
    if didPreprocessing:
        totalPreprocessed += 1
        # Write the record back out to its file
        record_json = helpers.json_object_to_string(record)
        data.write_string_to_file(td_file, record_json)
    else:
        totalReused += 1

    # Print progress
    sys.stdout.write("\r{}/{}".format(i + 1, len(training_data)))
    sys.stdout.flush()

# Print out statistics
print("\nDone!")
print("  Preprocessed {} files".format(totalPreprocessed))
print("  Reused {} existing results".format(totalReused))
