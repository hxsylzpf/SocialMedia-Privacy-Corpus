# privacy
Privacy project with Kylie Geller

## Requirements
Python 3 only

## Setup (Ubuntu)
Install system level prerequisites:

    sudo apt-get install build-essential python3-dev python3-tk

Recommend using a virtual environment:

    virtualenv -p python3 venv
    source venv/bin/activate

Make sure you have all `pip` requirements:

    pip install -r requirements.txt

Download English NLP model for `spacy`:

    python -m spacy.en.download

If using anything that touches the API, put API key in a file named api_key:

    echo "API-KEY-HERE" > api_key

## Usage
See the sections below for more information. Also see the `README.md` in the `scripts` folder for even more info.

For a quick look at usage, look at the script `classify.sh`.

### Classifying
Each step of the process is broken up into individual scripts that must be run sequentially. Use the following order:

1. `get_training_data.py`: downloads the training data specified in `training_data/*.ids` - **API access**
2. `preprocess_training_data.py`: preprocess the training data downloaded
3. `build_classifier.py`: builds the classifier
4. `get_test_data.py`: downloads the test data specified in `test_data/ids` - **API access**
5. `preprocess_test_data.py`: preprocess the test data downloaded
6. `classify_test_data.py`: uses the built classifier to classify the downloaded and preprocessed test data

### Analysis
Once the training data is downloaded, you can compare the different classifiers we evaluated:

    python compare_classifiers.py [number of folds for cross-validation]

If you ran through step 6 above, the classification results will be in `data/classified`. The YES results must be moved to the corpus folder and renamed as `ids` for the following step.

    python summarize_corpus.py

## Don't want to download data?
Downloading data is a hassle (requires an API key) and there is a lot of it (requires time and hits the API limit easily). We've provided the training and test data we used in the following folders:

    training_data/downloaded_data
    test_data/downloaded_data

Run the following commands to put these in the proper place for the other scripts:

    mkdir -p data
    cp -r training_data/downloaded_data data/training_data
    cp -r test_data/downloaded_data data/test_data

## Viewing the Results
We've provided our final corpus in the `corpus/ids` file. This provides the IDs of the articles in our corpus. Each one can be appended to `www.theguardian.com` to get to the article on the website. The corresponding downloaded article exists in the data folders, if you can find them (the file names are the MD5 hashes of the IDs, and the IDs are included inside the file).
