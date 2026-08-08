"""
PRAMAAN-SHIELD — Shared JSON data loader
File: backend/app/utils/json_io.py
"""

import json
from pathlib import Path
from typing import Any
from loguru import logger

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json_data(filename: str, *, default: Any = None, encoding: str = "utf-8") -> Any:
    """Load a JSON file from app/data, returning `default` if missing/invalid.

    Handles the three duplicated "read app/data json or fall back" helpers in
    registy/phishing/levenshtein under one definition.
    """
    path = _DATA_DIR / filename
    try:
        with open(path, "r", encoding=encoding) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        logger.warning(f"{filename} not found or unreadable, using fallback defaults: {e}")
        return default