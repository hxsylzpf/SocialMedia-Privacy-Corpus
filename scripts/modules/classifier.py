"""
    classifier.py
    Reponsible for building and validating the classifier(s).
    NOTE: Creating a new classifier is as simple as creating a classifier
    factory for it that subclasses PrivacyClassifierFactory. See
    NaiveBayesPrivacyClassifierFactory as an example.
"""
import abc
import nltk
import pickle
from . import helpers
from collections import Counter

# Create feature sets for a list of records
# If any of the feature parameters are None, assume no classification by them
def create_feature_sets(records, word_features=None, tag_features=None):
    # Create a feature set for each record in the data
    feature_sets = []
    for record in records:
        features = {}
        # Word features?
        if word_features:
            record_core_words = set(record['core-words'])
            for word in word_features:
                features["contains({})".format(word)] = (word in record_core_words)
        # Tag features?
        if tag_features:
            record_tags = set(record['tags'])
            for tag in tag_features:
                features["tagged({})".format(tag)] = (tag in record_tags)
        feature_sets.append((features, record['class']))
    return feature_sets

# Superclass for all classifier factory types
class PrivacyClassifierFactory:
    def __init__(self, useWords=True, useTags=True):
        self.useWords = useWords
        self.useTags = useTags
        self.training_data = None
        self.classifier = None
        self.word_features = None
        self.tag_features = None

    # Returns the constructed classifier, or loads it from a file
    def get_classifier(self, pickle_file):
        if pickle_file is not None:
            with open(pickle_file, 'rb') as model:
                self.classifier = pickle.load(model)
        return self.classifier

    # Write out classifier to file
    def write_classifier_to_file(self, filepath):
        with open(filepath, 'wb') as pickle_file:
            pickle.dump(self.classifier, pickle_file)

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

    # Create feature sets for a list of records
    def create_feature_sets(self, records):
        # Pull all the unique words/tags in the training data records if requested
        if self.useWords:
            self.word_features = self.get_all_unique_training_data_words()
        else:
            self.word_features = None
        if self.useTags:
            self.tag_features = self.get_all_unique_training_data_tags()
        else:
            self.tag_features = None
        return create_feature_sets(records, self.word_features, self.tag_features)

    # Generic method of building classifier. Includes getting the feature sets
    # and calling an abstract method for building the classifier depending
    # on the classifier type.
    def build_classifier(self):
        # Create feature sets for each record in training data
        feature_sets = self.create_feature_sets(self.training_data)

        # Build the classifier
        self.classifier = self.build_classifier_from_features(feature_sets)
        return self.classifier

    # Abstract class method for building the classifier. Should return the
    # classifier object, whatever it is.
    @abc.abstractmethod
    def build_classifier_from_features(self, feature_sets):
        raise NotImplementedError("Build classifier from features method not implemented")

    # Create folds of the training data
    def create_folds(self, numFolds):
        # Randomly shuffle the training data records
        shuffled = helpers.random_shuffle(self.training_data)

        # Divide the randomly shuffled data into numFolds
        return helpers.split(shuffled, numFolds)

    # Compute the metrics of a classifier on test data. Calls an abstract
    # method that implements the actual measurements on test data features.
    # Should return a PrivacyClassifierMetrics object.
    def compute_metrics_from_test_data(self, test_data):
        # Create feature sets for each record in the test data
        feature_sets = self.create_feature_sets(test_data)

        # Call the subclass abstract method
        return self.compute_metrics_from_test_features(feature_sets)

    # Given test features, compute metrics
    def compute_metrics_from_test_features(self, test_features):
        # Pull out the features and labels from the test_features
        features_only = [features for features, category in test_features]
        true_classifications = [category for features, category in test_features]

        # Run the classifier on the test data
        test_classifications = [self.classify_from_test_features(f) for f in features_only]

        # Combine test classification and ground truth classification
        results = list(zip(true_classifications, test_classifications))

        # Compute true/false positive and true/false negative values
        tp = sum(1 for true, test in results if true == True and test == True)
        fp = sum(1 for true, test in results if true == False and test == True)
        tn = sum(1 for true, test in results if true == False and test == False)
        fn = sum(1 for true, test in results if true == True and test == False)

        # Compute metrics
        metrics = PrivacyClassifierMetrics()
        metrics.accuracy = (tp + tn) / (tp + tn + fp + fn)
        metrics.precision = tp / (tp + fp)
        metrics.recall = tp / (tp + fn)
        metrics.fmeasure = (2 * tp) / ((2 * tp) + fp + fn)
        return metrics

    # Abstract class method to perform classification of the classifier
    @abc.abstractmethod
    def classify_from_test_features(self, test_features):
        raise NotImplementedError("Classify from test features method not implemented")

    # Perform an n-fold cross-validation test on the classifier
    # Returns a PrivacyClassifierMetrics object that contains the average.
    def cross_validate(self, numFolds, output=False):
        # Divide data up into n folds
        folds = self.create_folds(numFolds)

        # Use each fold as test data, the rest as training data
        all_metrics = []
        for i, test_fold in enumerate(folds):
            if output:
                print("Validating fold {}/{}".format(i + 1, numFolds))
            test_data = test_fold
            train_folds = folds[:i] + folds[i + 1:]
            train_data = [record for fold in train_folds for record in fold]

            # Create a classifier with this training data
            classifier_factory = self.__class__()
            classifier_factory.set_training_data(train_data)
            classifier = classifier_factory.build_classifier()

            # Get accuracy measures using test fold
            all_metrics.append(classifier_factory.compute_metrics_from_test_data(test_data))

        # Compute average of each metric
        metrics = PrivacyClassifierMetrics()
        metrics.accuracy = helpers.average([m.accuracy for m in all_metrics])
        metrics.precision = helpers.average([m.precision for m in all_metrics])
        metrics.recall = helpers.average([m.recall for m in all_metrics])
        metrics.fmeasure = helpers.average([m.fmeasure for m in all_metrics])
        return metrics

# Naive-Bayes Classifier factory
class NaiveBayesPrivacyClassifierFactory(PrivacyClassifierFactory):
    # Given features, build the actual classifier
    def build_classifier_from_features(self, feature_sets):
        self.classifier = nltk.NaiveBayesClassifier.train(feature_sets)
        return self.classifier

    # Given test features, cdetermine the classification
    def classify_from_test_features(self, test_features):
        return self.classifier.classify(test_features)

# Classifier metrics
class PrivacyClassifierMetrics(object):
    def __init__(self):
        self.accuracy = None
        self.precision = None
        self.recall = None
        self.fmeasure = None
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)
