"""
Engine agents module - Phase 0 placeholders.

Contains lightweight dataclasses and function stubs that follow the
contracts in implementation_plan_2025-09-27T18-06-45Z.md
(Contracts catalog, engine.agents). Keep implementations minimal; real
logic will be added in Phase 2.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


@dataclass
class MachineView:
    """
    Minimal view of a machine used by external callers and tests.

    Fields are intentionally simple for Phase 0 and may be extended later.
    - machine_id: identifier (UUID or str)
    - name: human-friendly name
    - cell_id: cell/area the machine belongs to
    - capacity: integer capacity (units of concurrent jobs)
    - status: current status (e.g., 'up', 'down', 'maintenance')
    - busy_until: optional ISO8601 timestamp indicating when current task ends
    """
    machine_id: str
    name: Optional[str] = None
    cell_id: Optional[str] = None
    capacity: int = 1
    status: str = "up"
    busy_until: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None


def get_machine_view(machine_id: str) -> MachineView:
    """
    Return a lightweight MachineView for the requested machine_id.

    Contract:
    - engine.agents.get_machine_view(machine_id: MachineId) -> MachineView

    Phase 0 behavior:
    - Return a sensible placeholder MachineView.
    - Do NOT access external systems in Phase 0.
    """
    return MachineView(
        machine_id=str(machine_id),
        name=f"machine-{machine_id}",
        cell_id="CELL-1",
        capacity=1,
        status="up",
        busy_until=None,
        metadata={}
    )


def update_operator_allocation(now: datetime) -> None:
    """
    Update operator allocations given the current time.

    Contract:
    - engine.agents.update_operator_allocation(now: Time) -> None

    Phase 0 behavior:
    - No-op placeholder that records the call (no persistent state).
    - Real allocation logic implemented in Phase 2.
    """
    # Intentionally minimal: No state mutation in Phase 0.
    return None