"""Integrity of the Campaign V1 custody record (lab#465).

The preserved artifacts must keep the bytes they had when they entered Lab
custody; a change to any of them is a custody failure, not an update.
"""

from __future__ import annotations

import hashlib
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ROOT / "docs" / "campaigns" / "longitudinal-learning-v1"
ARTIFACTS = CAMPAIGN / "artifacts"
PROTOCOL = ROOT / "docs" / "protocols" / "protocol-lab-longitudinal-learning-v1.md"
PROTOCOL_SHA256 = "e6b088a04ae3228d39da377438cfcb67d0de35891f6250f9a92db5e2250a14d2"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sums(path: Path) -> dict[str, str]:
    return {name: digest for digest, name in (line.split(maxsplit=1) for line in path.read_text().splitlines())}


def test_original_artifacts_keep_their_recorded_hashes() -> None:
    sums = _sums(ARTIFACTS / "original" / "SHA256SUMS")
    assert len(sums) == 7
    for name, digest in sums.items():
        assert _sha256((ARTIFACTS / "original" / name).read_bytes()) == digest, name


def test_every_original_is_listed_in_its_checksums() -> None:
    listed = set(_sums(ARTIFACTS / "original" / "SHA256SUMS"))
    present = {p.name for p in (ARTIFACTS / "original").iterdir()} - {"SHA256SUMS"}
    assert present == listed


def test_run_output_archive_and_manifest_keep_their_hashes() -> None:
    for name, digest in _sums(ARTIFACTS / "SHA256SUMS").items():
        assert _sha256((ARTIFACTS / name).read_bytes()) == digest, name


def test_run_output_archive_matches_its_manifest() -> None:
    rows = (ARTIFACTS / "run-outputs-manifest.tsv").read_text().splitlines()[1:]
    expected = {path.removeprefix("/tmp/"): (int(size), digest) for path, size, _, digest in (r.split("\t") for r in rows)}
    assert len(expected) == 515
    found = {}
    with tarfile.open(ARTIFACTS / "run-outputs.tar.gz") as archive:
        for member in archive.getmembers():
            if member.isfile():
                found[member.name] = (member.size, _sha256(archive.extractfile(member).read()))
    assert found == expected


def test_provenance_cites_the_recorded_hashes() -> None:
    provenance = (CAMPAIGN / "provenance.md").read_text()
    for digest in _sums(ARTIFACTS / "original" / "SHA256SUMS").values():
        assert digest in provenance


def test_frozen_protocol_is_unchanged_when_present() -> None:
    # The protocol is added by lab#561; this record does not depend on its merge order.
    if PROTOCOL.exists():
        assert _sha256(PROTOCOL.read_bytes()) == PROTOCOL_SHA256
