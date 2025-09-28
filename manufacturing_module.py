#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import random

ARTIFACTS_DIR = ".artifacts"


@dataclass
class RunManifest:
    run_id: str
    project_id: str
    scenario: Dict[str, Any]
    seed: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RunResultHandle:
    run_id: str
    manifest: RunManifest
    artifacts: Dict[str, str]  # mapping filename -> path


@dataclass
class ArtifactHandle:
    run_id: str
    kind: str
    path: str
    media_type: str


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def create_run_manifest(project_id: str, scenario: Dict[str, Any], seed: int) -> RunManifest:
    """
    Create a deterministic RunManifest with a UUID run_id.
    This matches the contract:
      create_run_manifest(project_id: UUID, scenario: ScenarioConfig, seed: int) -> RunManifest
    """
    run_id = uuid.uuid4().hex
    return RunManifest(run_id=run_id, project_id=project_id, scenario=scenario, seed=int(seed))


def _artifact_dir_for_run(run_id: str) -> str:
    return os.path.join(ARTIFACTS_DIR, run_id)


def store_artifact(run_id: str, kind: str, payload: bytes, media_type: str) -> ArtifactHandle:
    """
    Store an artifact under .artifacts/{run_id}/{kind}.{ext} and return an ArtifactHandle.
    """
    d = _artifact_dir_for_run(run_id)
    _ensure_dir(d)
    ext = "bin"
    if media_type == "text/csv":
        ext = "csv"
    elif media_type == "application/json":
        ext = "json"
    fname = f"{kind}.{ext}"
    path = os.path.join(d, fname)
    with open(path, "wb") as f:
        f.write(payload)
    return ArtifactHandle(run_id=run_id, kind=kind, path=path, media_type=media_type)


def load_artifact(handle: ArtifactHandle) -> bytes:
    with open(handle.path, "rb") as f:
        return f.read()


def collect_artifacts(run_id: str) -> Dict[str, str]:
    """
    Return a mapping of artifact filename -> absolute path for the given run_id.
    This matches the contract:
      collect_artifacts(handle: RunResultHandle) -> ArtifactIndex
    For simplicity this function accepts run_id and returns files found.
    """
    d = _artifact_dir_for_run(run_id)
    if not os.path.isdir(d):
        return {}
    out: Dict[str, str] = {}
    for fname in os.listdir(d):
        out[fname] = os.path.join(d, fname)
    return out


def _validate_scenario(scenario: Dict[str, Any]) -> None:
    if not isinstance(scenario, dict):
        raise TypeError("scenario must be a dict")
    jobs = scenario.get("jobs")
    if jobs is None or not isinstance(jobs, list):
        raise ValueError("scenario must contain 'jobs' as a list")
    for i, j in enumerate(jobs):
        if "job_id" not in j:
            raise ValueError(f"job at index {i} missing 'job_id'")
        if "process_time_mean" not in j:
            raise ValueError(f"job {j.get('job_id')} missing 'process_time_mean'")
        if not (isinstance(j["process_time_mean"], (int, float)) and j["process_time_mean"] > 0):
            raise ValueError(f"job {j.get('job_id')} has invalid process_time_mean")


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def run_simulation(manifest: RunManifest) -> RunResultHandle:
    """
    Minimal deterministic simulation:
    - Processes manifest.scenario['jobs'] sequentially using seeded RNG.
    - Writes .artifacts/{run_id}/timeline.csv and .artifacts/{run_id}/kpis.json.
    - Returns RunResultHandle referencing artifacts.

    This implements the contract:
      run_simulation(manifest: RunManifest) -> RunResultHandle
    """
    _validate_scenario(manifest.scenario)
    rng = random.Random(manifest.seed)
    base_time = manifest.created_at
    timeline_rows: List[Dict[str, Any]] = []
    jobs = manifest.scenario.get("jobs", [])
    for idx, job in enumerate(jobs):
        job_id = str(job.get("job_id"))
        product_id = job.get("product_id")
        mean_hours = float(job.get("process_time_mean"))
        # deterministic per-job draw: derive per-job seed from manifest.seed and index
        seed_advance = int(rng.random() * 1_000_000)
        job_rng = random.Random(manifest.seed + idx + seed_advance)
        # simple bounded gaussian around mean (sigma = 10% of mean)
        sigma = max(0.001, mean_hours * 0.1)
        process_time = max(0.0001, job_rng.gauss(mean_hours, sigma))
        start_time = base_time
        end_time = start_time + timedelta(hours=process_time)
        due_offset = job.get("due_offset_hours")
        due_time = None
        if due_offset is not None:
            try:
                due_time = base_time + timedelta(hours=float(due_offset))
            except Exception:
                due_time = None
        completed_on_time = True
        if due_time is not None and end_time > due_time:
            completed_on_time = False
        timeline_rows.append(
            {
                "run_id": manifest.run_id,
                "job_id": job_id,
                "product_id": product_id,
                "start_time": _iso(start_time),
                "end_time": _iso(end_time),
                "process_time_hours": f"{process_time:.6f}",
                "due_time": _iso(due_time) if due_time else "",
                "completed_on_time": str(completed_on_time),
            }
        )
        # advance base_time to end_time for sequential processing
        base_time = end_time

    # write timeline CSV
    artifact_dir = _artifact_dir_for_run(manifest.run_id)
    _ensure_dir(artifact_dir)
    timeline_path = os.path.join(artifact_dir, "timeline.csv")
    with open(timeline_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "run_id",
            "job_id",
            "product_id",
            "start_time",
            "end_time",
            "process_time_hours",
            "due_time",
            "completed_on_time",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in timeline_rows:
            writer.writerow(r)

    # compute simple KPIs
    total_jobs = len(timeline_rows)
    avg_process = sum(float(r["process_time_hours"]) for r in timeline_rows) / total_jobs if total_jobs else 0.0
    on_time = sum(1 for r in timeline_rows if r["completed_on_time"] == "True")
    kpis = {
        "run_id": manifest.run_id,
        "total_jobs": total_jobs,
        "avg_process_time_hours": avg_process,
        "on_time_count": on_time,
        "on_time_rate": on_time / total_jobs if total_jobs else 0.0,
    }
    kpis_bytes = json.dumps(kpis, indent=2).encode("utf-8")
    kpis_handle = store_artifact(manifest.run_id, "kpis", kpis_bytes, "application/json")
    timeline_handle = ArtifactHandle(run_id=manifest.run_id, kind="timeline", path=timeline_path, media_type="text/csv")

    artifacts = {
        os.path.basename(kpis_handle.path): kpis_handle.path,
        os.path.basename(timeline_handle.path): timeline_handle.path,
    }
    return RunResultHandle(run_id=manifest.run_id, manifest=manifest, artifacts=artifacts)


if __name__ == "__main__":
    # quick smoke test when run as script
    sample_scenario = {
        "jobs": [
            {"job_id": "job-1", "product_id": "p1", "process_time_mean": 1.0, "due_offset_hours": 2},
            {"job_id": "job-2", "product_id": "p2", "process_time_mean": 0.5, "due_offset_hours": 3},
        ]
    }
    m = create_run_manifest("proj-example", sample_scenario, seed=12345)
    result = run_simulation(m)
    print("Run artifacts:", result.artifacts)