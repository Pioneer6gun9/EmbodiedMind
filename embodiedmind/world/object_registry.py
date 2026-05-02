KNOWN_OBJECTS = {
    "red_block": {"aliases": ["red block", "red cube"], "type": "block", "color": "red"},
    "blue_box": {"aliases": ["blue box", "blue container"], "type": "container", "color": "blue"},
    "obstacle": {"aliases": ["gray obstacle", "cylinder"], "type": "cylinder", "color": "gray"},
}

def resolve_object_name(text: str) -> str | None:
    text = text.lower()
    for object_id, meta in KNOWN_OBJECTS.items():
        if object_id.replace("_", " ") in text:
            return object_id
        if any(alias in text for alias in meta["aliases"]):
            return object_id
    return None
