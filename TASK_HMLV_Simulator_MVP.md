# TASK: Design & scaffolding for an HMLV Manufacturing Simulator (MVP)

## Role
You are a senior product+engineering copilot. Your job is to turn a PRD for a **High-Mix/Low-Volume (HMLV) Manufacturing Simulator** into concrete deliverables: data templates, API + engine scaffolding, experiment configs, and UX artifacts that a team can implement immediately.

## Goal
Deliver a minimal but complete **implementation blueprint** and **starter assets** for an MVP that lets users:
- Import plant data
- Run **baseline** vs **scenario** simulations with configurable dispatching (EDD, SPT, ATC/ATCS, LSN), **CONWIP/POLCA**, sequence-dependent setups, failures/PM, and rework
- View KPIs and export a one-page debrief

## Context (from PRD)
- Users: Ops Excellence Lead (primary), Plant Scheduler, Manufacturing/IE, Facilitator
- Core scope: Hybrid sim (ABM shop floor + SD release control), multi-cell flow, finite machines & shared labor, setup matrix by product family, rework loops, PM/failures
- KPIs: OTD %, lead time (avg/p90), WIP, machine/labor utilization, setup hours, scrap/rework, plus baseline↔scenario deltas
- Non-goals: no 3D, no MRP replacement, simple PM only
- Tech direction: Python 3.11+, FastAPI backend, React/Next.js, BPTK-Py or equivalent for sim core, queue worker, Postgres, S3/MinIO, containerized

## What to Produce (deliverables)
1) **Data Contract Pack**
   - CSV templates (with headers, datatypes, examples) for:
     - `products.csv`, `routings.csv`, `machines.csv`, `operators.csv`, `setup_matrix.csv`, `demand.csv`, `calendars.csv`, `mtbf_mttr.csv`, `yields.csv`, `skills.csv`
   - A unified **JSON Schema** (`/schemas/project_config.schema.json`) that validates a project import (see “Output Formats”).
2) **Simulation Engine Scaffolding (Python)**
   - Module layout (files, classes, interfaces) enabling:
     - Agents: `Job`, `Machine`, `Operator`, optional `Cell`
     - Queues with pluggable dispatch rules; setup-time application via family→family matrix
     - Failures (MTBF/MTTR), planned downtime calendar, simple rework loop
     - SD wrapper controlling release via **CONWIP/POLCA** tokens and due-date quoting hook
   - Deterministic seeds & run manifest
3) **Experiment Runner**
   - A parameterized config format (`experiments.yaml`) supporting sweeps (e.g., setup_time_factor=[1.0,0.9,0.75], wip_cards=[8,12,16], rule∈{EDD,ATCS,LSN}, add_floater∈{0,1})
   - CLI examples to run N scenarios in parallel with unique seeds
4) **KPI & Reporting Spec**
   - SQL-free, code-level definitions for each KPI and required intermediate metrics
   - A one-page **Debrief template** (Markdown→PDF) with placeholders
5) **API & UI Contracts**
   - OpenAPI (YAML) for: upload, validate, run, get results, export
   - React component outline for: Data Wizard, Scenario Table, Results Dashboard (Baseline vs Scenario), Debrief view
6) **Validation Playbook**
   - Steps and checks to calibrate against last 30–90 days of history; pass criteria (±10% error on OTD/lead time)

## Output Formats
- **Primary answer**: a single structured Markdown document with code blocks.
- Include **copy-ready** files inside fenced code blocks with filenames.
- All machine-readable artifacts must be valid (JSON/JSON Schema/YAML/Python/TSX).

### JSON Schema (top-level) must include:
- `plant`: name, timezone
- arrays for each template with field constraints (types, enums, required)
- cross-file referential integrity (e.g., `routing.machine_id` must exist in `machines.id`)
- numeric constraints (e.g., `process_time_mean > 0`, `setup_time ≥ 0`)

### OpenAPI must include endpoints:
- `POST /projects/{id}/import:validate`
- `POST /projects/{id}/import:commit`
- `POST /projects/{id}/runs` (body: scenario config)
- `GET /projects/{id}/runs/{run_id}`
- `GET /projects/{id}/runs/{run_id}/results`
- `POST /projects/{id}/debriefs` (returns PDF handle)

## Constraints & Style
- Favor **clarity over completeness**; ship scaffolding that compiles.
- Keep external deps minimal; do not rely on GPUs or proprietary libs.
- Use docstrings and short comments explaining why (not just what).
- Provide small **worked examples** (toy dataset: 6 families, 3 cells, 7 machines).

## Reasoning Workflow (what you should show)
1) Derive minimal field sets for each CSV based on PRD needs.
2) Define algorithms (pseudo/actual code) for:
   - Dispatch rules (EDD, SPT, ATC/ATCS, LSN) with equations for ATCS
   - Setup selection: apply `setup_matrix[last_family][next_family]`
   - Failure events (exponential MTBF) and PM blackout windows
   - Rework probability and loop placement
   - CONWIP/POLCA token logic, due-date quoting heuristic
3) Specify KPIs precisely (inputs → formula → units → sampling).
4) Provide **testable** fixtures and a tiny baseline vs scenario run.

## Acceptance Criteria (for your outputs)
- All schemas validate against provided toy CSVs (include a `jq` or `python -m jsonschema` example).
- Python scaffolding imports and runs a toy baseline + 2 scenarios locally (no cloud).
- KPIs print as a compact table **and** write to CSV.
- Debrief renders to Markdown (include example output).
- The OpenAPI parses with `swagger-cli validate` (assume availability).

## Example Snippets to Include
- **ATCS priority**:
  ```
  priority = exp(-max(0, (d_j - p_j - t_now))/k1) / (s_j^k2 * setup_penalty)
  ```
  where `d_j` due date, `p_j` remaining proc time, `s_j` slack; choose reasonable k1,k2.
- **CONWIP**:
  ```
  if tokens_available(route) and wip(route) < wip_cap: release(job)
  ```

## Guardrails
- Do not add non-PRD scope (no 3D, no ERP connectors).
- Keep numeric examples modest (dozens of jobs) so snippets are runnable.
- Clearly separate MVP vs. post-MVP notes.

---

### Deliverable Skeleton (the LLM should fill these)
- `/schemas/project_config.schema.json` (JSON Schema)
- `/examples/toy/*.csv` (all templates with 10–30 rows each)
- `/engine/__init__.py`, `/engine/agents.py`, `/engine/dispatch.py`, `/engine/failures.py`, `/engine/rework.py`, `/engine/release_control.py`, `/engine/run.py`
- `/experiments.yaml`
- `/kpis/spec.md` (formulas) and `/kpis/compute.py`
- `/api/openapi.yaml`
- `/ui/Outline.md`
- `/reports/debrief_template.md`
- `/Makefile` with `make run_toy`, `make lint`, `make debrief`
