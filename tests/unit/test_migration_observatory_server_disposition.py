"""Keep the historical Observatory HTTP server out of TARGET migration."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
PATH = "lab/src/lab/observatory/server.py"
BLOB = "4f656e71647dfa05a10eb9e017f573d1fc5506cf"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"


def test_historical_observatory_server_is_dropped_as_target() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "10054"
    assert row["top_level_python_symbols"] == "_valid_instance_id;_Handler;ObservatoryServer;main"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET server/application implementation destination"
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and "34686bbad323801893321c95cdd00f3168db1c010bde2104ab996cc6c9865058" in rationale
    assert "loopback-only read-only HTTP/SSE server" in rationale
    assert "no target Observatory/server/application consumer" in rationale
    assert "future Lab presentation/transport" in rationale
    assert "claim scientific validity/equivalence/admission" in rationale

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 13, "REWRITE": 3, "DROP": 950, "DEFER": 198}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory server (Lab #271)" in migration
    assert BLOB in migration and "34686bbad323801893321c95cdd00f3168db1c010bde2104ab996cc6c9865058" in migration
    assert "| `SPLIT` | 13 |" in migration and "| `DROP` | 950 |" in migration
