# Notebook 11 — Final Model Selection: Report

**Status:** complete · **Project:** SWaT Industrial Anomaly Detection · **Workflow:** 12-notebook chain (NB11 of 12)

**Selection:** Outcome A — TCN Autoencoder, window 30, MinMaxScaler, seed 42 (the frozen NB08 configuration).

**Post-audit editorial note (2026-10-26):** Personal machine and Kaggle account paths were redacted, and benchmark findings were clarified to avoid implying production readiness or measured operator burden. No model, score, or evaluation result was recomputed. Related inventory and checksum metadata were refreshed.

---

## 1. Executive summary

Notebook 11 compared the nine selected anomaly-detection methods across point-level metrics, event-level behaviour, false-alarm burden, threshold stability, retraining robustness, computational cost, and interpretability. All metrics were drawn from frozen NB08/NB09 artifacts; no model was retrained, no threshold was retuned, no score was recomputed for the selection.

**The selected method is the TCN Autoencoder at its frozen NB08 configuration** — window 30, MinMaxScaler, seed 42, threshold 0.003907. Its metrics:

| Metric | Value |
|---|---:|
| pAUC@0.05 | 0.7597 |
| F1 | 0.8629 |
| Precision | 0.9449 |
| Recall | 0.7940 |
| FPR | 3.20% |
| ROC-AUC | 0.8240 |
| Event recall | 77.8% (28/36 scenarios) |
| Median detection delay (detected scenarios only) | 0.0 s |
| Alert periods (validation) | 73 |

TCN leads the field on pAUC@0.05, F1, the recorded validation alert-period count, and retraining robustness. Its weaknesses (ROC-AUC below LSTM and Simple Stat; largest F1 threshold swing in the table) are bounded and do not affect the low-FPR evaluation region prioritized by this study.

The alternatives — LSTM and Simple Stat — remain competitive on specific criteria but do not displace TCN under the weighting documented in Cell 11.

---

## 2. Selection decision

**Outcome A — Preferred model identified.**

- **Method:** TCN Autoencoder
- **Window:** 30
- **Scaler:** MinMaxScaler (frozen NB08, 42 features)
- **Seed:** 42
- **Threshold:** 0.003907 (99th percentile linear interpolation of the threshold-partition sequence scores)
- **Checkpoint:** `nb08_artifacts/tcn_preliminary/tcn_autoencoder_best.pth` (frozen, unchanged)
- **Parameters:** 40,554
- **Model size:** 0.16 MB
- **Training time:** 5.12 min (recorded in NB07)

The selected model is the existing frozen NB08 artifact. NB11 has not retrained, re-tuned, or re-scored it.

---

## 3. Evidence by criterion

### Point-level detection (pAUC@0.05, F1, Precision, Recall)

TCN is #1 on pAUC@0.05 (0.7597) and #1 on F1 (0.8629). LSTM is #2 on both (0.7289, 0.8386). Simple Stat is third on F1 (0.8144) but drops to fifth on pAUC (0.6434). TCN's precision (0.9449) is comparable to LSTM's (0.9478); its recall (0.7940) exceeds LSTM's (0.7519). **TCN leads the point-level criterion.**

### Event-level behaviour (recall, delay)

Simple Stat: 91.7% recall at 2.0 s median delay. LSTM: 83.3% at 1.5 s. TCN: 77.8% at 0.0 s. These delay medians apply only to detected scenarios; the TCN's p90 delay is 22.8 seconds and its maximum is about 24.8 minutes. **No method dominates** — Simple Stat leads recall, TCN has the lowest median delay among detected scenarios, and LSTM is between.

### False-alarm burden (FPR, alert periods)

TCN: 73 alert periods, FPR 3.20%. LSTM: 180 periods, FPR 2.86%. Simple Stat: 232 periods, FPR 13.69%. TCN's FPs are temporally clustered (avg ~35 consecutive observations per period); LSTM's are scattered (avg ~13). TCN has the fewest counted alert periods in this validation output among these three; this benchmark does not measure operator workload or establish an acceptable alert burden.

### Threshold stability

TCN's F1 swing across p95/p99/p99.5 is 0.1099 (largest in the table); LSTM's is 0.0223 (smallest). But the frozen p99 threshold sits at the F1 plateau for both — the frozen values are not fragile at the operating point actually used. **LSTM has the flatter curve; TCN is stable at the frozen threshold.**

### Retraining robustness

TCN's worst condition is −5.53% pAUC (StdScaler). LSTM's worst is −8.14% (seed 1). Both pass the ±10% rule, but TCN's margin is comfortable while LSTM's is near the boundary. TCN's perturbation effects are bidirectional (some improve, some degrade); LSTM's are uniformly negative. **TCN leads the robustness criterion.**

### Computational cost

Both deep models are computationally trivial at project scale: TCN 5.12 min training / 0.16 MB / ~440 ms per 1k sequences on CPU; LSTM 2.69 min / 0.51 MB / ~300 ms. Simple Stat has no model artifact. **Computational cost is a neutral criterion — none of the three competitive methods is disqualified by it.**

### Interpretability

Simple Stat is the most directly interpretable. LSTM and TCN are both deep autoencoders; TCN's reconstruction-error-per-feature profile is more traceable than LSTM's hidden-state error. **Simple Stat leads interpretability; neither learned method is disqualified by it.**

---

## 4. Alternative candidates and why they were not selected

### LSTM Autoencoder — viable but weighted-second

LSTM leads on event recall (83.3% vs 77.8%) and precision (0.9478 vs 0.9449). But it has 2.5× the validation alert-period count (180 vs 73), sits near the ±10% boundary on retraining robustness (worst −8.14% vs TCN's −5.53%), and has 3.3× the parameters (132,346 vs 40,554). Its every-axis-degrades pattern suggests its frozen result is a favourable draw rather than the typical case.

**Selection would flip to LSTM if the project weighted event recall above point-level ranking and alert burden.**

### Simple Stat — competitive but FPR-disqualifying

Simple Stat leads ROC-AUC (0.8839), PR-AUC (0.9056), recall (0.8231), and event recall (91.7%). But its FPR is 13.69% — roughly 4.3× TCN's and 4.8× LSTM's — and its pAUC@0.05 (0.6434) trails TCN by 11.6 pp. Its advantages are in high-FPR regions and event recall; its disadvantage is in the low-FPR region and validation alert counts prioritized by this study.

**Selection could change if the project weighted ROC-AUC or interpretability above FPR and pAUC; the 13.69% FPR remains a material trade-off under the documented criteria.**

### Methods excluded on evidentiary grounds

- **USAD** — training did not reach specification (`best_epoch=1`, adversarial term inactive). Its ranking position is a lower bound only.
- **LOF** — ROC-AUC 0.1946, score anti-correlated with the labels as configured. No threshold can repair this.
- **Isolation Forest** — 36.1% event recall at 111 s median delay.
- **One-Class SVM** — 22.2% event recall at 20.5 s median delay.
- **Rule-Based** — FPR 92.74%. Degenerate detector at sequence level.
- **Rolling Stat** — pAUC 0.0161, ROC-AUC below chance.

---

## 5. Trade-offs accepted

The TCN selection is defensible, not overwhelming:

- **TCN misses 22.2% of labeled scenarios** (8 of 36) at the frozen threshold.
- **TCN's ROC-AUC trails both LSTM and Simple Stat.** The gap is in the high-FPR region not prioritized by this evaluation, but it is a real limitation.
- **TCN's F1 has the largest threshold swing in the table** (0.1099). The frozen threshold is on the F1 plateau but the plateau is narrow.
- **The TCN-LSTM pAUC gap is 3.1 pp; the F1 gap is 2.4 pp.** Not a landslide. A different criteria weighting could defensibly select LSTM.
- **The selection rests on weighting pAUC/F1 and validation alert-period counts above event recall.** That weighting is documented in Cell 11 and can be challenged; it does not establish that the observed count is operationally acceptable.

---

## 6. Limitations summary

The full limitation set is in Cell 12 of the notebook. The most consequential ones for interpreting the selection:

- **Dataset scope.** SWaT is a research testbed, not a production deployment. Performance on real industrial plants may differ.
- **Evaluation design.** Single chronological split; no cross-validation; no rolling re-evaluation; no test of concept drift.
- **Feature scope.** 42 sensor features, MinMax scaled. Alternative feature sets and scalers were not tested.
- **Endpoint convention.** Sequence scoring at the last observation of each window; alternatives not tested.
- **Robustness scope.** Window, scaling, and seed tested for TCN and LSTM only. Other methods not retrained.
- **Event-level evidence.** w30 only. Whether TCN's event recall or delay would change at other windows is not measured.
- **USAD.** Inherited undertraining limitation from NB08; not repaired in NB11.
- **Statistical anomaly detection, not attack attribution.** TCN produces a reconstruction error; it does not classify anomalies as cyberattacks or equipment failures, and does not diagnose physical components.

---

## 7. Handoff to Notebook 12

Notebook 12's task is reproducibility audit. Items to verify:

1. Consolidate dependency versions into a single manifest (currently only numpy is recorded, in `frozen_thresholds.json`).
2. Audit path portability across all committed notebooks.
3. Verify random seeds are explicit everywhere.
4. Verify chronological split boundaries are reproducible from `normal.csv` + `attack.csv`.
5. Verify the frozen threshold (0.003907) is reproducible via 99th percentile linear interpolation.
6. Confirm all NB08/NB09/NB10/NB11 artifacts are present and hash-match.
7. Verify the notebook runs end-to-end from a clean kernel.
8. Confirm the selected model's reported metrics reproduce on a clean run.

The complete handoff note is Cell 13.

---

## 8. Artifact inventory

All NB11 outputs are stored in `nb11_artifacts/`:

- `comparison/nine_method_comparison.csv` — 9 methods × 25 columns
- `comparison/computational_cost.csv` — cost table (training, inference, params, file size)
- `comparison/NB11_STAGE_C_UNIFIED_COMPARISON.md`
- `comparison/NB11_STAGE_D6_COMPUTATIONAL_COST.md`
- `alignment/window_alignment_aligned_metrics.csv`
- `alignment/window_alignment_comparison.csv`
- `alignment/NB11_STAGE_B_WINDOW_ALIGNMENT.md`
- `NB11_STAGE_B_COMPARABILITY_STATE.md`
- `cell1_artifact_inventory.csv`
- `_inventory.csv`, `_nb11_checksums.csv`, `_verification_report.md`
- `NB11_FINAL_REPORT.md` (this document)

Frozen artifacts (unchanged by NB11):

- `nb08_artifacts/*` — all baseline artifacts
- `nb09_artifacts/*` — event-level results
- `nb10_artifacts/batch_scoring/*.csv` — NB10 robustness summary CSVs
- `nb10_artifacts/synthesis/*.csv` — NB10 cross-axis synthesis CSVs
- `nb10_artifacts/pilot/*` — 10 retrained checkpoints and histories

Regenerated in NB11:

- `nb10_artifacts/window_scores/window_scores.npz` — re-scored from the same checkpoints in Cell 3a; all 4 thresholds match NB10 reference exactly.

---

**End of report.** Notebook 11 is complete. Notebook 12 (reproducibility audit) is the final notebook of the twelve-notebook chain.
