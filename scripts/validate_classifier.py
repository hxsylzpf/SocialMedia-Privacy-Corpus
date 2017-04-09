"""
    validate_classifier.py
    Validate the classifier using cross-validation
"""
import os
import sys
import glob
from modules import config, helpers
from modules.classifier import NaiveBayesPrivacyClassifierFactory

CLASSIFY_WITH_WORDS = True
CLASSIFY_WITH_TAGS = True

# Command line argument specifies the number of folds to use
if len(sys.argv) != 2:
    print("Usage: validate_classifier.py [# of folds]")
    sys.exit(1)
numFolds = int(sys.argv[1])

# Get all downloaded training data paths
(DATA_FOLDER_PATH, YES_FOLDER_PATH, NO_FOLDER_PATH) = config.get_training_data_folder_paths()
print("Looking for downloaded training data...")
if not os.path.exists(YES_FOLDER_PATH) or not os.path.exists(NO_FOLDER_PATH):
    print("ERROR: Missing training data files! Run download script first.")
    sys.exit()
training_data_files = glob.glob(YES_FOLDER_PATH + "/*") + glob.glob(NO_FOLDER_PATH + "/*")

# Read all of the training data in and parse them into objects
print("Parsing training data...")
training_data = []
for fp in training_data_files:
    with open(fp, 'r') as f:
        record = helpers.json_string_to_object(f.read().strip())
        training_data.append(record)

# Get a Naive-Bayes Classifier factory object to setup the classifier for validation
print("Setting up classifier...")
classifier_factory = NaiveBayesPrivacyClassifierFactory()
classifier_factory.set_training_data(training_data)

# Perform cross-validation
metrics = classifier_factory.cross_validate(numFolds, output=True)

# Print out metrics
print("Done!")
print("\nStatistics")
print("    Accuracy: {}".format(metrics.accuracy))
print("    Precision: {}".format(metrics.precision))
print("    Recall: {}".format(metrics.recall))
print("    F-Measure: {}".format(metrics.fmeasure))
