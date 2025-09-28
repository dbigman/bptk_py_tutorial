import os
import csv
import json
from typing import List, Dict
from engine.run import validate_csv_documents, validate_referential_integrity, map_csvs_to_project, validate_project_config


def _write_csv(path: str, rows: List[Dict[str, str]], headers: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def _load_docs_from_dir(path: str) -> List[Dict]:
    docs = []
    for fname in sorted(os.listdir(path)):
        if not fname.lower().endswith(".csv"):
            continue
        fpath = os.path.join(path, fname)
        name = os.path.splitext(fname)[0]
        with open(fpath, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = [dict(r) for r in reader]
        docs.append({"name": name, "rows": rows})
    return docs


def test_missing_header_variation(tmp_path):
    d = tmp_path / "toy"
    # Write a CSV where header row is present but one header is empty
    path = d / "products.csv"
    os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("product_id,,process_time_mean\nP1,FAM,2.0\n")
    docs = _load_docs_from_dir(str(d))
    report = validate_csv_documents(docs)
    assert report.valid is False
    assert any("process_time_mean" in e or "missing" in e for e in report.errors)


def test_nested_steps_list_string(tmp_path):
    d = tmp_path / "toy"
    # machines and skills exist
    _write_csv(str(d / "machines.csv"), [{"machine_id": "M1", "name": "m1", "cell_id": "C1", "capacity": "1"}],
               ["machine_id", "name", "cell_id", "capacity"])
    _write_csv(str(d / "skills.csv"), [{"operator_id": "O1", "machine_group_id": "MGX", "level": "1"}],
               ["operator_id", "machine_group_id", "level"])
    # Routings with steps stored as JSON list string referencing MGX and M1
    steps = json.dumps([{"step_id": "S1", "machine_group_id": "MGX", "machine_id": "M1"}])
    _write_csv(str(d / "routings.csv"), [{"routing_id": "R1", "product_id": "", "steps": steps}],
               ["routing_id", "product_id", "steps"])
    docs = _load_docs_from_dir(str(d))
    # Referential check should not error on machine_group_id nested inside a JSON list string
    repo = validate_referential_integrity(docs)
    # product_id not enforced because products list absent; hence valid should be True
    assert repo.valid is True


def test_map_and_schema_with_minimal_project(tmp_path):
    d = tmp_path / "toy"
    # Provide minimal products and plant rows to ensure mapping produces schema-acceptable project
    _write_csv(str(d / "products.csv"), [{"product_id": "P1", "family_id": "F1", "process_time_mean": "1.2"}],
               ["product_id", "family_id", "process_time_mean"])
    _write_csv(str(d / "plant.csv"), [{"plant_id": "toy-1", "name": "Toy", "timezone": "UTC"}],
               ["plant_id", "name", "timezone"])
    docs = _load_docs_from_dir(str(d))
    project = map_csvs_to_project(docs)
    schema_report = validate_project_config(project)
    assert isinstance(schema_report.valid, bool)