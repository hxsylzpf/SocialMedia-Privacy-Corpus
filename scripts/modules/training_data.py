"""
    training_data.py
    Responsible for all training data related stuff
"""
import os
from . import api, data, helpers

# Write out a training data record to string
def get_training_data_record(articleId, classification, content):
    record = {
        'id': articleId,
        'class': classification,
        'content': content
    }
    record_json = helpers.json_string(record)
    return record_json

# Retrieve the content for each ID and write it out to file
def get_training_data_files_for_ids(ids, hashes, folder, classification, shouldReuse):
    # Statistics
    numRetrieved = 0
    numCached = 0
    for i, h in zip(ids, hashes):
        # Only retrieve and write out if the file does not exist already
        # (save API calls) unless told otherwise
        filepath = os.path.join(folder, h)
        if not os.path.exists(filepath) or not shouldReuse:
            body_content = api.get_body_content(i)
            record_json = get_training_data_record(i, classification, body_content)
            data.write_string_to_file(filepath, record_json)
            numRetrieved = numRetrieved + 1
        else:
            numCached = numCached + 1
    return (numRetrieved, numCached)
