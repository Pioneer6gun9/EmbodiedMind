from __future__ import annotations
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        ...

class RuleBasedLLMClient(LLMClient):
    """
    Deterministic local fallback used for reproducible evaluation.
    Replace this with OpenAI/Claude/local VLM calls for real experiments.
    """
    def complete(self, prompt: str) -> str:
        if "red block" in prompt.lower() and "blue box" in prompt.lower():
            return "locate red_block; approach red_block; grasp red_block; lift red_block; place red_block into blue_box"
        return "observe"
