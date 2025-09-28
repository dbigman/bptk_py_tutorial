# INSTRUCTION-3 — Engine Scaffolding (ABM + SD Wrapper) (Phase 2)
Source: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

Objective:
- Implement minimal actor/queue abstractions enabling dispatch rules, setup matrix, failures, rework, and release control with tokens.
- Establish deterministic seeds and run manifest pattern.

Principles:
- KISS: minimal actor types (machine, operator, job queue).
- YAGNI: limit PM windows to simple cases; defer advanced behaviors.

Authoritative interfaces:
- Run lifecycle:
  - [engine.run.create_run_manifest(project_id: UUID, scenario: ScenarioConfig, seed: int) -> RunManifest](engine/run.py:12)
  - [engine.run.run_simulation(manifest: RunManifest) -> RunResultHandle](engine/run.py:20)
  - [engine.run.collect_artifacts(handle: RunResultHandle) -> ArtifactIndex](engine/run.py:28)
- Dispatch & priority:
  - [engine.dispatch.select_next_job(queue_state: QueueState, rule: DispatchRule, now: Time) -> JobId](engine/dispatch.py:12)
  - [engine.dispatch.compute_priority(rule: DispatchRule, job: JobView, state: QueueState, now: Time) -> float](engine/dispatch.py:22)
- Release control:
  - [engine.release_control.release_jobs(now: Time, policy: ReleasePolicy, state: SystemState) -> list[JobId]](engine/release_control.py:12)
  - [engine.release_control.token_balance(route: RouteId) -> int](engine/release_control.py:20)
- Failures & rework:
  - [engine.failures.next_downtime(machine_id: MachineId, now: Time) -> DowntimeWindow](engine/failures.py:12)
  - [engine.rework.apply_rework_if_needed(job: JobId, step: RouteStep, outcome: InspectionOutcome) -> Optional[RouteStep]](engine/rework.py:12)
- Agents:
  - [engine.agents.get_machine_view(machine_id: MachineId) -> MachineView](engine/agents.py:12)
  - [engine.agents.update_operator_allocation(now: Time) -> None](engine/agents.py:20)
- Storage (artifacts):
  - [engine.run.store_artifact(run_id: RunId, kind: ArtifactKind, payload: Bytes, media_type: str) -> ArtifactHandle](engine/run.py:60)
  - [engine.run.load_artifact(handle: ArtifactHandle) -> Bytes](engine/run.py:68)

Steps:
1) Define minimal data types for QueueState, JobView, SystemState, MachineView sufficient to support interfaces (no code shown).
2) Implement dispatch rule calculation semantics for EDD, SPT, ATC/ATCS, LSN through compute_priority and select_next_job (interface-only).
3) Implement release control with token-based policies CONWIP/POLCA via release_jobs/token_balance.
4) Model failures using mtbf_mttr inputs: compute next_downtime windows per machine.
5) Model rework loops via yields/rework_probability with apply_rework_if_needed.
6) Create run manifest capturing scenario, seed, and deterministic RNG state; run_simulation produces timeline CSV artifacts.
7) Use store_artifact/save to persist CSV outputs; collect_artifacts assembles ArtifactIndex.

Acceptance criteria:
- Toy baseline run executes and produces queue timeline data and simple CSV artifacts.
- Seeded re-run reproduces identical KPIs within tolerance.

MCP usage notes:
- Context7: patterns for deterministic simulations and reproducible RNG (if connected).
- Octocode: search for dispatch rule implementations for reference semantics (no code copy).
- SequentialThinking: record modeling assumptions and simplifications.