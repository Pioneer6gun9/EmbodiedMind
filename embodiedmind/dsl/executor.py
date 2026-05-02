from __future__ import annotations
from embodiedmind.dsl.action_schema import Action
from embodiedmind.envs.robot_interface import RobotInterface
from embodiedmind.world.world_state import WorldState

class ActionExecutor:
    def __init__(self, robot: RobotInterface):
        self.robot = robot

    def execute(self, action: Action, state: WorldState):
        if action.name == "observe":
            return {"success": True, "message": "observation requested"}
        if action.name == "approach":
            obj = state.get(action.target)
            return self.robot.move_to((obj.pose[0], obj.pose[1], obj.pose[2] + 0.08))
        if action.name == "grasp":
            return self.robot.grasp(action.target)
        if action.name == "lift":
            return self.robot.lift(action.target, dz=0.10)
        if action.name == "place":
            container = state.get(action.container)
            pose = (container.pose[0], container.pose[1], container.pose[2] + 0.06)
            return self.robot.place(action.target, pose, container=action.container)
        if action.name == "release":
            return self.robot.release()
        if action.name == "move_to":
            return self.robot.move_to(action.pose)
        return {"success": False, "message": f"unsupported action {action.name}"}
