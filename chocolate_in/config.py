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


def create_zip(name, include, exclude):
    with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in include:
            if not os.path.exists(path):
                print(f"Warning: {path} does not exist.")
                continue
            for root, dirs, files in os.walk(path):
                if any(excl in root for excl in exclude):
                    dirs[:] = []
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(
                        file_path, os.path.commonpath(include)))


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
        self.config = ~Path(name)
        if not isinstance(self.config, dict):
            self.config = json.loads(self.config)

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
