"""Keep the historical Observatory server-test disposition auditable."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_server.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "997a603fc37dbb931790928016390972e2fcf8de"
SHA256 = "56cd25bd981f701c2d7b395eb139f9923fc9d40d9c153e79199b7676110e73b8"


def test_historical_server_tests_are_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "5376"
    assert row["top_level_python_symbols"] == "OUTSIDE_STATIC_ROOT;ServerTests"
    assert row["disposition"] == "DEFER"
    assert "Lab #289 coordinator" in row["target_owner"]
    assert row["target_path_or_status"] == (
        "No TARGET server, SSE endpoint, or stream/replay test contract/path authorized"
    )
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale and SHA256 in rationale
    assert "seven test methods" in rationale
    assert "do not split into authorized target test paths" in rationale
    assert all(issue in rationale for issue in ("#271", "#278", "#256", "#260/#266", "#38"))
    assert "Closure trigger:" in rationale
    assert "does not block bounded runtime transfer" in rationale
    assert "no scientific validity" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 30, "REWRITE": 3, "DROP": 949, "DEFER": 182}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory server-test disposition (Lab #289)" in migration
    assert BLOB in migration and SHA256 in migration
    assert "`SPLIT` | 30 |" in migration
    assert "`DEFER` | 182 |" in migration
