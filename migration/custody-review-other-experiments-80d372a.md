# Proposed custody review: remaining experiment artifacts

## Scope and status

This is a content-level, scope-specific proposal for the 38 files under the following pinned source subtrees:

- `lab/experiments/attention/`
- `lab/experiments/autonomous-life/`
- `lab/experiments/continuity/`
- `lab/experiments/ecology/`
- `lab/experiments/equivalence/`
- `lab/experiments/evidence/`
- `lab/experiments/genetics/`
- `lab/experiments/heritage/`
- `lab/experiments/integration/`
- `lab/experiments/observability/`
- `lab/experiments/world/`

Source: `alessbarb/symbiont-lab` at `80d372a186513035f85a769db886e505cabba52d`.

The proposal is deliberately separate from `scientific-custody-80d372a.tsv`. The canonical ledger remains unchanged: all 38 corresponding entries remain `DEFER`. Every proposed class below requires independent review and is explicitly **not admitted** as evidence. This is a custody classification proposal only; it does not assert validity, reproducibility, scientific equivalence, migration, publication, transfer, or deletion.

## Proposed classes

| Proposed review class | Count |
|---|---:|
| `WORKING_ARTIFACT` | 17 |
| `PROTOCOL` | 10 |
| `HISTORICAL_RECORD` | 8 |
| `SCIENTIFIC_EVIDENCE` | 2 |
| `DEFER` | 1 |
| **Total** | **38** |

The TSV is the element-level mapping and records each exact source path, source commit/blob, byte size, SHA-256, proposal, source/run/config references when present, custodial responsibility, and specific limitation/rationale.

## Important distinctions and limitations

- Generic directory-scaffolding READMEs are proposed as `WORKING_ARTIFACT`; the designation reflects their content, not their filename. Their linked study directories are classified separately.
- The reversible-selection TOML mixes protocol/design material with embedded result content. Because the artifact cannot be cleanly classified as a whole, it remains `DEFER`; its separate results file is only proposed as `SCIENTIFIC_EVIDENCE` pending independent review. The proposal notes missing run/software provenance and makes no validity claim.
- The two proposed `SCIENTIFIC_EVIDENCE` entries are candidate evidence records only. They are not admitted: classification does not establish scientific validity, successful replication, or equivalence.
- Genesis-v1 outputs, including the retired/non-replicated W03 material, remain proposed `HISTORICAL_RECORD`; they are not promoted as scientific evidence and must not be regenerated as a migration shortcut.
- `PROTOCOL` identifies a document that specifies intended methods/conditions; it is not proof that a run occurred or that its result is valid.
- No source artifact is changed or removed. Uncertainty and missing provenance are recorded per entry in the TSV.

## Review boundary

Independent review must reconcile these proposals against the canonical custody ledger before any canonical reclassification. Lab retains scientific custody responsibility; that responsibility alone does not admit evidence or authorize artifact transfer. Preserve the pinned source unchanged while review is pending.
