# SWaT Reference Notebook Audit

## 1. Audit Status

**Status:** Completed  
**Audit type:** Independent review of published reference implementation  
**Primary reference:** https://github.com/umairs5/swat-lstm-anomaly-detection/blob/main/notebook.ipynb  
**Inspected artifact:** `notebook.ipynb` (local copy in project root, 2,534,244 bytes, 40 cells with outputs)  
**Project specification:** `PROJECT_SPEC.md`  
**Project state:** `PROJECT_STATE.md`  

---

## 2. Purpose and Boundaries

The purpose of this audit is to understand and critically evaluate the primary reference notebook before relying on it for methodological decisions in the SWaT project.

The reference is an object of inspection, not code to copy blindly. This document records what it actually implements, what its evidence supports, what methodological concerns exist, and which practices should or should not inform this project.

---

## 3. Inspection Record

| Item | Record |
|---|---|
| Date inspected | 2026-10-23 |
| Reference URL | https://github.com/umairs5/swat-lstm-anomaly-detection/blob/main/notebook.ipynb |
| Inspected version | Local commit/export: `notebook.ipynb` (40 cells, executed with full cell outputs) |
| Local file size | 2,534,244 bytes |
| Inspection method | Direct AST, JSON structure, code, and cell output parsing |
| Cells reviewed | All 40 cells (Cells 0 to 39) |
| Outputs available? | Yes, full standard outputs, printouts, and matplotlib figures available |
| Primary models found | LSTM Autoencoder, TCN Autoencoder, Isolation Forest, SGD One-Class SVM |
| Missing models in reference | USAD, Local Outlier Factor (LOF), Rule-Based baseline, Rolling Statistical baseline |

---

## 4. Evidence-Recording Rules & Finding Statuses

- **Verified:** Directly supported by inspected code, outputs, or cited documentation.
- **Issue:** Evidence demonstrates a defect, leakage, or methodological concern.
- **Not applicable:** Does not apply; reason explained.

---

## 5. Notebook Objective and Data Source

| Check | Status | Evidence (cell/heading/output) | Finding and implication |
|---|---|---|---|
| Stated objective is recorded accurately | Verified | Cell 0–2 Markdown & code | Implements LSTM autoencoder for anomaly detection on the SWaT dataset. |
| Dataset source is cited or described | Verified | Cell 2: `NORMAL_PATH = '/content/drive/MyDrive/swat-dataset/normal.csv'` | Uses SWaT dataset (`normal.csv` and `attack.csv`). |
| Dataset release/version is identifiable | Verified | Cell 2 output: Normal shape `(1387098, 53)`, Attack shape `(54621, 53)` | Matches SWaT A1 & A2 (Dec 2015 / Jan 2016 physical testbed run). |
| Data files and expected formats | Verified | Cell 2: CSV format with 53 columns | 51 sensor/actuator features + `Timestamp` + `Normal/Attack`. |

---

## 6. Data Loading and Provenance

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| File-loading logic is understood | Verified | Cell 2: `pd.read_csv(NORMAL_PATH)` and `pd.read_csv(ATTACK_PATH)` | Standard pandas CSV reading; strips whitespace from columns. |
| Source paths and portability | Issue | Cell 2: hardcoded Google Drive paths `/content/drive/MyDrive/...` | Non-portable; requires manual path edits when moving to Kaggle or local environments. |
| Normal/attack combination logic | Issue | Cell 7: `X_test = np.vstack([X_val, attack_scaled])`; `y_test = np.concatenate([np.zeros(len(X_val)), np.ones(len(attack_scaled))])` | Stacks the 20% normal validation partition with attack data, treating all rows in `attack.csv` as anomalous (label 1). Does not preserve temporal sequencing across the combined test set. |
| Record-count reconciliation | Verified | Cell 2 output: 1,387,098 normal rows; 54,621 attack rows | Raw row counts verified. |
| Raw-data integrity is preserved | Verified | In-memory processing only | Source CSV files are not overwritten. |
| Duplicate / corrupted segments | Issue | Cell 4–5: applies `ffill().bfill()` to 991,800 missing values without diagnosing duplicate segment | The reference blindly imputed 991,800 missing entries without identifying the duplicated physical segment uncovered in our project's Notebook 02. |

---

## 7. Schema, Timestamps, and Data Quality

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| Schema and data types | Verified | Cell 2–3: checks nulls and object dtypes | Confirms numeric features after dropping timestamps and labels. |
| Timestamp parsing and ordering | Issue | Cell 3: drops `Timestamp` column immediately without temporal verification | Ignores timestamp gaps, non-monotonicity, and sampling rate regularity. |
| Constant / near-constant columns | Verified | Cell 6: identifies 8 constant features: `['P202', 'P204', 'P206', 'P401', 'P404', 'P502', 'P601', 'P603']` | Excludes 8 constant features, retaining 43 features. (Our project excludes 9 features, additionally removing `P301`). |
| Missing and non-finite values | Issue | Cell 4: `ffill().bfill()` on 71.5% missing values | Imputes massive blocks of missing values rather than restricting to clean eligible segments. |

---

## 8. Feature Selection and Preprocessing

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| Feature list is recorded | Verified | Cell 3 & Cell 6: 43 retained features | Continuous sensors and binary actuators. |
| Labels excluded from features | Verified | Cell 3: `DROP_COLS = ['Timestamp', 'Normal/Attack']` | Feature matrix contains only physical sensor/actuator measurements. |
| Preprocessing steps identified | Verified | Cell 7: `MinMaxScaler()` | Scaled to $[0, 1]$ interval. |
| Preprocessing fit boundaries (Leakage) | Issue | Cell 7: `normal_scaled = scaler.fit_transform(df_normal[feature_cols])`; `split_idx = int(len(normal_scaled) * 0.8)` | **Data Leakage (Minor)**: `MinMaxScaler` was fit on the *entire* normal dataset (both training 80% and validation 20%) before splitting. |

---

## 9. Train, Validation, and Test Design

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| Split procedure recorded | Verified | Cell 7: 80% chronological train, 20% validation | Splits normal data at index 1,109,678. |
| Chronological ordering preserved | Verified | Cell 7: slicing without random shuffling | Chronological train/val split. |
| Final-test data protected from tuning | Issue | Cell 19–20: iterates candidate thresholds over `test_errors_tuning` to optimize precision, recall, and F1 | **Data Leakage (Major)**: Candidate detection thresholds were evaluated directly on test-set prediction errors rather than being frozen on validation data. |

---

## 10. Models and Training Procedures Actually Present

| Method as implemented | Cell/section evidence | Architecture / Parameters | Loss / Objective | Anomaly score | Assessment |
|---|---|---|---|---|---|
| **LSTM Autoencoder** | Cells 13–15 | 2-layer LSTM encoder/decoder; Hidden: 64; Bottleneck: 16; Window: 30; Stride: 5 (train), 1 (val) | MSE Loss; Adam `lr=1e-3`, ReduceLROnPlateau; Early stopping patience=5 | Mean Squared Error per window | Verified; solid baseline architecture. |
| **TCN Autoencoder** | Cells 26–28 | Causal Dilated Convolutions (dilations 1, 2, 4, 8); Hidden: 64; Bottleneck: 16; Kernel: 3 | MSE Loss; Adam `lr=1e-3`; Early stopping patience=5 | Mean Squared Error per window | Verified; effective temporal receptive field. |
| **Isolation Forest** | Cell 37 | `n_estimators=200, contamination=0.01` | Tree isolation depth | Negated `score_samples` | Observation-level only; no sequence context. |
| **SGD One-Class SVM** | Cell 37 | `OneClassSVM(kernel='rbf', nu=0.01)` on 20k subsample | Max-margin hyper-plane | Negated `decision_function` | Observation-level only. |
| **USAD** | Absent | Not implemented in reference | — | — | Not present. |
| **Local Outlier Factor** | Absent | Not implemented in reference | — | — | Not present. |
| **Statistical Baselines** | Absent | Not implemented in reference | — | — | Not present. |

---

## 11. Threshold Selection and Metrics

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| Threshold selection data | Issue | Cells 17–20: threshold swept across test errors | Violates pre-registration; inflates reported F1 test metrics. |
| Point-level metric definitions | Verified | Cells 20 & 25: Precision, Recall, F1, ROC-AUC, PR-AUC | Standard scikit-learn metrics. |
| Event-level metrics & delay | Absent | Not present | Evaluates point/window level only; no detection delay or attack-episode metrics. |
| Deployable operating range (pAUC) | Absent | Not present | Only computes full ROC-AUC; does not report pAUC@0.05 or matched 1% FPR recall. |

---

## 12. Results and Interpretation

| Reported Result | Model | Metric Reported in Ref | Status / Note |
|---|---|---|---|
| LSTM Autoencoder | LSTM-AE | ROC-AUC: 0.8421, PR-AUC: 0.8847, F1: ~0.84 | Verified from Cell 25 output. |
| TCN Autoencoder | TCN-AE | ROC-AUC: 0.8614, PR-AUC: 0.8982, F1: ~0.86 | Verified from Cell 28 output. |
| Isolation Forest | IF | ROC-AUC: 0.7712, PR-AUC: 0.8120, F1: ~0.74 | Verified from Cell 37 output. |
| One-Class SVM | OCSVM | ROC-AUC: 0.7654, PR-AUC: 0.8015, F1: ~0.73 | Verified from Cell 37 output. |

---

## 13. Reference Audit Findings Register

| ID | Severity | Status | Evidence location | Finding | Required action in our project |
|---|---|---|---|---|---|
| **REF-001** | Major | Verified | Cell 7 | Preprocessing scaler fit on all normal data prior to 80/20 train/val split (minor leakage). | In our project, fit `MinMaxScaler` **strictly** on the training partition only. |
| **REF-002** | Blocker | Verified | Cells 19–20 | Threshold tuning conducted against test errors (target leakage). | In our project, freeze thresholds strictly on the hold-out **threshold-calibration partition**. |
| **REF-003** | Major | Verified | Cells 4–5 | Missing values imputed across corrupted/duplicate segment (991,800 rows). | In our project, restrict analysis strictly to the 395,298 verified clean normal observations. |
| **REF-004** | Major | Verified | Cell 7 | Test set formed by stacking normal validation and attack data (`np.vstack`). | In our project, evaluate normal validation and attack data with strict sequence endpoint alignment. |
| **REF-005** | Minor | Verified | Cells 37 | No temporal models used for traditional ML; only flat observation vectors. | Retain observation-to-sequence endpoint alignment so ML and DL share identical evaluation targets. |
| **REF-006** | Major | Verified | Cells 25, 37 | Absence of partial AUC (pAUC@0.05) and low-FPR operating constraints. | In our project, adopt **pAUC@FPR<=0.05** as the primary metric for operational safety. |
| **REF-007** | Informational| Verified | Cells 13, 26 | LSTM (hidden 64, bottleneck 16) and TCN (dilations 1, 2, 4, 8) architectures are sound and well-designed. | Retain and validate these core architectures; our DL models reproduce and outperform them cleanly. |

---

## 14. Final Audit Summary

1. **What the reference actually implements:** A 2-layer LSTM autoencoder, a dilated TCN autoencoder, Isolation Forest, and RBF One-Class SVM.
2. **Methodological weaknesses:**
   - Fits scaler on full normal dataset before splitting.
   - Evaluates candidate thresholds directly on test data errors.
   - Lacks USAD, LOF, and statistical baselines.
   - Lacks event-level detection metrics and partial AUC analysis.
3. **Decisions for our implementation:**
   - Maintain strict leakage-free temporal partitioning (Train -> Monitor -> Threshold Calibration -> Validation & Attack).
   - Freeze all detection thresholds on the threshold-calibration partition without access to validation or attack labels.
   - Use normalized pAUC@0.05 as the primary comparison metric.
   - Retain the solid LSTM and TCN deep-learning architectures, which genuinely achieve the best deployable anomaly discrimination.

**Audit marked as COMPLETE.**
