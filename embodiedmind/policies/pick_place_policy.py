from __future__ import annotations
from embodiedmind.dsl.action_schema import Action

class PickPlacePolicy:
    def generate(self, obj: str, container: str):
        return [
            Action(name="observe"),
            Action(name="approach", target=obj),
            Action(name="grasp", target=obj),
            Action(name="lift", target=obj),
            Action(name="place", target=obj, container=container),
        ]
