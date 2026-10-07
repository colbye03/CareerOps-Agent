"""Legacy v0.1 explicit-input scorer; the CLI uses the generic engine instead.

Kept for API compatibility only. New integrations should use careerops.engine.run.
"""
from __future__ import annotations

from dataclasses import dataclass, fields


DEFAULT_WEIGHTS = {
    "technical_alignment": 0.25,
    "architecture_alignment": 0.20,
    "seniority_scope": 0.15,
    "domain_alignment": 0.10,
    "compensation": 0.10,
    "location": 0.10,
    "interview_probability": 0.05,
    "career_direction": 0.05,
}


@dataclass(frozen=True)
class FitInputs:
    technical_alignment: float
    architecture_alignment: float
    seniority_scope: float
    domain_alignment: float
    compensation: float
    location: float
    interview_probability: float
    career_direction: float

    def validate(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if not 0 <= value <= 100:
                raise ValueError(f"{field.name} must be between 0 and 100")


@dataclass(frozen=True)
class FitResult:
    score: float
    decision: str


def score_fit(
    inputs: FitInputs,
    *,
    weights: dict[str, float] | None = None,
    apply_threshold: float = 85,
    maybe_threshold: float = 70,
) -> FitResult:
    """Return a deterministic weighted fit score and recommendation."""
    inputs.validate()
    active_weights = weights or DEFAULT_WEIGHTS

    if abs(sum(active_weights.values()) - 1.0) > 1e-9:
        raise ValueError("weights must sum to 1.0")

    score = sum(
        getattr(inputs, dimension) * weight
        for dimension, weight in active_weights.items()
    )
    score = round(score, 2)

    if score >= apply_threshold:
        decision = "APPLY"
    elif score >= maybe_threshold:
        decision = "MAYBE"
    else:
        decision = "SKIP"

    return FitResult(score=score, decision=decision)
