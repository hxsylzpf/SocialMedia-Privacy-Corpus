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

# Toggle True/False to use word presence/word counts
USE_WORD_PRESENCE = True

# Create feature sets for a list of records
# If any of the feature parameters are None, assume no classification by them
def create_feature_sets(records, word_features=None, tag_features=None, use_core_words=True, include_class=True):
    # Create a feature set for each record in the data
    feature_sets = []
    for record in records:
        features = {}
        # Word features?
        if word_features:
            # Word presence vs. word count
            if USE_WORD_PRESENCE:
                if use_core_words:
                    record_words = set(record['core-words'].keys())
                else:
                    record_words = set(record['words'].keys())
                for word in word_features:
                    features["contains({})".format(word)] = (word in record_words)
            else:
                if use_core_words:
                    record_words = record['core-words']
                else:
                    record_words = record['words']
                for word in word_features:
                    if word in set(record_words.keys()):
                        word_count = record_words[word]
                    else:
                        word_count = 0
                    features["contains({})".format(word)] = word_count

        # Tag features?
        if tag_features:
            record_tags = set(record['tags'])
            for tag in tag_features:
                features["tagged({})".format(tag)] = (tag in record_tags)

        # Include class if specified and training data
        if include_class and record['class'] is not None:
            feature_sets.append((features, record['class']))
        else:
            feature_sets.append(features)
    return feature_sets

# Load classifier from file. Returns the classifier and features.
def load_classifier_from_file(pickle_file):
    with open(pickle_file, 'rb') as model:
        classifier, word_features, tag_features, use_core_words = pickle.load(model)
    return (classifier, word_features, tag_features, use_core_words)

# Superclass for all classifier factory types
class PrivacyClassifierFactory:
    def __init__(self, use_core_words=True, use_all_words=False, use_tags=True, word_limit=None, use_accuracy_weighted=None):
        if use_core_words and use_all_words:
            raise Exception("Can't use both core words and all words")
        self.use_core_words = use_core_words
        self.use_all_words = use_all_words
        self.use_tags = use_tags
        self.word_limit = word_limit
        self.use_accuracy_weighted = use_accuracy_weighted
        self.training_data = None
        self.classifier = None
        self.word_features = None
        self.tag_features = None

    # Returns the constructed classifier
    def get_classifier(self):
        return self.classifier

    # Loads the classifier from a file
    def get_classifier_from_file(self, pickle_file):
        with open(pickle_file, 'rb') as model:
            self.classifier, self.word_features, self.tag_features, self.use_core_words = pickle.load(model)
            self.use_all_words = not self.use_core_words
            self.use_tags = self.tag_features is not None
        return self.classifier

    # Write out classifier to file
    def write_classifier_to_file(self, filepath):
        with open(filepath, 'wb') as pickle_file:
            pickle.dump([self.classifier, self.word_features, self.tag_features, self.use_core_words], pickle_file)

    # Set the classifier's training data
    def set_training_data(self, training_data):
        self.training_data = training_data

    # Get all words from the core or unique words across all training data records
    def get_all_training_data_words(self, use_core_words=True):
        return self.get_n_most_common_training_data_words(None, use_core_words)

    # Get a count of each word in the training_data
    def get_training_data_word_counter(self, use_core_words=True):
        if use_core_words:
            dicts = [record['core-words'] for record in self.training_data]
        else:
            dicts = [record['words'] for record in self.training_data]
        counters = [Counter(d) for d in dicts]
        return sum(counters, Counter())

    # Get all UNIQUE words from the core words across all training data records
    def get_all_unique_training_data_words(self, use_core_words=True):
        return list(self.get_training_data_word_counter(use_core_words))

    # Get the n most common words in the training data
    def get_n_most_common_training_data_words(self, n, use_core_words=True):
        return [w for w, wc in self.get_training_data_word_counter(use_core_words).most_common(n)]

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
        return [t for t, tc in self.get_training_data_tag_counter().most_common(n)]

    # Create feature sets for a list of records
    def create_feature_sets(self, records, limit=None):
        # Pull all the unique words/tags in the training data records if requested
        if self.use_core_words:
            # Limit by word limit if provided
            self.word_features = self.get_n_most_common_training_data_words(limit)
        elif self.use_all_words:
            # Limit by word limit if provided
            self.word_features = self.get_n_most_common_training_data_words(limit, False)
        else:
            self.word_features = None
        if self.use_tags:
            self.tag_features = self.get_all_unique_training_data_tags()
        else:
            self.tag_features = None
        return create_feature_sets(records, self.word_features, self.tag_features, self.use_core_words)

    # Generic method of building classifier. Includes getting the feature sets
    # and calling an abstract method for building the classifier depending
    # on the classifier type.
    def build_classifier(self):
        # Create feature sets for each record in training data
        feature_sets = self.create_feature_sets(self.training_data, self.word_limit)

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
            classifier_factory = self.__class__(use_core_words=self.use_core_words,
                                                use_all_words=self.use_all_words,
                                                use_tags=self.use_tags,
                                                word_limit=self.word_limit,
                                                use_accuracy_weighted=self.use_accuracy_weighted)
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

# Classifier metrics
class PrivacyClassifierMetrics(object):
    def __init__(self):
        self.accuracy = None
        self.precision = None
        self.recall = None
        self.fmeasure = None
        self.train_time = None
        self.test_time = None
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)

""" Naive Bayes """
# Naive-Bayes Classifier factory
class NaiveBayesPrivacyClassifierFactory(PrivacyClassifierFactory):
    # Given features, build the actual classifier
    def build_classifier_from_features(self, feature_sets):
        self.classifier = NaiveBayesPrivacyClassifier.train(feature_sets)
        return self.classifier

    # Given test features, determine the classification
    def classify_from_test_features(self, test_features):
        return self.classifier.classify(test_features)

# Naive-Bayes Classifier
class NaiveBayesPrivacyClassifier(nltk.NaiveBayesClassifier):
    # Perform classification
    def classify(self, test_features):
        return super().classify(test_features)

""" Keyword """
# Keyword classifier factory
class KeywordPrivacyClassifierFactory(PrivacyClassifierFactory):
    # Given features, build the actual classifier
    def build_classifier(self):
        self.classifier = KeywordPrivacyClassifier()
        return self.classifier

    # Override to change what the features are for this classifier
    def compute_metrics_from_test_data(self, test_data):
        # Feature sets are just the content
        feature_sets = [(x['content'], x['class']) for x in test_data]

        # Call the subclass abstract method
        return self.compute_metrics_from_test_features(feature_sets)

    # Given test features, determine the classification
    def classify_from_test_features(self, content):
        return self.classifier.classify(content.lower())

# Keyword classifier
class KeywordPrivacyClassifier():
    # Privacy keywords
    privacy_keywords = ["privacy"]

    # Names of social medias
    social_media_keywords = ["social media", "facebook", "snapchat", "twitter",
        "instagram", "linkedin", "reddit", "whatsapp", "google+", "myspace",
        "tumblr", "pinterest", "hangouts", "social network"]

    # Privacy threshold
    privacy_threshold = 0

    # Social media threshold
    social_media_threshold = 0

    def classify(self, content):
        # Check privacy
        privacy_count = sum(content.lower().count(keyword) for keyword in self.privacy_keywords)
        # Check social media
        social_count = sum(content.lower().count(keyword) for keyword in self.social_media_keywords)

        # Want privacy to be present (>0), social media to be common (>1)
        if privacy_count > self.privacy_threshold and social_count > self.social_media_threshold:
            return True
        else:
            return False

""" Tag """
# Tag classifier factory
class TagPrivacyClassifierFactory(PrivacyClassifierFactory):
    # Given features, build the actual classifier
    def build_classifier(self):
        self.classifier = TagPrivacyClassifier()
        return self.classifier

    # Override to change what the features are for this classifier
    def compute_metrics_from_test_data(self, test_data):
        # Feature sets are just the content
        feature_sets = [(x['tags'], x['class']) for x in test_data]

        # Call the subclass abstract method
        return self.compute_metrics_from_test_features(feature_sets)

    # Given test features, determine the classification
    def classify_from_test_features(self, tags):
        return self.classifier.classify(tags)

# Tag classifier
class TagPrivacyClassifier():
    privacy_tags = ["world/privacy", "info/privacy", "media/privacy",
    "technology/data-protection", "technology/hacking"]

    # Names of social medias
    social_media_tags = ["technology/facebook", "technology/snapchat",
        "technology/twitter", "technology/instagram", "technology/linkedin",
        "technology/reddit", "technology/whatsapp", "technology/google-plus",
        "technology/myspace", "technology/tumblr", "technology/pinterest",
        "media/social-media", "media/socialnetworking"]

    # Tags to look for. Each list is an OR, the list of lists is an AND.
    tags = [privacy_tags, social_media_tags]

    def classify(self, tags):
        for tag_list in self.tags:
            count = sum(1 for tag in tag_list if tag in tags)
            if count == 0:
                return False
        return True

""" Ensemble classifier - Naive Bayes and Keyword """
# Ensemble Classifier factory
class EnsemblePrivacyClassifierFactory(PrivacyClassifierFactory):
    # Given features, build the actual classifier
    def build_classifier_from_features(self, feature_sets):
        # Build one Naive-Bayes and one keyword classifier
        self.classifier = EnsemblePrivacyClassifier(self.training_data, self.use_accuracy_weighted)
        self.classifier.train(use_core_words=self.use_core_words,
                              use_all_words=self.use_all_words,
                              use_tags=self.use_tags,
                              word_limit=self.word_limit)
        return self.classifier

    # Override to change what the features are for this classifier
    def compute_metrics_from_test_data(self, test_data):
        # Feature sets are different for each classifier
        naive_bayes_features = self.create_feature_sets(test_data)
        keyword_features = [(x['content'], x['class']) for x in test_data]  # just content

        feature_sets = []
        for nbf, record in zip(naive_bayes_features, test_data):
            # Pack the naive bayes and keywords features together
            nb_features_only = nbf[0]
            nb_class_only = nbf[1]
            feature_sets.append(([nb_features_only, record['content']], nb_class_only))
            # Sanity check
            if nb_class_only != record['class']:
                raise Exception("ERROR: Cannot match up features for ensemble")

        # Call the subclass abstract method
        return self.compute_metrics_from_test_features(feature_sets)

    # Given test features, determine the classification
    def classify_from_test_features(self, test_features):
        return self.classifier.classify(test_features)

# Ensemble Classifier
class EnsemblePrivacyClassifier():
    num_folds = 5       # for evaluation of the classifiers
    threshold = 0.85    # vote threshold

    def __init__(self, training_data, use_accuracy_weighted=True):
        self.training_data = training_data
        self.use_accuracy_weighted = use_accuracy_weighted
        self.naive_bayes = None
        self.naive_bayes_accuracy = None
        self.keyword = None
        self.keyword_accuracy = None

    # Run cross-validation to compute the accuracy weights for each classifier
    def train(self, use_core_words=True, use_all_words=False, use_tags=True, word_limit=None):
        # Naive Bayes evaluation
        nb_factory = NaiveBayesPrivacyClassifierFactory(use_core_words=use_core_words,
                                                        use_all_words=use_all_words,
                                                        use_tags=use_tags,
                                                        word_limit=word_limit)
        nb_factory.set_training_data(self.training_data)
        self.naive_bayes = nb_factory.build_classifier()
        if self.use_accuracy_weighted:
            self.naive_bayes_accuracy = nb_factory.cross_validate(self.num_folds).precision

        # Keyword evaluation
        kw_factory = KeywordPrivacyClassifierFactory()
        kw_factory.set_training_data(self.training_data)
        self.keyword = kw_factory.build_classifier()
        if self.use_accuracy_weighted:
            self.keyword_accuracy = kw_factory.cross_validate(self.num_folds).precision

    # Perform classification of single test record
    # Abstracts the step of needing to build appropriate test features
    def classify_record(self, test_record, word_features, tag_features, use_core_words=True):
        # Build features for the Naive-Bayes classifier
        naive_bayes_features = create_feature_sets(records=[test_record],
                                                   word_features=word_features,
                                                   tag_features=tag_features,
                                                   use_core_words=use_core_words,
                                                   include_class=False)[0]

        # Build features for keyword classifier
        keyword_features = test_record['title'].lower() + test_record['content'].lower()

        # Classify with these features
        return self.classify([naive_bayes_features, keyword_features])

    # Perform classification from test features
    # We expect test features to be a list [x1, x2] where x1 is the test
    # features for the nltk Naive Bayes classifier and x2 is the article text
    def classify(self, test_features):
        # Naive Bayes classification
        naive_bayes_features = test_features[0]
        naive_bayes_class = self.naive_bayes.classify(naive_bayes_features)

        # Keyword classification
        keyword_features = test_features[1]
        keyword_class = self.keyword.classify(keyword_features)

        # If accuracy weighted, make a vote. Otherwise, reach consensus.
        if naive_bayes_class == keyword_class:
            return naive_bayes_class
        else:
            if self.use_accuracy_weighted:
                # TODO: test with probability weighting
                naive_bayes_prob = self.naive_bayes.prob_classify(naive_bayes_features).prob(True)
                vote = self.naive_bayes_accuracy * (naive_bayes_prob if naive_bayes_class else 0) + \
                       self.keyword_accuracy * (1 if keyword_class else 0)
                if vote >= self.threshold:
                    return True
                else:
                    return False
            else:
                return False
