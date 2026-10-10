# BAW-001 — EV-0356–EV-0361 and ADR Tension Reconciliation

**Record type:** Biopeia-side historical-source review and provenance record  
**Scope:** `biopeia/.github-private#9`  
**Prepared:** 2026-10-10  
**Biopeia Lab base:** `eba19ce6dcb06fc3004b2448e4a53401d8ff50dc` (`origin/main` when this record was prepared)  
**Disposition:** scoped reconciliation recorded; source evidence remains historical

## Purpose and custody boundary

This record reconciles the bounded claims and ADR tensions identified by BAW-001
against the exact sealed source dossier and its later corrections. It is a
review/provenance record, not new scientific evidence, an admission of evidence
to a Biopeia study, a rewrite of the source audit, or a new architecture
decision. It does not copy source evidence artifacts into Biopeia.

Biopeia Lab is custodian of this migration review record. The historical source
audit and its original evidence remain in the read-only source repository. Lab
custody here does not confer authority over Organism, Observation, or other
domain state, and does not admit any underlying scientific artifact.

## Exact source and integrity reference

| Field | Value |
| --- | --- |
| Source repository | `https://github.com/alessbarb/symbiont-lab` |
| Pinned audit base | `cef998a55aae32ed8b2f7373079c11667b01e915` |
| Supplied sealed dossier | Workspace-local `repos/docs/.local/symbiont-lab/.audit.zip` |
| Dossier SHA-256 | `ff258afcb1c80b9feefacc28575d1e5ccd5f15c062dd36499498747df4d57df2` |
| Primary records | `.audit/registers/evidence.md` (EV-0356–EV-0365); `.audit/registers/review_resolutions.md` (REV-0024) |
| Independent sampling report | `.audit/reviews/independent_sampling/ANTIGRAVITY_EV-0356-0361.md` |

The SHA-256 was calculated over the local ZIP and matches the adjacent
`BIOPEIA_ARCHITECTURE_V1_AUDIT_BASELINE.sha256` reference. This verifies the
local bytes against that recorded digest; it is not a digital signature or an
independent attestation of the archive's origin. The `REV-0024` cited here is
specifically the entry in `.audit/registers/review_resolutions.md`; it is not
the separate reviewer file whose title also contains `REV-0024`.

No files or registers in `symbiont-lab` were changed. Source wording and source
reviewer artifacts remain untouched.

## Evidence dispositions

These are dispositions of the bounded claims in the pinned source dossier.
They do not upgrade the claims into runtime observations or scientific
conclusions.

| Source claim | Biopeia-side disposition | Scope and limitation |
| --- | --- | --- |
| EV-0356 | `CONFIRMED_WITH_NARROWER_BOUND` — selected Physics3D step-loop composition and writers only | EV-0364 identifies additional conditional Organism model-configuration/adoption/promotion writers and checkpoint-triggered lifecycle effects. This is not a census of all Lab-origin writers. H-04 remains partial; no automatic AD-0018 defect is inferred. |
| EV-0357 | `CONFIRMED_WITH_NARROWER_BOUND` — bounded habitat mutable-state/writer placement | EV-0363 corrects that `SharedHabitat.renew()` has a test caller, not a located production caller, and that the social-habitat caller list was incomplete. The bounded placement conclusion remains; completeness is not claimed. |
| EV-0358 | `CONFIRMED_WITH_NARROWER_BOUND` — bounded tracked host-clock conclusion | `monotonic_timestamp_ns` is also copied in interoception (EV-0363). Copying alone does not establish causal use. Do not generalize beyond inspected routes. |
| EV-0359 | `CONFIRMED_WITH_NARROWER_BOUND` — bounded Environment-kernel usage claim | `PeriodicFieldLaw` is constructed, evaluated, and exported in Environment genesis (EV-0363). Broad non-use wording is narrowed; this does not change TARGET authority. |
| EV-0360 | `CONFIRMED_WITH_NARROWER_BOUND` / `PARTIAL INTEGRITY JOIN` | EV-0364 verifies the traced exported Physics3D ZIP contains manifest/runtime/model artifacts with per-artifact hashes. The inspected attach path did not close Organism registry `artifact_hash` against the loaded artifact. H-10 remains partial; absence of this join is not evidence of tampering, corruption, or a demonstrated defect. |
| EV-0361 | `NOT_REPRODUCED` for its broad “no contradiction / H-00 closed” conclusion | Preserve only as the original keyword/Decision-section screen. EV-0363 notes ADR-0072 has a `Proposal`, not a `Decision`, section, and the screen was not a full clause-by-clause review. It cannot establish broad H-00 closure. |

EV-0363, EV-0364, and EV-0365 are later source-dossier corrections and
cross-checks; they supplement rather than rewrite EV-0356–EV-0361 or the
immutable reviewer originals. H-00, H-04, and H-10 are not declared fully
closed by this record.

## ADR tension dispositions

| Tension | Reconciliation | What remains outside this record |
| --- | --- | --- |
| ADR-0067 × AD-0018 — revisioned Organism sections and passive Observation | Historical evidence identifies a bounded projection/export ambiguity, not a proven universal conflict or proof of field-level authorization. For Biopeia TARGET, the approved Observation architecture keeps semantic authority with the source domain and requires passive projections; this resolves the conceptual TARGET authority question for BAW-001. | It does not prove historical/source conformance, authorize every historical field, or establish a full H-00 closure. Historical path conformance remains migration/audit work. See [Observation architecture v1](https://github.com/biopeia/docs/blob/main/technical/design/observation/observation-architecture-biopeia-v1.md) and [Observation Semantic Model v1](https://github.com/biopeia/docs/blob/main/technical/design/observability/observation-semantic-model-v1.md). |
| ADR-0064 × AD-0020 — `DevelopmentalContext` and somatic capacity | Compatible when `DevelopmentalContext` means static body affordance/capacity, distinct from live somatic reserve. EV-0365 reports no tracked implementation/caller establishing a contrary live-reserve interpretation. No constitutional conflict or current implementation conformance is inferred. | Any future live somatic input still needs explicit owner, producer, and provenance; this record does not supply them. |
| ADR-0036 × AD-0020 — retained body schemas and competence | EV-0363 narrows this as compatible: historical body schemas may be retained as unverified hypotheses while body-bound competence/calibration is reacquired. No necessary conflict is established. | This does not demonstrate a runtime re-embodiment implementation or validate a scientific method. |
| Other same-family ADR clauses sampled by the dossier | Treat only the clause-level dispositions recorded in EV-0363–EV-0365 and the source review-resolution register as bounded compatible/already disposed; do not reopen them as new conflicts based on the earlier screen. | The sampled set is not a complete ADR-by-AD cross-product. Later source records continue to mark H-00 as partial. |

**Owner-decision result:** no additional Architecture Owner decision is required
to reconcile the specific EV-0356–EV-0361 claims and ADR tensions within BAW-001.
This statement is scoped to this issue; it is not a claim that every historical
ADR clause, source implementation, or H-00 question is resolved.

## Review and closure conditions

- Independent review is preserved in the source dossier as the Antigravity
  sampling report and `.audit/registers/review_resolutions.md#REV-0024`.
- A separate independent Advisor review of this Biopeia-side transcription
  found no blocking factual errors or omissions. It is not a constitutional
  approval or a GitHub review approval.
- The Architecture Owner's BAW-001 follow-up is recorded at
  <https://github.com/biopeia/.github-private/issues/9#issuecomment-6091293563>.
- Any separately required repository review remains distinct; the source
  review does not substitute for review of this transcription.
- BAW-001 may be marked resolved only after this record is merged and the issue
  and Project #1 status/link are updated. This PR alone does not close the
  issue.

## Explicit exclusions

This record does not:

- modify, copy, admit, publish, or delete source scientific evidence;
- amend `symbiont-lab` or its immutable audit records;
- claim a complete source writer census, complete integrity chain, full ADR
  cross-product, or closure of H-00/H-04/H-10;
- establish runtime behavior, experiment execution, scientific effect,
  tampering, corruption, or a CURRENT defect;
- reopen or change ratified Biopeia architecture, or authorize Pass 15/16B.
