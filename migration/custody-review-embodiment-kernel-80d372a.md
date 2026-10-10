# Custody review: Embodiment, kernel characterization, and Physics3D

**Disposition:** Lab owner accepted all non-`DEFER` proposal classes as custody labels only, including the eight results as `SCIENTIFIC_EVIDENCE`; those results remain explicitly not admitted because execution provenance is incomplete. See [canonical reconciliation](custody-reconciliation-80d372a.md).

**Review status:** Independent review completed; Lab owner disposition is recorded in the canonical ledger.
**Source repository:** `alessbarb/symbiont-lab` (historical, read-only)
**Source commit:** `80d372a186513035f85a769db886e505cabba52d`
**Scope:** 92 source artifacts, mapped individually in [`custody-review-embodiment-kernel-80d372a.tsv`](custody-review-embodiment-kernel-80d372a.tsv).

This is a content-level custody classification proposal, not a scientific validation, evidence-admission decision, method-equivalence claim, code-migration decision, or authorization to copy, publish, regenerate, modify, or delete source artifacts. `WORKING_ARTIFACT` is not deletion authority. `DEFER` means preserve at source pending evidence/provenance review.

## Proposed counts

| Source subtree | Paths | PROTOCOL | SCIENTIFIC_EVIDENCE | HISTORICAL_RECORD | WORKING_ARTIFACT | DEFER |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lab/experiments/embodiment/**` | 64 | 19 | 25 | 11 | 1 | 8 |
| `lab/experiments/kernel-characterization/**` | 26 | 1 | 0 | 13 | 12 | 0 |
| `lab/experiments/physics3d/**` | 2 | 1 | 0 | 0 | 1 | 0 |
| **Total** | **92** | **21** | **25** | **24** | **14** | **8** |

Each TSV row contains the exact pinned source path, source commit, Git blob ID, byte length, independently recomputed SHA-256, artifact identity/version as visible, proposed class, protocol/run linkage, producer/source, applicable seed/configuration information, Lab custodial role, and item-specific rationale/limits. The TSV records the reviewed proposal. The canonical ledger records owner disposition; the `DEFER` items remain exceptions, not admission decisions.

## Basis by homogeneous group

### Embodiment

- **Protocol definitions and study-specific protocol descriptions (19):** the ten `experiment.toml` files plus their paired study README files, except the functional-transfer README. The TOML content identifies experiment/protocol IDs and versions; declared hypotheses, criteria, seeds, horizons, or conditions are recorded where present. The functional-transfer README is instead `HISTORICAL_RECORD` because its central content is the superseded-stage/runability history and explicit absence of confirmation runs. No method is ratified for Biopeia by this classification.
- **Governed E8 confirmation package and RFT r8 development output (25):** the 23 non-README files in `label-invariance-governed-20261001-0a901ea/` and the paired RFT `development-receipt.json` / `horizons.json`. The E8 manifest/report and per-seed receipts/results cross-link protocol `embodiment.label-invariance` v1, candidate `0a901ea273ac8cbcf8c165419e9120033f09c1f0`, the runner/protocol/aggregator hashes, run IDs, ten seeds, 300-step horizon and protocol-generated input. RFT r8 records the development run ID, protocol, commit, fingerprints, development seeds and selected horizons. The classifications are bounded custody proposals, not verification or acceptance of scientific findings. RFT is development-stage evidence only; its README explicitly says no confirmation seed was run.
- **Historical records (11):** the E8 package README, the functional-transfer README, and all nine items under `development-r5/`, `development-r6/`, and `development-r7/`. These preserve the versioned campaign context and superseded development/runability stages. Do not combine their outputs as if they were one current confirmation.
- **Working artifact (1):** the generic `lab/experiments/embodiment/README.md`, which describes folder-level organization rather than a study protocol or execution.
- **Ordinary result files (8):** `results.json` for `causal-revision-sequence`, `heredity-leakage-challenge`, `hidden-common-cause`, `label-invariance`, `somatic-correlation-trap`, `temporal-causality-challenge`, `tool-body-distinction`, and `yoked-external-causation`. The reviewed proposal map records `DEFER` because the files lack an executing source-code commit, runner/config content hashes, and a governed execution receipt. The Lab owner separately accepted `SCIENTIFIC_EVIDENCE` as a custody label only; this does not resolve those provenance gaps or admit/validate the results.

### Kernel characterization

- **Protocol (1):** `capacity/experiment.toml` declares K1-A/version 1, the abstract-synthetic arm, parameter sweep, seeds, and phases.
- **Historical records (13):** `FINAL-REPORT-2026-09-22.md` and the twelve dated K1–K12 reports. The reports explicitly bound their conclusions (including that the synthetic screens do not establish production cognitive capacity). The raw artifacts are referenced under `/tmp/symbiont-kernel-characterization/1c70371e/`, outside this source subtree; this proposal therefore does not classify those summaries as independently reviewable primary scientific evidence.
- **Working artifacts (12):** the root and eleven category README files are generic folder-scope guidance, not run payloads or study-specific protocols.

### Physics3D

- **Protocol (1):** `constitution-audit/README.md` specifies audit questions, apparatus command, conditions, output schema version 2, and measurement definitions. The audited two-file subtree contains no output/run record; no execution is inferred.
- **Working artifact (1):** the generic `physics3d/README.md`.

## Validation boundary

The TSV is a source-pinned mapping, not a transfer manifest. Source bytes remain untouched. The eight results are `SCIENTIFIC_EVIDENCE` as custody labels only. Their rows retain the candidate protocol identity, seeds/configuration, and explicit gaps: no executing source-code commit, runner/config hashes, or governed execution receipt. No unique run or producer is inferred; these artifacts remain `NOT_ADMITTED` and `NOT_SCIENTIFICALLY_VALIDATED`. The canonical ledger records this owner disposition.
