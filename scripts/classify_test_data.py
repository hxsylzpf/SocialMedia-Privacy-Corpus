"""
    classify_test_data.py
    Performs classification on the test data, pulling the positive classes.
"""
import sys
import glob
from modules import config, data, helpers
from modules import classifier as classifierlib

# Data folder - should already exist
DATA_FOLDER_PATH = config.get_test_data_folder_path()

# Read in each file in the test set
print("Finding test data...")
test_data = glob.glob(DATA_FOLDER_PATH + "/*")

# Load the classifier from file
print("Loading classifier...")
filepath = config.get_classifier_pickle_file_path("ensemble")
(classifier, word_features, tag_features, use_core_words) = classifierlib.load_classifier_from_file(filepath)

# Perform classification on each file
print("Classifying...")
pos_class = []
neg_class = []
for i, td_file in enumerate(test_data):
    # Print progress
    sys.stdout.write("\r{}/{}".format(i + 1, len(test_data)))
    sys.stdout.flush()

    # Convert json string in file to object
    with open(td_file, 'r') as f:
        record_json = f.read().strip()
    record = helpers.json_string_to_object(record_json)

    # Classify
    classification = classifier.classify_record(record, word_features, tag_features, use_core_words)
    if classification:
        pos_class.append(record['id'])
    else:
        neg_class.append(record['id'])

# Write out results to file
print("Writing out results...")
(folderpath, yes_id_file, no_id_file) = config.get_classified_test_data_ids_path()
data.create_data_folder(folderpath)
with open(yes_id_file, 'w+') as f:
    f.write("\n".join(pos_class))
    print("  pos class written to {}".format(yes_id_file))
with open(no_id_file, 'w+') as f:
    f.write("\n".join(neg_class))
    print("  neg class written to {}".format(no_id_file))

# Print out statistics
print("\nDone!")
print("  Classified {} files".format(len(test_data)))
print("  pos: {}".format(len(pos_class)))
print("  neg: {}".format(len(neg_class)))
