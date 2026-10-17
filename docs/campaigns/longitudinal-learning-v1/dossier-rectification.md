# Rectification of `DOSSIER-LAB-LONGITUDINAL-LEARNING-V1`

**Revision:** rectification 1, 2026-10-17, by Claude. Each correction is
checked against the preserved scripts and outputs; nothing was re-run.

**Historical version:** `artifacts/original/longitudinal_learning_v1_evidence_dossier.md`,
SHA-256 `6ba54a2ecca580d9ad6017a436df8c60a268893e0d9638bd9aae687800596773`,
kept unchanged. Line numbers below refer to it. Where this rectification and
the dossier disagree, this rectification applies. The dossier was not
submitted for review; it is rectified here because it is the only written
account of the results.

## Corrections

| Line(s) | Dossier says | Rectification | Evidence |
|---|---|---|---|
| 7 | "Campaña experimental completa … continuidad multicorte" | An exploratory pilot of a non-conforming variant, with one interruption | deviations.md |
| 13, 40 | "retroalimentación somática autorizada" | Joint proprioception (`KinematicSomaticTransductionV1`), not interoception | README, Classification |
| 16 | Level 1, "plasticidad no supervisada Oja" | Δw = +0.03887 holds, under an **experimenter-scheduled** Oja update: rate 0.15, modulation 1.0, one eligible edge, all set by the script | `run_pilot_factorial.py` line 230; `pilot_results.json` |
| 17 | Level 2 "comprobado positivamente … bajo sonda normalizada" | **Withdrawn.** No script applies a probe, and $D_{func}$ was never computed. Functional change was **not measured** | `grep -c probe` returns 0 for all three scripts |
| 18, 111–124 | Level 3, primitive `primitive.5f3bafe20185257e` "robusta", tick 12, 3 samples, consistency 0.6488 | The values match the preserved outputs: present from target tick 12; at tick 20, 3 samples, `directional_consistency` 0.6488, `effect_mean` 0.2698. "Robusta" is not supported by 3 samples. The primitive also forms in G2, with no plasticity | G4 owner checkpoints in `run-outputs.tar.gz` |
| 19, 84–104 | Level 4, "bit a bit idéntica … cold restore", "caída del proceso, restauración en frío en un nuevo runtime de World", diagram "[CRASH]", "Bit a bit IDÉNTICO" | **Withdrawn as stated.** See "Restore at cut 10" below | `run_pilot_factorial.py` lines 346–371; outputs |
| 19, 66–71 | "retención del 100% … tras extinción" | The weight is unchanged across the 10 extinction cycles. Whether that shows retention or only a zero update under zero input was not examined. The field was replaced by the script, not changed by the Environment | `e2_results.json`; `run_environmental_variability.py` lines 322–332 |
| 20, 73–78 | Level 5 "observada parcialmente"; E3 "mecánica perturbada/amortiguada"; "demostrando que Organism no fabrica retroalimentación sintética" | **Withdrawn.** E3 changes motor gain (`scale` 0.5 → 0.2), not damping or load. Joint speed is lower under the lower gain. The competence engine gives **identical** primitives and horizon counts in both conditions, so it does not distinguish them. No adaptation is shown | `e3_results.json`; `run_bodily_perturbation.py` lines 255, 329–330 |
| 39 | η = 0.15 | Executed value. The frozen protocol says η = 0.05; this deviation is not disclosed in the dossier | deviations.md |
| 61–63 | E1 "aumentan monótonamente … hasta converger" | **Withdrawn.** No E1 run exists, and no weight trajectory was recorded: only initial and final values | scripts; `pilot_results.json` |
| 125 | Ticks 13–20, selection "no sustituyó completamente la exploración estocástica"; reuse needs 50–100 cycles | Reuse was **not measured**, so nothing about it can be said, including the cycle count it would need | scripts |
| 134 | world `8266b8998818dd177b960959f77f59160d5bfa7f` | Names no commit. The revision is `8266b8968b4dd52231723564d833077675a316d2` | provenance.md |
| 136–139 | artifacts under `scratch/` | Preserved under Lab custody in `artifacts/`; see provenance.md | `artifacts/` |
| 146 | "computacionalmente sólida, determinista y matemáticamente reproducible" | Not shown. Each cell ran once, nothing was re-run, and neither the working tree nor the environment was recorded | provenance.md, "Reproducibility limits" |
| 150 | "evidencia técnica concluyente de los niveles 1, 2, 3 y 4" | Level 1 is shown under the scheduled update, and primitive formation is counted (level 3, as a count only). Level 2 was not measured. Level 4 is not shown, for the reasons below | this table |

## Restore at cut 10 (dossier lines 19, 84–104)

What was run (`run_g4_multicut_restore`):

- 10 cycles, then `restore_scalar_sensorimotor_runtime` **in the same
  process**, with `owner_checkpoint_verifier=lambda refs: True`, which
  disables owner-checkpoint verification;
- 10 more cycles under different run identifiers (`session-G4-cut10`, then
  `session-G4-resumed`).

There was no crash and no new process.

What the preserved outputs show, at tick 20 only:

- The World manifests of the separate uninterrupted G4 run and of the
  restored run name **different** SHA-256 digests for the Organism,
  Embodiment and world-journal checkpoints, and for one of the two
  Environment checkpoints.
- For the Organism checkpoint, the only differing fields are `commit_id` and
  `physical_step_id`, which are derived from the run identifier. Its
  `transition_state`, `engine` and `action_domain` contents are equal byte
  for byte.
- The Embodiment, Environment and journal differences were not analysed.

So: the summarised end state matches, and the Organism checkpoint matches
apart from identifiers. That supports neither "bit a bit idéntica" nor
durability: verification was disabled, there was no process boundary, and
only tick 20 was compared.

## Unchanged

The rest of the dossier, including the factor-separation observations
(lines 51–55) and the D2 table values (lines 37–49), agrees with
`pilot_results.json`. It is to be read under the classification in the
README.
