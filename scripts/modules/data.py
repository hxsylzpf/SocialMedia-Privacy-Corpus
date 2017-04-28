"""
    data.py
    Responsible for handling data
"""
import os
import shutil

# Create data folders
def create_data_folder(f):
    if not os.path.exists(f):
        os.makedirs(f)

# Delete file
def delete_file(f):
    if os.path.isfile(f):
        os.remove(f)
    elif os.path.isdir(f):
        shutil.rmtree(f)

# Write string to file
def write_string_to_file(f, string):
    with open(f, 'w+') as f:
        f.write(string)

# Copy data between folders, no overwrite
def copy_between_folders(from_dir, to_dir):
    data_to_copy = os.listdir(from_dir)
    for data in data_to_copy:
        old_path = os.path.join(from_dir, data)
        new_path = os.path.join(to_dir, data)
        if not os.path.exists(new_path):
            shutil.copyfile(old_path, new_path)
