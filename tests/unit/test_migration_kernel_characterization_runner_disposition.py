"""Keep the historical kernel-characterization runner disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/kernel_characterization/runner.py"
SOURCE_BLOB = "ee911bbf77e8620281cd140a439ecef760afc5ff"


def test_historical_kernel_runner_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "37213"
    assert row["top_level_python_symbols"] == (
        "_git_sha;_graph;_feature_scale;_probe_target;_run_seed;_run_physics_seed;"
        "_summary_frontier;_grouped;run_k1;run_k1_b;run_k2;run_k3;"
        "_run_structural_seed;run_k4_k5;run_k6;run_k7;run_k8;run_k9;run_k10;"
        "run_k11;run_k12;write_run"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical kernel-characterization")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "study outputs and evidence remain preserved" in rationale
    assert "no scientific-validity" in rationale
    assert not (ROOT / "src/lab/kernel_characterization/runner.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 48, "REWRITE": 3, "DROP": 945, "DEFER": 168}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 48 |" in migration
    assert "`DROP` | 945 |" in migration
    assert "### Historical kernel-characterization study runner (Lab #213)" in migration
