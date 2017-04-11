"""
    build_classifier.py
    Builds a classifier from the training data
    Reference: http://www.nltk.org/book/ch06.html
"""
import os
import sys
import glob
from modules import config, helpers
from modules import classifier as classifierlib
from modules.classifier import *

CLASSIFY_WITH_CORE_WORDS = True
CLASSIFY_WITH_ALL_WORDS = not CLASSIFY_WITH_CORE_WORDS
CLASSIFY_WITH_TAGS = True
CLASSIFY_WITH_LIMIT = None
CLASSIFY_WITH_ACCURACY_WEIGHTS = True

# Set random seed to the one we know
helpers.set_random_seed(config.get_random_seed())

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

# Get a classifier factory object of our chosing to build the classifier
print("Building classifier...")
classifier_factory = EnsemblePrivacyClassifierFactory(use_core_words=CLASSIFY_WITH_CORE_WORDS,
                                                      use_all_words=CLASSIFY_WITH_ALL_WORDS,
                                                      use_tags=CLASSIFY_WITH_TAGS,
                                                      word_limit=CLASSIFY_WITH_LIMIT,
                                                      use_accuracy_weighted=CLASSIFY_WITH_ACCURACY_WEIGHTS)

# Add training data to classifier
classifier_factory.set_training_data(training_data)

# Build classifier
classifier = classifier_factory.build_classifier()

# Write out classifier factory to file
filepath = config.get_classifier_pickle_file_path("ensemble")
print("Writing classifier out to file {}...".format(filepath))
classifier_factory.write_classifier_to_file(filepath)

# Verify file write out
print("Validating classifier output...")
(written_out_classifier, wf, tg, ucw) = classifierlib.load_classifier_from_file(filepath)
results = [written_out_classifier.classify_record(r, wf, tg, ucw) for r in training_data]
if len(results) != len(training_data) or written_out_classifier.naive_bayes.most_informative_features(5) != classifier.naive_bayes.most_informative_features(5):
    print("ERROR: Written out classifier does not match constructed")
    sys.exit(1)

# Print out statistics
print("Done!\n")
print("Statistics:")
print("    Total of {} examples".format(len(training_data)))
print("    Total of {} words".format(len(classifier_factory.get_all_training_data_words(CLASSIFY_WITH_CORE_WORDS))))
print("    Total of {} unique words".format(len(classifier_factory.get_all_unique_training_data_words(CLASSIFY_WITH_CORE_WORDS))))
print("    Top 10 words are: {}".format(classifier_factory.get_n_most_common_training_data_words(10, CLASSIFY_WITH_CORE_WORDS)))
print("    Total of {} tags".format(len(classifier_factory.get_all_training_data_tags())))
print("    Total of {} unique tags".format(len(classifier_factory.get_all_unique_training_data_tags())))
print("    Top 10 tags are: {}".format(classifier_factory.get_n_most_common_training_data_tags(10)))
print()

# Print out classifier information
classifier.naive_bayes.show_most_informative_features(10)
