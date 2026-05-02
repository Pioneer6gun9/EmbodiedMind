from __future__ import annotations
from abc import ABC, abstractmethod
from embodiedmind.world.world_state import WorldState

class PerceptionModel(ABC):
    @abstractmethod
    def predict(self, observation) -> WorldState:
        ...

class ColorSegmentationModel(PerceptionModel):
    """
    Lightweight default perception backend.

    In real robot deployment this can be replaced with GroundingDINO,
    Segment Anything, OWL-ViT, or a custom RGB-D detector. The simulator
    provides symbolic observations, so this model mainly represents the
    model-adapter boundary.
    """
    def predict(self, observation) -> WorldState:
        return observation
