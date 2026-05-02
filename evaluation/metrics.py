from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass
class EvalSummary:
    success_rate: float
    avg_steps: float
    avg_replans: float
    constraint_violation_rate: float

def summarize(results: List[dict]) -> EvalSummary:
    n = max(1, len(results))
    return EvalSummary(
        success_rate=sum(r["success"] for r in results) / n,
        avg_steps=sum(r["steps"] for r in results) / n,
        avg_replans=sum(r["replans"] for r in results) / n,
        constraint_violation_rate=sum(1 for r in results if r["violations"] > 0) / n,
    )
