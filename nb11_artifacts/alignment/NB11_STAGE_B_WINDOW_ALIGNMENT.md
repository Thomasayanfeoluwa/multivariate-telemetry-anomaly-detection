# NB11 Stage B — Window Alignment Audit

## 1. Method

The frozen w30 evaluation uses the first 29 observations of each partition
(unscored) as the leading edge that cannot yet form a full 30-observation
window. w60 requires 59 unscored leading observations; w90 requires 89.

The intersection of the three evaluated observation sets is
`end_index ∈ [89, N-1]` — that is, exactly the w90 evaluated set. To compare
the three windows on the same observations, w30 and w60 scores are reindexed
to that common set. Thresholds from NB10 are preserved unchanged
(`window_scores_metadata.json` for w60/w90; `frozen_thresholds.json` for w30).

Aligned set sizes: threshold 47,348 (was 47,408 at w30, 47,378 at w60);
validation 78,971 (was 79,031 at w30, 79,001 at w60);
attack 54,532 (was 54,592 at w30, 54,562 at w60).

## 2. Aligned metrics (common observation set)

| arch   |   window |   n_val |   n_atk |   pAUC_05 |     F1 |   ROC_AUC |    FPR |
|:-------|---------:|--------:|--------:|----------:|-------:|----------:|-------:|
| tcn    |       30 |   78971 |   54532 |    0.7605 | 0.8634 |    0.8248 | 0.032  |
| tcn    |       60 |   78971 |   54532 |    0.7681 | 0.8474 |    0.8224 | 0.0482 |
| tcn    |       90 |   78971 |   54532 |    0.7684 | 0.8479 |    0.836  | 0.0568 |
| lstm   |       30 |   78971 |   54532 |    0.7297 | 0.8391 |    0.852  | 0.0286 |
| lstm   |       60 |   78971 |   54532 |    0.71   | 0.8139 |    0.8641 | 0.0206 |
| lstm   |       90 |   78971 |   54532 |    0.6834 | 0.7877 |    0.8486 | 0.0198 |

## 3. NB10 reported deltas vs aligned deltas

| model    |   nb10_delta_pAUC |   aligned_delta_pAUC |   delta_pAUC_diff |   nb10_delta_F1 |   aligned_delta_F1 |   delta_F1_diff | verdict_pAUC   |
|:---------|------------------:|---------------------:|------------------:|----------------:|-------------------:|----------------:|:---------------|
| TCN w60  |              1.05 |                 1    |             -0.05 |           -1.83 |              -1.86 |           -0.03 | survives       |
| TCN w90  |              1.14 |                 1.04 |             -0.11 |           -1.74 |              -1.8  |           -0.06 | survives       |
| LSTM w60 |             -2.64 |                -2.69 |             -0.05 |           -2.97 |              -3    |           -0.03 | survives       |
| LSTM w90 |             -6.25 |                -6.35 |             -0.1  |           -6.07 |              -6.12 |           -0.06 | survives       |

Verdict rule: "survives" if aligned delta within 2 pp of NB10's reported
delta; "reverses" if signs differ; "attenuates" if aligned magnitude is less
than half NB10's; otherwise "changes".

## 4. Interpretation

- TCN w60: NB10 ΔpAUC +1.05% -> aligned +1.00% (verdict: survives)
- TCN w90: NB10 ΔpAUC +1.14% -> aligned +1.04% (verdict: survives)
- LSTM w60: NB10 ΔpAUC -2.64% -> aligned -2.69% (verdict: survives)
- LSTM w90: NB10 ΔpAUC -6.25% -> aligned -6.35% (verdict: survives)

All verdicts are computed programmatically and saved to
`window_alignment_comparison.csv`. NB11's window-sensitivity decision
(Cell 10) uses these aligned deltas as the authoritative values.
