# SWaT Industrial Anomaly Detection — Project State

**Last updated:** 23 October 2026

## 1. Authoritative Documents

- `PROJECT_SPEC.md` — project objectives, fixed workflow, selected methods, methodology, and repository standards.
- `PROJECT_STATE.md` — current progress, verified findings, outstanding questions, and next action.
- `REFERENCE_NOTEBOOK_AUDIT.md` — completed independent audit of the published reference implementation.
- `DEEPSEEK_REVIEW_PROMPT.md` — requirements for independent code review.

The project specification must not be silently changed. Any material inconsistency or required change must be identified and resolved explicitly.

## 2. Project Identity

Investigate anomaly detection in multivariate time-series data from the Secure Water Treatment (SWaT) industrial control-system testbed.

The project follows the fixed twelve-notebook workflow and the nine selected detection methods defined in `PROJECT_SPEC.md`.

All conclusions must be supported by verified data, documented methodology, or reproducible experimental evidence.

## 3. Current Position & Milestone Status

**Current stage:** Full Systemic Correction & Evaluation Harmonization (Notebooks 01–08).  
**Current status:** All structural, methodological, and path-loading issues have been resolved across notebooks 01 through 08.

### Completed Milestones

1. **Reference Notebook Audit (`REFERENCE_NOTEBOOK_AUDIT.md`):**
   - Completed full audit of `notebook.ipynb` (40 cells).
   - Identified test-set threshold optimization leakage in the reference implementation.
   - Identified preprocessing scaler leakage (scaler fit on all normal data prior to 80/20 train/val split).
   - Marked audit as **Complete**.

2. **Universal Kaggle / Local / Colab Portability:**
   - Provisioned `src/utils/paths.py` and embedded universal path resolution across all notebooks.
   - Dynamic auto-detection of `/kaggle/input` datasets and creation of `/kaggle/working/swat-artifacts` for seamless Kaggle execution on CPU/GPU.
   - Automatic artifact packaging utility (`swat_artifacts_complete.zip`) added to Notebook 08 for single-click downloads.

3. **Methodological Corrections across Notebooks 01–08:**
   - **Score Quantization Diagnosis (Notebooks 04 & 08):** Documented that the Simple Baseline's apparent high ROC-AUC (0.8839) is a trapezoidal integration artifact of integer violation counts (86.3% mass at 0). Established **pAUC@0.05** as the primary deployable comparison metric, under which **TCN (0.7597)** and **LSTM (0.7289)** decisively outperform the simple baseline (0.6434).
   - **Operational Distribution Shift (Notebooks 02, 03 & 08):** Formally analyzed and documented the shift in normal sensor readings between the training period (Dec 28–31) and validation period (Jan 1–2), explaining why baseline reconstruction errors on normal validation data are 45–59% higher.
   - **Temporal Concurrency (Notebooks 02 & 08):** Documented that `attack.csv` and `normal.csv` cover the same calendar dates (Dec 28 to Jan 2), confirming that the evaluation assesses concurrent discrimination rather than multi-month time-series forecasting.
   - **Local Outlier Factor (LOF) Resolution (Notebooks 06 & 08):** Diagnosed distance collapse in 42D space on 221k points (ROC-AUC = 0.4927). Implemented PCA (15 components) + representative systematic subsampling (10,000 points, stride ~22) with $k=50$ neighbors to restore meaningful density estimation.
   - **USAD Stabilization (Notebooks 07 & 08):** Diagnosed that the preliminary USAD checkpoint was saved at epoch 1 (adversarial term $\beta=0$ inactive). Stabilized the training loop with $lr = 1\times 10^{-5}$, gradient clipping at 0.1, and an eligibility constraint requiring epoch $\ge 5$ to ensure active adversarial learning.
   - **Rolling Statistical Baseline Limitation (Notebooks 04 & 08):** Documented that 60-second moving windows adapt to persistent-step attacks, driving Z-scores back to zero during attacks (ROC-AUC = 0.4711), establishing this as an inherent architectural limitation on persistent ICS attacks.

## 4. Execution Sequence for Kaggle Retraining

To rerun and retrain cleanly on Kaggle with CPU/GPU:

1. **Notebook 02 (`02_data_quality_and_temporal_split.ipynb`):**
   - Environment: Kaggle CPU / Standard.
   - Action: Validates CSV headers, missing values, duplicate segments, attack concurrency, and distribution shift.
2. **Notebook 03 (`03_exploratory_analysis.ipynb`):**
   - Environment: Kaggle CPU / Standard.
   - Action: Generates exploratory time-series plots, correlation heatmaps, and intra-normal regime drift KDEs.
3. **Notebook 04 (`04_baseline_anomaly_detection.ipynb`):**
   - Environment: Kaggle CPU / Standard.
   - Action: Computes rule-based, rolling, and simple statistical baseline scores; analyzes score quantization; exports `baseline_scores.npz`.
4. **Notebook 05 (`05_lstm_autoencoder.ipynb`):**
   - Environment: Kaggle GPU (T4 x 2 or P100).
   - Action: Fits scaler on training partition only, creates sliding windows, trains 2-layer LSTM autoencoder (100 epochs), saves `lstm_autoencoder.pth` and `evaluation_sequences.npz`.
5. **Notebook 06 (`06_traditional_ml_anomaly_detection.ipynb`):**
   - Environment: Kaggle CPU (High-memory recommended) or GPU.
   - Action: Trains Isolation Forest, SGD One-Class SVM, and corrected PCA+LOF pipeline; exports `traditional_ml_scores.npz`.
6. **Notebook 07 (`07_deep_learning_anomaly_detection.ipynb`):**
   - Environment: Kaggle GPU (T4 x 2 or P100).
   - Action: Trains TCN Autoencoder (dilated causal convolutions) and stabilized adversarial USAD; exports `tcn_autoencoder_scores.npz` and `usad_scores.npz`.
7. **Notebook 08 (`08-threshold-and-evaluation.ipynb`):**
   - Environment: Kaggle GPU (T4 x 2 or P100) / CPU.
   - Action: Performs full 9-method evaluation; calculates pAUC@0.05, Recall@1%FPR, event-level metrics; generates evaluation plots; packages all artifacts into `swat_artifacts_complete.zip` for download.

## 5. Next Steps

- Proceed with Notebook 09 (`09_error_and_event_analysis.ipynb`) for detailed per-attack scenario breakdown and physical sensor attribution.
- Proceed with Notebook 10 (`10_robustness_analysis.ipynb`) for window size and threshold sensitivity testing.