"""
    preprocessing.py
    Responsible for performing preprocessing on the data
"""
from . import nlp

# Checks whether a record (json object) has already been preprocessed
def is_record_preprocessed(record):
    re = True
    try:
        if record['core-words'] is None or len(record['core-words']) == 0:
            re = False
        if record['words'] is None or len(record['words']) == 0:
            re = False
    except KeyError:
        re = False
    return re

# Performs preprocessing. Modifies the record in place
def preprocess(record, shouldReuse):
    # Only do preprocessing if it has not already been completed or
    # we are explicitly specified to
    if not is_record_preprocessed(record) or not shouldReuse:
        # Pull out the core words from the article
        title = record['title']
        content = record['content']
        summarized = nlp.summarize(title, content)
        core_words = nlp.top_words(summarized)
        record['core-words'] = core_words
        # Pull out the article words
        all_words = nlp.all_words(content)
        record['words'] = all_words
        return True
    else:
        return False

# Removes preprocessing from a record
def remove_preprocessing(record):
    record['core-words'] = None
    record['words'] = None
