# Product Requirements Document (PRD)

## 1) Introduction
**Purpose.** Create a simulation product that helps high‑mix/low‑volume (HMLV) manufacturers design and test operations policies (dispatching, WIP control, lot sizing, PM) before changing the real shop floor.

**Audience.** Product, engineering, data science, ops excellence leaders, pilot customers, and facilitators.

## 2) Product Overview
**Vision.** A practical, data‑driven “digital sandbox” for HMLV plants to cut lead time and improve on‑time delivery (OTD) without brute‑force capacity increases.

**Goals & Objectives.**
- Reduce simulated lead time and tardiness; generate actions that translate to ≥10% OTD lift in pilots.
- Let users A/B/C‑test policies safely in hours, not weeks.
- Be easy to adopt: import data, run a baseline, compare policies, export a one‑page debrief.

**What it does (scope).**
- Hybrid simulation (ABM + SD) of multi‑cell HMLV flows with sequence‑dependent changeovers, finite machines, shared labor, QC/rework, and PM.
- Scenario authoring, experiment runner, dashboards, and report export.

**What it does NOT do (out of scope for MVP).**
- Detailed CAD/layout simulation or 3D visualization.
- Full MRP/APS replacement; no automatic schedule release to shop systems.
- Predictive maintenance modeling beyond schedule‑based and simple condition thresholds.

## 3) User Stories & Requirements
**Personas.**
- *Ops Excellence Lead (primary):* needs to test policies and present ROI.
- *Plant Scheduler:* wants dispatch rules and WIP caps that reduce firefighting.
- *Manufacturing/Industrial Engineer:* calibrates process/setup data and validates results.
- *Facilitator/Consultant:* runs workshops with cohorts and exports debriefs.

**User Stories.**
1. As an Ops Lead, I want to **import routings, times, and setup matrix** from CSV/Excel so I can build a baseline quickly.
2. As a Scheduler, I want to **toggle dispatch rules (EDD, SPT, ATC/ATCS, LSN)** and **set WIP caps (CONWIP/POLCA)** so I can compare tardiness.
3. As an Engineer, I want **failure/PM calendars (MTBF/MTTR, planned downtime)** so I can reflect machine reality.
4. As a Facilitator, I want to **define experiments** (e.g., setup −25%, add 1 cross‑trained floater) and **export a one‑page debrief**.
5. As any user, I want **KPIs** (lead time distribution, OTD, WIP, utilization, setup hours) **with before/after deltas**.

**Functional Requirements (MVP).**
- Data ingest: CSV/Excel templates for **Products/Families**, **Routings & eligible machines**, **Process times (avg/σ)**, **Setup matrix (family↔family)**, **Demand mix & arrivals**, **Calendars**, **Labor skills**, **MTBF/MTTR**, **Yields**.
- Modeling: Agents for *Job, Machine, Operator, QC/Rework*; queues with pluggable dispatching; sequence‑dependent setups; rework loops; finite labor pools; PM/failures; SD wrapper for backlog ↔ release (CONWIP/POLCA tokens) and due‑date quoting.
- Experiments: parameter sweeps; scenario cloning; randomized seeds; side‑by‑side comparison.
- Analytics: KPI dashboards; lead‑time histograms; Gantt‑like machine timelines; contribution analysis for tardiness (queue vs. setup vs. failure vs. process).
- Collaboration: project workspaces; scenario versioning; role‑based access (Owner/Editor/Viewer).
- Reporting: export **PDF/PNG** debriefs and **CSV** results.

**Non‑Functional Requirements.**
- **Performance:** baseline of 10k jobs simulated ≤5 minutes on a standard cloud instance; experiments run in parallel.
- **Accuracy:** calibration workflow to match historical OTD/lead‑time within ±10%.
- **Security:** SSO (OAuth/OIDC), data encryption at rest/in transit.
- **Reliability:** ≥99.5% monthly uptime; deterministic replays via seeds and versioned models.
- **Accessibility:** WCAG 2.1 AA for the web app.

## 4) Acceptance Criteria (MVP)
- Users can upload all required templates; validation highlights missing/invalid fields and offers sample files.
- Simulation engine supports EDD, SPT, ATC/ATCS, LSN; CONWIP and POLCA between cells; sequence‑dependent setup times via matrix; failure & PM calendars; basic rework.
- Dashboard shows: OTD %, average/90th lead time, WIP, machine & labor utilization, setup hours, scrap/rework rate; all metrics compare **Baseline vs. Scenario** with charts and deltas.
- Experiment runner executes ≥10 scenarios in parallel and returns results with seed logs.
- Report export produces a one‑page PDF with context, KPIs, and “Recommended Policy”.

## 5) Assumptions, Constraints, Dependencies
- Plants can provide minimal historical data for calibration (last 30–90 days).
- Data variability: where σ missing, default coefficients or triangular distributions are acceptable.
- Dependencies: Python simulation framework (BPTK‑Py or equivalent), job queue, charting library, PDF service, cloud object storage.

## 6) User Experience Guidelines
- **Home/Projects:** card list of plants; CTA: *Start New Simulation*.
- **Data Setup:** stepper wizard (Templates → Upload → Validate → Map columns → Preview).
- **Scenarios:** table with parameters; “Clone as Experiment”; quick diffs.
- **Results:** tabs *KPIs*, *Timelines*, *Bottlenecks*, *Assumptions*; comparison toggle (Baseline ⇄ Scenario).
- **Debrief:** auto‑generated one‑pager with executive summary and next‑steps.

## 7) Technical Considerations
- **Backend:** Python 3.11+, FastAPI; BPTK‑Py hybrid simulation; Celery/RQ + Redis for async runs; PostgreSQL for metadata; MinIO/S3 for artifacts; containerized with Docker.
- **Frontend:** React/Next.js; REST/GraphQL API; charts via Plotly or ECharts.
- **Architecture:** stateless API; simulation workers autoscale; scenario/model versions stored immutably; seeds for reproducibility.
- **Integrations (post‑MVP):** import from ERP/MES (CSV first; connectors later).

## 8) Metrics & Success Criteria
- **Time‑to‑Baseline:** ≤60 minutes from project creation to first calibrated run.
- **Activation:** ≥70% of new projects run ≥3 scenarios within week 1.
- **Outcome:** In 2 pilot plants, recommended policy yields ≥10% OTD lift or ≥20% lead‑time reduction within 60 days.
- **Reliability:** Failed runs <1% (excluding invalid data). NPS ≥40 among pilot users.

## 9) Release Criteria (MVP Go/No‑Go)
- All Acceptance Criteria met; security review passed; P0/P1 bugs closed.
- Two reference pilots completed with written case studies.
- Documentation: data template guide, modeling assumptions, and admin runbook.

---
**Roadmap (post‑MVP, not in scope):** multi‑plant what‑ifs, reinforcement‑learning policy tuner, cost/CO2 accounting, basic layout distance modeling, connectors (Odoo, SAP, Oracle), and LMS‑style cohort facilitation.

