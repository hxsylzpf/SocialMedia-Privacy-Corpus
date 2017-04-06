"""
    build_classifier.py
    Builds a Naive-Bayes classifier from the training data
    Reference: http://www.nltk.org/book/ch06.html
"""
import os
import sys
import glob
from collections import Counter
from modules import config, helpers

# Download nltk if necessary
import nltk

# Get all downloaded training data paths
(DATA_FOLDER_PATH, YES_FOLDER_PATH, NO_FOLDER_PATH) = config.get_training_data_folder_paths()
print("Looking for downloaded training data...")
if not os.path.exists(YES_FOLDER_PATH) or not os.path.exists(NO_FOLDER_PATH):
    print("ERROR: Missing training data files! Run download script first.")
    sys.exit()
training_data_files = glob.glob(YES_FOLDER_PATH + "/*") + glob.glob(NO_FOLDER_PATH + "/*")

# Read all of the training data in and parse them into objects
training_data = []
for fp in training_data_files:
    with open(fp, 'r') as f:
        record = helpers.json_string_to_object(f.read().strip())
        training_data.append(record)

# Pull all words from the core words across all training data records
all_words = [x for record in training_data for x in record['core-words']]

# Create a frequency distribution of all the words
words_freqdist = Counter(all_words)

# Construct features
training_data_features = []
for record in training_data:
    # Convert to a set as searching a set is faster (hashed)
    core_words = set(record['core-words'])

    # Construct features
    features = {}
    for word in words_freqdist:
        features["contains({})".format(word)] = (word in core_words)
    training_data_features.append(features)

# Train the N-B classifier
featuresets = [(feature, category) for feature, category in zip(training_data_features, [x['class'] for x in training_data])]
classifier = nltk.NaiveBayesClassifier.train(featuresets)
classifier.show_most_informative_features(10)

# Print out statistics
print("Statistics:")
print("    Total of {} examples".format(len(training_data)))
print("    Total of {} words".format(len(all_words)))
print("    Total of {} unique words".format(len(words_freqdist)))
print("    Top 10 words are: {}".format([w for w, wc in words_freqdist.most_common(10)]))
