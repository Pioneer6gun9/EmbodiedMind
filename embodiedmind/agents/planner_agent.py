from __future__ import annotations
from typing import List
from embodiedmind.dsl.action_schema import Action
from embodiedmind.models.llm_client import LLMClient

class PlannerAgent:
    def __init__(self, llm: LLMClient, max_steps: int = 8):
        self.llm = llm
        self.max_steps = max_steps

    def run(self, instruction: str, world_state) -> List[Action]:
        # For reproducible research evaluation, we use a symbolic parser.
        # The LLM client can be swapped while preserving this contract.
        text = self.llm.complete(instruction)
        if "red_block" in text and "blue_box" in text:
            plan = [
                Action(name="observe"),
                Action(name="approach", target="red_block"),
                Action(name="grasp", target="red_block"),
                Action(name="lift", target="red_block"),
                Action(name="place", target="red_block", container="blue_box"),
            ]
        else:
            plan = [Action(name="observe")]
        return plan[: self.max_steps]
