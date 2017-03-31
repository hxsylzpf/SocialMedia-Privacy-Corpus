"""
    preprocessing.py
    Responsible for performing preprocessing on the data
"""
from collections import Counter

# Checks whether a record (json object) has already been preprocessed
def is_record_preprocessed(record):
    re = True
    if record['core-words'] is None or len(record['core-words']) == 0:
        re = False
    return re

# Performs reprocessing. Modifies the record in place
def preprocess(record, shouldReuse):
    # Only do preprocessing if it has not already been completed or
    # we are explicitly specified to
    if not is_record_preprocessed(record) or not shouldReuse:
        # Pull out the core words from the article
        # TODO: use article summarizer
        content = record['content']
        content_words = [x.lower() for x in content.split(" ")]
        freq_counts = Counter(content_words).most_common(100)
        core_words = [x[0] for x in freq_counts]
        record['core-words'] = core_words
        return True
    else:
        return False

# Removes preprocessing from a record
def remove_preprocessing(record):
    record['core-words'] = None
