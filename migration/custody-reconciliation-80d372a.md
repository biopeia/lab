# Lab-owner custody disposition: source-pinned historical artifacts

## Authority and scope

This record applies the Biopeia Architecture Owner's ratified custody decision to the six independently reviewed path maps covering the 364 experiment artifacts, 112 research artifacts, and one replay (477 total), all pinned to `alessbarb/symbiont-lab` source commit `80d372a186513035f85a769db886e505cabba52d`.

The accepted labels describe **document custody only**:

- `SCIENTIFIC_EVIDENCE` does not mean scientifically validated, reproducible, admissible, or TARGET-applicable.
- `PROTOCOL` does not mean scientifically accepted or executed.
- `HISTORICAL_RECORD` is retained historical material.
- `WORKING_ARTIFACT` is not permission to delete.
- `DEFER` is an explicitly documented unresolved classification exception, preserved at source and not admitted.

No source artifact was modified, copied, deleted, or scientifically admitted by this disposition. `Biopeia Lab` is the TARGET custodian; `symbiont-lab` remains the read-only historical source. The canonical ledger retains exact source repository/path/commit/blob, byte count, SHA-256, identity, known linkage, producer, seed/configuration, custodian, and limitations.

## Verification and reconciliation

- Canonical ledger: 477 unique rows.
- Six reviewed maps: 477 unique paths; exact set equality with the canonical ledger.
- Every row's source commit, Git blob, byte count, and SHA-256 matched the pinned source.
- Existing item-specific independent reviews were checked alongside the source content and linked protocol/run materials where applicable.
- The owner accepted 448 proposed classifications where content, provenance limits, and review were coherent. The `proposal_review_status` field marks these as `LAB_OWNER_ACCEPTED_CUSTODY_CLASSIFICATION; NOT_SCIENTIFICALLY_VALIDATED; NOT_ADMITTED`.
- Twenty-nine rows remain `DEFER`; each canonical ledger row contains a specific conflict, content-boundary, or missing-provenance reason and a condition for reopening. These are preserved exceptions, not silently classified artifacts.

## Final canonical custody counts

| Custody class | Count |
| --- | ---: |
| `SCIENTIFIC_EVIDENCE` | 83 |
| `PROTOCOL` | 221 |
| `HISTORICAL_RECORD` | 95 |
| `WORKING_ARTIFACT` | 49 |
| `DEFER` (documented exception; not admitted) | 29 |
| **Total** | **477** |

## Specific boundaries

- The three v0.24 results (`baseline.json`, `causal.json`, `causal_validation.json`) are `SCIENTIFIC_EVIDENCE` **as a custody label only**. Their adjacent protocol, seeds, and configuration are linked; no unique `run_id`, scientific validity, independent reproduction, or admission is asserted.
- The eight Embodiment result JSONs are `SCIENTIFIC_EVIDENCE` as custody labels only. They include candidate protocol identity, schema/configuration material, seeds, timestamps, and outputs; the source commit/blob/content hash pins the preserved artifact. They do not identify an executing source-code commit, runner/config content hashes, or a governed execution receipt. No run ID or producer is inferred; they remain `NOT_ADMITTED` and `NOT_SCIENTIFICALLY_VALIDATED`, with no reproducibility or validity claim. An independent Advisor reviewed this owner override against the clarified custody/admission distinction.
- The Observatory replay is `WORKING_ARTIFACT`, based on its content and the adjacent README's local-inspection description. It is not a study result or evidence record; the producing execution is unknown. Its bytes remain preserved.
- Three cognitive-cycle results remain `DEFER` because each result declares a baseline/exploratory protocol regime while the paired execution manifest identifies a confirmatory experiment/confirmation scope. The owner/source must reconcile that mismatch; filenames and sibling records do not resolve it.
- Mixed protocol/result documents remain `DEFER` where assigning one class would erase a material boundary or require splitting an artifact without provenance-preserving evidence.

## Exclusions and retention

This disposition does not close the separate 129-study implementation disposition (`lab#45`) or authorize migration of the 76 source Lab test files (already `DROP` as TARGET tests). Unclassified source artifacts remain at the pinned historical source. No deletion is authorized. `DEFER` rows must be revisited before declaring the artifact inventory fully classified; they may be resolved only with the row-specific evidence identified in the ledger.
