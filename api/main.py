from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel

# Lightweight reuse of engine run stubs
from engine.run import create_run_manifest, run_simulation, ValidationReport

X_API_KEY_ENV = os.environ.get("X_API_KEY", "changeme-local")

app = FastAPI(title="HMLV Manufacturing Simulator API (Phase 0)")


def require_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> None:
    """
    Dependency that enforces the presence of a valid X-API-Key header.
    Phase 0: simple equality check with X_API_KEY_ENV.
    """
    if not x_api_key or x_api_key != X_API_KEY_ENV:
        raise HTTPException(status_code=401, detail="Unauthorized")


class ProjectImportPayload(BaseModel):
    files: Dict[str, str] = {}


class ProjectSnapshot(BaseModel):
    snapshot_id: str
    project_id: str
    imported_at: datetime


class ScenarioConfig(BaseModel):
    dispatch_rule: Optional[str] = "EDD"
    wip_caps: Optional[Dict[str, int]] = None


class RunEnqueued(BaseModel):
    run_id: str
    project_id: str
    status: str
    seed: Optional[int] = None


class RunStatus(BaseModel):
    run_id: str
    status: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    progress_pct: Optional[int] = 0
    message: Optional[str] = None


class RunResultsIndex(BaseModel):
    artifacts: list = []
    summary: Dict[str, Any] = {}


class DebriefRequest(BaseModel):
    run_id: str
    template_id: Optional[str] = None


class DebriefArtifact(BaseModel):
    artifact_handle: str
    url: Optional[str] = None
    expires_at: Optional[datetime] = None


@app.post("/projects/{project_id}/import:validate", response_model=ValidationReport)
def post_validate_import(
    project_id: str,
    payload: ProjectImportPayload,
    _auth: None = Depends(require_api_key),
) -> ValidationReport:
    """
    Validate uploaded project import payload.
    Phase 0: perform trivial structure checks and return ValidationReport.
    """
    # Minimal validation: ensure required top-level CSV filenames are present
    required = {"products.csv", "routings.csv", "machines.csv"}
    present = set(payload.files.keys())
    missing = required - present
    if missing:
        return ValidationReport(
            valid=False,
            warnings=[],
            errors=[f"missing files: {sorted(missing)}"],
        )
    return ValidationReport(valid=True, warnings=[], errors=[])


@app.post("/projects/{project_id}/import:commit", response_model=ProjectSnapshot, status_code=201)
def post_commit_import(
    project_id: str,
    payload: ProjectImportPayload,
    _auth: None = Depends(require_api_key),
) -> ProjectSnapshot:
    """
    Commit an import. Phase 0: return a trivial snapshot object.
    """
    snapshot_id = f"snapshot-{project_id}-1"
    return ProjectSnapshot(
        snapshot_id=snapshot_id,
        project_id=project_id,
        imported_at=datetime.utcnow(),
    )


@app.post("/projects/{project_id}/runs", response_model=RunEnqueued, status_code=202)
def post_runs(
    project_id: str,
    scenario: ScenarioConfig,
    seed: Optional[int] = None,
    _auth: None = Depends(require_api_key),
) -> RunEnqueued:
    """
    Enqueue a run. Uses engine.run.create_run_manifest and run_simulation (phase 0 stubs).
    """
    sdict = scenario.dict()
    seed_value = int(seed) if seed is not None else 0
    manifest = create_run_manifest(project_id, sdict, seed_value)
    handle = run_simulation(manifest)
    return RunEnqueued(
        run_id=handle.run_id,
        project_id=project_id,
        status=handle.status,
        seed=seed_value,
    )


@app.get("/projects/{project_id}/runs/{run_id}", response_model=RunStatus)
def get_run(project_id: str, run_id: str, _auth: None = Depends(require_api_key)) -> RunStatus:
    """
    Return run status. Phase 0: return queued/placeholder status.
    """
    # Phase 0: we don't persist runs, so return a minimal queued status
    return RunStatus(
        run_id=run_id,
        status="queued",
        started_at=None,
        finished_at=None,
        progress_pct=0,
        message="placeholder",
    )


@app.get("/projects/{project_id}/runs/{run_id}/results", response_model=RunResultsIndex)
def get_run_results(project_id: str, run_id: str, _auth: None = Depends(require_api_key)) -> RunResultsIndex:
    """
    Return run results index. Phase 0: empty artifacts and minimal summary.
    """
    return RunResultsIndex(artifacts=[], summary={"kpis": {}})


@app.post("/projects/{project_id}/debriefs", response_model=DebriefArtifact, status_code=201)
def post_debriefs(request: DebriefRequest, project_id: str, _auth: None = Depends(require_api_key)) -> DebriefArtifact:
    """
    Render a debrief for a completed run. Phase 0: return placeholder artifact handle.
    """
    handle = f"debrief://{request.run_id}/1"
    url = f"s3://{project_id}/{request.run_id}/debrief.pdf"
    return DebriefArtifact(artifact_handle=handle, url=url, expires_at=None)


@app.get("/health")
def health() -> dict:
    """Simple health endpoint used by Docker healthchecks."""
    return {"status": "ok", "ts": datetime.utcnow().isoformat()}