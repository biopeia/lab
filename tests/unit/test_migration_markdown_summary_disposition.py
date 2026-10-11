"""Keep the bounded Markdown formatting helper disposition source-pinned."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/studies/common/summaries.py"
SOURCE_BLOB = "3ba4a1f396fd7888cb67651d069af01c55b01582"


def test_markdown_summary_helper_is_dropped_as_migration_input() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == SOURCE_PATH)

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "828"
    assert row["top_level_python_symbols"] == "format_markdown_table"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "no current Biopeia package or test consumer exists" in row[
        "rationale_and_caveat"
    ]
    assert "any future reporting need must justify a new TARGET implementation" in row[
        "rationale_and_caveat"
    ]
    assert "does not claim the formatter is generally useless" in row[
        "rationale_and_caveat"
    ]

    # Keep the inventory's source-code disposition and summary in sync.
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "summaries.py::format_markdown_table`: `DROP`" in migration
    compared_heads = (
        "ba0011797a6a3b4d48c7731651e50560c4043f18",
        "b5714f985d0aa970d3a412a7d29e43fa0bcb89d6",
        "caa885a11ec0170717bb4b71d271ab171807197e",
        "a4d04928a82fb0f53f6a1ca7e6362686d4c894d5",
        "79b779152d4bff2ab4191dc6601c8f1640e4cae3",
        "6aac3c76684834722440f53c9d8604ac4c16b138",
        "f5dc75d6a94b13b9c650f64d0f94e33e6db2e425",
    )
    assert all(head in migration for head in compared_heads)

    # The current target has no implementation or test consumer for this helper.
    symbol = "format_" + "markdown_table"
    for tree_name in ("src", "tests"):
        for path in (ROOT / tree_name).rglob("*.py"):
            if path == Path(__file__):
                continue
            assert symbol not in path.read_text(encoding="utf-8"), path
