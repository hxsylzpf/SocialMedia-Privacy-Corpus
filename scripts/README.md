# Scripts
Contained within this folder are various scripts and modules for our project. This file shall maintain a listing of these scripts with usage information.

## Authors
Michael Meli and Kylie Geller

## Scripts
The scripts folder contains various scripts that perform individual tasks. They should be run in certain orders for correct functionality.

### Core Functionality
Listed below are relevant scripts for core functionality in order of execution

##### get_training_data.py
Get training data based on the `yes.ids` and `no.ids` files in the `root/training_data` folder. This queries the API for that data.

Parameters: If none provided, this will only get data from the API that we do not already have (to save API calls and time). If `update` provided, this will re-retrieve all data from the API, regardless if we already have it.

##### preprocess_training_data.py
Performs various preprocessing steps on the training data downloaded previously. Namely, summarizes the articles using a tf-idf algorithm.

Parameters: If none provided, this will only pre-process data that has not been pre-processed. If `update` provided, this will re-pre-process all data. If `remove` provided, this will simply delete all existing pre-process data, but leave the actual training data intact.

##### validate_classifer.py
Performs n-fold cross-validation on the classifier with the training data.

Parameters: The number of folds to use

### Support functionality
Listed below are scripts that can be used for supporting purposes, but aren't needed for core functionality.

##### compare_summarizer.py
Prints out the results of the summarizer on training data to compare to commercially available solutions, or just to see the results.

Parameters: If none, selects a random article and returns the 7 best sentences. Optionally, 1st argument is the number of sentences to return, and optionally, 2nd argument is the hash of the file to compare (optional)

##### content_from_tags.py
Prints out content (title and web URL) for a tag query. You can use boolean operators in the tag query.

Parameters: the tag query and the page number of results (i.e. `python content_from_tags.py "technology/apple" 3`)

##### content_response.py
TBD

##### find_tags.py
Find tags for a query.

Parameters: the query (i.e. `python find_tags.py apple`)

##### get_random_articles.py
Get `n` number of random article IDs from the API.

Parameters: the number of articles to retrieve

## Modules
The modules folder contains various files that have useful functions that may be shared across scripts. The scripts tend to wrap these modules.

##### theguardian
This is The Guardian API library based off of [this](https://github.com/prabhath6/theguardian-api-python) repo that we forked [here](https://github.com/mjmeli/theguardian-api-python) to make various changes (i.e. https support, bug fix).

##### api
Wrapper functions for `theguardian` library.

##### config
Common environment configuration

##### data
Helper functions for accessing data/files

##### nlp
Functions that use NLP libraries

##### preprocessing
Functions that perform preprocessing

##### training_data
Functions that get and operate on training data
