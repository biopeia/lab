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
