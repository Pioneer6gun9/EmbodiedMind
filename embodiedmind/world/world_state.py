from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import math

Pose = Tuple[float, float, float]

class ObjectState(BaseModel):
    id: str
    type: str
    color: str
    pose: Pose
    size: Tuple[float, float, float]
    confidence: float = 1.0
    held: bool = False

class RobotState(BaseModel):
    ee_pose: Pose = (0.0, 0.0, 0.25)
    holding: Optional[str] = None

class WorldState(BaseModel):
    objects: Dict[str, ObjectState] = Field(default_factory=dict)
    robot: RobotState = Field(default_factory=RobotState)
    relations: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    history: List[str] = Field(default_factory=list)

    def get(self, object_id: str) -> Optional[ObjectState]:
        return self.objects.get(object_id)

    def update_object(self, obj: ObjectState) -> None:
        self.objects[obj.id] = obj

    def distance_xy(self, a: str, b: str) -> float:
        oa, ob = self.objects[a], self.objects[b]
        return math.dist(oa.pose[:2], ob.pose[:2])

    def inside(self, obj: str, container: str) -> bool:
        o, c = self.objects[obj], self.objects[container]
        dx, dy = abs(o.pose[0] - c.pose[0]), abs(o.pose[1] - c.pose[1])
        return dx < c.size[0] / 2 and dy < c.size[1] / 2 and o.pose[2] >= c.pose[2]

    def to_compact_dict(self):
        return {
            "objects": {k: v.model_dump() for k, v in self.objects.items()},
            "robot": self.robot.model_dump(),
            "relations": self.relations,
            "history": self.history[-8:],
        }
