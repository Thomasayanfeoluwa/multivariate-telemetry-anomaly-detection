# Notebook 12 — Reproducibility and Final Audit: Report

**Status:** complete · **Project:** SWaT Industrial Anomaly Detection · **Workflow:** 12 of 12 notebooks

**Selected method (from NB11):** TCN Autoencoder, window 30, MinMaxScaler, seed 42, threshold 0.003907.

**Post-audit editorial note (2026-10-26):** Personal machine and Kaggle account paths were redacted, and the report wording was clarified. No notebook cells were rerun, and no model, score, or evaluation result was recomputed. Related inventory and checksum metadata were refreshed.

---

## 1. Executive summary

Notebook 12 audited the SWaT anomaly-detection project for reproducibility. It verified the environment, the frozen artifacts, the temporal partitions, the threshold procedures, and the final selection decision from NB11. Every check was performed against actual files, not against assumptions. The audit passes all ten reproducibility checks in Cell 8, and all eleven audit areas in Cell 11 are settled — six with plain PASS and five with documented ISSUEs that do not affect the TCN selection.

**The project is:**
- Structurally complete (all 12 notebooks present, all 5 artifact directories populated, all raw data on disk).
- Fully traceable (every reported result links to a hashed artifact; 18/18 frozen checksums verified unmodified).
- Demonstrably executed (frozen artifacts exist with recorded contents; the TCN threshold is bit-for-bit reproducible from the frozen scores).
- **Not** independently reproduced by a second practitioner — that remains the honest boundary.

**The TCN selection is defensible as an experimental result.** It is not a deployment recommendation.

---

## 2. Selection decision (from NB11)

| Field | Value |
|---|---|
| Method | TCN Autoencoder (4 causal-conv blocks, kernel 3, dilations [1,2,4,8], 32 channels) |
| Window | 30 |
| Scaler | MinMaxScaler (frozen NB08, 42 features) |
| Seed | 42 |
| Threshold | 0.003907 (99th pct, linear interp) |
| Parameters | 40,554 |
| Checkpoint | `nb08_artifacts/tcn_preliminary/tcn_autoencoder_best.pth` |

Reported metrics at the frozen threshold: pAUC@0.05 = 0.7597, F1 = 0.8629, Precision = 0.9449, Recall = 0.7940, FPR = 3.20%, ROC-AUC = 0.8240, event recall = 77.8% (28/36), median delay = 0.0 s, alert periods = 73.

---

## 3. Eleven audit areas

| # | Audit area | Status |
|---|---|---|
| 1 | Notebook workflow (12 present, order documented) | PASS |
| 2 | Data provenance (hashes recorded, release unrecorded) | PASS with ISSUE |
| 3 | Environment (audit documented, training partially lost) | PASS with ISSUE |
| 4 | Experimental configuration (register complete, seeds missing 6/9) | PASS with ISSUE |
| 5 | Temporal design (partitions verified, overlap documented) | PASS with ISSUE |
| 6 | Model artifacts (33 hashed, 32 present, 18/18 checksums match) | PASS |
| 7 | Model selection (traced to NB11 evidence) | PASS |
| 8 | Portability (8 notebooks require edit, 2 false alarms, 2 clean) | PASS with ISSUE |
| 9 | Reproducibility checks (10/10 passed) | PASS |
| 10 | Limitations (15 cataloged with impact) | PASS |
| 11 | Final documentation (9-question summary, evidence-grounded) | PASS |

**No UNVERIFIED. No NOT APPLICABLE. All 11 areas settled.**

---

## 4. The four levels of evidence

| Level | Status |
|---|---|
| Structurally complete | YES |
| Traceable | YES |
| Executed | YES |
| Independently reproduced | NO |

The project has not been reproduced by an independent practitioner. The frozen artifacts are internally consistent and traceable, but a from-scratch re-run by a second party has not been attempted. This is the honest boundary — the correct claim is "auditable, traceable, and executed," not "reproducible from scratch."

---

## 5. Reproducibility checks (from Cell 8)

All 10 checks pass:

1. Selected model checkpoint present.
2. TCN metrics match NB11's cited values (6/6 within 1e-3).
3. Scaler has 42 documented features.
4. **TCN frozen threshold bit-for-bit reproducible** from frozen scores (`|delta| = 0.00e+00`).
5. `frozen_thresholds.json` structure complete (9 required fields).
6. NB11 report present and cites Outcome A + TCN.
7. All 12 workflow notebooks present.
8. `requirements.txt` present with 12 pinned versions.
9. Three required raw data files present.
10. **Frozen artifact integrity verified** — 15/15 NB08 checksums, 3/3 NB11 checksums.

---

## 6. Documented limitations (from Cell 9)

Fifteen limitations are cataloged with evidence and impact. The five most consequential:

1. **Dataset provenance** — the specific SWaT release is not recorded in project artifacts; only the file SHA256s are preserved.
2. **Environment drift** — the training environment (Kaggle T4) is only partially documented; only NumPy's version is preserved (`2.1.3`).
3. **Seed metadata** — 6 of 9 frozen checkpoints lack seed records in the artifact (only USAD's wrapper has it).
4. **Path portability** — 8 of 12 workflow notebooks contain hardcoded Kaggle paths in executable cells, blocking a full re-run outside Kaggle.
5. **Evaluation design** — single chronological split; attack partition temporally overlaps with normal data (inherited from SWaT structure); no cross-validation.

Each limitation is qualified by Cell 9 as to whether it affects the TCN selection (**none does**) or only a from-scratch reproduction (**two do — environment drift and seed metadata, plus portability**).

---

## 7. What the project establishes

- A documented, artifact-audited offline comparison of nine anomaly-detection methods on the available SWaT testbed data under a leakage-safe, chronologically-split protocol. The threshold and frozen-artifact checks are reproducible; a clean independent from-scratch reproduction has not been demonstrated.
- That the TCN Autoencoder at w30 / MinMax / seed 42 is the most defensible of the nine methods under the project's documented weighting — leading on pAUC@0.05, F1, validation alert-period count, and the tested retraining-robustness comparisons.
- That seven of seven leakage safeguards required by the specification are met.
- That the frozen artifacts are internally consistent, traceable, and their threshold is reproducible from the recorded scores.

## 8. What the project does not establish

- That TCN is the best possible detector for this dataset (only that it's the best of the nine evaluated).
- That TCN would work on a production system (only that it performs as reported on the frozen SWaT test partitions).
- That a from-scratch reproduction would produce bit-identical checkpoints (only that frozen artifacts are intact).
- That detections correspond to confirmed cyberattacks (labels are proxy signals from SWaT experimental design).

---

## 9. Artifact inventory

Under `nb12_artifacts/`:

- `NB12_FINAL_REPORT.md` (this document)
- `_verification_report.md` (audit trail)
- `_inventory.csv`, `_nb12_checksums.csv`
- `cell1_project_inventory.csv` (structure audit)
- `cell2_dataset_provenance.json` (SHA256 hashes and schema)
- `cell3_environment.json`, `requirements.txt` (audit environment)
- `cell4_configuration_register.csv`, `.json` (9-method configuration register)
- `cell5_temporal_splits.json` (partition boundaries + safeguards)
- `cell6_artifact_inventory.csv`, `cell6_artifact_stats.json` (33-artifact hash record)
- `cell7b_portability_check.json` (path scan per notebook)
- `cell8_reproducibility_checks.json` (10/10 PASS)

Frozen artifacts (unchanged across NB01–NB12):

- `nb08_artifacts/` — frozen baseline (163.91 MB)
- `nb09_artifacts/` — event analysis (25.03 MB)
- `nb10_artifacts/` — robustness results (14.47 MB)
- `nb11_artifacts/` — model selection (0.04 MB)

Regenerated during NB11:

- `nb10_artifacts/window_scores/window_scores.npz` — verified matching NB10 reference thresholds exactly.

---

## 10. Final statement

Notebook 12 completes the audit and reproducibility stage of the twelve-notebook SWaT anomaly-detection project. The selection of the TCN Autoencoder is documented, evidenced, and bounded by the project's stated limitations. The frozen artifacts are intact and traceable. All reproducibility checks pass.

**The twelve-notebook research and audit workflow is complete.** Production deployment, additional methods, cross-dataset validation, and an independent from-scratch reproduction remain future work; the current NB12 audit defines the starting conditions those efforts would inherit.

---

**End of report. Notebook 12 and the twelve-notebook workflow are complete.**
