# Proposed custody review: Observatory replay fixture

## Scope and status

This one-row proposal covers `lab/examples/replays/symbiont-replay.json` at pinned source commit `80d372a186513035f85a769db886e505cabba52d`. Its exact source blob, byte count, and SHA-256 are in the accompanying TSV.

## Proposed class

`WORKING_ARTIFACT`, based on content and the adjacent Observatory README, which calls it a curated local-inspection example. It contains 20 schema-v1 display snapshots (ticks 1-20), but no study/protocol/run identity, timestamp, seed, checkpoint, execution receipt, source software revision, or environment. The CLI's ability to produce replay files does not prove this particular fixture's origin.

Independent Advisor review found no blocker to this proposed class. This is not scientific evidence, a validated historical record, evidence admission, migration authorization, or deletion authority. The pinned source remains unchanged. The canonical ledger's existing `custody_classification` remains authoritative pending Lab owner disposition; proposal fields are separate.
