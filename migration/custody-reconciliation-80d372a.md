# Source-pinned custody proposal reconciliation

## Scope and decision boundary

Reconciles the five independently reviewed scoped maps plus the individually reviewed Observatory replay fixture against the Lab canonical ledger. All entries point to `alessbarb/symbiont-lab` at source commit `80d372a186513035f85a769db886e505cabba52d`. This is a custody-classification proposal, not scientific admission, scientific validation, evidence transfer, migration authorization, deletion, method-preservation approval, or TARGET applicability. Historical source bytes are unchanged.

The authoritative `custody_classification` field is preserved exactly. The reconciled candidate is stored in separate `proposed_review_class`, `proposal_source_map`, and `proposal_review_status` columns. Every proposal row remains `LAB_OWNER_DISPOSITION_PENDING; NOT_ADMITTED`; do not interpret it as a final owner decision.

## Reconciliation checks

- Canonical ledger: 477 rows.
- Scoped maps plus replay: 477 unique paths; exact set equality with the ledger.
- Every path was cross-checked for source commit, Git blob, byte count, and SHA-256; no identity mismatch.
- No duplicate path across maps.
- The only previously unmapped row was `lab/examples/replays/symbiont-replay.json`; its proposed `WORKING_ARTIFACT` class is content-based and independently reviewed.
- The three v0.24 result JSONs are linked to adjacent `PROTOCOL.md` and proposed as `SCIENTIFIC_EVIDENCE`; no unique `run_id`, per-run raw stream, independent reproduction, or scientific validity is asserted. The existing canonical class values for those rows already match that proposal.
- Unresolved cognitive-cycle manifest/result protocol-regime mismatches remain `DEFER`.

## Reconciled proposed custody classes

| Proposal class | Count |
| --- | ---: |
| `SCIENTIFIC_EVIDENCE` | 75 |
| `PROTOCOL` | 222 |
| `HISTORICAL_RECORD` | 95 |
| `WORKING_ARTIFACT` | 48 |
| `DEFER` | 37 |
| **Total** | **477** |

The current authoritative `custody_classification` counts remain unchanged: `DEFER` 470, `HISTORICAL_RECORD` 3, `PROTOCOL` 1, `SCIENTIFIC_EVIDENCE` 3. They will not be replaced without an explicit Lab owner disposition.

## Scope exclusions

This reconciles the 364 experiment artifacts, 112 research artifacts, and one replay artifact (477 total) only. It does not dispose the 129 study/capability implementations or the 76 source Lab test files; their separate ratified dispositions remain in force. `WORKING_ARTIFACT` is not deletion authority, and `DEFER` requires later review before migration completion.
