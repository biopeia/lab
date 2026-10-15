"""The semantic capability model belongs to the Observation package."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/semantic.py"
SOURCE_BLOB = "125c906cd4a2d52d797f577172a33133534ef230"
SYMBOLS = (
    "T;_token;_text;AuthorityDomain;IdentityLinkState;ConditionDimension;ConditionOrigin;"
    "ActorRef;SemanticContractRef;SemanticFamily;IdentityRef;IdentityAssertion;IdentityLink;"
    "SubjectScope;DomainTimeRef;AcquisitionBasis;TransformationRef;LineageSourceRef;Lineage;"
    "ObservationCondition;OrchestrationContext;SemanticClaim;SemanticObservation"
)


def test_semantic_model_moves_as_capability_primitives_to_observation() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "12321"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "MOVE"
    assert row["target_owner"] == "Observation"
    assert row["target_path_or_status"] == "repos/observation/src/observation/semantic.py (capability primitives only)"
    rationale = row["rationale_and_caveat"]
    assert "same bounded capability model" in rationale
    assert "Lab evidence custody/admission is separate" in rationale
    assert "does not grant semantic authority" in rationale
    assert not (ROOT / "src/lab/observation/semantic.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 38, "REWRITE": 3, "DROP": 948, "DEFER": 175}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical semantic model disposition (Lab #243)" in migration
    assert "`MOVE` | 8 |" in migration
    assert "`SPLIT` | 38 |" in migration
