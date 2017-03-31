"""
    config.py
    Responsible for configuring the environment for the other modules
"""
import os
import sys

# Add these modules to the import path
def set_import_paths():
    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# Retrieve the API key from the designated file
def get_api_key():
    api_key_path = os.path.abspath(
                    os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        "../../api_key"))
    if os.path.exists(api_key_path):
        with open(api_key_path, 'r') as f:
            return f.readline().strip()
    else:
        print("ERROR: API key not found at path: {}".format(api_key_path))
        sys.exit()

# Get the data folder paths
def get_training_data_folder_paths():
    data_folder_path = os.path.abspath(
                        os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            "../../data/training_data"))
    yes_folder_path = os.path.join(data_folder_path, "yes")
    no_folder_path = os.path.join(data_folder_path, "no")
    return (data_folder_path, yes_folder_path, no_folder_path)

# Get the ID file paths
def get_training_data_id_file_paths():
    training_data_path = os.path.abspath(
                            os.path.join(
                                os.path.dirname(os.path.realpath(__file__)),
                                "../../training_data"))
    yes_id_file = os.path.join(training_data_path, "yes.ids")
    no_id_file = os.path.join(training_data_path, "no.ids")
    return (training_data_path, yes_id_file, no_id_file)
