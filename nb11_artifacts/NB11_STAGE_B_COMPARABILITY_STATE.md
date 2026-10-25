# NB11 Stage B — Comparability Audit (State)

## 1. Baseline accessibility

- Frozen baseline loaded from `evaluation_summary.csv`
- All 9 expected methods present: if, lof, lstm, ocsvm, rolling, rule, simple, tcn, usad
- Frozen thresholds loaded from `frozen_thresholds.json` (structured: `thresholds`, `sources`, `rule_text`, `numpy_version` — 9 per-method thresholds under the `thresholds` key)

## 2. Frozen baseline metrics

| Method   |   pAUC_05 |   ROC_AUC |   PR_AUC |   F1_Frozen_Thr |   Precision |   Recall |   FPR_at_Thr |
|:---------|----------:|----------:|---------:|----------------:|------------:|---------:|-------------:|
| tcn      |    0.7597 |    0.824  |   0.8778 |          0.8629 |      0.9449 |   0.794  |       0.032  |
| lstm     |    0.7289 |    0.8513 |   0.8925 |          0.8386 |      0.9478 |   0.7519 |       0.0286 |
| usad     |    0.6438 |    0.7934 |   0.8471 |          0.7723 |      0.9654 |   0.6436 |       0.016  |
| simple   |    0.6434 |    0.8839 |   0.9056 |          0.8144 |      0.8059 |   0.8231 |       0.1369 |
| ocsvm    |    0.641  |    0.7802 |   0.8294 |          0.7693 |      0.9815 |   0.6325 |       0.0082 |
| if       |    0.6266 |    0.7754 |   0.8294 |          0.747  |      0.9664 |   0.6088 |       0.0146 |
| rule     |    0.6187 |    0.7686 |   0.8207 |          0.5417 |      0.3933 |   0.8703 |       0.9274 |
| lof      |    0.0584 |    0.1946 |   0.3276 |          0.1117 |      0.6098 |   0.0615 |       0.0272 |
| rolling  |    0.0161 |    0.4711 |   0.3779 |          0.3727 |      0.3796 |   0.3661 |       0.4134 |

## 3. Data partitions (verified from .npz shapes)

| Partition | Observation rows | Sequence rows (w30) |
|---|---:|---:|
| Threshold | 47,437 | 47,408 |
| Validation | 79,060 | 79,031 |
| Attack | 54,621 | 54,592 |

Observation counts match the documented NB08 protocol: 47,437 / 79,060 / 54,621.
Sequence counts at window 30 reflect the loss of the first 29 observations
per partition (no full window available): 47,408 / 79,031 / 54,592.

## 4. Preprocessing (frozen, shared by all learned methods)

- Scaler: MinMaxScaler, fit on the training partition only (`scaler.joblib`)
- Features: 42 sensor columns in NB08 order (`scaler.feature_names_in_`)
- Training rows: 221,366; monitoring rows: 47,435
- Chronological split preserved: training -> monitoring -> threshold -> validation
- Attack partition is a separate evaluation set

Baselines (rule, rolling, simple) use their own established feature definitions
from NB04/NB06. Feature-set differences are inherited from NB08 and documented
there; not re-derived in NB11.

## 5. Score orientation and threshold semantics

| Method class | Score type | Orientation | Threshold rule |
|---|---|---|---|
| Deep learning (LSTM, TCN, USAD) | Float reconstruction error | Higher = more anomalous (`score > thr`) | 99th pct of threshold partition |
| Traditional ML (IF, OCSVM, LOF) | Float decision function / distance | Higher = more anomalous (verified per-method in NB10) | 99th pct of threshold partition |
| Baselines (rule, rolling, simple) | Integer 0/1 decision | Higher = more anomalous (`score > 0`) | Fixed, established in NB04/NB06 |

Score orientation for score-based methods was verified in NB10's threshold
cell by matching frozen TP/FP counts per method. It is not re-verified here.

## 6. Sequence endpoint convention (the alignment issue)

Sequence-based methods score at the last observation of each window. For a
partition of N observation rows and window W, sequence count is N - W + 1:

- Window 30: first 29 observations per partition cannot receive a score
- Window 60: first 59 observations per partition cannot receive a score
- Window 90: first 89 observations per partition cannot receive a score

This is why w30, w60, w90 have different evaluated observation counts. Cell 3
quantifies how much this matters for the window-sensitivity comparison.

## 7. Known limitations inherited from NB08

Documented in NB08 / NB09 and carried forward unchanged:

- USAD: best_epoch = 1, adversarial term inactive. Weak detector, documented
  as such in NB08. Not retrained in NB11.
- LOF: ROC-AUC 0.19 — score direction anti-correlated with labels as
  configured. No threshold can repair this. Documented in NB08.
- Rule-Based: FPR 92.74% at fixed threshold. No continuous score — quantile
  thresholds are not applicable (reported fixed-only in NB10).
- Feature sets: baselines and learned methods use different feature
  definitions. Documented in NB04/NB06. Not harmonised in NB11.

## 8. Baseline reproducibility

Verified in NB10, cited here (not re-run):

- 18/18 pAUC@0.05 and ROC-AUC checks match `evaluation_summary.csv` to 1e-4
- 9/9 p99 integer-count reproductions (TP and FP match frozen exactly)
- 3/3 baseline fixed-threshold reproductions

The frozen baseline is intact and reproducible. NB11 does not re-verify it.

## 9. What Cell 3 verifies

Cell 3 will:
- Re-score the 4 window models (w60/w90 for TCN and LSTM) since `window_scores.npz`
  is missing from the local NB10 extraction
- Align w30/w60/w90 scores to a common observation set per partition
- Recompute pAUC / F1 / ROC-AUC on the aligned set
- Report whether NB10's window deltas survive alignment

## 10. What carries forward to Cell 4

The unified comparison table (Cell 4) will join:
- Point-level metrics from this frozen baseline
- Event-level metrics from NB09
- Robustness findings from NB10
- Computational cost from NB10 pilot metadata

No method, metric, or configuration is re-derived. Every row traces to a
specific artifact in NB08, NB09, or NB10.
