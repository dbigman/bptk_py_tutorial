"""
Engine failures module - Phase 0 placeholders.

Contracts (authoritative):
- engine.failures.next_downtime(machine_id: MachineId, now: Time)
  -> DowntimeWindow

Phase 0 behavior:
- Provide a simple, deterministic placeholder DowntimeWindow.
- No I/O or persistence; real stochastic scheduling added in Phase 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import math
import random


@dataclass
class DowntimeWindow:
    """Represents a planned or predicted downtime window for a machine."""
    machine_id: str
    start: Optional[datetime]
    end: Optional[datetime]
    reason: Optional[str] = None


def next_downtime(
    machine_id: str,
    now: datetime,
    mtbf_hours: float = 24.0,
    mttr_hours: float = 4.0,
    rng: Optional[random.Random] = None,
) -> DowntimeWindow:
    """
    Return the next expected downtime window for a machine.

    Phase 2 starter semantics (still KISS but stochastic when rng provided):
    - Uses an exponential draw for time-to-failure with mean `mtbf_hours`.
      ttf = -mtbf_hours * ln(U) where U ~ Uniform(0,1)
    - Downtime duration is `mttr_hours` (deterministic here).
    - If rng is None, falls back to deterministic default (24h / 4h) for reproducibility.
    - This keeps the original contract while allowing deterministic seeded draws
      when an RNG is provided by the run manifest.

    Parameters:
    - machine_id: machine identifier
    - now: current time
    - mtbf_hours: mean time between failures in hours (default 24)
    - mttr_hours: mean time to repair in hours (default 4)
    - rng: optional `random.Random` instance for deterministic sampling
    """
    # If no RNG provided, behave deterministically as Phase 0 did
    if rng is None:
        # deterministic fallback: fixed window mtbf_hours -> mttr_hours
        start = now + timedelta(hours=float(mtbf_hours))
        end = start + timedelta(hours=float(mttr_hours))
        return DowntimeWindow(
            machine_id=str(machine_id),
            start=start,
            end=end,
            reason="scheduled-placeholder",
        )

    # Sample time-to-failure in hours using exponential distribution with mean mtbf_hours
    try:
        u = rng.random()
        # guard against 0
        if u <= 0.0:
            u = 1e-12
        ttf_hours = -float(mtbf_hours) * math.log(u)
    except Exception:
        # fallback deterministic
        ttf_hours = float(mtbf_hours)

    start = now + timedelta(hours=ttf_hours)
    end = start + timedelta(hours=float(mttr_hours))
    return DowntimeWindow(
        machine_id=str(machine_id),
        start=start,
        end=end,
        reason="predicted-failure",
    )