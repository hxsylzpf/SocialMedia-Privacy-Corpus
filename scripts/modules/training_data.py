"""
    training_data.py
    Responsible for all training data related stuff
"""
import os
import sys
from . import api, data, helpers

# Write out a training data record to string
def get_training_data_record(articleId, classification, title, content, tags):
    record = {
        'id': articleId,
        'class': classification,
        'title': title,
        'content': content,
        'tags': tags,
        'core-words': None
    }
    record_json = helpers.json_object_to_string(record)
    return record_json

# Retrieve the content for each ID and write it out to file
def get_training_data_files_for_ids(ids, hashes, folder, classification, shouldReuse=True, progress=False):
    # Statistics
    numRetrieved = 0
    numCached = 0
    for index, (i, h) in enumerate(zip(ids, hashes)):
        # Print out progress is flag set
        if progress:
            sys.stdout.write("\r{}/{}".format(index + 1, len(ids)))
            sys.stdout.flush()
        # Only retrieve and write out if the file does not exist already
        # (save API calls) unless told otherwise
        filepath = os.path.join(folder, h)
        if not os.path.exists(filepath) or not shouldReuse:
            title, content, tags = api.get_title_body_tags_for_article_id(i)
            record_json = get_training_data_record(i, classification, title, content, tags)
            data.write_string_to_file(filepath, record_json)
            numRetrieved = numRetrieved + 1
        else:
            numCached = numCached + 1
    if progress:
        sys.stdout.write("\n")
        sys.stdout.flush()
    return (numRetrieved, numCached)
