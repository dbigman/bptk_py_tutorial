# [`tests/test_validation_edgecases.py`](tests/test_validation_edgecases.py:1)
import os
import csv
import json
from typing import List, Dict
from engine.run import validate_csv_documents, map_csvs_to_project, validate_project_config, validate_referential_integrity


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


def test_missing_header(tmp_path):
    d = tmp_path / "toy"
    # write a CSV with missing header (empty header row) - simulate bad file
    path = d / "products.csv"
    os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(",,\nP1,FAM,2.0\n")
    docs = _load_docs_from_dir(str(d))
    report = validate_csv_documents(docs)
    # parser may treat missing headers as keys '', expect validation to mark missing process_time_mean
    assert report.valid is False


def test_extra_columns_and_nonstandard_delimiters(tmp_path):
    d = tmp_path / "toy"
    headers = ["product_id", "family_id", "process_time_mean", "extra_col"]
    rows = [
        {"product_id": "P1", "family_id": "FAM", "process_time_mean": "3.5", "extra_col": "X"},
    ]
    _write_csv(str(d / "products.csv"), rows, headers)
    docs = _load_docs_from_dir(str(d))
    report = validate_csv_documents(docs)
    # Extra columns should be ignored, valid should be True for this happy-path
    assert report.valid is True


def test_steps_as_json_string_and_nested_machine_group(tmp_path):
    d = tmp_path / "toy"
    # Machines and skills to populate reference sets
    _write_csv(str(d / "machines.csv"), [{"machine_id": "M1", "name": "m1", "cell_id": "C1", "capacity": "1"}],
               ["machine_id", "name", "cell_id", "capacity"])
    _write_csv(str(d / "skills.csv"), [{"operator_id": "O1", "machine_group_id": "MG1", "level": "1"}],
               ["operator_id", "machine_group_id", "level"])
    # Routings with steps as JSON string referencing machine_group_id and machine_id
    steps = json.dumps({"step_id": "S1", "machine_group_id": "MG1", "machine_id": "M1"})
    _write_csv(str(d / "routings.csv"), [{"routing_id": "R1", "product_id": "P1", "steps": steps}],
               ["routing_id", "product_id", "steps"])
    docs = _load_docs_from_dir(str(d))
    # referential integrity should pass because MG1 and M1 exist
    repo = validate_referential_integrity(docs)
    assert repo.valid is True


def test_invalid_numeric_fields_and_negative_case(tmp_path):
    d = tmp_path / "toy"
    # products with invalid numeric strings and a zero process_time_mean negative case
    _write_csv(
        str(d / "products.csv"),
        [
            {"product_id": "P_GOOD", "family_id": "FA", "process_time_mean": "2.5", "process_time_sigma": "0.1"},
            {"product_id": "P_BAD", "family_id": "FB", "process_time_mean": "0", "process_time_sigma": "0.0"},
            {"product_id": "P_STR", "family_id": "FC", "process_time_mean": "N/A", "process_time_sigma": "x"},
        ],
        ["product_id", "family_id", "process_time_mean", "process_time_sigma"],
    )
    docs = _load_docs_from_dir(str(d))
    csv_report = validate_csv_documents(docs)
    # Should detect the zero and invalid numeric as errors
    assert csv_report.valid is False
    assert any("process_time_mean" in e for e in csv_report.errors)
    # Map and run schema validation to ensure schema pipeline tolerates (map creates defaults)
    project = map_csvs_to_project(docs)
    schema_report = validate_project_config(project)
    assert isinstance(schema_report.valid, bool)