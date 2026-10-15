"""Keep the historical Pareto helper disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/kernel_characterization/pareto.py"
SOURCE_BLOB = "e1dd23edf35487cf59df5642a549742387f80421"


def test_historical_kernel_pareto_helper_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "1365"
    assert row["top_level_python_symbols"] == "_numeric;pareto_frontier"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical Pareto-frontier helper; no current TARGET consumer"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "not a claim" in rationale
    assert "future Lab analysis is unnecessary" in rationale
    assert not (ROOT / "src/lab/kernel_characterization/pareto.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 73, "REWRITE": 3, "DROP": 927, "DEFER": 161}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 73 |" in migration
    assert "`DROP` | 927 |" in migration
    assert "### Historical kernel-characterization Pareto helper" in migration
