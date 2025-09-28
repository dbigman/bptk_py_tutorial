"""
Engine run module - Phase 0 placeholders.

Provides minimal dataclasses and function stubs for run lifecycle and
artifact handling. Real implementations belong to Phase 2+.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import itertools
import os
import json
import random
import csv
from jsonschema import Draft7Validator, FormatChecker
from zoneinfo import available_timezones


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


@dataclass
class ArtifactIndex:
    run_id: str
    artifacts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ArtifactHandle:
    handle: str
    url: Optional[str] = None


@dataclass
class ValidationReport:
    valid: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def _parse_issue_string(s: str) -> Dict[str, Optional[str]]:
    """
    Parse an issue string of the form:
      "file:{name},row:{row},column:{col},message:{text}"
    into a dict { "file": name, "row": row, "column": col, "message": text }.
    Returns None for missing parts.
    """
    parts: Dict[str, Optional[str]] = {"file": None, "row": None, "column": None, "message": None}
    try:
        for part in s.split(","):
            if ":" in part:
                k, v = part.split(":", 1)
                k = k.strip()
                v = v.strip()
                if k in parts:
                    parts[k] = v
    except Exception:
        # best-effort: return message under 'message'
        parts["message"] = s
    return parts


from dataclasses import asdict

@dataclass
class ValidationIssue:
    file: Optional[str]
    row: Optional[int]
    column: Optional[str]
    message: str
    severity: str = "error"

def build_structured_report(report: ValidationReport) -> Dict[str, Any]:
    """
    Convert ValidationReport with string entries into a structured report using ValidationIssue.
    Keeps original warnings/errors lists as well.
    """
    structured_errors = []
    for e in report.errors:
        parts = _parse_issue_string(e)
        row_val = None
        try:
            row_val = int(parts.get("row")) if parts.get("row") and parts.get("row").isdigit() else None
        except Exception:
            row_val = None
        issue = ValidationIssue(
            file=parts.get("file"),
            row=row_val,
            column=parts.get("column"),
            message=parts.get("message") or e,
            severity="error",
        )
        structured_errors.append(asdict(issue))

    structured_warnings = []
    for w in report.warnings:
        parts = _parse_issue_string(w)
        row_val = None
        try:
            row_val = int(parts.get("row")) if parts.get("row") and parts.get("row").isdigit() else None
        except Exception:
            row_val = None
        issue = ValidationIssue(
            file=parts.get("file"),
            row=row_val,
            column=parts.get("column"),
            message=parts.get("message") or w,
            severity="warning",
        )
        structured_warnings.append(asdict(issue))

    return {
        "valid": report.valid,
        "warnings": report.warnings,
        "errors": report.errors,
        "structured_warnings": structured_warnings,
        "structured_errors": structured_errors,
    }


@dataclass
class ProjectSnapshot:
    snapshot_id: str
    project_id: str
    imported_at: datetime = field(default_factory=datetime.utcnow)
    file_counts: Dict[str, int] = field(default_factory=dict)
    checksum: Optional[str] = None


def create_run_manifest(
    project_id: str, scenario: Dict[str, Any], seed: int
) -> RunManifest:
    """Create a deterministic run manifest (Phase 0 placeholder)."""
    rid = str(uuid4())
    return RunManifest(
        run_id=rid,
        project_id=project_id,
        scenario=scenario,
        seed=int(seed),
    )


def run_simulation(manifest: RunManifest) -> RunResultHandle:
    """
    Run a tiny deterministic simulation producing a simple timeline CSV artifact.

    Phase 2 starter behavior:
    - Uses manifest.seed to create a deterministic RNG.
    - Emits a small timeline CSV `.artifacts/{run_id}/timeline.csv`.
    - Registers the artifact via store_artifact (which writes to disk).
    - Returns a completed RunResultHandle with timestamps.
    """
    rng = random.Random(int(manifest.seed))
    run_dir = os.path.join(".artifacts", manifest.run_id)
    os.makedirs(run_dir, exist_ok=True)

    timeline_path = os.path.join(run_dir, "timeline.csv")
    # Produce 3 deterministic events as a tiny timeline
    events = []
    baseline = manifest.created_at
    for i in range(3):
        ts = (baseline).isoformat()
        job_id = f"job-{i+1}"
        action = rng.choice(["queued", "started", "finished"])
        events.append({"timestamp": ts, "event": action, "job_id": job_id, "action": action})

    # Write CSV
    with open(timeline_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["timestamp", "event", "job_id", "action"])
        writer.writeheader()
        for ev in events:
            writer.writerow(ev)

    # Register artifact by storing the file bytes (store_artifact persists to .artifacts)
    try:
        with open(timeline_path, "rb") as fh:
            payload = fh.read()
        store_artifact(manifest.run_id, "timeline.csv", payload, "text/csv")
    except Exception:
        # best-effort: continue even if registration fails
        pass

    handle = RunResultHandle(
        run_id=manifest.run_id,
        status="completed",
        started_at=manifest.created_at,
        finished_at=datetime.utcnow(),
    )
    return handle


def collect_artifacts(handle: RunResultHandle) -> ArtifactIndex:
    """
    Collect artifacts produced by a completed run.

    Phase 2 behavior:
    - Scan .artifacts/{run_id}/ and return a list of artifact entries with name and path.
    """
    run_dir = os.path.join(".artifacts", handle.run_id)
    artifacts: List[Dict[str, Any]] = []
    if os.path.isdir(run_dir):
        for fname in sorted(os.listdir(run_dir)):
            path = os.path.join(run_dir, fname)
            artifacts.append({"name": fname, "path": path})
    return ArtifactIndex(run_id=handle.run_id, artifacts=artifacts)


def store_artifact(
    run_id: str, kind: str, payload: bytes, media_type: str
) -> ArtifactHandle:
    """
    Persist artifact bytes to disk under .artifacts/{run_id}/.

    - `kind` is used as filename (e.g. "timeline.csv"). If kind contains path separators,
      they are sanitized by taking basename.
    - Returns a file:// handle and the filesystem path as url for local development.
    """
    run_dir = os.path.join(".artifacts", run_id)
    os.makedirs(run_dir, exist_ok=True)
    filename = os.path.basename(str(kind))
    path = os.path.join(run_dir, filename)
    with open(path, "wb") as fh:
        fh.write(payload)
    handle = f"file://{os.path.abspath(path)}"
    url = path
    return ArtifactHandle(handle=handle, url=url)


def load_artifact(handle: str) -> bytes:
    """
    Load artifact bytes from a file:// handle or a filesystem path.
    """
    if handle.startswith("file://"):
        path = handle[len("file://") :]
    else:
        path = handle
    with open(path, "rb") as fh:
        return fh.read()


def generate_scenarios(
    base: Dict[str, Any], sweeps: Dict[str, List[Any]]
) -> List[Dict[str, Any]]:
    """
    Generate scenario configurations from base and parameter sweeps.

    Phase 0 behaviour:
    - Produce a cartesian product of sweep parameter values.
    - Return a list of scenario dicts that merge `base` with each combination.
    - Keep ordering deterministic by sorting sweep keys.
    """
    if not sweeps:
        return [dict(base)]

    keys = sorted(sweeps.keys())
    value_lists = [list(sweeps[k]) for k in keys]
    results: List[Dict[str, Any]] = []

    for combo in itertools.product(*value_lists):
        cfg = dict(base)
        for k, v in zip(keys, combo):
            cfg[k] = v
        results.append(cfg)

    return results


def execute_experiments(
    configs: List[Dict[str, Any]], seed_base: int, parallelism: int
) -> str:
    """
    Execute a batch of experiment scenarios.

    Phase 0 behaviour (minimal, deterministic):
    - Create a lightweight batch id.
    - For each scenario config, create a RunManifest (with unique seed derived
      from seed_base + index) and call run_simulation to enqueue a run.
    - Persist a small batch index file under ./.experiments/{batch_id}.json so
      tools can inspect created run_ids during local development.
    - Return the batch id string.
    """
    batch_id = f"batch-{str(uuid4())}"
    os.makedirs(".experiments", exist_ok=True)
    batch_entries: List[Dict[str, Any]] = []

    for idx, cfg in enumerate(configs):
        seed = int(seed_base) + idx
        manifest = create_run_manifest(project_id=cfg.get("project_id", "unknown"), scenario=cfg, seed=seed)
        handle = run_simulation(manifest)
        entry = {
            "index": idx,
            "run_id": handle.run_id,
            "project_id": manifest.project_id,
            "seed": seed,
            "status": handle.status,
            "scenario": manifest.scenario,
        }
        batch_entries.append(entry)

    batch_path = os.path.join(".experiments", f"{batch_id}.json")
    with open(batch_path, "w", encoding="utf-8") as fh:
        json.dump({"batch_id": batch_id, "runs": batch_entries}, fh, indent=2, default=str)

    return batch_id


def get_experiment_batch(batch_id: str) -> Dict[str, Any]:
    """Return a minimal ExperimentBatchView for the given batch id."""
    return {"batch_id": batch_id, "status": "created", "results": []}


def validate_project_config(doc: Dict[str, Any]) -> ValidationReport:
    """
    Validate a project config doc against the canonical JSON Schema.

    - Loads schemas/project_config.schema.json from repo root (relative to package).
    - Uses Draft7Validator to collect schema errors and returns them as ValidationReport.
    - Errors are returned as human-readable strings including a JSON path.
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(doc, dict):
        errors.append("file:project_config.json,row:<n/a>,column:<n/a>,message:document must be a dict")
        return ValidationReport(valid=False, warnings=warnings, errors=errors)

    # Attempt to load the authoritative schema file
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas", "project_config.schema.json")
    try:
        with open(schema_path, "r", encoding="utf-8") as fh:
            schema = json.load(fh)
    except Exception as ex:
        errors.append(f"file:project_config.schema.json,row:<n/a>,column:<n/a>,message:schema load error: {ex}")
        return ValidationReport(valid=False, warnings=warnings, errors=errors)

    # Validate using Draft7Validator and collect detailed errors (with format checking)
    try:
        validator = Draft7Validator(schema, format_checker=FormatChecker())
        for ve in sorted(validator.iter_errors(doc), key=lambda e: e.path):
            # Build a readable path (dot-separated)
            path = ".".join([str(p) for p in ve.absolute_path]) or "<root>"
            msg = ve.message
            errors.append(f"file:project_config.json,row:<n/a>,column:{path},message:{msg}")
    except Exception as ex:
        errors.append(f"file:project_config.json,row:<n/a>,column:<n/a>,message:validation failure: {ex}")
        return ValidationReport(valid=False, warnings=warnings, errors=errors)

    # Post-schema integrity checks: timezones (IANA) and enums (dispatch/release) where present.
    try:
        tzs = set(available_timezones())
    except Exception:
        tzs = set()

    # Check plant timezone
    plant = doc.get("plant", {})
    p_tz = plant.get("timezone")
    if p_tz and tzs and p_tz not in tzs:
        errors.append(f"file:project_config.json,row:<n/a>,column:plant.timezone,message:unknown timezone '{p_tz}'")

    # Check calendars timezones
    for idx, cal in enumerate(doc.get("calendars", [])):
        tz = cal.get("timezone")
        row = idx + 2
        if tz and tzs and tz not in tzs:
            errors.append(f"file:calendars,row:{row},column:timezone,message:unknown timezone '{tz}'")

    # Find and validate enum-like fields in the document (simple recursive search)
    def _find_values(d, key):
        vals = []
        if isinstance(d, dict):
            for k, v in d.items():
                if k == key:
                    vals.append(v)
                else:
                    vals.extend(_find_values(v, key))
        elif isinstance(d, list):
            for item in d:
                vals.extend(_find_values(item, key))
        return vals

    allowed_dispatch = {"EDD", "SPT", "ATC", "ATCS", "LSN"}
    allowed_release = {"CONWIP", "POLCA"}

    for val in _find_values(doc, "dispatch_rule"):
        if val not in allowed_dispatch:
            errors.append(f"file:project_config.json,row:<n/a>,column:dispatch_rule,message:invalid dispatch rule '{val}'")
    for val in _find_values(doc, "release_policy"):
        if val not in allowed_release:
            errors.append(f"file:project_config.json,row:<n/a>,column:release_policy,message:invalid release policy '{val}'")

    valid = len(errors) == 0
    return ValidationReport(valid=valid, warnings=warnings, errors=errors)


def validate_csv_documents(documents: List[Dict[str, Any]]) -> ValidationReport:
    """
    Validate a set of parsed CSV documents.

    Additional KISS check:
    - Detect empty/missing header entries produced by malformed CSVs where a header
      column is blank (e.g., "product_id,,process_time_mean"). This is treated as
      a validation error on the header row (row 1).

    Each document is expected to be a dict:
      { "name": "<logical name>", "rows": [ {col: val, ...}, ... ] }

    Produces ValidationReport entries formatted as:
      "file:{name},row:{row_number},column:{column},message:{text}"

    Minimal checks implemented (KISS/YAGNI):
    - products: process_time_mean present and > 0
    - setup_matrix: setup_time present and >= 0
    - yields: yield_rate in (0,1]
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Quick scan for malformed header rows: if any document has rows and the
    # first row contains an empty-string key (CSV with an empty header), emit an error.
    for doc in documents:
        name = doc.get("name", "<unknown>")
        rows = doc.get("rows", [])
        if rows:
            first_row = rows[0]
            # csv.DictReader will use '' as key for empty header entries
            if any((k == "" or (isinstance(k, str) and k.strip() == "")) for k in first_row.keys()):
                errors.append(f"file:{name},row:1,column:<header>,message:empty or missing header column detected")
    # Continue with detailed per-row validation below.

    for doc in documents:
        name = doc.get("name", "<unknown>")
        rows = doc.get("rows", [])
        for idx, row in enumerate(rows):
            # CSV row numbers: header is row 1, so data starts at row 2
            row_number = idx + 2
            if "products" in name.lower():
                pt = row.get("process_time_mean")
                if pt is None or pt == "":
                    errors.append(f"file:{name},row:{row_number},column:process_time_mean,message:missing")
                else:
                    try:
                        if float(pt) <= 0.0:
                            errors.append(f"file:{name},row:{row_number},column:process_time_mean,message:must be > 0")
                    except Exception:
                        errors.append(f"file:{name},row:{row_number},column:process_time_mean,message:invalid number")
            if "setup_matrix" in name.lower():
                st = row.get("setup_time")
                if st is None or st == "":
                    errors.append(f"file:{name},row:{row_number},column:setup_time,message:missing")
                else:
                    try:
                        if float(st) < 0.0:
                            errors.append(f"file:{name},row:{row_number},column:setup_time,message:must be >= 0")
                    except Exception:
                        errors.append(f"file:{name},row:{row_number},column:setup_time,message:invalid number")
            if "yields" in name.lower():
                yr = row.get("yield_rate")
                if yr is None or yr == "":
                    errors.append(f"file:{name},row:{row_number},column:yield_rate,message:missing")
                else:
                    try:
                        v = float(yr)
                        if not (0.0 < v <= 1.0):
                            errors.append(f"file:{name},row:{row_number},column:yield_rate,message:must be (0,1]")
                    except Exception:
                        errors.append(f"file:{name},row:{row_number},column:yield_rate,message:invalid number")

    valid = len(errors) == 0
    return ValidationReport(valid=valid, warnings=warnings, errors=errors)


# referential integrity implemented below in the extended validator to avoid duplicate definitions


def map_csvs_to_project(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Naive mapper: accepts list of parsed CSV dicts with 'name' keys mapping them.
    Returns a ProjectConfig skeleton used by the runner.

    Notes:
    - Ensure `plant` is a dict (schema expects an object). If no plant document is
      provided, create a minimal default plant object to make schema validation
      and downstream checks robust for Phase-1.
    - Populate known arrays from CSV documents by logical name.
    """
    project: Dict[str, Any] = {
        "plant": {"plant_id": "toy-plant", "name": "toy-plant", "timezone": "UTC"},
        "products": [],
        "routings": [],
        "machines": [],
        "operators": [],
        "setup_matrix": [],
        "demand": [],
        "calendars": [],
        "mtbf_mttr": [],
        "yields": [],
        "skills": [],
        "jobs": [],
    }

    for d in documents:
        name = d.get("name", "").lower()
        rows = d.get("rows", []) or []
        if name == "products":
            project["products"] = rows
        elif name == "routings":
            project["routings"] = rows
        elif name == "machines":
            project["machines"] = rows
        elif name == "operators":
            project["operators"] = rows
        elif name == "setup_matrix":
            project["setup_matrix"] = rows
        elif name == "demand":
            project["demand"] = rows
        elif name == "calendars":
            project["calendars"] = rows
        elif name == "mtbf_mttr":
            project["mtbf_mttr"] = rows
        elif name == "yields":
            project["yields"] = rows
        elif name == "skills":
            project["skills"] = rows
        elif name == "jobs":
            project["jobs"] = rows
        elif name == "plant":
            # If a plant CSV is provided, expect a single row with plant_id,name,timezone
            if rows:
                first = rows[0]
                project["plant"] = {
                    "plant_id": first.get("plant_id", "toy-plant"),
                    "name": first.get("name", first.get("plant_id", "toy-plant")),
                    "timezone": first.get("timezone", first.get("tz", "UTC")),
                }

    return project
def validate_referential_integrity(documents: List[Dict[str, Any]]) -> ValidationReport:
    """
    Extended cross-file referential integrity checks.

    - Verifies routings.product_id exists in products
    - Verifies routings.machine_group_id exists in machines.machine_id OR skills.machine_group_id
    - Verifies skills.operator_id exists in operators

    Returns a ValidationReport with entries formatted as:
      file:{name},row:{row_number},column:{column},message:{text}
    This function intentionally replaces any earlier, simpler implementation by name.
    """
    errors: List[str] = []
    warnings: List[str] = []

    products = set()
    operators = set()
    machines = set()
    skill_machine_groups = set()

    # Collect reference sets
    for doc in documents:
        name = doc.get("name", "").lower()
        rows = doc.get("rows", [])
        if name == "products":
            for row in rows:
                pid = row.get("product_id")
                if pid:
                    products.add(str(pid))
        if name == "operators":
            for row in rows:
                oid = row.get("operator_id")
                if oid:
                    operators.add(str(oid))
        if name == "machines":
            for row in rows:
                mid = row.get("machine_id")
                if mid:
                    machines.add(str(mid))
        if name == "skills":
            for row in rows:
                mg = row.get("machine_group_id")
                if mg:
                    skill_machine_groups.add(str(mg))

    # Validate routings.product_id and routings.machine_group_id
    for doc in documents:
        if doc.get("name", "").lower() == "routings":
            for idx, row in enumerate(doc.get("rows", [])):
                rownum = idx + 2
                pid = row.get("product_id")
                # Only enforce product_id referential integrity if products list was provided.
                if products and pid and str(pid) not in products:
                    errors.append(f"file:routings,row:{rownum},column:product_id,message:unknown product_id '{pid}'")
                # Check top-level machine_group_id on routing row (some CSVs may include it)
                mg = row.get("machine_group_id")
                if mg:
                    mg_str = str(mg)
                    if (mg_str not in machines) and (mg_str not in skill_machine_groups):
                        errors.append(
                            f"file:routings,row:{rownum},column:machine_group_id,message:unknown machine_group_id '{mg}'"
                        )
                # Also check nested steps for machine_group_id fields
                steps = row.get("steps") or row.get("Steps") or []
                if isinstance(steps, list):
                    for sidx, step in enumerate(steps):
                        # step may be a dict or a JSON string in CSV; attempt to handle both
                        step_obj = step
                        if isinstance(step, str):
                            try:
                                step_obj = json.loads(step)
                            except Exception:
                                step_obj = {}
                        mg2 = step_obj.get("machine_group_id")
                        if mg2:
                            mg2s = str(mg2)
                            if (mg2s not in machines) and (mg2s not in skill_machine_groups):
                                errors.append(
                                    f"file:routings,row:{rownum},column:steps[{sidx}].machine_group_id,message:unknown machine_group_id '{mg2}'"
                                )

    # Validate skills.operator_id -> operators
    for doc in documents:
        if doc.get("name", "").lower() == "skills":
            for idx, row in enumerate(doc.get("rows", [])):
                rownum = idx + 2
                oid = row.get("operator_id")
                # Only enforce operator referential integrity if operators list exists
                if operators and oid and str(oid) not in operators:
                    errors.append(f"file:skills,row:{rownum},column:operator_id,message:unknown operator_id '{oid}'")

    valid = len(errors) == 0
    return ValidationReport(valid=valid, warnings=warnings, errors=errors)