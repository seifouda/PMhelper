"""
PMhelper Edu — V2 Demo Loader.

Loads JSON demo files from ``data/demos/v2/`` and returns typed dicts
that can be fed directly into the educational calculator tabs.

Each demo JSON has the schema::

    {
        "name": "Three-Point Demo",
        "description": "8 activities with O/M/P values",
        "version": 1,
        "data": { ... feature-specific payload ... }
    }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# Resolve once at import time
_DEMO_DIR = Path(__file__).resolve(
).parent.parent.parent.parent / "data" / "demos" / "v2"


def demo_dir() -> Path:
    """Return the absolute path to the V2 demos directory."""
    return _DEMO_DIR


def list_demos(feature: Optional[str] = None) -> List[Path]:
    """List available demo JSON files, optionally filtered by feature prefix.

    Parameters
    ----------
    feature : str, optional
        If given, only return files whose stem starts with *feature*
        (e.g. ``"three_point"`` matches ``three_point_demo.json``).
    """
    if not _DEMO_DIR.is_dir():
        return []
    files = sorted(_DEMO_DIR.glob("*.json"))
    if feature:
        files = [f for f in files if f.stem.startswith(feature)]
    return files


def load_demo(filename: str) -> Dict[str, Any]:
    """Load and return the parsed contents of a demo file.

    Parameters
    ----------
    filename : str
        File name (not full path) relative to the V2 demos directory,
        e.g. ``"three_point_demo.json"``.

    Returns
    -------
    dict
        The full JSON object with keys ``name``, ``description``,
        ``version``, ``data``.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the JSON is malformed or missing required keys.
    """
    path = _DEMO_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Demo file not found: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    if not isinstance(raw, dict):
        raise ValueError(f"Demo file must be a JSON object: {path}")
    for key in ("name", "data"):
        if key not in raw:
            raise ValueError(f"Demo file missing required key '{key}': {path}")

    return raw


def load_demo_data(filename: str) -> Any:
    """Convenience: return only the ``data`` payload from a demo file."""
    return load_demo(filename)["data"]
