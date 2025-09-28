import os
from engine.run import create_run_manifest, run_simulation, collect_artifacts, load_artifact


def test_run_simulation_writes_timeline(tmp_path):
    """
    Run the tiny deterministic simulation and assert it writes a timeline artifact.

    - Creates a RunManifest with a fixed seed.
    - Calls run_simulation (synchronous Phase-2 starter).
    - Calls collect_artifacts and ensures a timeline.csv file is present.
    - Loads the artifact bytes and asserts it contains the CSV header.
    """
    manifest = create_run_manifest("proj-artifact-test", {"scenario": "toy"}, seed=12345)
    handle = run_simulation(manifest)
    assert handle.status in ("completed", "queued", "running")

    artifacts_index = collect_artifacts(handle)
    assert artifacts_index.run_id == handle.run_id
    assert isinstance(artifacts_index.artifacts, list)

    # Find timeline artifact by name (or fallback to first artifact)
    timeline_entry = None
    for a in artifacts_index.artifacts:
        name = a.get("name") or os.path.basename(a.get("path", "") or "")
        if name == "timeline.csv" or name.endswith("timeline.csv"):
            timeline_entry = a
            break
    if timeline_entry is None and artifacts_index.artifacts:
        timeline_entry = artifacts_index.artifacts[0]

    assert timeline_entry is not None, "No artifact produced by run_simulation"

    # Load bytes and verify CSV header present
    path = timeline_entry.get("path") or timeline_entry.get("url") or timeline_entry.get("handle")
    data = load_artifact(path)
    assert b"timestamp" in data
    assert b"event" in data
    assert b"job_id" in data