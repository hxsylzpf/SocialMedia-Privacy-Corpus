"""
    compare_classifiers.py
    Compare various classifiers using cross-validation
"""
import os
import sys
import glob
import time
import random
from tabulate import tabulate
from modules.classifier import *
from modules import config, helpers

# Number of tests to run. If 1, uses known random seed.
NUM_TESTS = 1

# Set random seed. If number of tests = 1, use known random seed.
if NUM_TESTS == 1:
    RANDOM_SEED = "495/591"
else:
    RANDOM_SEED = random.randint(0, 10000)

# List of classifiers to test - should have an appropriate factory
classifers = [
    # Classifier Name               UseCoreWords UseAllWords UseTags
    ("NaiveBayesPrivacyClassifier", True,        False,      True),  # N-B core words + tags
    ("NaiveBayesPrivacyClassifier", False,       True,       True),  # N-B all words + tags
    ("NaiveBayesPrivacyClassifier", True,        False,      False), # N-B core words only
    ("NaiveBayesPrivacyClassifier", False,       True,       False), # N-B all words only
    ("NaiveBayesPrivacyClassifier", False,       False,      True),  # N-B tags only
    ("KeywordPrivacyClassifier",    None,        None,       None),  # N-B keywords
    ("TagPrivacyClassifier",        None,        None,       None)   # N-B tags
]

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

# Get a Naive-Bayes Classifier factory object to setup the classifier for validation
metrics = []
for i in range(NUM_TESTS):
    for classifier in classifers:
        print("Validating classifier {} (useCoreWords={}, useAllWords={}, useTags={})..."
            .format(classifier[0], classifier[1], classifier[2], classifier[3]))

        # Get classifier factory
        classifier_factory_classname = "{}Factory".format(classifier[0])
        classifier_factory_class = getattr(sys.modules[__name__], classifier_factory_classname)
        classifier_factory = classifier_factory_class(useCoreWords=classifier[1],
                                                      useAllWords=classifier[2],
                                                      useTags=classifier[3])
        classifier_factory.set_training_data(training_data)

        # Set random seed for reproducability
        helpers.set_random_seed(RANDOM_SEED)

        # Perform cross-validation
        metrics_results = classifier_factory.cross_validate(numFolds)

        # Compute train time
        start = time.process_time()
        classifier_factory.build_classifier()
        end = time.process_time()
        metrics_results.train_time = end - start

        # Compute average classify time - we don't have a great way to do this
        # at the moment
        start = time.process_time()
        classifier_factory.compute_metrics_from_test_data(training_data)
        end = time.process_time()
        metrics_results.test_time = (end - start)/len(training_data)

        # Store results
        metrics.append(list(classifier) + [metrics_results])
            #[v for (k, v) in sorted(metrics_results.__dict__.items())])

# Sort metrics
metrics = sorted(metrics, key=lambda x: (x[0], x[1], x[2], x[3]))

# Average metrics
averaged_metrics = []
for i in range(0, len(metrics), NUM_TESTS):
    sublist = metrics[i:i + NUM_TESTS]
    metric = PrivacyClassifierMetrics()
    metric.accuracy = sum(x[len(classifier)].accuracy for x in sublist)/float(NUM_TESTS)
    metric.fmeasure = sum(x[len(classifier)].fmeasure for x in sublist)/float(NUM_TESTS)
    metric.precision = sum(x[len(classifier)].precision for x in sublist)/float(NUM_TESTS)
    metric.recall = sum(x[len(classifier)].recall for x in sublist)/float(NUM_TESTS)
    metric.test_time = sum(x[len(classifier)].test_time for x in sublist)/float(NUM_TESTS)
    metric.train_time = sum(x[len(classifier)].train_time for x in sublist)/float(NUM_TESTS)
    averaged_metrics.append(sublist[0][:len(classifier)] +
        [v for (k, v) in sorted(metric.__dict__.items())])

# Print
print()
print("* Averaged over {} iterations".format(NUM_TESTS))
print()
headers = ["Classifier", "UseCoreWords", "UseAllWords", "UseTags"] + [k for (k, v) in sorted(metrics_results.__dict__.items())]
print(tabulate(averaged_metrics, headers=headers))
