"""
    divide_training_data.py
    Sources the data IDs and separates them into training and validation sets.
    Creates new separation each time it is run.

    Optional input parameter gives percentage (i.e. 70) that should go into
    training. Otherwise, uses default of 70.
"""
import os
import sys
from modules import config, data, helpers, training_data

# Set division percentage based on whether an optional argument is provided
training_split = 70
if len(sys.argv) == 2:
    temp = int(sys.argv[1])
    if temp >= 0 and temp <= 100:
        training_split = temp
    else:
        print("Usage: divide_training_data.py [training split percentage]")
        sys.exit()

# Open ID files
(TRAINING_DATA_PATH, YES_ID_FILE, NO_ID_FILE) = config.get_training_data_id_file_paths()
print("Reading ID files...")
if not os.path.exists(YES_ID_FILE) or not os.path.exists(NO_ID_FILE):
    print("ERROR: Missing ID files! yes.ids and no.ids")
    sys.exit()
with open(YES_ID_FILE, 'r') as f:
    yes_ids = [x.strip() for x in f.readlines()]
with open(NO_ID_FILE, 'r') as f:
    no_ids = [x.strip() for x in f.readlines()]

# Convert IDs to hashes. We will store hashes in the split.
yes_hashes = [helpers.md5_hash(i) for i in yes_ids]
no_hashes = [helpers.md5_hash(i) for i in no_ids]

# Shuffle the yes and no lists to allow for random sampling
print("Randomly sampling the IDs...")
yes_hashes_shuffled = helpers.random_shuffle(yes_hashes)
no_hashes_shuffled = helpers.random_shuffle(no_hashes)

# Split each list into the correct percentages
print("Splitting the IDs into a {}/{} split...".format(training_split, 100 - training_split))
yes_split = (training_split / 100.0) * len(yes_hashes_shuffled)
yes_hashes_training = yes_hashes_shuffled[yes_split:]
yes_hashes_validation = yes_hashes_shuffled[:yes_split]
no_split = (training_split / 100.0) * len(no_hashes_shuffled)
no_hashes_training = no_hashes_shuffled[no_split:]
no_hashes_validation = no_hashes_shuffled[:no_split]

# Write them out to files
print("Writing out splits to files...")
(TRAINING_IDS_PATH, VALIDATION_IDS_PATH) = config.get_training_data_splits_paths()
with open(TRAINING_IDS_PATH, 'w+') as f:
    f.write("\n".join(yes_hashes_training + no_hashes_training))
with open(VALIDATION_IDS_PATH, 'w+') as f:
    f.write("\n".join(yes_hashes_validation + no_hashes_validation))

print("Done!")
