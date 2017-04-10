import os
import sys
import glob
from modules import config, helpers
from modules.classifier import KeywordPrivacyClassifierFactory

# Get all downloaded training data paths
(DATA_FOLDER_PATH, YES_FOLDER_PATH, NO_FOLDER_PATH) = config.get_training_data_folder_paths()
print("Looking for downloaded training data...")
if not os.path.exists(YES_FOLDER_PATH) or not os.path.exists(NO_FOLDER_PATH):
    print("ERROR: Missing training data files! Run download script first.")
    sys.exit()
training_data_files = glob.glob(NO_FOLDER_PATH + "/*") + glob.glob(YES_FOLDER_PATH + "/*")

# Read all of the training data in and parse them into objects
print("Parsing training data...")
training_data = []
for fp in training_data_files:
    with open(fp, 'r') as f:
        record = helpers.json_string_to_object(f.read().strip())
        training_data.append(record)

# Classifier
classifier_factory = KeywordPrivacyClassifierFactory()
classifier = classifier_factory.build_classifier()

# Find precision issues
print("Precision Error")
for record in training_data:
    if not record['class'] and classifier.classify(record['content']):
        print(record['id'])

print("")

# Find recall issues
print("Recall Error")
for record in training_data:
    if record['class'] and not classifier.classify(record['content']):
        print(record['id'])
