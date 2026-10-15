"""Historical Lab Observatory runtime adapter is not a TARGET API/schema."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observatory/adapter.py"
SOURCE_BLOB = "9efdb6ac867699039fa2f3621190f7c4d5082fac"
SYMBOLS = (
    "SCHEMA_VERSION;BODY_SCHEMA_SNAPSHOT_VERSION;ENVELOPE_TYPE;_text;_enum_value;_quality;"
    "loss_class;_certainty;_discrete_class;_undeveloped_body_schema;_body_schema_state;"
    "_edge_deltas;_developmental_divergence;_cognition_state;_generative_cognition_state;"
    "_physiology_state;_metabolism_state;_development_state;_degradation_state;_attention_state;"
    "_social_state;_social_resource_state;_cultural_state;_communication_telemetry;_state;"
    "_sensory_phenotype_state;_embodiment_state;project_tick;project_topology;envelope;write_replay"
)


def test_historical_observatory_adapter_is_dropped_from_target_migration() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "69145"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner for historical composite adapter"
    assert row["target_path_or_status"] == "No TARGET adapter/envelope/replay path"
    assert "no consumer for this legacy snapshot envelope/replay API" in row["rationale_and_caveat"]
    assert "No claim of scientific validity" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/observatory/adapter.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 48, "REWRITE": 3, "DROP": 945, "DEFER": 168}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical Observatory runtime adapter disposition (Lab #250)" in migration
