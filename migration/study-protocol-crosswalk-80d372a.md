# Historical study protocol crosswalk (source-pinned)

## Scope and source

This is a navigation aid for the Lab migration inventory, not a scientific
assessment, a TARGET protocol catalogue, or authorization to migrate code or
evidence. It is derived from the historical `lab/src/lab/experiments/registry.py`
at source repository `alessbarb/symbiont-lab`, commit
`80d372a186513035f85a769db886e505cabba52d`. The source remains read-only.

The TSV contains one row per registered `protocol_id` in that pinned registry.
Callable/module links are resolved statically from registry imports; for lazy
registry wrappers, the target module is taken from the wrapper-local import. Experiment spec/artifact paths are **candidates** found by exact protocol-ID
substring or by a normalized terminal-slug path segment that equals or starts
with that slug; prefix siblings (for example, parameterized variants) can be
included and are not asserted to belong to the protocol. Test paths are **candidates** found by
literal protocol ID or registry callable name. These searches can miss indirect
links and may include shared tests/artifacts; every association requires review
before being treated as a scientific relation. `NONE_FOUND...` is not proof
that no related material exists.

The supplemental
[`study-protocol-test-links-80d372a.tsv`](study-protocol-test-links-80d372a.tsv)
adds exact source-blob evidence for the registered implementation symbol and
statically demonstrable test-symbol links. It scans Python test ASTs at the
same pinned source commit and records a link only when a named test function
either calls the imported registered implementation callable or calls
`get_protocol` with that literal protocol ID. The table records **42** protocol
IDs with a direct implementation-call link, **10** with only a direct
registry-ID lookup, and **24** with `NO_DIRECT_TEST_LINK`; some direct-call
tests also perform registry lookup. A direct call proves only that the test
invokes that source callable, not that the test validates a scientific method
or that any result is admissible evidence. A registry-ID lookup proves only
that the test queries that key. `NO_DIRECT_TEST_LINK` means these explicit
static patterns did not establish a link; it does not prove no indirect or
dynamic association exists. Test and implementation blob IDs are from the
pinned source tree. Test-link evidence does not change scientific disposition;
the separately maintained study disposition register records approved unit-level
dispositions and limitations.

## Disposition

The 76 registered IDs are candidate units, not 76 proven independent studies.
The companion
[`study-disposition-register-80d372a.tsv`](study-disposition-register-80d372a.tsv)
records **39 manifest-level decisions**: 10 `HISTORICAL_PROTOCOL`, one `REIMPLEMENT_METHOD`, and 28 bounded `DEFER`. The register includes the owner-authorized, exact-manifest dispositions for Lab #154 (`learning.emergent-symbol-grounding`, historical protocol with archival result claims unverified/not admitted) and Lab #155 (`learning.episodic-memory-utility`, bounded DEFER). These decisions do not close their tracking Issues or authorize experiments. The TSV is the canonical itemized list; the following notes describe evidence and limitations for selected units. For #124, the registry-level candidate row still groups nine manifests; this manifest-specific alias records a bounded DEFER only for the HIST arm, with no run artifact or scientific-evidence admission, and leaves the other eight manifests unresolved. For #125, the pinned protocol directory contains the manifest and README only; the README specifies the chance-corrected E8 v3 arm but is not run evidence, and a bounded search of Lab main found no literal current consumer. The manifest-specific DEFER leaves TARGET applicability open and does not alter the other eight candidates. For #126, the exact factorized-effects manifest and README describe an E6 gate protocol for a synthetic four-actuator body; there is no run or physical-body result artifact in the pinned directory. A bounded current Lab source/test search found no literal consumer. This DEFER leaves TARGET applicability open and does not decide the other eight registry candidates. For #127, the pinned BH membership manifest and README specify an E6 gate rerun and 3/3-seed success criterion; the directory contains no run/result artifact. A bounded current Lab source/test search found no exact BH manifest consumer. The owner-authorized bounded DEFER leaves TARGET applicability open and does not decide the other eight registry candidates. For #128, the exact BHB block-replicated membership manifest is distinct from the BH manifest in #127. The owner-authorized bounded DEFER records no execution or result artifact and keeps TARGET applicability open. Its README and TOML identify an FP-3 E6 gate protocol, not outcomes; all claims remain migration-only. For #129, the exact FP-1 membership-M manifest is distinct from BH (#127) and BHB (#128). Its preregistered manifest/README specify 3,000 steps, seeds 101/127/149, and a 3/3 gate criterion, but the protocol directory has no run/result artifact. A bounded current `src/`/`tests/` search found no literal manifest or FP-1/M consumer; this does not resolve future TARGET applicability. The owner-authorized bounded DEFER is migration-only. For #130, the exact FP-1 membership-T/time-matched quiet-baseline manifest is distinct from membership-M (#129) and its other siblings. The pinned README/TOML describe an E6 3/3-seed gate with 3,000 steps and seeds 101/127/149, but the protocol directory contains no run/result artifact. A bounded current Lab source/test search found no exact-manifest or membership-T consumer. This owner-authorized DEFER applies only to #130 and leaves TARGET applicability open. For #133, the pinned protocol directory contains the manifest and README only; the README combines protocol design with reported gate-reachability diagnostics (5/10 and 7/10 openings) without a separate pinned diagnostic artifact or run identity. This bounded DEFER does not treat those figures as validated results or admit them as scientific evidence; the current Lab callable and direct-call tests do not themselves settle whether an authorized TARGET question requires this method. Its closure trigger is the Lab owner’s recorded TARGET consumer/question disposition and resolution of the README diagnostic provenance/role in the custody ledger. For #134, the pinned protocol directory contains only README and TOML; they specify an embodied intervention design and criteria but no observed run/result. Mechanical tests are not result evidence. The bounded DEFER awaits the Lab owner’s authorized TARGET question/consumer determination and any new-method specification. For #135, the pinned directory contains only README/TOML; the README records protocol evolution and says v3 was not a clean test, but no run/result artifact or outcome is present. Static code search found no literal non-migration consumer in current Lab src/tests; applicability remains for Lab Owner determination. For #136, the pinned README reports v1 aggregate outcomes with a run ID and code commit prefix resolving to a full SHA; no independent result artifact is pinned, and v2 has no recorded run identity/outcomes. README custody remains DEFER; no scientific evidence is admitted. For #137, the pinned directory contains only README/TOML describing an intent-persistence comparison, with no run/result artifact; the shared callable and mechanical tests are not outcome evidence. Static source search found no literal non-migration consumer in current Lab src/tests. The bounded DEFER awaits Lab Owner TARGET applicability decision. For #138, the pinned protocol directory contains only README/TOML describing a four-arm study design and protocol revisions; no run/result artifact or identity is present. Shared callable/mechanical tests are not outcome evidence; bounded static source search found no literal non-migration consumer in current Lab src/tests. Lab Owner TARGET applicability remains undecided. For #139, the pinned protocol directory contains only README/TOML, while a separately pinned historical audit reports ACA1–ACA10/replay and per-seed outcomes (2/4/5 useful multi-contributor composites, 67/71/62 transmission attempts, 178/180/185 cultural costs). The audit has no explicit run ID, execution commit, or raw output; its claims remain audit-reported, not independently verified or admitted. It describes an explicit deterministic baseline rather than emergent learned cooperation. Bounded static source search found no literal non-migration TARGET consumer. Lab Owner TARGET applicability and audit provenance/role remain unresolved; closure trigger is owner-recorded authorized TARGET need plus any new-method specification and custody resolution. For #140, the pinned protocol directory contains only README/TOML specifying a three-arm stopping design and criteria; no run identity or result artifact is present. The associated source test constructs/compares requests and does not establish study outcomes. Bounded static source search found no literal non-migration TARGET consumer; Lab Owner applicability remains undecided. Closure trigger is owner-recorded authorized TARGET need and any new-method specification. For #141, the exact HIST manifest is one of two arms sharing registry key `learning.binding-degradation`; the sibling OFF arm remains separately unresolved. Its pinned README/TOML specify the arm, while the linked design record reports 2026-09-28 results (including 0/79 true detections) but contains no raw run bundles in the protocol directory and its status says “preregistered, not implemented” despite reporting runs. The report is not independently validated or admitted, and its custody linkage is unresolved. Bounded static search found no literal non-migration TARGET consumer; owner TARGET applicability is open. A manifest-specific alias row separates HIST from the registry-level candidate. For #142, the exact OFF manifest is the sibling of HIST under registry key `learning.binding-degradation`. The pinned protocol directory contains README/TOML only; the linked design doc reports OFF 0/197 false invalidations and 13 spurious satisfactions, but no raw run bundle is pinned here and the same document says “preregistered, not implemented”. The true-detection metric is specific to HIST, not OFF. The report remains unvalidated/unadmitted; custody linkage and TARGET applicability remain open. A manifest-specific crosswalk alias keeps OFF separate. For #143, the pinned README/TOML define a three-seed matched intact/damaged-body adaptation protocol; RESULTS.md reports three passing trials but has no run ID, exact executed code revision, environment lock or raw output. Its `validated=true` label is source-authored metadata; the linked custody ledger classifies the report as SCIENTIFIC_EVIDENCE but NOT_ADMITTED and NOT_SCIENTIFICALLY_VALIDATED. Bounded current Lab source search found no literal non-migration consumer. The DEFER leaves TARGET applicability and the report provenance/use decision to the Lab owner. For #144, the pinned README combines the opaque sensorimotor-agency protocol with reported 3/3 outcomes but no run ID, exact execution commit, environment lock or raw output. The custody ledger therefore keeps that README DEFER and NOT_ADMITTED; the TOML remains PROTOCOL custody. The report is not independently validated. Bounded current Lab source search found no literal non-migration consumer. TARGET applicability and README content-role/provenance remain for Lab owner decision. For #145, the pinned README combines counterfactual protocol and reported 3/3 results but gives no run ID, exact execution revision, environment lock, or raw output. Its custody remains DEFER/NOT_ADMITTED. The TOML remains PROTOCOL custody. Reported outcomes are not independently validated; bounded current Lab source search found no literal non-migration consumer. TARGET applicability and README role/provenance remain for the Lab owner. For #146, the pinned protocol folder contains only README/TOML, while separate `lab/research/STATUS.md` reports run `20260921T115809Z-learning-cognitive-ecology-embodiment-6022a88-e459` (code prefix resolved to `6022a8832c3a2a0b8c12667f44b3ca482eb4dc50`) and aggregate gate outcomes. It is a WORKING_ARTIFACT rather than raw run output; no receipts/raw bundles are linked. The report notes two subjects died before 3000 ticks and limits the claim to structural monopoly correction, not useful motor control. The report is not independently validated/admitted. Owner TARGET applicability remains undecided. The other 42 candidate IDs remain without a per-protocol disposition record and retain their candidate `DEFER` state. Historical implementations and
source tests for these resolved units are `DROP` as TARGET code/tests; these
classifications do not copy, move, or delete historical source bytes or artifact
records. The genesis-viability unit's linked result has an unresolved
configuration/population discrepancy and is not treated as conformant or
scientifically validated; the recurrent-restoration unit has no result/run
artifact at the pinned source commit. The causal-revision result records a run ID
and source SHA but also `software.dirty=true`, so its exact executed source tree
is not reconstructible; it remains custody-only `SCIENTIFIC_EVIDENCE`, not admitted
or scientifically validated. The somatic-correlation-trap disposition is
migration classification only: it does not import historical thresholds, an
activation/temperature relation, or inference rules, and it makes no scientific
validity, reproducibility, method-equivalence, evidence-admission, or Biopeia
applicability claim. Its artifact custody remains separately recorded. The
crosswalk alone does not close any study unit. Remaining per-study dispositions
must be one of:

- `REIMPLEMENT_METHOD` with a scientifically reviewed method/estimand record;
- `HISTORICAL_PROTOCOL` where the source protocol remains historical;
- `DROP_IMPLEMENTATION` while preserving separately admitted evidence/protocol;
- `DEFER` with a concrete reason and review trigger.

Do not claim method preservation, TARGET applicability, efficacy, or result
reproducibility from registry membership, tests, configuration files, or
historical artifacts alone. Equivalence claims require independent Advisor
review and Lab/repository-owner acceptance; Architecture Owner review is also
required if an authority boundary changes.

## Coverage limits

The registry has 76 distinct IDs at the pinned source SHA. It is not a count of
all study capabilities: helper modules, unregistered study code, `experiment.toml`
files, tests, and artifact groups are different units. This crosswalk does not
classify unregistered code or resolve the historical, unreconciled “129” count.
Custody classification is maintained separately in
[`scientific-custody-80d372a.tsv`](scientific-custody-80d372a.tsv): 477 source artifacts
are accounted for, with 448 owner-accepted custody classifications and 29
row-specific pending exceptions. This study crosswalk does not alter those
artifact-level custody dispositions.
