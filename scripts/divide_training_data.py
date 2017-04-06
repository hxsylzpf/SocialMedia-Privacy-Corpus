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
        sys.exit(1)

# Open ID files
(DATA_FOLDER_PATH, YES_FOLDER_PATH, NO_FOLDER_PATH) = config.get_training_data_folder_paths()
print("Looking for downloaded training data...")
if not os.path.exists(YES_FOLDER_PATH) or not os.path.exists(NO_FOLDER_PATH):
    print("ERROR: Missing training data files! Run download script first.")
    sys.exit(1)
yes_hashes = os.listdir(YES_FOLDER_PATH)
no_hashes = os.listdir(NO_FOLDER_PATH)

# Shuffle the yes and no lists to allow for random sampling
print("Randomly sampling the IDs...")
yes_hashes_shuffled = helpers.random_shuffle(yes_hashes)
no_hashes_shuffled = helpers.random_shuffle(no_hashes)

# Split each list into the correct percentages
print("Splitting the IDs into a {}/{} split...".format(training_split, 100 - training_split))
yes_split = int((training_split / 100.0) * len(yes_hashes_shuffled))
yes_hashes_training = yes_hashes_shuffled[:yes_split]
yes_hashes_validation = yes_hashes_shuffled[yes_split:]
no_split = int((training_split / 100.0) * len(no_hashes_shuffled))
no_hashes_training = no_hashes_shuffled[:no_split]
no_hashes_validation = no_hashes_shuffled[no_split:]

# Write them out to files
print("Writing out splits to files...")
(TRAINING_IDS_PATH, VALIDATION_IDS_PATH) = config.get_training_data_splits_paths()
with open(TRAINING_IDS_PATH, 'w+') as f:
    f.write("\n".join(yes_hashes_training + no_hashes_training))
with open(VALIDATION_IDS_PATH, 'w+') as f:
    f.write("\n".join(yes_hashes_validation + no_hashes_validation))

print("Done!")
