# Lab

Biopeia Lab apparatus/application extraction candidate. It is not a complete
Lab application and does not establish scientific results.

Included utilities validate seed pairing/disjointness and summarize scalar
study measurements. They do not run experiments, own simulated life, or carry
scientific artifacts.

The apparatus package includes a bounded opaque body-interoception transducer.
It consumes Embodiment-owned body state and requires callers to supply receptor
identifiers; it does not assign meanings to channels or claim scientific
validity. See `MIGRATION.md` for source provenance and transfer limits.

## Development

```sh
python -m pip install -e '.[dev]'
python -m pytest
```

Python package and distribution name: `lab`.

The base package supports Python 3.11+. Integration dependencies require
Python 3.12 because the pinned Environment and World revisions require it.
Lab CI runs unit tests on Python 3.11 and 3.12, builds and installs the wheel
on Python 3.11, and runs the cross-repository integration suite on Python 3.12.
The integration dependencies are immutable Biopeia commit pins in
`pyproject.toml`; changing them is an explicit integration-contract update.
The integration job installs those dependencies and invokes the full test
directory directly, so missing packages or setup fail the job rather than
turning it into a successful skip.

Run the same integration suite locally with:

```sh
python -m pip install -e '.[integration]'
python -m pytest tests/integration
```

The isolated wheel check imports `lab.apparatus.interoception` and
`lab.studies.common.pairing` from the installed distribution outside the source
checkout. These CI jobs validate packaging and the tested software contracts;
they do not establish scientific validity, efficacy, or equivalence.
