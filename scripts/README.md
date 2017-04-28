# Scripts
Contained within this folder are various scripts and modules for our project. This file shall maintain a listing of these scripts with usage information.

## Authors
Michael Meli and Kylie Geller

## Scripts
The scripts folder contains various scripts that perform individual tasks. They should be run in certain orders for correct functionality.

### Core Functionality
Listed below are relevant scripts for core functionality in order of execution

##### get_training_data.py
Get training data based on the `yes.ids` and `no.ids` files in the `root/training_data` folder and writes them to `root/data/training_data`. This queries the API for that data.

Parameters: If none provided, this will only get data from the API that we do not already have (to save API calls and time). If `update` provided, this will re-retrieve all data from the API, regardless if we already have it.

##### preprocess_training_data.py
Performs various preprocessing steps on the training data downloaded previously. Namely, summarizes the articles using a tf-idf algorithm.

Parameters: If none provided, this will only pre-process data that has not been pre-processed. If `update` provided, this will re-pre-process all data. If `remove` provided, this will simply delete all existing pre-process data, but leave the actual training data intact.

##### compare_classifiers.py
Performs n-fold cross-validation on various classifier configurations on the training data.

Parameters: The number of folds to use

##### build_classifier.py
Builds our selected classifier. Pickles it out to a file for use later.

Parameters: None

##### get_test_data.py
Get test data based on the `ids` file in the `root/test_data` folder and writes them to `root/data/test_data`. This queries the API for that data. Note that there are thousands of IDs in this file. Not only will this process take a while, but you will likely hit your API limit.

Parameters: If none provided, this will only get data from the API that we do not already have (to save API calls and time). If `update` provided, this will re-retrieve all data from the API, regardless if we already have it.

##### preprocess_test_data.py
Performs various preprocessing steps on the test data downloaded previously. Namely, summarizes the articles using a tf-idf algorithm.

Parameters: If none provided, this will only pre-process data that has not been pre-processed. If `update` provided, this will re-pre-process all data. If `remove` provided, this will simply delete all existing pre-process data, but leave the actual training data intact.

##### classifer_test_data.py
Runs the classifier built in `build_classifier.py` on the preprocessed test data. Writes out the positively and negatively identified articles to the `root/data/classified` folder.

Parameters: None

##### summarize_corpus.py
Performs various summarization tasks. Open the file and toggle the booleans to enable/disable which summarizations to use.

Parameters: None

## Modules
The modules folder contains various files that have useful functions that may be shared across scripts. The scripts tend to wrap these modules.

##### theguardian
This is The Guardian API library based off of [this](https://github.com/prabhath6/theguardian-api-python) repo that we forked [here](https://github.com/mjmeli/theguardian-api-python) to make various changes (i.e. https support, bug fix).

##### api
Wrapper functions for `theguardian` library.

##### classifier
Our classifiers. You can add more classifiers by extending the classes in here (see file for examples)

##### config
Common environment configuration

##### data
Helper functions for accessing data/files

##### helpers
General helper functions

##### nlp
Functions that use NLP libraries (i.e. tf-idf)

##### preprocessing
Functions that perform preprocessing

##### sentiment
Functions that perform sentiment analysis

##### test_data
Functions that get and operate on test data

##### training_data
Functions that get and operate on training data
