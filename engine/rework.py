"""
Engine rework module - Phase 0 placeholders.

Contract:
- engine.rework.apply_rework_if_needed(job: JobId, step: RouteStep,
  outcome: InspectionOutcome) -> Optional[RouteStep]

Phase 0 behavior:
- Simple deterministic rule:
  - If outcome.inspection_failed is True and outcome.rework_allowed is True,
    return the same step to indicate rework should be applied.
  - Otherwise return None.
- No side effects or persistence in Phase 0.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class InspectionOutcome:
    """Minimal inspection outcome used by rework logic."""
    inspection_failed: bool = False
    rework_allowed: bool = False
    details: Optional[str] = None


def apply_rework_if_needed(
    job_id: str,
    step: Any,
    outcome: InspectionOutcome,
    max_rework_attempts: int = 1,
) -> Optional[Any]:
    """
    Decide whether a job/step requires rework and return a RouteStep to
    re-execute, or None if no rework is needed.

    Phase 2 starter semantics (still KISS):
    - If outcome.inspection_failed and outcome.rework_allowed is True:
      - If the step (treated as a dict) has a private `_rework_attempts` counter
        that is less than `max_rework_attempts`, return a copy of the step with
        `_rework_attempts` incremented by 1.
      - If `_rework_attempts` >= max_rework_attempts, return None (no more reworks).
    - If the step is not a dict, fallback to returning the original step once.
    - This function is side-effect free (returns a new step when rework is required).
    """
    if not (outcome.inspection_failed and outcome.rework_allowed):
        return None

    # Phase 2: try to be conservative and avoid infinite loops
    if isinstance(step, dict):
        try:
            attempts = int(step.get("_rework_attempts", 0))
        except Exception:
            attempts = 0
        if attempts >= int(max_rework_attempts):
            return None
        # return a shallow copy with incremented attempts counter
        new_step = dict(step)
        new_step["_rework_attempts"] = attempts + 1
        return new_step

    # If step is opaque (non-dict), allow one deterministic rework attempt
    if max_rework_attempts >= 1:
        return step

    return None