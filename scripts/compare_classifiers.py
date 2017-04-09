"""
    compare_classifiers.py
    Compare various classifiers using cross-validation
"""
import os
import sys
import glob
from tabulate import tabulate
from modules.classifier import *
from modules import config, helpers

# List of classifiers to test - should have an appropriate factory
classifers = [
    # Classifier Name         UseCoreWords UseTags
    ("NaiveBayesPrivacyClassifier", True, True),
    ("NaiveBayesPrivacyClassifier", False, True),
    ("NaiveBayesPrivacyClassifier", True, False),
    ("KeywordPrivacyClassifier", None, None),
    ("TagPrivacyClassifier", None, None)
]

# Random seed to ensure comparability across classifiers
RANDOM_SEED = "495/591"

# Command line argument specifies the number of folds to use
if len(sys.argv) != 2:
    print("Usage: compare_classifiers.py [# of folds]")
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

# Set random seed for reproducability
helpers.set_random_seed(RANDOM_SEED)

# Get a Naive-Bayes Classifier factory object to setup the classifier for validation
metrics = []
for classifier in classifers:
    print("Validating classifier {} (useWords={}, useTags={})..."
        .format(classifier[0], classifier[1], classifier[2]))

    # Get classifier factory
    classifier_factory_classname = "{}Factory".format(classifier[0])
    classifier_factory_class = getattr(sys.modules[__name__], classifier_factory_classname)
    classifier_factory = classifier_factory_class(useCoreWords=classifier[1],
                                                  useTags=classifier[2])
    classifier_factory.set_training_data(training_data)

    # Perform cross-validation
    metrics_results = classifier_factory.cross_validate(numFolds)

    # Store results
    metrics.append(list(classifier) + \
        [v for (k, v) in sorted(metrics_results.__dict__.items())])

print("Done!")
print("")

# Print out metrics
headers = ["Classifier", "UseWords", "UseTags"] + [k for (k, v) in sorted(metrics_results.__dict__.items())]
print(tabulate(metrics, headers=headers))
