from os.path import isfile
from typing import Any
from path import Path
import json
import os
from rich import print
import zipfile


def normalize_path(path):
    """Normalize the path to a standard format."""
    return path.rstrip('/')


def create_zip_from_lists(zip_name, include, exclude):
    """Create a ZIP file from included files, excluding specified files."""
    # Normalize paths
    include = [normalize_path(path) for path in include]
    exclude = set(normalize_path(path) for path in exclude)

    with zipfile.ZipFile(zip_name, 'w') as zip_file:
        for path in include:
            if os.path.exists(path):
                # If the path is a directory, include its contents
                if os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Check if the file should be excluded
                            if file_path not in exclude:
                                # Add with relative path
                                zip_file.write(file_path, os.path.relpath(
                                    file_path, start=os.path.dirname(path)))
                                print(f'Added {file_path} to {zip_name}')
                else:
                    # If it's a single file, just check for exclusion
                    if os.path.basename(path) not in exclude:
                        zip_file.write(path, os.path.basename(path))
                        print(f'Added {path} to {zip_name}')
                    else:
                        print(f'Skipped {path} (excluded)')
            else:
                print(f'[red] {path} does not exist and cannot be added.')


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    elif os.path.isfile(path):
        raise (FileExistsError(
            f'Tried to make the folder ({path}) but file exists.'))


def ensure_length(pkgs, mini, maxi):
    l = len(pkgs)
    if l < mini:
        print(f'[red]This function requires at least {mini} arguments.')
        quit(1)
    elif l > maxi:
        print(f'[red]This function requires at most {maxi} arguments.')
        quit(1)


class JsonConfig:
    def __init__(self, name: str) -> None:
        self.name = name
        self.config = json.loads(~Path(name))

    def __getitem__(self, items):
        if not isinstance(items, tuple):
            items = items,
        value = self.config
        for i in items:
            value = value[i]
        return value

    def commit(self):
        Path()[self.name] = self.config

    def __setitem__(self, key, value):
        self.config[key] = value
        self.commit()
