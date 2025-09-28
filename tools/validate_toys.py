# [`tools/validate_toys.py`](tools/validate_toys.py:1)
"""
Lightweight validation runner for toy CSVs and project mapping.

- Loads CSVs from examples/toy and examples/toy/negative (if present).
- Runs engine.run.validate_csv_documents and engine.run.validate_project_config.
- Emits .artifacts/validation/validation_report.json containing CSV + schema validation results.
"""
from __future__ import annotations

import os
import sys
import csv
import json
from typing import List, Dict

# Ensure repo root is on path so 'engine' package imports work when run as script.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from datetime import datetime  # noqa: E402
from engine.run import (  # noqa: E402
    validate_csv_documents,
    map_csvs_to_project,
    validate_project_config,
    validate_referential_integrity,
)


def load_csv_documents(path: str = "examples/toy") -> List[Dict]:
    docs: List[Dict] = []
    neg_dir = os.path.join(path, "negative")
    if not os.path.isdir(path):
        return docs
    for fname in sorted(os.listdir(path)):
        fpath = os.path.join(path, fname)
        if os.path.isdir(fpath):
            continue
        if not fname.lower().endswith(".csv"):
            continue
        name = os.path.splitext(fname)[0]
        with open(fpath, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = [dict(r) for r in reader]
        docs.append({"name": name, "rows": rows})
    # include negative folder CSVs if present
    if os.path.isdir(neg_dir):
        for fname in sorted(os.listdir(neg_dir)):
            if not fname.lower().endswith(".csv"):
                continue
            fpath = os.path.join(neg_dir, fname)
            name = "negative_" + os.path.splitext(fname)[0]
            with open(fpath, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                rows = [dict(r) for r in reader]
            docs.append({"name": name, "rows": rows})
    return docs


def run() -> None:
    documents = load_csv_documents()
    csv_report = validate_csv_documents(documents)
    project = map_csvs_to_project(documents)
    schema_report = validate_project_config(project)
    referential_report = validate_referential_integrity(documents)

    # Aggregate reports, include structured sections for downstream tools
    # Helper to parse issue string into dict (mirrors engine/run._parse_issue_string)
    def _parse_issue_string(s: str) -> Dict[str, Optional[str]]:
        parts = {"file": None, "row": None, "column": None, "message": None}
        try:
            for part in s.split(","):
                if ":" in part:
                    k, v = part.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if k in parts:
                        parts[k] = v
        except Exception:
            parts["message"] = s
        return parts

    def _structured(report_section: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "valid": report_section.get("valid"),
            "warnings": report_section.get("warnings", []),
            "errors": report_section.get("errors", []),
            "structured_warnings": [_parse_issue_string(w) for w in report_section.get("warnings", [])],
            "structured_errors": [_parse_issue_string(e) for e in report_section.get("errors", [])],
        }

    report = {
        "csv_validation": _structured({"valid": csv_report.valid, "warnings": csv_report.warnings, "errors": csv_report.errors}),
        "schema_validation": _structured({"valid": schema_report.valid, "warnings": schema_report.warnings, "errors": schema_report.errors}),
        "referential_validation": _structured({"valid": referential_report.valid, "warnings": referential_report.warnings, "errors": referential_report.errors}),
        "generated_at": datetime.utcnow().isoformat(),
    }

    artdir = os.path.join(".artifacts", "validation")
    os.makedirs(artdir, exist_ok=True)
    path = os.path.join(artdir, "validation_report.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("Wrote validation report to", path)


if __name__ == "__main__":
    run()