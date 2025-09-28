"""
Engine release control module - Phase 0 placeholders.

Contracts:
- release_jobs(now: Time, policy: ReleasePolicy, state: SystemState)
  -> list[JobId]
- token_balance(route: RouteId) -> int

Phase 0 behaviour:
- Deterministic, side-effect-free placeholders.
- release_jobs returns up to `wip_cap` job ids from state['pending'].
- token_balance reads from state.get('tokens', {}) if available.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


def release_jobs(
    now: datetime,
    policy: str,
    state: Dict[str, Any],
) -> List[str]:
    """
    Decide which jobs to release based on the policy and system state.

    Minimal, side-effect-free token-aware CONWIP/POLCA implementation (Phase 2 starter):
    - Reads tokens from state.get("tokens", {}) (route -> int)
    - Reads current WIP counts from state.get("wip_counts", {}) (route -> int)
    - Reads per-route caps from state.get("wip_caps", {}) with fallback to global cap
    - For CONWIP/POLCA: prefer releasing jobs whose route has available tokens and under cap.
    - Deterministic: preserves pending order as tiebreaker.

    Parameters:
    - now: current time (datetime)
    - policy: release policy name, e.g., "CONWIP" or "POLCA"
    - state: dictionary containing at least:
      - 'pending': list of job dicts with 'job_id' and optional 'route_id' or 'route'
      - 'wip_caps': dict route_id -> int (optional). 'global' key used for fallback.
      - 'tokens': dict route_id -> int (optional)
      - 'wip_counts': dict route_id -> int (optional)

    Returns:
    - list of job_id strings to release (may be empty)
    """
    pending = state.get("pending", [])
    if not pending:
        return []

    wip_caps = state.get("wip_caps", {})
    global_cap = int(wip_caps.get("global", len(pending)))

    tokens = state.get("tokens", {}) or {}
    wip_counts = state.get("wip_counts", {}) or {}

    # Helper to get route id from job
    def _route_of(job: Dict[str, Any]) -> str:
        return str(job.get("route_id") or job.get("route") or "default")

    # CONWIP / POLCA policy: release up to global_cap but prefer jobs whose
    # route has tokens and is below its per-route cap.
    if policy in ("CONWIP", "POLCA"):
        selected: List[str] = []
        # Track local view of token usage and wip to avoid mutating input state
        local_tokens = {str(k): int(v) for k, v in tokens.items()}
        local_wip = {str(k): int(v) for k, v in wip_counts.items()}
        # Determine per-route caps, falling back to global_cap
        def _route_cap(route: str) -> int:
            try:
                return int(wip_caps.get(route, global_cap))
            except Exception:
                return global_cap

        for job in pending:
            if len(selected) >= global_cap:
                break
            jid = job.get("job_id")
            if not jid:
                continue
            route = _route_of(job)
            cap = _route_cap(route)
            current = local_wip.get(route, 0)
            available_tokens = local_tokens.get(route, 0)
            # Release only if route under cap and has tokens (tokens=0 means blocked)
            if current < cap and available_tokens > 0:
                selected.append(str(jid))
                # Reserve one token and increment local wip
                local_tokens[route] = available_tokens - 1
                local_wip[route] = current + 1
            else:
                # If no route-specific token, fall back to global token if present under 'global'
                global_tokens = local_tokens.get("global", None)
                if current < cap and global_tokens is not None and global_tokens > 0:
                    selected.append(str(jid))
                    local_tokens["global"] = global_tokens - 1
                    local_wip[route] = current + 1
                # else skip this job for now
        return selected

    # Default fallback: release single job (FIFO).
    first = pending[0].get("job_id")
    return [str(first)] if first else []


def token_balance(route: str, state: Dict[str, Any]) -> int:  # noqa: E501
    """
    Return the token balance for a route.

    Phase 0:
    - Read from state['tokens'][route] if available, else return 0.
    """
    tokens = state.get("tokens", {})
    try:
        return int(tokens.get(route, 0))
    except Exception:
        return 0