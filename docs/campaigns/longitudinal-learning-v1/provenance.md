# Campaign V1 — provenance manifest

Recorded 2026-10-17 by Claude from the files on the machine where the
campaign ran. Nothing was re-run. Every hash below is checked by
`tests/unit/test_campaign_v1_custody.py`.

## Artifacts

### Originals, copied byte for byte (`artifacts/original/`)

Each was copied from the agent's private working directory
`/home/alessbarb/.gemini/antigravity-cli/brain/a1bbe301-b17c-40db-b33c-7f92d7b9541d/`
(subdirectory `scratch/` for the scripts and data). The copies were compared
with the originals by SHA-256, and the originals were left in place.

| File | Bytes | Last written (UTC) | SHA-256 |
|---|---:|---|---|
| `run_pilot_factorial.py` | 19,263 | 2026-10-16T23:26:34Z | `6d01c27aad376b35e3ed6dc5313cf43a67ab88d32e84efa6ce0ff4c9d9259e6b` |
| `pilot_results.json` | 2,309 | 23:27:29Z | `21a2adeea2d2b9a6a432a13047c6df8fa437e4fda3cadc2737c391837f4a9461` |
| `run_environmental_variability.py` | 15,828 | 23:28:13Z | `0f7e3107bf2135a5c31ad52ab06fab839d9a1266c6568a15d38836c86a454501` |
| `e2_results.json` | 400 | 23:28:25Z | `23899e164940c2082f499e65edae06eed5732e37e4e960ab7004a2ec594d286d` |
| `run_bodily_perturbation.py` | 14,472 | 23:28:51Z | `e914fc05061e61dcfaabbedb4d2635ff6b8f8ce426b332c7e431abce98d5de91` |
| `e3_results.json` | 761 | 23:29:04Z | `c0d7fda2122dec75ad65774b6dfb42f0e853a5a23cfdb08b82b4ae852d8cb6cc` |
| `longitudinal_learning_v1_evidence_dossier.md` | 11,707 | 23:30:43Z | `6ba54a2ecca580d9ad6017a436df8c60a268893e0d9638bd9aae687800596773` |

The six script and data hashes match those declared in the publication
record on lab#465. The protocol itself is not duplicated here: lab#561 holds
it, byte-identical to the original
`protocol_v1_longitudinal_learning.md` (sha256 `e6b088a0…`, last written
23:22:45Z).

### Run outputs (`artifacts/run-outputs.tar.gz`)

The scripts wrote World manifests, journals and owner checkpoints under
`/tmp/biopeia_longitudinal_pilot`, `/tmp/biopeia_variability_pilot` and
`/tmp/biopeia_e3_pilot`. Those directories were still present on 2026-10-17
and were archived unchanged: 515 files, with modification times from
2026-10-16T23:26Z to 23:29Z.

- Archive: deterministic tar (names sorted, owner normalised), gzip without
  a timestamp. It keeps the original paths, relative to `/tmp`, and the
  original modification times.
- `run-outputs-manifest.tsv` lists every original file: path, size,
  modification time and SHA-256, computed from the originals before
  archiving.
- SHA-256 of the archive and of the manifest: `artifacts/SHA256SUMS`.

`/tmp` is volatile; after this archive, Lab's copy is the reference copy.

## Revisions

The scripts declare no revisions. These come from the publication record,
the World lock file and the repository histories:

| Repository | Revision | How established |
|---|---|---|
| world | `8266b8968b4dd52231723564d833077675a316d2` | head of `main` at run time, by committer dates: `8266b89` at 23:17:43Z, the next `main` commit `873c8a9` at 00:15:52Z. The dossier's full hash `8266b8998818dd177b960959f77f59160d5bfa7f` names no commit |
| organism | `779c097d21236cba0409f5fc52fbcd71bf2049d9` | pinned in World's `uv.lock` at `8266b89` |
| modality | `9b72e16f6bfea4b24191015177364d560f7f6715` | pinned in World's `uv.lock` at `8266b89` |
| embodiment | `957af224e4400fc30a9d8d78d987cec16a8e959e` | pinned in World's `uv.lock` at `8266b89` |
| environment | `d59770c05366b24a604b220fc9f7b551b27877f7` | pinned in World's `uv.lock` at `8266b89` |
| observation | `2c506900aa5ad0864eef7f0ce0ed70d7e8e4ea07` | pinned in World's `uv.lock` at `8266b89` |

World's `uv.lock` at `8266b89` has SHA-256
`016e26fa32356c8cf914903fc53c1ed1251150583bc0fe3be0a3f9f4c936e957`.

## Commands and environment

The agent's step log records each run as `uv run python <script>`, run from
`/home/alessbarb/workspace/repos/active/biopeia-workspace/repos/world`:

- `uv run python …/scratch/run_pilot_factorial.py`
- `uv run python …/scratch/run_environmental_variability.py`
- `uv run python …/scratch/run_bodily_perturbation.py`

Each script puts `repos/world` and `repos/world/src` first on `sys.path`, so
**World came from the working tree, not from an installed package**. The
other domains came from World's virtual environment. At the time of
recording, that environment was Python 3.14.3, MuJoCo 3.15.0 and NumPy 2.5.4.
The environment may have changed between the runs and this record.

## Reproducibility limits

1. **Working tree unknown.** No clean-tree check was recorded, so it cannot
   be shown that World's working tree equalled `8266b89`.
2. **Environment not frozen.** `uv run` was used without `--locked`, and no
   environment snapshot was taken, so the installed versions at run time
   cannot be shown.
3. **Hardcoded paths.** The scripts use absolute paths: World under the
   workspace, outputs under `/tmp`, results in the agent directory. They
   also import World's test module
   `tests/integration/test_end_to_end_causal_cycle_acceptance.py` by file
   path. They run unchanged only on this machine layout.
4. **Iterated during collection.** The pilot script was edited after
   failures during collection; see deviations.md, "Execution history". The
   failed attempts left no result file. The output directories were
   overwritten per group (`shutil.rmtree`), so only the final run's outputs
   exist.
5. **Not reconstructed.** Nothing in this directory was reconstructed or
   generated from the originals, except the archive and manifests described
   above. No artifact found missing was recreated.

## Not found

- No log of standard output or error from the successful runs, beyond what
  the agent's step log holds. That log was not copied: it is the agent's
  private session record, not a campaign output.
- No record of seeds; the scripts set none.
