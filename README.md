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

The default package CI suite is isolated (`tests/unit`) and installs no private
domain packages. The actual material-transfer cross-package tests remain in
`tests/integration`; they are not mocked or silently skipped. GitHub's default
repository token cannot clone the private Biopeia domain repositories, so run
these from the Biopeia workspace, where the pinned domain checkouts are present:

```sh
python -m pip install -r requirements-integration.txt
cd lab
python -m pytest -o testpaths= tests/integration
```

Alternatively, an authorized consumer may install `lab[integration]` at the
immutable dependency revisions declared in `pyproject.toml`. A green package CI
run validates only the isolated unit suite; it is not integration evidence.
