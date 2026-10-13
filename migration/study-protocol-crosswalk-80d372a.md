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
records ten unit-level dispositions: nine `HISTORICAL_PROTOCOL` units
(`continuity.recurrent-restoration`, `embodiment.causal-revision-sequence`,
`world.genesis-viability-characterization`, `embodiment.heredity-leakage-challenge`,
`learning.visual-predictor-audit`, `embodiment.label-invariance`,
`embodiment.somatic-correlation-trap`, `embodiment.temporal-causality-challenge`, and
`embodiment.tool-body-distinction`) and one `REIMPLEMENT_METHOD` question
(`embodiment.hidden-common-cause`) whose new protocol design is separately tracked.
The other 66 candidate IDs remain `DEFER`. Historical implementations and
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
