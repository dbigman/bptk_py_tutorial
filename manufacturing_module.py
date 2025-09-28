# [`manufacturing_module.py`](manufacturing_module.py:1)
"""
Manufacturing module - minimal, deterministic simulation utilities for HMLV MVP.

Implements authoritative Phase-0/Phase-1 interfaces described in:
- implementation_plan_2025-09-27T18-06-45Z.md
- agent_instructions/INSTRUCTION-2.md

KISS/YAGNI: small, well-typed, deterministic behavior suitable for integration
tests and local development. Produces CSV/JSON artifacts under .artifacts/{run_id}/
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
import random
import os
import json
import csv
import statistics

# ---- Data classes (contracts) ----


@dataclass
class RunManifest:
    run_id: str
    project_id: str
    scenario: Dict[str, Any]
    seed: int
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RunResultHandle:
    run_id: str
    status: str = "queued"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    artifacts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ArtifactHandle:
    handle: str
    url: Optional[str] = None
    kind: Optional[str] = None


@dataclass
class ArtifactIndex:
    run_id: str
    artifacts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ValidationReport:
    valid: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ---- Utilities ----


def _ensure_artifact_dir(run_id: str) -> str:
    path = os.path.join(".artifacts", run_id)
    os.makedirs(path, exist_ok=True)
    return path


def _local_url_for(path: str) -> str:
    return f"file://{os.path.abspath(path)}"


# ---- Core contracts implementations ----


def create_run_manifest(project_id: str, scenario: Dict[str, Any], seed: int) -> RunManifest:
    """
    Create a deterministic run manifest.
    """
    rid = str(uuid4())
    return RunManifest(run_id=rid, project_id=project_id, scenario=dict(scenario), seed=int(seed))


def run_simulation(manifest: RunManifest) -> RunResultHandle:
    """
    Run a minimal deterministic simulation based on manifest. Phase-1 behaviour:
    - Expects manifest.scenario to include:
        - jobs: List[Dict] each with job_id, product_id, process_time_mean, due_offset_hours
        - routings: Optional mapping (ignored in this minimal runner)
        - setup_matrix: Optional list rows with from_family,to_family,setup_time_hours
        - wip_policy: dict with release policy parameters (ignored here)
    - Produces timeline CSV and KPIs JSON/CSV artifacts under .artifacts/{run_id}/
    """
    handle = RunResultHandle(run_id=manifest.run_id, status="running", started_at=datetime.utcnow())
    rng = random.Random(manifest.seed)

    # Map input scenario to internal collections with defaults
    jobs_input = manifest.scenario.get("jobs", [])
    setup_matrix = manifest.scenario.get("setup_matrix", [])
    # Build a quick lookup for setup times by (from_family,to_family)
    setup_lookup: Dict[Tuple[str, str], float] = {}
    for row in setup_matrix:
        ff = str(row.get("from_family_id", ""))
        tf = str(row.get("to_family_id", ""))
        st = float(row.get("setup_time", 0.0))
        setup_lookup[(ff, tf)] = st

    # Minimal state
    timeline_rows: List[Dict[str, Any]] = []
    machine_busy_until: Dict[str, datetime] = {}
    machine_work_seconds: Dict[str, float] = {}
    job_completion_times: Dict[str, datetime] = {}

    now = datetime.utcnow()
    base_time = now

    # For simplicity, assume single machine 'M1' and single family per job via product_id
    last_family: Optional[str] = None
    machine_id = "M1"
    machine_available_at = base_time

    for idx, job in enumerate(jobs_input):
        jid = str(job.get("job_id", f"job-{idx}"))
        product = str(job.get("product_id", f"prod-{idx}"))
        process_time_hours = float(job.get("process_time_mean", 1.0))
        due_offset = float(job.get("due_offset_hours", 24.0))
        release_time = base_time + timedelta(hours=float(job.get("release_offset_hours", 0.0)))
        # Apply sequence-dependent setup if family changed
        setup_hours = 0.0
        if last_family is not None:
            setup_hours = setup_lookup.get((last_family, product), 0.0)
        # Introduce small random jitter but deterministic via seeded RNG
        jitter = rng.uniform(-0.05, 0.05) * process_time_hours
        effective_process = max(0.0, process_time_hours + jitter)
        # Start time is when machine is free and after release_time
        start_time = max(machine_available_at, release_time)
        # Account for setup as separate event
        if setup_hours > 0:
            setup_start = start_time
            setup_end = setup_start + timedelta(hours=setup_hours)
            timeline_rows.append({
                "run_id": manifest.run_id,
                "job_id": jid,
                "machine_id": machine_id,
                "event": "setup",
                "start": setup_start.isoformat(),
                "end": setup_end.isoformat(),
                "duration_hours": setup_hours,
                "product_family_from": last_family,
                "product_family_to": product,
            })
            start_time = setup_end
            machine_work_seconds[machine_id] = machine_work_seconds.get(machine_id, 0.0) + setup_hours * 3600.0
        # Processing event
        proc_start = start_time
        proc_end = proc_start + timedelta(hours=effective_process)
        timeline_rows.append({
            "run_id": manifest.run_id,
            "job_id": jid,
            "machine_id": machine_id,
            "event": "process",
            "start": proc_start.isoformat(),
            "end": proc_end.isoformat(),
            "duration_hours": effective_process,
            "product_family": product,
        })
        # Update states
        machine_available_at = proc_end
        machine_work_seconds[machine_id] = machine_work_seconds.get(machine_id, 0.0) + effective_process * 3600.0
        job_completion_times[jid] = proc_end
        last_family = product

    # Compute KPIs
    due_dates: Dict[str, datetime] = {}
    lead_times_hours: List[float] = []
    otd_count = 0
    total_jobs = len(jobs_input)
    for idx, job in enumerate(jobs_input):
        jid = str(job.get("job_id", f"job-{idx}"))
        completion = job_completion_times.get(jid, base_time)
        due_offset = float(job.get("due_offset_hours", 24.0))
        due = base_time + timedelta(hours=due_offset)
        due_dates[jid] = due
        lead_hours = max(0.0, (completion - (base_time + timedelta(hours=float(job.get("release_offset_hours", 0.0))))).total_seconds() / 3600.0)
        lead_times_hours.append(lead_hours)
        if completion <= due:
            otd_count += 1

    otd_pct = (otd_count / total_jobs * 100.0) if total_jobs > 0 else 0.0
    lead_avg = statistics.mean(lead_times_hours) if lead_times_hours else 0.0
    lead_p90 = statistics.quantiles(lead_times_hours, n=10)[-1] if len(lead_times_hours) >= 1 else 0.0

    util = {}
    for mid, busy_secs in machine_work_seconds.items():
        # horizon approximated as last completion - base_time
        horizon_secs = (machine_available_at - base_time).total_seconds() if machine_available_at > base_time else 1.0
        util[mid] = min(1.0, busy_secs / horizon_secs) if horizon_secs > 0 else 0.0

    kpi_report = {
        "run_id": manifest.run_id,
        "project_id": manifest.project_id,
        "seed": manifest.seed,
        "total_jobs": total_jobs,
        "otd_pct": round(otd_pct, 4),
        "lead_time_avg_hours": round(lead_avg, 4),
        "lead_time_p90_hours": round(lead_p90, 4),
        "machine_utilization": {k: round(v, 4) for k, v in util.items()},
        "generated_at": datetime.utcnow().isoformat(),
    }

    # Persist artifacts
    artdir = _ensure_artifact_dir(manifest.run_id)
    timeline_path = os.path.join(artdir, "timeline.csv")
    with open(timeline_path, "w", newline="", encoding="utf-8") as fh:
        fieldnames = ["run_id", "job_id", "machine_id", "event", "start", "end", "duration_hours", "product_family", "product_family_from", "product_family_to"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in timeline_rows:
            writer.writerow(row)

    kpi_json_path = os.path.join(artdir, "kpis.json")
    with open(kpi_json_path, "w", encoding="utf-8") as fh:
        json.dump(kpi_report, fh, indent=2)

    kpi_csv_path = os.path.join(artdir, "kpis.csv")
    with open(kpi_csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["metric", "value"])
        writer.writerow(["total_jobs", total_jobs])
        writer.writerow(["otd_pct", kpi_report["otd_pct"]])
        writer.writerow(["lead_time_avg_hours", kpi_report["lead_time_avg_hours"]])
        writer.writerow(["lead_time_p90_hours", kpi_report["lead_time_p90_hours"]])

    # Build handle artifacts
    artifacts = [
        {"kind": "timeline.csv", "path": timeline_path, "url": _local_url_for(timeline_path)},
        {"kind": "kpis.json", "path": kpi_json_path, "url": _local_url_for(kpi_json_path)},
        {"kind": "kpis.csv", "path": kpi_csv_path, "url": _local_url_for(kpi_csv_path)},
    ]

    handle.status = "completed"
    handle.finished_at = datetime.utcnow()
    handle.artifacts = artifacts
    return handle


def collect_artifacts(handle: RunResultHandle) -> ArtifactIndex:
    """
    Return artifact index for a completed run.
    """
    artdir = os.path.join(".artifacts", handle.run_id)
    artifacts: List[Dict[str, Any]] = []
    if os.path.isdir(artdir):
        for fname in sorted(os.listdir(artdir)):
            fpath = os.path.join(artdir, fname)
            artifacts.append({"kind": fname, "path": fpath, "url": _local_url_for(fpath)})
    return ArtifactIndex(run_id=handle.run_id, artifacts=artifacts)


def store_artifact(run_id: str, kind: str, payload: bytes, media_type: str) -> ArtifactHandle:
    """
    Store arbitrary artifact bytes to .artifacts/{run_id}/{kind} and return handle.
    """
    artdir = _ensure_artifact_dir(run_id)
    filename = f"{kind}"
    path = os.path.join(artdir, filename)
    with open(path, "wb") as fh:
        fh.write(payload)
    return ArtifactHandle(handle=f"artifact://{run_id}/{kind}", url=_local_url_for(path), kind=kind)


def load_artifact(handle: str) -> bytes:
    """
    Load artifact bytes from a handle of the form artifact://{run_id}/{kind}
    """
    try:
        prefix = "artifact://"
        if not handle.startswith(prefix):
            return b""
        body = handle[len(prefix) :]
        run_id, kind = body.split("/", 1)
        path = os.path.join(".artifacts", run_id, kind)
        with open(path, "rb") as fh:
            return fh.read()
    except Exception:
        return b""


# ---- Scenario helpers ----


def generate_scenarios(base: Dict[str, Any], sweeps: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """
    Generate cartesian product of sweeps merged with base (deterministic ordering).
    """
    if not sweeps:
        return [dict(base)]
    keys = sorted(sweeps.keys())
    lists = [list(sweeps[k]) for k in keys]
    results: List[Dict[str, Any]] = []
    import itertools

    for combo in itertools.product(*lists):
        cfg = dict(base)
        for k, v in zip(keys, combo):
            cfg[k] = v
        results.append(cfg)
    return results


def execute_experiments(configs: List[Dict[str, Any]], seed_base: int, parallelism: int = 1) -> str:
    """
    Enqueue and run experiments sequentially (parallelism ignored for Phase-1).
    Writes a batch file under .experiments/.
    """
    batch_id = f"batch-{str(uuid4())}"
    os.makedirs(".experiments", exist_ok=True)
    batch_entries = []
    for idx, cfg in enumerate(configs):
        seed = int(seed_base) + idx
        proj = cfg.get("project_id", "unknown")
        manifest = create_run_manifest(project_id=proj, scenario=cfg, seed=seed)
        handle = run_simulation(manifest)
        batch_entries.append({
            "index": idx,
            "run_id": handle.run_id,
            "project_id": proj,
            "seed": seed,
            "status": handle.status,
        })
    batch_path = os.path.join(".experiments", f"{batch_id}.json")
    with open(batch_path, "w", encoding="utf-8") as fh:
        json.dump({"batch_id": batch_id, "runs": batch_entries}, fh, indent=2, default=str)
    return batch_id


# ---- Validation / Import mapping ----


def validate_project_config(doc: Dict[str, Any]) -> ValidationReport:
    """
    Minimal validation consistent with INSTRUCTION-2:
    - Ensures top-level keys exist and simple numeric constraints.
    """
    errors: List[str] = []
    warnings: List[str] = []
    required = ("plant", "products", "routings", "machines")
    if not isinstance(doc, dict):
        return ValidationReport(valid=False, warnings=warnings, errors=["document must be a dict"])
    for k in required:
        if k not in doc:
            errors.append(f"missing required key: {k}")
    # Numeric constraint example
    products = doc.get("products", [])
    for p in products:
        pt = p.get("process_time_mean")
        if pt is None:
            warnings.append(f"product {p.get('product_id', '<unknown>')} missing process_time_mean")
        else:
            try:
                if float(pt) <= 0.0:
                    errors.append(f"product {p.get('product_id', '<unknown>')} has non-positive process_time_mean")
            except Exception:
                errors.append(f"product {p.get('product_id', '<unknown>')} invalid process_time_mean")
    return ValidationReport(valid=(len(errors) == 0), warnings=warnings, errors=errors)


def map_csvs_to_project(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Naive mapper: accepts list of parsed CSV dicts with 'name' keys mapping them.
    Returns a ProjectConfig skeleton used by the runner.
    """
    project: Dict[str, Any] = {"plant": "toy-plant", "products": [], "routings": [], "machines": [], "jobs": []}
    for d in documents:
        name = d.get("name", "").lower()
        rows = d.get("rows", [])
        if name == "products":
            project["products"] = rows
        elif name == "routings":
            project["routings"] = rows
        elif name == "machines":
            project["machines"] = rows
        elif name == "jobs":
            project["jobs"] = rows
    return project