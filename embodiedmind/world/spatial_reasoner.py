from __future__ import annotations
from .world_state import WorldState

class SpatialReasoner:
    def compute_relations(self, state: WorldState) -> WorldState:
        ids = list(state.objects)
        relations = {}
        for a in ids:
            relations[a] = {}
            ax, ay, _ = state.objects[a].pose
            for b in ids:
                if a == b:
                    continue
                bx, by, _ = state.objects[b].pose
                if ax < bx:
                    relations[a][f"left_of:{b}"] = "true"
                if ax > bx:
                    relations[a][f"right_of:{b}"] = "true"
                if ay > by:
                    relations[a][f"behind:{b}"] = "true"
                if ay < by:
                    relations[a][f"in_front_of:{b}"] = "true"
        state.relations = relations
        return state
