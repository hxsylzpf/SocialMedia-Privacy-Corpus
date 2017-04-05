"""
    compare_summarizer.py
    Compares the summarizer pre-processing to a commercially available solution
"""
import os
import sys
from modules import config, helpers, nlp

# Number of sentences to summarize to
# API by default returns the 7 best sentences
N_BEST = 7

# Get access to the yes/no training data
(DATA_FOLDER_PATH, YES_FOLDER_PATH, NO_FOLDER_PATH) = config.get_training_data_folder_paths()
all_id_hashes = os.listdir(YES_FOLDER_PATH) + os.listdir(NO_FOLDER_PATH)

# If command line argument is provided, use that as the key. Otherwise use a
# random hash from the yes/no training data.
if len(sys.argv) == 2:
    selected_hash = sys.argv[1]
else:
    selected_hash = helpers.random_sample(all_id_hashes)

# Open the selected file
filepath = os.path.join(YES_FOLDER_PATH, selected_hash)
if not os.path.exists(filepath):
    filepath = os.path.join(NO_FOLDER_PATH, selected_hash)
with open(filepath, 'r') as f:
    record = helpers.json_string_to_object(f.read().strip())

# Summarize the article using our summarizer
best_sentences = nlp.summarize(record['title'], record['content'], N_BEST)

# Print out the results
for i, s in enumerate(best_sentences.split('\n')):
    print("{}: {}".format(i, s))
