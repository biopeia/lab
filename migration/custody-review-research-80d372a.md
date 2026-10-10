# Custody review: research artifacts

**Disposition:** Lab owner accepted all non-`DEFER` map classes as custody labels only; 15 row-specific exceptions remain `DEFER`. See [canonical reconciliation](custody-reconciliation-80d372a.md).

## Scope and status

This is a content-reviewed, path-level proposal for all 112 files under `lab/research/` at source commit `80d372a186513035f85a769db886e505cabba52d` in `alessbarb/symbiont-lab`.

The accompanying TSV gives one row per pinned source path, with its source blob, byte count, SHA-256, content-derived title/identity, proposed class, explicit linkage/producer/configuration information where present, custodial responsibility, and per-item rationale/limits. Missing linkage is stated rather than inferred. The source commit identifies the source snapshot; it is not automatically the software revision that produced any result.

This review map records the independently reviewed proposals. The Lab owner dispositions are recorded in the canonical ledger. These custody classifications do not authorize source changes, deletion, transfer, publication, TARGET code migration, evidence admission, scientific validation, replication, or preservation of a historical method. No candidate is promoted as truth merely because it is classified as `SCIENTIFIC_EVIDENCE`.

The canonical `migration/scientific-custody-80d372a.tsv` records the owner-accepted classes and the unresolved exceptions. No class is scientific admission or validation.

## Proposed classes

| Proposed review class | Count |
|---|---:|
| `SCIENTIFIC_EVIDENCE` | 18 |
| `PROTOCOL` | 5 |
| `HISTORICAL_RECORD` | 62 |
| `WORKING_ARTIFACT` | 12 |
| `DEFER` | 15 |
| **Total** | **112** |

These are proposed per-artifact custody classes, not scientific dispositions or validity grades. `PROTOCOL` records intended procedure, not execution. `HISTORICAL_RECORD` preserves prior audit, decision, execution or technical records. `WORKING_ARTIFACT` covers navigational/status/design material without demonstrated standalone evidentiary or protocol status. `DEFER` preserves mixed or insufficiently attributable artifacts without forcing a classification.

## Evidence and provenance limits

- Candidate evidence rows preserve the exact source bytes and identify study/run/seed/configuration only when the artifact states them. Unknown producers, absent run identifiers, missing raw inputs, and unavailable runtime/software provenance remain explicit limitations in the TSV.
- Execution receipts and manifests are not treated as scientific outcomes. Linked raw traces and result records remain distinct artifacts.
- A result, negative finding, or historical assertion is not thereby scientifically validated, admitted into a study, or reproducible.
- Mixed documents remain whole and are not split into newly authoritative records by this map.
- The three cognitive-cycle confirmatory execution manifests state run IDs, confirmatory experiment identity, confirmation scope, and seeds. Their paired result files instead state the baseline protocol identity and `exploratory` regime. The three result rows therefore remain `DEFER` pending owner reconciliation; the manifest/result mismatch is not resolved by filename or sibling inference.
- No source artifacts were changed. Preserve unclassified artifacts at the pinned source until an owner completes review.

## Review boundary

Independent Advisor review was completed for the scope and specifically reassessed the three v0.24 result JSONs. It recommended `SCIENTIFIC_EVIDENCE` as a custody class (not admission) because explicit seeds/configuration link them to the adjacent pinned protocol. No unique run_id is asserted; scripts, the referenced snapshot, dependency lock and per-run raw traces are unavailable. These rows' canonical custody class is `SCIENTIFIC_EVIDENCE`; they remain `NOT_ADMITTED` and `NOT_SCIENTIFICALLY_VALIDATED`. The separate cognitive-cycle manifest/result mismatch entries remain documented `DEFER` exceptions in the canonical ledger pending source-owner reconciliation.
