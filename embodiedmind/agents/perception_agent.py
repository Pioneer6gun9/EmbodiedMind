from __future__ import annotations
from embodiedmind.models.perception_model import PerceptionModel
from embodiedmind.world.spatial_reasoner import SpatialReasoner

class PerceptionAgent:
    def __init__(self, model: PerceptionModel, confidence_threshold: float = 0.65):
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.reasoner = SpatialReasoner()

    def run(self, observation):
        state = self.model.predict(observation)
        state.objects = {
            k: v for k, v in state.objects.items()
            if v.confidence >= self.confidence_threshold
        }
        return self.reasoner.compute_relations(state)
