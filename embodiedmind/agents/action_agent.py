from __future__ import annotations
from embodiedmind.dsl.executor import ActionExecutor

class ActionAgent:
    def __init__(self, executor: ActionExecutor):
        self.executor = executor

    def run(self, action, world_state):
        return self.executor.execute(action, world_state)
