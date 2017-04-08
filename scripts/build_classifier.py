"""
    build_classifier.py
    Builds a Naive-Bayes classifier from the training data
    Reference: http://www.nltk.org/book/ch06.html
"""
import os
import sys
import glob
from modules import config, helpers
from modules.classifier import NaiveBayesPrivacyClassifierFactory

CLASSIFY_WITH_WORDS = True
CLASSIFY_WITH_TAGS = True

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

# Get a Naive-Bayes Classifier factory object to build the classifier
print("Building classifier...")
classifier_factory = NaiveBayesPrivacyClassifierFactory()

# Add training data to classifier
classifier_factory.set_training_data(training_data)

# Build classifier
classifier = classifier_factory.build_classifier(CLASSIFY_WITH_WORDS, CLASSIFY_WITH_TAGS)

# Write out classifier factory to file
filepath = config.get_classifier_pickle_file_path("naive_bayes")
print("Writing classifier out to file {}...".format(filepath))
classifier_factory.write_classifier_to_file(filepath)

# Verify file write out
written_out_classifier = classifier_factory.get_classifier(filepath)
if written_out_classifier.most_informative_features(5) != classifier.most_informative_features(5):
    print("ERROR: Written out classifier does not match constructed")
    sys.exit(1)

# Print out statistics
print("Done!\n")
print("Statistics:")
print("    Total of {} examples".format(len(training_data)))
print("    Total of {} words".format(len(classifier_factory.get_all_training_data_words())))
print("    Total of {} unique words".format(len(classifier_factory.get_all_unique_training_data_words())))
print("    Top 10 words are: {}".format([w for w, wc in classifier_factory.get_n_most_common_training_data_words(10)]))
print("    Total of {} tags".format(len(classifier_factory.get_all_training_data_tags())))
print("    Total of {} unique tags".format(len(classifier_factory.get_all_unique_training_data_tags())))
print("    Top 10 tags are: {}".format([w for w, wc in classifier_factory.get_n_most_common_training_data_tags(10)]))
print()

# Print out classifier information
classifier.show_most_informative_features(10)
