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

## Disposition

Every protocol is currently `DEFER`. The crosswalk does not close any study
unit. A later per-study disposition must be one of:

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
It does not classify the 470 unclassified custody artifacts or alter the seven
previously classified records. Those remain governed by the Lab custody ledger.
