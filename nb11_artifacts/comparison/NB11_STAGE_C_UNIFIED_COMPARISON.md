# NB11 Stage C — Unified Nine-Method Comparison

## 1. Sources

- Point-level: `evaluation_summary.csv` (frozen NB08)
- Event-level: NB09 `event_recall.csv`, `detection_delay_summary.csv`, `validation_false_alarm_summary.csv`
- Robustness verdicts: NB10 `window/scaling/seed_summary.csv`
- Threshold F1 swing: NB10 `threshold_sensitivity_summary.csv` (score-based methods only)
- Training times: documented NB05/NB07 records for TCN and LSTM

## 2. Point-level metrics

| display          | class          |   pAUC_05 |   ROC_AUC |   PR_AUC |     F1 |   Precision |   Recall |    FPR |    TP |    FP |    TN |    FN |
|:-----------------|:---------------|----------:|----------:|---------:|-------:|------------:|---------:|-------:|------:|------:|------:|------:|
| Rule-Based       | baseline       |    0.6187 |    0.7686 |   0.8207 | 0.5417 |      0.3933 |   0.8703 | 0.9274 | 47509 | 73295 |  5736 |  7083 |
| Rolling Stat     | baseline       |    0.0161 |    0.4711 |   0.3779 | 0.3727 |      0.3796 |   0.3661 | 0.4134 | 19987 | 32669 | 46362 | 34605 |
| Simple Stat      | baseline       |    0.6434 |    0.8839 |   0.9056 | 0.8144 |      0.8059 |   0.8231 | 0.1369 | 44933 | 10823 | 68208 |  9659 |
| Isolation Forest | traditional_ml |    0.6266 |    0.7754 |   0.8294 | 0.747  |      0.9664 |   0.6088 | 0.0146 | 33236 |  1155 | 77876 | 21356 |
| One-Class SVM    | traditional_ml |    0.641  |    0.7802 |   0.8294 | 0.7693 |      0.9815 |   0.6325 | 0.0082 | 34529 |   650 | 78381 | 20063 |
| LOF              | traditional_ml |    0.0584 |    0.1946 |   0.3276 | 0.1117 |      0.6098 |   0.0615 | 0.0272 |  3355 |  2147 | 76884 | 51237 |
| LSTM AE          | deep_learning  |    0.7289 |    0.8513 |   0.8925 | 0.8386 |      0.9478 |   0.7519 | 0.0286 | 41046 |  2259 | 76772 | 13546 |
| TCN AE           | deep_learning  |    0.7597 |    0.824  |   0.8778 | 0.8629 |      0.9449 |   0.794  | 0.032  | 43345 |  2528 | 76503 | 11247 |
| USAD             | deep_learning  |    0.6438 |    0.7934 |   0.8471 | 0.7723 |      0.9654 |   0.6436 | 0.016  | 35135 |  1261 | 77770 | 19457 |

## 3. Event-level and robustness

| display          |   events_detected |   events_represented |   event_recall |   median_delay_s |   validation_alerts |   validation_fp_obs | robust_window   | robust_scaling   | robust_seed   |
|:-----------------|------------------:|---------------------:|---------------:|-----------------:|--------------------:|--------------------:|:----------------|:-----------------|:--------------|
| Rule-Based       |                36 |                   36 |       1        |              0   |                 232 |               73295 | not tested      | not tested       | not tested    |
| Rolling Stat     |                36 |                   36 |       1        |              0   |                6646 |               32669 | not tested      | not tested       | not tested    |
| Simple Stat      |                33 |                   36 |       0.916667 |              2   |                 232 |               10823 | not tested      | not tested       | not tested    |
| Isolation Forest |                13 |                   36 |       0.361111 |            111   |                  45 |                1155 | not tested      | not tested       | not tested    |
| One-Class SVM    |                 8 |                   36 |       0.222222 |             20.5 |                  48 |                 650 | not tested      | not tested       | not tested    |
| LOF              |                15 |                   36 |       0.416667 |             82   |                  76 |                2147 | not tested      | not tested       | not tested    |
| LSTM AE          |                30 |                   36 |       0.833333 |              1.5 |                 180 |                2259 | stable          | stable           | stable        |
| TCN AE           |                28 |                   36 |       0.777778 |              0   |                  73 |                2528 | stable          | stable           | stable        |
| USAD             |                24 |                   36 |       0.666667 |              7.5 |                  52 |                1261 | not tested      | not tested       | not tested    |

## 4. Cost and threshold stability

| display          | train_min   | threshold_F1_swing   |
|:-----------------|:------------|:---------------------|
| Rule-Based       | -           | -                    |
| Rolling Stat     | -           | -                    |
| Simple Stat      | -           | -                    |
| Isolation Forest | -           | 0.010963064715851734 |
| One-Class SVM    | -           | 0.03399386060201648  |
| LOF              | -           | 0.04841962759973921  |
| LSTM AE          | 2.69        | 0.02228825324947159  |
| TCN AE           | 5.12        | 0.10987527429246391  |
| USAD             | -           | 0.025105608297463    |

## 5. Notes

- Values shown as `-` are unavailable from the artifacts. They are not zero.
- `events_detected` refers to scenarios detected, out of `events_represented` scenarios that had data.
- `validation_alerts` is the number of distinct false-alarm periods in the validation partition.
- `validation_fp_obs` is the raw observation-level false-positive count in the same partition.
- Robustness verdicts apply to TCN and LSTM only; other methods were not retrained in NB10.
- Threshold F1 swing is the range across p95/p99/p99.5 for score-based methods.
- Training times for USAD, IF, OCSVM, LOF are not separately recorded in NB08.
- USAD training resulted in best_epoch=1 with the adversarial term inactive;
  documented in NB08 and carried forward unchanged.
