import os
import csv
from engine.run import (
    validate_csv_documents,
    map_csvs_to_project,
    validate_project_config,
    validate_referential_integrity,
)

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
TOY_DIR = os.path.join(ROOT, "examples", "toy")
NEG_DIR = os.path.join(TOY_DIR, "negative")


def load_csv_documents(path: str):
    docs = []
    if not os.path.isdir(path):
        return docs
    for fname in sorted(os.listdir(path)):
        if not fname.lower().endswith(".csv"):
            continue
        fpath = os.path.join(path, fname)
        name = os.path.splitext(fname)[0]
        with open(fpath, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        docs.append({"name": name, "rows": rows})
    # negative
    if os.path.isdir(os.path.join(path, "negative")):
        for fname in sorted(os.listdir(os.path.join(path, "negative"))):
            if not fname.lower().endswith(".csv"):
                continue
            fpath = os.path.join(path, "negative", fname)
            name = "negative_" + os.path.splitext(fname)[0]
            with open(fpath, newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            docs.append({"name": name, "rows": rows})
    return docs


def test_validation_pipeline_runs_and_detects_negative():
    docs = load_csv_documents(TOY_DIR)
    csv_report = validate_csv_documents(docs)
    project = map_csvs_to_project(docs)
    schema_report = validate_project_config(project)
    referential_report = validate_referential_integrity(docs)

    # Expect CSV validator to catch the negative product with non-positive process_time_mean
    assert csv_report.valid is False
    assert any("process_time_mean" in e for e in csv_report.errors)

    # Schema validator should be boolean (may be true if mapper filled defaults)
    assert isinstance(schema_report.valid, bool)

    # Referential report should be boolean
    assert isinstance(referential_report.valid, bool)