"""
Engine dispatch module - Phase 0/2 dispatch helpers.

Contracts:
- engine.dispatch.select_next_job(queue_state: QueueState, rule: DispatchRule, now: Time) -> JobId
- engine.dispatch.compute_priority(rule: DispatchRule, job: JobView, state: QueueState, now: Time) -> float

This module implements simple, readable priority functions for:
- EDD (Earliest Due Date)
- SPT (Shortest Processing Time)
- ATC (Apparent Tardiness Cost) - baseline variant
- ATCS (ATC with setup penalty) - alias to ATC for Phase 2
- LSN (Least Slack Now / Least Laxity First)

KISS: keep formulas simple and deterministic. All datetime parsing uses ISO format when possible.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
import math

def select_next_job(queue_state: Dict[str, Any], rule: str, now: datetime) -> str:
    """
    Select the next job id based on queue_state and dispatch rule.

    Behavior:
    - Compute priority for each job using compute_priority and select job with highest priority.
    - Tie-breaker: preserve queue order (stable).
    """
    jobs = queue_state.get("jobs", [])
    if not jobs:
        return ""

    best_idx: Optional[int] = None
    best_prio: Optional[float] = None

    for idx, job in enumerate(jobs):
        prio = compute_priority(rule, job, queue_state, now)
        # Higher priority wins
        if best_prio is None or prio > best_prio:
            best_prio = prio
            best_idx = idx

    if best_idx is None:
        return str(jobs[0].get("job_id", ""))
    return str(jobs[best_idx].get("job_id", ""))

def _parse_due(due: Any) -> Optional[datetime]:
    if due is None:
        return None
    if isinstance(due, datetime):
        return due
    if isinstance(due, str):
        try:
            return datetime.fromisoformat(due)
        except Exception:
            return None
    return None

def compute_priority(rule: str, job: Dict[str, Any], state: Dict[str, Any], now: datetime) -> float:
    """
    Compute job priority as a float for sorting.

    Returns higher values for higher priority.

    Rules implemented:
    - EDD: earlier due_date => higher priority (returns negative seconds until due)
    - SPT: shorter processing time => higher priority (1 / processing_time)
    - ATC: baseline ATC -> exp(-lead_hours/k1) / (pt^k2)
    - ATCS: alias to ATC for Phase 2 (setup penalty not modelled yet)
    - LSN: least slack now -> negative slack (less slack -> higher priority)
    """
    try:
        rule = (rule or "").upper()
        # Common fields
        due_raw = job.get("due_date")
        due_dt = _parse_due(due_raw)
        pt_raw = job.get("process_time_mean", job.get("processing_time", 0.0))
        try:
            pt = float(pt_raw) if pt_raw is not None and pt_raw != "" else 0.0
        except Exception:
            pt = 0.0

        if rule == "EDD":
            if due_dt is None:
                return 0.0
            # earlier due -> larger priority (we invert seconds so nearer due -> larger number)
            seconds_to_due = (due_dt - now).total_seconds()
            return -seconds_to_due

        if rule == "SPT":
            # shorter processing time -> larger priority
            return 1.0 / (pt + 1e-6)

        if rule in ("ATC", "ATCS"):
            if due_dt is None:
                return 0.0
            # lead time in hours (non-negative)
            lead_hours = max(0.0, (due_dt - now).total_seconds() / 3600.0)
            # ATC baseline parameters (tunable)
            k1 = 168.0  # decay parameter (hours)
            k2 = 1.0    # processing time exponent
            setup_penalty = 1.0
            try:
                denom = (pt ** k2) if pt > 0 else 1.0
                return math.exp(-lead_hours / k1) / (denom * setup_penalty)
            except Exception:
                return 0.0

        if rule == "LSN":
            if due_dt is None:
                return 0.0
            # slack in seconds: (due - now) - processing_time_in_seconds
            slack_seconds = (due_dt - now).total_seconds() - (pt * 3600.0)
            # less slack => higher priority, so invert sign
            return -slack_seconds

    except Exception:
        return 0.0

    # default neutral priority
    return 0.0