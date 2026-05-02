from __future__ import annotations
import yaml
from pathlib import Path
from typing import Any, Dict

def load_yaml(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    data = yaml.safe_load(path.read_text()) or {}
    if "inherits" in data:
        parent = load_yaml(data.pop("inherits"))
        return deep_update(parent, data)
    return data

def deep_update(base: dict, update: dict) -> dict:
    out = dict(base)
    for k, v in update.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_update(out[k], v)
        else:
            out[k] = v
    return out
