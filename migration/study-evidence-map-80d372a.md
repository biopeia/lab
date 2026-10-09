# Lab study evidence map (source-pinned)

This map is a migration-navigation aid for Lab's historical study/protocol surface. It is **not** a scientific assessment, protocol catalogue, evidence-admission record, migration authorization, or disposition decision. It makes no method-preservation or equivalence claims.

## Scope and pin

All source relationships are derived from `alessbarb/symbiont-lab` at commit `80d372a186513035f85a769db886e505cabba52d`. The historical repository is read-only. Source paths and Git blob IDs in the TSV refer to that exact commit; artifact byte hashes and custody classifications are copied from Lab's pinned custody ledger. The Biopeia Lab inventory tables used as inputs are:

- [`study-protocol-crosswalk-80d372a.tsv`](study-protocol-crosswalk-80d372a.tsv)
- [`study-protocol-test-links-80d372a.tsv`](study-protocol-test-links-80d372a.tsv)
- [`scientific-custody-80d372a.tsv`](scientific-custody-80d372a.tsv)
- [`source-inventory-80d372a.tsv`](source-inventory-80d372a.tsv)

The work is tracked by [Lab issue #21](https://github.com/biopeia/lab/issues/21). The TSV contains 125 rows: 76 registered protocol IDs and 49 unregistered entrypoint-candidate modules. A row is an evidence pointer, not a unit-level scientific disposition.

## What the links mean

The table distinguishes these evidence classes:

- **Pinned source identity:** registry, implementation, test, specification and artifact paths have source blob IDs or, for custody artifacts, source blob and content SHA-256. These identify exact bytes at the pin; they do not establish scientific meaning.
- **Static test link:** registered-protocol test links are inherited from the AST crosswalk: a test symbol calls the registered implementation symbol and/or invokes `get_protocol` with that literal registry ID. For unregistered candidates, the scan records only a test function that imports a named top-level `run_*` or `*_study` symbol from that exact module and calls it directly. Dynamic/reflection, CLI, indirect helper and runtime links may be missed. A call is not scientific validation.
- **Heuristic path candidate:** specification/document/artifact candidates are selected from normalized protocol or module-name path segments. A path match is not proof that the file belongs to that protocol or capability. Candidate paths are deliberately retained as candidates.
- **Absent by bounded search:** the recorded search found no matching path or static call under its stated rules. This is not proof of absence.
- **Not validated from content:** the map does not assert that a registry protocol ID is a scientific study ID or a run ID. It does not parse candidate manifests to establish study/run relations. Run identity and protocol-to-artifact linkage therefore remain unresolved unless separately reviewed and recorded.

Candidate custody references include the existing ledger's source path, blob, content hash, classification, and linkage text. They preserve the ledger as recorded; they do not promote a `DEFER` item, admit evidence, or certify a protocol/run relationship. In particular, the custody ledger has 477 rows: 470 `DEFER`, 3 `HISTORICAL_RECORD`, 3 `SCIENTIFIC_EVIDENCE`, and 1 `PROTOCOL`; the seven non-DEFER entries are adjacent items under `lab/research/audits/historical/v024/`, and the ledger does not assert a unique `run_id` for them.

## Coverage at this pin

| Evidence unit | Count | Interpretation / limit |
| --- | ---: | --- |
| Distinct registered `protocol_id` values | 76 | The registry inventory only; not a count of all historical study capabilities. |
| Registered implementation modules / module-symbol pairs | 59 / 76 | Every registered symbol is recorded as defined at the pin; two registry callables resolve through lazy wrapper imports. |
| Registered IDs with specification path candidates | 75 / 76 | 96 unique candidate paths; associations remain heuristic. |
| Registered IDs with protocol-document path candidates | 75 / 76 | 101 unique candidate Markdown/text paths; path matches are not protocol validation. |
| Registered IDs with artifact/custody path candidates | 75 / 76 | 151 unique source paths, each joining exactly by path to a ledger row; the protocol/run relation remains unvalidated. |
| Registered IDs with direct implementation-call test links | 42 / 76 | 27 direct-call-only and 15 direct call plus registry-ID lookup. |
| Registered IDs with registry-ID lookup only | 10 / 76 | The test queries the ID; it does not call that protocol's implementation. |
| Registered IDs without a direct static test link | 24 / 76 | No link under the bounded AST patterns; indirect/dynamic tests may exist. |
| Non-`__init__.py` Python files under `lab/src/lab/studies/` | 121 | File count; includes shared helpers and other non-study modules. |
| Unregistered files with top-level `run_*` or `*_study` names | 49 / 62 | Candidate modules, not 49 confirmed independent studies; functions may be stage helpers, CLI wrappers or other entry points. Thirteen other unregistered files may still contain relevant capabilities under different naming. |
| Candidate unregistered modules with direct imported-symbol test calls | 41 / 49 | Static calls only; no semantic validation implied. |
| Candidate unregistered modules with name-based experiment spec candidates | 6 / 49 | Heuristic only. |
| Candidate unregistered modules with name-based artifact/custody candidates | 11 / 49 | Heuristic only. |

The 76 registry entries do not resolve the separately reported historical count of 129 studies/capabilities. The 49 unregistered candidates are a discovery queue, not a replacement count. The remaining 13 unregistered source files and code outside `lab/studies/` are not ruled out as study-related.

## Reproduction and limitations

Reproduce the registered rows by joining the source-pinned registry crosswalk, source-pinned test-link table, source inventory, and custody ledger on exact protocol ID/path. Candidate spec and artifact path associations inherit the bounded path-matching rules in `study-protocol-crosswalk-80d372a.md`. The unregistered scan enumerates Python modules under `lab/src/lab/studies/`, excludes registered implementation modules and `__init__.py`, then retains modules with top-level `run_*` or `*_study` function names. It links tests only for direct imported-symbol calls found by AST at the same pin. Candidate paths use normalized module basename matches against `lab/experiments/` and `lab/research/`.

No method or study dispositions are assigned here. Do not use this map alone to choose `REIMPLEMENT_METHOD`, `HISTORICAL_PROTOCOL`, `DROP_IMPLEMENTATION`, or `DEFER`; to claim scientific equivalence; to transfer/admit/delete artifacts; or to identify a run. Those require their separate scientific, custody and owner review. The map intentionally does not classify candidate implementations, inspect study content for scientific meaning, parse every run manifest, or adjudicate the “129” count.
