# NB11 Stage D.6 — Computational Cost

## 1. Sources

- Training times: recorded NB05 (LSTM) and NB07 (TCN) runs
- Inference times: measured in Cell 3a for the four w60/w90 retrained models only
- Model file sizes: on-disk checkpoint / joblib sizes
- Parameter counts: extracted from TCN, LSTM, USAD checkpoints

## 2. Cost table

| method   | display          | train_min   | model_mb   | params   | inf_ms_per_1k_w60   | inf_ms_per_1k_w90   |
|:---------|:-----------------|:------------|:-----------|:---------|:--------------------|:--------------------|
| rule     | Rule-Based       | -           | -          | -        | -                   | -                   |
| rolling  | Rolling Stat     | -           | -          | -        | -                   | -                   |
| simple   | Simple Stat      | -           | -          | -        | -                   | -                   |
| if       | Isolation Forest | -           | 2.27       | -        | -                   | -                   |
| ocsvm    | One-Class SVM    | -           | 0.0        | -        | -                   | -                   |
| lof      | LOF              | -           | 85.73      | -        | -                   | -                   |
| lstm     | LSTM AE          | 2.69        | 0.51       | 132346.0 | 299.0               | 436.9               |
| tcn      | TCN AE           | 5.12        | 0.16       | 40554.0  | 439.7               | 348.1               |
| usad     | USAD             | -           | 1.91       | 0.0      | -                   | -                   |

## 3. What is measured vs unavailable

Measured:
- TCN and LSTM training times (single-run, on Tesla T4)
- TCN and LSTM w60/w90 inference times (Cell 3a, on CPU)
- Model file sizes for all six learned methods
- Parameter counts for TCN, LSTM, USAD

Not measured / not available:
- Training times for USAD, IF, OCSVM, LOF, or the three baselines
- Frozen w30 inference times (Cell 3a measured w60/w90 only)
- Inference times for IF, OCSVM, LOF, or the three baselines
- Memory usage during training or inference
- Cold-start / model-loading time

## 4. Notes

- `train_min` is single-run training time, not a repeated benchmark. It is
  sufficient to establish order of magnitude, not a latency benchmark.
- Parameter counts for sklearn models (IF, OCSVM, LOF) are not comparable
  to neural-network parameter counts. File sizes are the memory proxy.
- Baselines (Rule, Rolling, Simple) have no trained model artifact.
  Their cost is per-observation compute of a fixed rule.
