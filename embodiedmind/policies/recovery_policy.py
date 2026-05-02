from __future__ import annotations
from embodiedmind.dsl.action_schema import Action

class RecoveryPolicy:
    def from_failure(self, reason: str):
        if reason == "grasp_missed":
            return [Action(name="observe"), Action(name="approach", target="red_block"), Action(name="grasp", target="red_block")]
        return [Action(name="observe")]
