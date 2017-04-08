"""
    classifier.py
    Reponsible for building and validating the classifier(s).
"""
import abc
import nltk
import pickle
from collections import Counter

# Superclass for all classifier factory types
class PrivacyClassifierFactory:
    def __init__(self):
        self.training_data = None
        self.classifier = None
        self.word_features = None
        self.tag_features = None

    # Returns the constructed classifier
    def get_classifier(self):
        return self.classifier

    # Set the classifier's training data
    def set_training_data(self, training_data):
        self.training_data = training_data

    # Get all words from the core words across all training data records
    def get_all_training_data_words(self):
        return [x for record in self.training_data for x in record['core-words']]

    # Get a count of each word in the training_data
    def get_training_data_word_counter(self):
        return Counter(self.get_all_training_data_words())

    # Get all UNIQUE words from the core words across all training data records
    def get_all_unique_training_data_words(self):
        return list(self.get_training_data_word_counter())

    # Get the n most common words in the training data
    def get_n_most_common_training_data_words(self, n):
        return self.get_training_data_word_counter().most_common(n)

    # Get all tags across all training data records
    def get_all_training_data_tags(self):
        return [x for record in self.training_data for x in record['tags']]

    # Get a count of each tag in the training_data
    def get_training_data_tag_counter(self):
        return Counter(self.get_all_training_data_tags())

    # Get all UNIQUE tags across all training data records
    def get_all_unique_training_data_tags(self):
        return list(self.get_training_data_tag_counter())

    # Get the n most common tags in the training data
    def get_n_most_common_training_data_tags(self, n):
        return self.get_training_data_tag_counter().most_common(n)

    # Get the classification category for a record
    def get_class(self, record):
        return record['class']

    # Get the feature set for a record
    # Use useWords/useTags booleans to indicate whether to enable those features
    def record_features(self, record, useWords=True, useTags=True):
        # Get features if not yet retrieved
        if self.word_features is None:
            self.word_features = self.get_all_unique_training_data_words()
        if self.tag_features is None:
            self.tag_features = self.get_all_unique_training_data_tags()

        # Create features for the record
        features = {}
        if useWords:
            record_core_words = set(record['core-words'])
            for word in self.word_features:
                features["contains({})".format(word)] = (word in record_core_words)
        if useTags:
            record_tags = set(record['tags'])
            for tag in self.tag_features:
                features["tagged({})".format(tag)] = (tag in record_tags)
        return features

    # Generic method of building classifier. Includes getting the feature sets
    # and calling an abstract method for building the classifier depending
    # on the classifier type.
    def build_classifier(self, useWords=True, useTags=True):
        # Pull all the unique words/tags in the training data records
        self.word_features = self.get_all_unique_training_data_words()
        self.tag_features = self.get_all_unique_training_data_tags()

        # Create feature sets for each record
        feature_sets = []
        for r in self.training_data:
            feature = (self.record_features(r, useWords, useTags), self.get_class(r))
            feature_sets.append(feature)

        # Build the classifier
        self.classifier = self.build_classifier_from_features(feature_sets)
        return self.classifier

    # Abstract class method for building the classifier. Should return the
    # classifier object, whatever it is.
    @abc.abstractmethod
    def build_classifier_from_features(self, feature_sets):
        return

# Naive-Bayes Classifier
class NaiveBayesPrivacyClassifierFactory(PrivacyClassifierFactory):
    # Load classifier from pickle file if provided
    def __init__(self, pickle_file=None):
        if pickle_file is not None:
            with open(pickle_file, 'rb') as model:
                self.classifier = pickle.load(model)
        else:
            super().__init__()

    # Given features, build the actual classifier
    def build_classifier_from_features(self, feature_sets):
        self.classifier = nltk.NaiveBayesClassifier.train(feature_sets)
        return self.classifier

    # Write out to file
    def write_classifier_to_file(self, filepath):
        with open(filepath, 'wb') as pickle_file:
            pickle.dump(self.classifier, pickle_file)
