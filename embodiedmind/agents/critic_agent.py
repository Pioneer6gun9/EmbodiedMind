from __future__ import annotations
import math
from embodiedmind.dsl.action_schema import Action
from embodiedmind.world.world_state import WorldState

class CriticAgent:
    def __init__(self, reach_radius: float = 0.55, min_confidence: float = 0.65):
        self.reach_radius = reach_radius
        self.min_confidence = min_confidence

    def validate(self, action: Action, state: WorldState) -> dict:
        if action.name in {"observe", "release"}:
            return {"valid": True, "reason": "no constraint"}
        if action.target and action.target not in state.objects:
            return {"valid": False, "reason": "target_not_found"}
        if action.container and action.container not in state.objects:
            return {"valid": False, "reason": "container_not_found"}

        target = state.get(action.target) if action.target else None
        if target and target.confidence < self.min_confidence:
            return {"valid": False, "reason": "low_confidence"}

        if target and action.name in {"approach", "grasp", "lift"}:
            dist = math.dist((0, 0), target.pose[:2])
            if dist > self.reach_radius:
                return {"valid": False, "reason": "target_out_of_reach", "distance": dist}

        if action.name == "place":
            if state.robot.holding != action.target:
                return {"valid": False, "reason": "robot_not_holding_target"}

        return {"valid": True, "reason": "constraints_satisfied"}
