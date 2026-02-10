import json
import os
from typing import Any

def load_json(file: str, default: Any = None) -> Any:
    """
    Load JSON data from a file. Returns default if file doesn't exist or is invalid.
    """
    if default is None:
        default = []
    if not os.path.exists(file):
        return default
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default

def save_json(file: str, data: Any) -> None:
    """
    Save data to a JSON file safely.
    """
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Error saving {file}: {e}")
