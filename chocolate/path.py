import os
from os.path import isfile
from typing import Union
import json
import mimetypes


def is_binary(filename):
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type is None or mime_type.startswith("application/")


class Path:
    def __init__(self, base: Union[None, str] = None) -> None:
        self.base = os.getcwd() if base is None else base

    def __setattr__(self, name: str, value: Union[str, bytes, dict]) -> None:
        if name == "base":  # Prevent recursion
            super().__setattr__(name, value)
            return

        path = os.path.join(self.base, name)

        if isinstance(value, bytes):
            mode = 'wb'
        elif isinstance(value, str):
            mode = 'wt'
        elif isinstance(value, dict):
            mode = 'wt'
            value = json.dumps(value, indent=2)
        else:
            raise ValueError(f'Unsupported type: {type(value)}')

        with open(path, mode) as fp:
            fp.write(value)

    def __setitem__(self, name: str, value: Union[str, bytes, dict]) -> None:
        self.__setattr__(name, value)

    def __getattr__(self, attr):
        path = os.path.join(self.base, attr)
        return Path(path)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __repr__(self) -> str:
        return f'<Path(base={self.base})>'

    def __str__(self) -> str:
        return self.base

    def __invert__(self):
        if isfile(self.base):
            mode = 'rb' if is_binary(self.base) else 'rt'
            with open(self.base, mode) as fp:
                if self.base.endswith('.json'):
                    return json.load(fp)
                return fp.read()
        raise FileNotFoundError(f"File not found: {self.base}")

    def __iter__(self):
        yield from os.listdir(self.base)
