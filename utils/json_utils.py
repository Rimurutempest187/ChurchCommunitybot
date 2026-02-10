# utils/json_utils.py
import os
import json
import logging
from typing import Any, Dict

logger = logging.getLogger("ChurchBot.json_utils")

def init_data_files(data_dir: str) -> None:
    """
    Ensure required JSON data files exist inside `data_dir`.
    If missing, create them with sensible defaults.
    """
    os.makedirs(data_dir, exist_ok=True)

    files_with_defaults: Dict[str, Any] = {
        "admins.json": [],
        "groups.json": [],
        "prayers.json": [],
        "events.json": []
    }

    for filename, default in files_with_defaults.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default, f, ensure_ascii=False, indent=2)
                logger.info("Created %s with default value.", path)
            except Exception as e:
                logger.exception("Failed to initialize %s: %s", path, e)
        else:
            # Validate JSON; if invalid, overwrite with default (safe fallback)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(default, f, ensure_ascii=False, indent=2)
                    logger.warning("Reinitialized corrupted file %s with default.", path)
                except Exception as e:
                    logger.exception("Failed to reinitialize %s: %s", path, e)

def load_json(file_path: str, default=None):
    if default is None:
        default = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default
    except Exception as e:
        logger.exception("Unexpected error loading %s: %s", file_path, e)
        return default

def save_json(file_path: str, data) -> None:
    try:
        dirpath = os.path.dirname(file_path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception("Error saving %s: %s", file_path, e)
