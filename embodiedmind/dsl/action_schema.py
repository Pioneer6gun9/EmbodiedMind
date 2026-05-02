from __future__ import annotations
from typing import Literal, Optional, Tuple
from pydantic import BaseModel, field_validator

ActionName = Literal["locate", "approach", "grasp", "lift", "move_to", "place", "release", "observe"]

class Action(BaseModel):
    name: ActionName
    target: Optional[str] = None
    container: Optional[str] = None
    pose: Optional[Tuple[float, float, float]] = None

    @field_validator("target")
    @classmethod
    def target_required_for_manipulation(cls, v, info):
        if info.data.get("name") in {"approach", "grasp", "lift", "place"} and not v:
            raise ValueError("target is required for manipulation actions")
        return v
