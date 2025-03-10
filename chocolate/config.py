from typing import Any
from path import Path
import json


class JsonConfig:
    def __init__(self, name: str) -> None:
        self.config = json.loads(~Path(name))

    def __getitem__(self, items):
        if not isinstance(items, tuple):
            items = items,
        value = self.config
        for i in items:
            value = value[i]
        return value
