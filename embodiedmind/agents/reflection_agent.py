from __future__ import annotations
from embodiedmind.dsl.action_schema import Action

class ReflectionAgent:
    def __init__(self, max_replans: int = 3):
        self.max_replans = max_replans

    def diagnose(self, failure: dict, state, trace: list) -> dict:
        reason = failure.get("failure") or failure.get("reason") or "unknown_failure"
        if reason in {"grasp_missed", "low_confidence"}:
            revised = [Action(name="observe"), Action(name="approach", target="red_block"), Action(name="grasp", target="red_block"), Action(name="lift", target="red_block"), Action(name="place", target="red_block", container="blue_box")]
            return {"diagnosis": reason, "strategy": "refresh_perception_and_retry_grasp", "plan": revised}
        if reason in {"not_holding_target", "robot_not_holding_target"}:
            revised = [Action(name="approach", target="red_block"), Action(name="grasp", target="red_block"), Action(name="lift", target="red_block"), Action(name="place", target="red_block", container="blue_box")]
            return {"diagnosis": reason, "strategy": "recover_missing_grasp", "plan": revised}
        revised = [Action(name="observe")]
        return {"diagnosis": reason, "strategy": "observe_and_replan", "plan": revised}
