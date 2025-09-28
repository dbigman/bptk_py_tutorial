# INSTRUCTION-4 — Experiment Runner (Phase 3)
Source: [implementation_plan_2025-09-27T18-06-45Z.md](implementation_plan_2025-09-27T18-06-45Z.md)

Objective:
- Support parameter sweeps via experiments.yaml and orchestrate batch runs with unique seeds and parallelism.

Principles:
- KISS: flat list of scenarios; simple parallel execution.
- YAGNI: avoid nested sweeps or complex DOE.

Authoritative interfaces:
- [engine.run.generate_scenarios(base: ScenarioSpec, sweeps: ParamSweepSpec) -> list[ScenarioConfig]](engine/run.py:36)
- [engine.run.execute_experiments(configs: list[ScenarioConfig], seed_base: int, parallelism: int) -> ExperimentBatchId](engine/run.py:44)
- [engine.run.get_experiment_batch(batch_id: ExperimentBatchId) -> ExperimentBatchView](engine/run.py:52)

Steps:
1) Author [experiments.yaml](experiments.yaml) to allow parameters: setup_time_factor, wip_cards, rule, add_floater, etc.
2) Implement generate_scenarios to produce distinct ScenarioConfig entries from base + sweeps.
3) Implement execute_experiments to run N >= 10 scenarios in parallel locally; seed per scenario = seed_base + index.
4) Persist batch result index and include per-scenario seed in structured logs.
5) Provide get_experiment_batch view summarizing statuses and artifact links.

Acceptance criteria:
- N (>=10) scenarios run in parallel locally.
- Batch result index persisted; per-scenario seed logged.

MCP usage notes:
- Context7: Celery patterns for parallelism and progress reporting (if connected).
- Octocode: review exemplar experiment runner orchestration structures.
- SequentialThinking: capture decisions on seeding, parallelism, and batch metadata.