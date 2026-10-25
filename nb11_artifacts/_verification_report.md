# NB11 Verification Report

Generated: 2026-10-25T17:19:49.888994Z

## Baseline reproducibility (from NB10, cited not re-run)

- 18/18 pAUC@0.05 and ROC-AUC checks match `evaluation_summary.csv` to 1e-4.
- 9/9 p99 integer-count reproductions (TP and FP match frozen exactly).
- 3/3 baseline fixed-threshold reproductions.

## NB11-specific verifications

- **Cell 2** — Baseline integrity: 9/9 methods present with all metrics.
  Partitions verified against `.npz` shapes (47,437 / 79,060 / 54,621 obs;
  47,408 / 79,031 / 54,592 seqs at w30).
- **Cell 3a** — Window re-score: 4 models re-scored; all thresholds match
  NB10 reference exactly (TCN w60=0.00278136, TCN w90=0.0033261,
  LSTM w60=0.0333297, LSTM w90=0.0401166).
- **Cell 3b** — Window alignment: all 4 window deltas survive alignment
  (aligned vs NB10 reported differences within 0.11 pp).

## Artifacts regenerated in NB11

- `nb10_artifacts/window_scores/window_scores.npz` — regenerated in Cell 3a
  because the original was missing (NB10 Phase 5d state-dict abbreviation bug
  prevented the original save). Regeneration is byte-comparable via the
  threshold values, which match the NB10 reference exactly.

## Frozen artifacts NOT modified by NB11

- `nb08_artifacts/*` — unchanged
- `nb09_artifacts/*` — unchanged
- `nb10_artifacts/batch_scoring/*.csv` — unchanged
- `nb10_artifacts/synthesis/*.csv` — unchanged
- `nb10_artifacts/pilot/*` — unchanged

## Selection decision recorded

- **Outcome A** — TCN Autoencoder, window 30, MinMaxScaler, seed 42.
- Selected checkpoint: `nb08_artifacts/tcn_preliminary/tcn_autoencoder_best.pth`.
- Threshold: 0.003907 (99th percentile linear interpolation of the
  threshold-partition sequence scores).

## Known limitations carried forward

See `NB11_FINAL_REPORT.md` §6 and Notebook 11 Cell 12 for the full limitation
set. Key items: dataset scope (SWaT testbed), evaluation design (single split,
no cross-validation), feature scope (42 features, MinMax), endpoint convention
(last-observation scoring), robustness scope (window/scaling/seed only,
TCN/LSTM only), event-level evidence (w30 only), USAD undertraining (inherited
from NB08), and the anomaly-vs-attack attribution caveat.

## Reproduction instructions

1. Ensure `nb08_artifacts/`, `nb09_artifacts/`, `nb10_artifacts/`, and
   `data/raw/` are present at the project root.
2. Open `nb11.ipynb` in a fresh kernel.
3. Run all cells top to bottom.
4. If `nb10_artifacts/window_scores/window_scores.npz` is missing, Cell 3a
   regenerates it from the checkpoints (requires PyTorch; CPU sufficient).
5. All output artifacts are written to `nb11_artifacts/` — nothing is
   overwritten elsewhere.
