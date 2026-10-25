# NB10 verification report

Generated: 2026-10-25T02:15:47.772396Z

## Baseline reproducibility (NB08 frozen result)

- 18/18 pAUC@0.05 and ROC-AUC checks match `evaluation_summary.csv` to 1e-4.
- 9/9 p99 integer-count reproductions (TP and FP match frozen exactly):
  TCN 43,345 / 2,528; LSTM 41,046 / 2,259; USAD 35,135 / 1,261;
  IF 33,236 / 1,155; OCSVM 34,529 / 650; LOF 3,355 / 2,147.
- 3/3 baseline fixed-threshold reproductions:
  Rule F1 0.5417; Rolling F1 0.3727; Simple F1 0.8144.

## Robustness results

- 10/10 retraining conditions inside the ±10% stability band.
- Worst TCN condition: −5.53% pAUC (StdScaler).
- Worst LSTM condition: −8.14% pAUC (seed 1).

## Cross-axis summary

- Window: all 4 conditions stable.
- Scaling: both conditions stable.
- Seed: all 4 conditions stable.
- Threshold: 6 score-based methods scored at p95 / p99 / p99.5;
  3 baselines at fixed threshold only.

## Folder layout

- `pilot/` — 10 retrained checkpoints + histories + metadata + 2 StdScaler joblibs
- `batch_scoring/` — 5 summary CSVs + reports
- `synthesis/` — 3 cross-axis CSVs + NB10 synthesis report
- `plots/` — 4 PNG figures (Fig 1–4)

## Protection of earlier artifacts

NB08 and NB09 artifacts live under
`/kaggle/input/datasets/thomasadegoke/10-robustness-analysis/` and were
not modified by any NB10 cell. `pre_run_hashes.json` records the state of
the frozen models before NB10 retraining began.
