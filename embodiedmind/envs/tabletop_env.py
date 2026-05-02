from __future__ import annotations
import random, copy, math
from typing import Tuple
from embodiedmind.envs.robot_interface import RobotInterface
from embodiedmind.world.world_state import WorldState, ObjectState

class TabletopEnv(RobotInterface):
    def __init__(self, task: dict, seed: int = 42, action_noise: float = 0.012, placement_noise: float = 0.018):
        self.rng = random.Random(seed)
        self.task = task
        self.action_noise = action_noise
        self.placement_noise = placement_noise
        self.state = self._init_state(task)

    def _init_state(self, task: dict) -> WorldState:
        state = WorldState()
        for obj in task["objects"]:
            pose = tuple(obj["initial_pose"])
            state.update_object(ObjectState(
                id=obj["id"], type=obj["type"], color=obj["color"], pose=pose,
                size=tuple(obj["size"]), confidence=1.0
            ))
        return state

    def reset(self, randomize: bool = True) -> WorldState:
        self.state = self._init_state(self.task)
        if randomize:
            for obj in self.state.objects.values():
                if obj.type != "container":
                    x = obj.pose[0] + self.rng.uniform(-0.06, 0.06)
                    y = obj.pose[1] + self.rng.uniform(-0.05, 0.05)
                    obj.pose = (x, y, obj.pose[2])
        return copy.deepcopy(self.state)

    def observe(self) -> WorldState:
        observed = copy.deepcopy(self.state)
        for obj in observed.objects.values():
            obj.confidence = max(0.50, min(0.99, self.rng.gauss(0.88, 0.06)))
            obj.pose = (
                obj.pose[0] + self.rng.gauss(0, 0.006),
                obj.pose[1] + self.rng.gauss(0, 0.006),
                obj.pose[2],
            )
        return observed

    def move_to(self, pose: Tuple[float, float, float]) -> dict:
        self.state.robot.ee_pose = pose
        self.state.history.append(f"move_to({pose})")
        return {"success": True, "message": "moved", "pose": pose}

    def grasp(self, target: str) -> dict:
        obj = self.state.get(target)
        if obj is None:
            return {"success": False, "failure": "object_not_found"}
        dist = math.dist(self.state.robot.ee_pose[:2], obj.pose[:2])
        success = dist < 0.09 and self.rng.random() > 0.06
        if success:
            self.state.robot.holding = target
            obj.held = True
            self.state.history.append(f"grasp({target})")
            return {"success": True, "message": f"grasped {target}"}
        return {"success": False, "failure": "grasp_missed", "distance": dist}

    def lift(self, target: str, dz: float) -> dict:
        if self.state.robot.holding != target:
            return {"success": False, "failure": "not_holding_target"}
        obj = self.state.get(target)
        obj.pose = (obj.pose[0], obj.pose[1], obj.pose[2] + dz)
        self.state.history.append(f"lift({target})")
        return {"success": True, "message": "lifted"}

    def place(self, target: str, pose: Tuple[float, float, float], container: str | None = None) -> dict:
        if self.state.robot.holding != target:
            return {"success": False, "failure": "not_holding_target"}
        obj = self.state.get(target)
        nx = pose[0] + self.rng.gauss(0, self.placement_noise)
        ny = pose[1] + self.rng.gauss(0, self.placement_noise)
        obj.pose = (nx, ny, pose[2])
        obj.held = False
        self.state.robot.holding = None
        self.state.history.append(f"place({target}, {container})")
        success = True
        if container:
            success = self.state.inside(target, container)
        return {"success": success, "message": "placed", "container": container}

    def release(self) -> dict:
        self.state.robot.holding = None
        return {"success": True, "message": "released"}

    def is_success(self) -> bool:
        goal = self.task["goal"]
        return self.state.inside(goal["object"], goal["target"])
