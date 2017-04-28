#!/bin/bash

# Required steps for classification
python scripts/get_training_data.py
python scripts/preprocess_training_data.py
python scripts/build_classifier.py
python scripts/get_test_data.py
python scripts/preprocess_test_data.py
python scripts/classify_test_data.py

# Optional
python scripts/compare_classifiers.py
cp data/classified/yes.ids corpus/ids # copy classified ids to the corpus
python scripts/summarize_corpus.py
