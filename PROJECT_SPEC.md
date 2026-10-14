# SWaT Industrial Anomaly Detection Project

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Purpose and Objectives](#2-project-purpose-and-objectives)
3. [Research Questions](#3-research-questions)
4. [Dataset Provenance and Industrial Context](#4-dataset-provenance-and-industrial-context)
5. [Primary Reference Notebook](#5-primary-reference-notebook)
6. [The Nine Selected Detection Methods](#6-the-nine-selected-detection-methods)
7. [Fixed Twelve-Notebook Workflow](#7-fixed-twelve-notebook-workflow)
8. [Industrial, Mathematical, and Statistical Foundations](#8-industrial-mathematical-and-statistical-foundations)
9. [Data Quality and Temporal Evaluation](#9-data-quality-and-temporal-evaluation)
10. [Exploratory Data Analysis](#10-exploratory-data-analysis)
11. [Baseline Methodology](#11-baseline-methodology)
12. [Traditional Machine-Learning Methodology](#12-traditional-machine-learning-methodology)
13. [Deep-Learning Methodology](#13-deep-learning-methodology)
14. [Threshold Selection and Evaluation](#14-threshold-selection-and-evaluation)
15. [Error, Event, and Robustness Analysis](#15-error-event-and-robustness-analysis)
16. [Final Model Selection](#16-final-model-selection)
17. [Reproducibility and Repository Standards](#17-reproducibility-and-repository-standards)
18. [Project-State and Progress Tracking](#18-project-state-and-progress-tracking)
19. [Collaboration and Execution Protocol](#19-collaboration-and-execution-protocol)
20. [Final Deliverables](#20-final-deliverables)
21. [Definition of Success](#21-definition-of-success)

---

## 1. Project Overview

This project is a rigorous, reproducible, and technically defensible anomaly-detection study that uses the Secure Water Treatment (SWaT) industrial control-system dataset.

The work is both a structured learning exercise and a research-oriented portfolio project. Its emphasis is on:

- Understanding the industrial water-treatment process.
- Validating dataset provenance, structure, and quality.
- Applying appropriate statistical and machine-learning methods.
- Evaluating those methods under a leakage-safe temporal design.
- Explaining the relevant mathematics and industrial reasoning.
- Investigating errors, missed events, and robustness.
- Drawing conclusions that are supported only by verified evidence.

The project is **not** a completed industrial deployment. No model is claimed to have achieved a particular performance level until verified experimental results have been obtained and reviewed.

The project progresses through a fixed sequence of twelve notebooks. Work advances one stage at a time. Modelling does not begin until the reference audit, dataset verification, data-quality assessment, and exploratory analysis have supplied the necessary evidence.

---

## 2. Project Purpose and Objectives

### Purpose

Develop a transparent experimental pipeline that:

1. Inspects a published reference implementation critically.
2. Establishes the identity and limitations of the SWaT data actually available.
3. Implements nine carefully selected anomaly-detection methods.
4. Evaluates all methods under a common, temporally valid protocol.
5. Documents trade-offs honestly so that another practitioner can understand, reproduce, and extend the work.

### Primary Objectives

1. **Audit the primary reference notebook** before building our own pipeline. The sole primary reference is  
   [`https://github.com/umairs5/swat-lstm-anomaly-detection/blob/main/notebook.ipynb`](https://github.com/umairs5/swat-lstm-anomaly-detection/blob/main/notebook.ipynb).  
   Treat it as an object of critical inspection, not as code to copy blindly.

2. **Establish dataset provenance and identity.** Determine the source, version (if identifiable), collection period, experimental setup, file layout, sampling cadence, label semantics, and any discrepancies with official documentation.

3. **Understand the industrial process.** Learn the water-treatment stages, sensors, actuators, control loops, normal process transitions, and the distinction between an anomalous observation and evidence of a cyberattack or physical fault.

4. **Validate data quality and temporal structure.** Check schemas, timestamps, ordering, sampling intervals, gaps, missing values, duplicates, constant variables, and label distributions. Preserve the meaning of the original observations.

5. **Perform grounded exploratory analysis.** Use descriptive statistics and visualisations that answer concrete questions about process behaviour, data quality, and detection feasibility.

6. **Implement nine anomaly-detection methods** organised into three equal categories (baseline, traditional machine learning, deep learning). Do not assume that more complex methods will outperform simpler ones.

7. **Evaluate models fairly.** Use chronological partitions, prevent leakage, select thresholds without final-test labels, and report both point-level and event-level metrics.

8. **Investigate errors and robustness.** Examine false positives, false negatives, missed events, detection delays, threshold sensitivity, and stability under reasonable methodological changes.

9. **Select a final approach on evidence.** Consider performance, false-alarm burden, detection delay, interpretability, computational cost, and known limitations. Complexity alone is not a selection criterion.

10. **Deliver a reproducible portfolio project.** Provide ordered notebooks, documented assumptions, portable paths, recorded configurations, honest limitations, and a clear statement of what the evidence does and does not support.

### Scope and Working Principles

- Progress **one notebook stage at a time**.
- Inspect and understand existing code before changing it.
- Prefer a small, justified next step over premature complexity.
- Do not invent results, process limits, dataset properties, or conclusions.
- Do not treat code that merely executes as evidence that a stage is complete.
- Keep observed results, interpretations, conclusions, and limitations distinct.
- Preserve chronological order; never randomly shuffle time-series rows for the main evaluation.
- Fit learned preprocessing only on permitted training data.
- Never use final-test labels for model selection, hyperparameter tuning, or threshold selection.
- Do not automatically equate a labelled anomaly with a confirmed cyberattack.
- Do not introduce production infrastructure, APIs, or streaming systems unless explicitly authorised later.
- Keep paths portable and notebooks suitable for independent review.

---

## 3. Research Questions

The project is organised around the following questions. Answers must be grounded in verified data and experimental results.

1. What is the precise identity, provenance, and structure of the SWaT data available to us?
2. How should the data be partitioned chronologically so that training, threshold calibration, and final evaluation remain free of leakage?
3. Which simple, interpretable detectors provide a useful performance baseline on this data?
4. How do Isolation Forest, One-Class SVM, and Local Outlier Factor compare with the baselines under the same temporal protocol?
5. How do LSTM Autoencoder, TCN Autoencoder, and USAD compare with both the baselines and the traditional machine-learning methods?
6. What trade-offs exist between point-level scores, event-level detection, false-alarm rate, and detection delay?
7. Which failure modes (false positives during normal transitions, missed events, delayed detections) dominate each method?
8. How sensitive are the results to reasonable changes in window length, threshold, scaling, and missing-data handling?
9. Which single approach (or combination of approaches) offers the most defensible operational trade-off for the verified data, and under what limitations?

---

## 4. Dataset Provenance and Industrial Context

### Provisional Data and Official Sources

The project may initially use a provisionally obtained Kaggle copy while official access is pending. Treat any third-party copy as provisional until its correspondence to a documented SWaT release has been verified.

Authoritative resources that must be consulted:

- Dataset characteristics: https://www.sutd.edu.sg/itrust/itrust-labs/datasets/dataset-characteristics/swat/
- Dataset request process: https://www.sutd.edu.sg/itrust/request-for-datasets/
- Terms of usage: https://www.sutd.edu.sg/itrust/itrust-labs/datasets/terms-of-usage/
- iTrust dataset portal: https://www.sutd.edu.sg/itrust/itrust-labs/datasets/
- CI-AI Challenge 2024 data resources: https://itrust.sutd.edu.sg/ci-ai-challenge-2024/resources/data/

Dataset releases and experimental setups can differ. Characteristics of one version must not be assumed for another.

### Required Verification Items

For every local file the following must be recorded and checked against documentation where possible:

- Source and acquisition method.
- Identifiable version or release.
- Collection period and experimental context.
- File names, sizes, row counts, and column counts.
- Timestamp format and any documented timezone.
- Sampling cadence and temporal continuity (gaps, duplicates, ordering).
- Sensor and actuator identifiers and their documented meanings.
- Label definitions and alignment with observations.
- Differences between separate normal/attack files and any merged file.
- Differences between the local copy, the reference notebook, and official documentation.
- Applicable usage restrictions.

Do not assume that filenames such as `normal.csv` or `attack.csv` alone establish version, chronology, or correct evaluation procedure.

### Industrial Process Context

SWaT is a scaled-down water-treatment testbed. Typical process stages include:

- P1 – Raw-water intake
- P2 – Chemical dosing / pre-treatment
- P3 – Ultrafiltration
- P4 – Dechlorination
- P5 – Reverse osmosis
- P6 – Backwash / clean-in-place

Sensors measure flow, level, pressure, and water-quality indicators; actuators control pumps, valves, and chemical dosing. Normal operation contains intentional process transitions (tank filling/emptying, filter backwash, pump cycling). An anomalous observation is therefore not automatically evidence of a cyberattack or a specific physical failure. The project must keep this distinction explicit.

---

## 5. Primary Reference Notebook

**Sole primary reference**  
https://github.com/umairs5/swat-lstm-anomaly-detection/blob/main/notebook.ipynb

No other repository may be mixed into the primary audit. Secondary literature may be consulted for methodological ideas, but findings must be clearly labelled as external.

### Known Content (Subject to Verification)

From earlier discussion the notebook is expected to contain implementations of:

- Isolation Forest
- One-Class SVM
- LSTM Autoencoder
- TCN Autoencoder

This expectation does **not** constitute proof that every cell has been audited or that these are the only methods present. The actual notebook must be inspected.

The five methods that belong to our nine-method plan but are **not** assumed to exist in the reference are:

- Rule-Based Detection
- Rolling Statistical Detection
- Simple Statistical Threshold
- Local Outlier Factor (LOF)
- USAD

### Mandatory Audit Checklist

The audit must establish, with evidence from the notebook itself:

1. Stated objective and any cited dataset source.
2. Expected filenames and hardcoded paths.
3. How normal and attack data are loaded and combined.
4. Timestamp parsing, sorting, and sampling-interval checks.
5. Handling of missing values, duplicates, and constant columns.
6. Feature selection and numerical conversion.
7. Preprocessing and scaling (and whether fitted on training data only).
8. Definition of training, validation, and test periods.
9. Presence or absence of temporal or label leakage.
10. Exact models implemented and their architectures/hyperparameters.
11. Sequence/window construction and stride.
12. Loss functions and training objectives.
13. Anomaly-score calculation.
14. Threshold-selection procedure and whether labels are used.
15. Evaluation metrics (point-level vs event-level).
16. Assessment of false alarms, missed events, and detection delay.
17. Presentation and interpretation of results.
18. Justified choices, questionable choices, and missing requirements.
19. Methods or evaluation practices that our project must develop independently.

Verified facts must be separated from unanswered questions. No performance number reported by the reference may be treated as reproducible until its data, split, threshold, and metric definitions have been checked.

---

## 6. The Nine Selected Detection Methods

The project contains **exactly nine** methods, three in each category. No method may be replaced without explicit authorisation.

### Summary Table

| Category | Method | Detection Principle | Intended Role | Current Status |
|----------|--------|---------------------|---------------|----------------|
| A. Baseline | Rule-Based Detection | Documented process rules or justified empirical bounds | Interpretable operational reference | Selected for the project |
| A. Baseline | Rolling Statistical Detection | Deviation from recent historical behaviour (causal rolling statistics) | Captures local temporal context | Selected for the project |
| A. Baseline | Simple Statistical Threshold | Fixed statistical threshold on a chosen score | Global distributional baseline | Selected for the project |
| B. Traditional ML | Isolation Forest | Isolation-based (path length in random trees) | Global multivariate outlier detection | Documented in reference (subject to audit) |
| B. Traditional ML | One-Class SVM | Boundary-based (hypersphere / hyperplane in feature space) | Support-vector description of normality | Documented in reference (subject to audit) |
| B. Traditional ML | Local Outlier Factor (LOF) | Local-density deviation relative to neighbours | Local density-based novelty detection | Selected for the project |
| C. Deep Learning | LSTM Autoencoder | Recurrent sequence reconstruction | Temporal dependence via recurrence | Documented in reference (subject to audit) |
| C. Deep Learning | TCN Autoencoder | Causal dilated convolutional sequence reconstruction | Temporal dependence via convolution | Documented in reference (subject to audit) |
| C. Deep Learning | USAD | Dual-autoencoder adversarial reconstruction | Alternative reconstruction objective | Selected for the project |

Status vocabulary used above:

- **Selected for the project** – required by the plan; not yet implemented or audited.
- **Documented in reference** – appears in the reference notebook; still requires full audit.
- **Audited** – reference implementation has been inspected and findings recorded.
- **Implemented** – code exists in our notebooks.
- **Experimentally evaluated** – metrics obtained under the project protocol.
- **Completed and verified** – results reviewed and accepted.

Only evidence-supported statuses may be marked complete.

### Category A – Baseline Anomaly Detection

**1. Rule-Based Detection**  
Uses documented process rules, justified operating bounds, or evidence-based conditions.  
Where certified engineering limits are unavailable, any bounds derived from training data must be labelled **empirical reference limits**, never certified safety limits. Do not invent physical safety thresholds.

**2. Rolling Statistical Detection**  
Scores each observation relative to a causal historical window. Candidate techniques include rolling Z-score, rolling median + MAD, EWMA, or CUSUM. The concrete choice must be justified after data inspection. The reference window, warm-up period, score aggregation, and zero-variance handling must be defined explicitly. Future values must never enter the statistic used to score time \(t\).

**3. Simple Statistical Threshold**  
Applies a single, pre-defined statistical threshold (for example a high quantile of a global score computed on normal training data) to an appropriate univariate or multivariate statistic. It is deliberately distinct from the rolling detector: it does not maintain a moving historical context.

The three baselines must not collapse into three variants of the same Z-score implementation.

### Category B – Traditional Machine Learning

**1. Isolation Forest**  
Isolates observations by random recursive partitioning. Anomalies tend to require fewer splits and therefore receive shorter average path lengths. Training is normally performed on normal data only.

**2. One-Class SVM**  
Learns a boundary that encloses the training distribution (typically normal data). Observations lying outside the boundary are scored as anomalous. Performance is sensitive to scaling, kernel choice, and the parameter \(\nu\).

**3. Local Outlier Factor (LOF)**  
Measures the local density of an observation relative to its \(k\) nearest neighbours. An observation whose density is substantially lower than that of its neighbours receives a high LOF score.  

**Critical distinction for LOF**  
- *Outlier detection mode* identifies outliers **inside** the fitted dataset.  
- *Novelty detection mode* scores previously unseen observations after the model has been fitted on training data.  

The project must use novelty detection when scoring validation and test periods. LOF’s computational cost on large multivariate series must be benchmarked; it must not be assumed to scale without evidence.

Gaussian Mixture Models (GMM) are **not** part of the required nine-method set.

### Category C – Deep Learning

**1. LSTM Autoencoder**  
Encodes a temporal window with an LSTM, compresses it to a bottleneck, and reconstructs the window with a second LSTM. Anomaly score is typically the reconstruction error (MSE or MAE) of the window or of its last time step.

**2. TCN Autoencoder**  
Replaces recurrence with stacked causal dilated convolutions. The receptive field grows exponentially with depth while remaining strictly causal. Reconstruction error again serves as the anomaly score.

**3. USAD (UnSupervised Anomaly Detection)**  
Employs two autoencoders trained with an adversarial objective: one autoencoder reconstructs the input; the second autoencoder is trained to distinguish original from reconstructed inputs. The combined reconstruction and adversarial losses yield the anomaly score. USAD therefore supplies a reconstruction-based method whose training dynamics differ from a standard autoencoder.

No claim of superiority among the three deep-learning models is permitted before experiments are completed.

---

## 7. Fixed Twelve-Notebook Workflow

The project retains the original ten-stage intent and expands it to twelve notebooks so that each method group receives a dedicated implementation stage. The notebooks must appear in exactly this order; they may not be renamed, reordered, merged, or removed.

| # | Notebook | Purpose |
|---|----------|---------|
| 1 | `01_data_and_process_understanding` | Industrial context, process variables, dataset purpose, limits of inference |
| 2 | `02_data_quality_and_temporal_split` | Provenance, schema, timestamps, quality checks, chronological partitions |
| 3 | `03_exploratory_analysis` | Distributions, temporal behaviour, relationships, normal vs attack periods |
| 4 | `04_baseline_anomaly_detection` | Rule-Based, Rolling Statistical, Simple Statistical Threshold |
| 5 | `05_lstm_autoencoder` | Dedicated LSTM Autoencoder experiment |
| 6 | `06_traditional_ml_anomaly_detection` | Isolation Forest, One-Class SVM, LOF |
| 7 | `07_deep_learning_anomaly_detection` | TCN Autoencoder and USAD |
| 8 | `08_threshold_and_evaluation` | Unified threshold protocol and metrics for all nine methods |
| 9 | `09_error_and_event_analysis` | False positives/negatives, missed events, detection delay |
| 10 | `10_robustness_analysis` | Sensitivity to parameters, missing data, operating regimes |
| 11 | `11_final_model` | Evidence-based selection and trade-off discussion |
| 12 | `12_reproducibility` | Environment, seeds, paths, execution order, known limitations |

### Stage-Gating Rule

Work advances one notebook at a time. Modelling stages (04–07) may not begin until the reference audit, dataset verification, data-quality assessment, and EDA have produced the necessary evidence.

At the end of every notebook the following must be recorded:

- What was investigated.
- What was actually completed.
- Verified findings.
- Outstanding questions.
- Known limitations.
- Next required action.
- Conditions that must be satisfied before the subsequent notebook may start.

### Notebook Responsibilities in Detail

**01_data_and_process_understanding**  
Document water-treatment stages, sensors, actuators, control loops, normal transitions, and the distinction between anomalous observations and confirmed attacks or faults. Establish what can and cannot be inferred from the data.

**02_data_quality_and_temporal_split**  
Inventory files, verify schemas, parse timestamps, check ordering, sampling cadence, gaps, duplicates, missing values, constant columns, and label semantics. Define chronological training / validation / test partitions **after** the data structure is understood. Fit any learned preprocessing exclusively on the training partition. Document partition dates, sizes, and label composition.

**03_exploratory_analysis**  
Produce tables and figures that answer concrete questions about size, distributions, missingness, temporal behaviour, sensor relationships, operating regimes, and differences between normal and attack-labelled periods. Do not infer causation from correlation.

**04_baseline_anomaly_detection**  
Implement the three baseline methods in clearly separated sections. For each method record assumptions, mathematical formulation (where applicable), parameters, score definition, threshold procedure, limitations, and preliminary observations.

**05_lstm_autoencoder**  
Implement the LSTM Autoencoder as a self-contained experiment: sequence construction, architecture, loss, training loop, reconstruction-error definition, and validation behaviour. Final-test data remain untouched.

**06_traditional_ml_anomaly_detection**  
Implement Isolation Forest, One-Class SVM, and LOF. Apply identical leakage-safe preprocessing. Document differences in training assumptions, score orientation, computational cost, and limitations. Use LOF in novelty-detection mode.

**07_deep_learning_anomaly_detection**  
Implement TCN Autoencoder and USAD. Explain architectures, objectives, sequence inputs, training procedures, anomaly scores, hyperparameters, and computational cost. This notebook supplements, and does not replace, notebook 05.

**08_threshold_and_evaluation**  
Define a single evaluation protocol applied to all nine methods. Cover score orientation, threshold selection on permitted data only, point-level metrics (precision, recall, F1, PR-AUC), event-level metrics (event recall, detection delay, false alarms per unit time), alert-grouping rules, and the limitations of each metric. Never optimise thresholds on final-test labels.

**09_error_and_event_analysis**  
Compare false positives, false negatives, missed events, event coverage, and detection delays across methods. Examine concentration of errors by variable, time period, or operating condition. Separate observed patterns from causal hypotheses.

**10_robustness_analysis**  
Test sensitivity to window length, threshold, scaling, missing-data handling, and other justified factors. Document experimental design, quantities varied, results, and limitations. Untested properties must not be presented as findings.

**11_final_model**  
Compare all nine methods on the documented metrics. Select the preferred approach (or combination) on the basis of point-level performance, event-level behaviour, false-alarm burden, detection delay, robustness, interpretability, computational cost, and industrial relevance. Record remaining trade-offs. If the evidence does not identify a single winner, state that fact.

**12_reproducibility**  
Provide environment specification, dependency list, portable path handling, recorded configurations, random seeds, split definitions, threshold settings, notebook execution order, artefact layout, and known reproduction caveats. Personal-machine paths are forbidden.

---

## 8. Industrial, Mathematical, and Statistical Foundations

Theory is introduced in Markdown cells at the moment it becomes relevant to the analysis being performed. Equations must define every symbol and state the practical implication for the experiment.

### Industrial Process Understanding

- Water-treatment stages and their inter-dependencies.
- Sensor measurements versus actuator states.
- Control loops and feedback.
- Intentional process transitions versus abnormal conditions.
- Distinction between an anomalous observation and evidence of a cyberattack or physical failure.

### Time-Series Analysis

- Temporal ordering and sampling cadence.
- Autocorrelation and temporal dependence.
- Non-stationarity and operating regimes.
- Risks of random splitting.

### Statistical Foundations

- Mean, variance, standard deviation, empirical distributions.
- Robust statistics (median, MAD).
- Standardisation and robust scaling (fitted on training data only).
- Rolling statistics, Z-scores, EWMA, CUSUM.
- Threshold selection and the assumptions that underlie it.

### Traditional Machine Learning

- Isolation Forest: path-length anomaly score, contamination parameter.
- One-Class SVM: kernel, \(\nu\), margin geometry.
- LOF: local reachability density, novelty versus outlier mode.

### Deep Learning

- LSTM recurrence and sequence reconstruction.
- Causal and dilated convolutions in TCNs.
- Autoencoder bottleneck and reconstruction loss.
- USAD dual-autoencoder adversarial objective.
- Window construction, stride, and boundary handling.
- Conversion of reconstruction error into a comparable anomaly score.

### Evaluation Theory

- Confusion matrix, precision, recall, F1.
- Precision–recall curves and PR-AUC.
- False-positive rate and false alarms per unit time.
- Event-level recall and detection delay.
- Point-level versus event-level metrics.
- Class imbalance.
- Temporal validation and leakage.
- Threshold sensitivity and uncertainty.

Only the theory required by the current notebook is presented; unrelated mathematics is omitted.

---

## 9. Data Quality and Temporal Evaluation

### Mandatory Checks

- Schema and data types.
- Timestamp parsing and chronological ordering.
- Duplicate timestamps and duplicate observations.
- Sampling intervals and gaps.
- Missing values and infinite values.
- Constant and near-constant variables.
- Label distribution and semantics.
- File overlap and temporal continuity.
- Sensor/actuator identification.
- Potentially invalid measurements.

Extreme values are not removed automatically; they may themselves be anomalies.

### Temporal Split Design

The final split strategy is chosen only after the dataset has been verified. Requirements:

- Strictly chronological partitions.
- Training data for fitting models and learned preprocessing.
- Validation data for model selection and threshold calibration (preferablyally normal-only).
- A final test period reserved exclusively for unbiased evaluation.
- Documentation of each partition’s date range, size, and label composition.
- No random shuffling of time-series observations.
- No use of final-test labels for any selection decision.

If a clean normal-only training/validation design is impossible, the limitation is documented and the least-misleading alternative is justified.

### Leakage Prevention

Explicitly forbidden:

- Scaling fitted on the whole series.
- Rolling statistics that incorporate future observations.
- Overlapping windows that cross partition boundaries.
- Labels or attack metadata inside the feature matrix.
- Future information used for imputation.
- Threshold optimisation on final-test labels.
- Repeated model selection against the test set.

For online-style detection the score at time \(t\) may use only information available at prediction time.

---

## 10. Exploratory Data Analysis

EDA must answer concrete questions about data quality, process behaviour, and detection feasibility. Typical examinations (adapted to the verified schema) include:

- Dataset size, columns, data types, label distribution.
- Timestamp continuity, sampling intervals, gaps, ordering.
- Missing values, duplicates, constant columns, suspicious patterns.
- Sensor and actuator distributions and their evolution over time.
- Behaviour during normal versus attack-labelled periods, respecting chronology and operating regimes.
- Relationships among process variables, including possible lagged relationships.
- Whether individual variables or combinations supply useful anomaly evidence.
- Patterns that reflect ordinary process transitions rather than faults or attacks.

Every claim must be tied to a table, statistic, plot, or reproducible result. Causation is never inferred from correlation alone.

---

## 11. Baseline Methodology

Each baseline receives its own section inside notebook 04.

### Rule-Based Detection

- Source of rules (documentation or empirical training quantiles).
- Explicit statement that empirical bounds are not certified engineering limits.
- Feature set and logical conditions.
- Binary decision rule.
- Strengths (interpretability) and limitations (brittleness to unmodelled regimes).

### Rolling Statistical Detection

- Choice of statistic (Z-score, MAD, EWMA, CUSUM, \ldots) and justification.
- Reference-window length and warm-up period.
- Causal computation (no future leakage).
- Score aggregation across variables if multivariate.
- Handling of zero-variance windows.
- Threshold procedure.
- Computational cost and limitations.

### Simple Statistical Threshold

- Definition of the global score (e.g., Mahalanobis distance, max absolute Z-score, \ldots).
- Derivation of the threshold from normal training data only.
- Clear differentiation from the rolling method.
- Output interpretation and limitations.

For all three baselines the following are recorded: features, assumptions, parameters, score/rule definitions, threshold selection, output interpretation, limitations, computational cost, and evaluation results under the common protocol.

---

## 12. Traditional Machine-Learning Methodology

Each method is implemented in notebook 06 with a dedicated subsection.

### Isolation Forest

- Objective and isolation principle.
- Input representation (typically flattened windows or raw feature vectors).
- Scaling requirements.
- Training on normal data.
- Key hyperparameters (`n_estimators`, `max_samples`, `contamination`).
- Anomaly-score orientation (usually negative path length or decision function).
- Conversion to binary alerts.
- Computational profile and limitations on high-dimensional series.

### One-Class SVM

- Boundary-learning objective.
- Kernel choice and \(\nu\) parameter.
- Mandatory feature scaling.
- Training-data requirements.
- Score orientation (distance to the learned boundary).
- Threshold selection.
- Computational constraints (especially for large training sets).
- Sensitivity to hyperparameters and scaling.

### Local Outlier Factor (LOF)

- Local density deviation principle.
- Distinction between outlier-detection mode and novelty-detection mode.
- Mandatory use of novelty detection for unseen validation/test data.
- Neighbourhood size \(k\) and its effect.
- Scaling considerations.
- Score orientation.
- Computational cost on large multivariate series; benchmarking required.
- Limitations for industrial time series (curse of dimensionality, sensitivity to \(k\)).

No method may receive attack labels as features. Thresholds are selected exclusively on permitted training/validation information.

---

## 13. Deep-Learning Methodology

### LSTM Autoencoder (notebook 05)

- Input sequence shape \((T, F)\), sequence length, stride.
- Feature scaling fitted on training data only.
- Encoder/decoder architecture, hidden size, number of layers, bottleneck dimension.
- Reconstruction loss (MSE or MAE).
- Optimiser, learning-rate schedule, early stopping, gradient clipping.
- Random seeds.
- Training and validation procedure.
- Reconstruction-error definition (per-window or per-timestep).
- Threshold selection on validation reconstruction errors.
- Boundary handling so that sequences never cross partition borders.
- Computational cost and limitations.

### TCN Autoencoder (notebook 07)

- Causal dilated convolutions and receptive-field calculation.
- Number of residual blocks, kernel size, dilation schedule.
- Bottleneck and reconstruction pathway.
- Same sequence-construction and leakage rules as the LSTM model.
- Training objective and anomaly-score definition.
- Hyperparameters, computational cost, and limitations relative to recurrence.

### USAD (notebook 07)

- Dual-autoencoder architecture.
- Adversarial training objective (reconstruction + discrimination).
- How the two losses are combined into an anomaly score.
- Sequence construction identical to the other deep models for fairness.
- Training procedure, hyperparameters, and computational cost.
- Limitations and differences from a standard autoencoder.

All three deep models produce comparable anomaly scores under a unified threshold and evaluation protocol. Reconstruction losses alone are not used for ranking because objectives and score distributions differ.

---

## 14. Threshold Selection and Evaluation

### Concepts

- **Anomaly score** – continuous value produced by a detector.
- **Threshold** – cut-off that converts the score into a binary alert.
- **Binary prediction** – the alert sequence.
- **Ground-truth label** – the reference annotation.

Thresholds are selected using only permitted training/validation information. Final-test labels are never used for threshold optimisation.

### Unified Protocol (notebook 08)

Applied to all nine methods wherever method differences permit:

- Score-orientation normalisation (higher score = more anomalous).
- Threshold derivation (e.g., high quantile of normal validation scores, or a target false-positive budget).
- Point-level metrics: precision, recall, F1, PR-AUC, confusion matrix.
- Explanation of why accuracy alone is inadequate under class imbalance.
- Event-level metrics:
  - Definition of an annotated event.
  - Alert-grouping rule (minimum duration, merging of consecutive alerts).
  - Matching of predicted alerts to annotated events.
  - Event recall / event coverage.
  - Detection delay (time from event start to first correct alert).
  - False alarms per unit time.
- Computational cost (training time, inference time, memory).
- Threshold-sensitivity analysis.

Point-adjustment or other non-standard evaluation procedures, if considered at all, must be defined explicitly, justified, and reported separately from the main results. Fabricated numbers are never inserted into result tables.

---

## 15. Error, Event, and Robustness Analysis

### Error and Event Analysis (notebook 09)

- False positives during normal process transitions.
- False negatives and completely missed events.
- Detection delay distributions.
- Performance broken down by available attack scenarios or event categories.
- Concentration of errors on particular variables or time periods.
- Distinction between observed patterns and causal hypotheses.

### Robustness Analysis (notebook 10)

- Sensitivity to sequence length / rolling-window length.
- Sensitivity to threshold.
- Effect of alternative scaling methods.
- Behaviour under controlled missingness (original data preserved; corruption procedure, affected variables, severity, and seeds documented).
- Stability across operating regimes.
- Computational cost under different configurations.
- Reproducibility of results under fixed seeds.

A distributional change is not automatically labelled an attack. Untested robustness claims are forbidden.

---

## 16. Final Model Selection

Selection occurs only after notebooks 04–10 are complete. Criteria include:

- Point-level performance on the untouched test period.
- Event-level detection and detection delay.
- False-alarm burden.
- Threshold stability.
- Sensitivity to preprocessing choices.
- Computational cost.
- Interpretability.
- Reproducibility.
- Industrial relevance.
- Known limitations.

The most complex model is not automatically preferred. If a simpler method yields a better operational trade-off, that conclusion is stated honestly. Remaining trade-offs and limitations are documented. If the evidence does not identify a single winner, the document says so.

---

## 17. Reproducibility and Repository Standards

- Portable, project-relative paths or robust path discovery; no personal-machine or transient cloud paths in committed code.
- Documented dependencies and environment specification.
- Recorded configurations, split boundaries, thresholds, and model settings.
- Random seeds where applicable (with the caveat that seeds do not guarantee bit-identical results across every platform).
- Clear separation of raw data, derived data, models, and results.
- Notebooks that execute in order from a clean kernel, subject to documented data availability.
- Compliance with dataset terms of use; no restricted data or credentials committed.
- Clear figures, tables, and descriptive captions.
- Attribution of the dataset provider and observance of any required publication notifications.

Production infrastructure, Docker services, or streaming pipelines are out of scope unless later authorised.

---

## 18. Project-State and Progress Tracking

### Progress Table

| Notebook | Objective | Status | Completion Evidence | Outstanding Work | Next Action |
|----------|-----------|--------|---------------------|------------------|-------------|
| 01_data_and_process_understanding | Industrial context & process variables | Not yet verified | — | — | Begin reference-notebook audit and process documentation |
| 02_data_quality_and_temporal_split | Provenance, quality, chronological splits | Not yet verified | — | — | — |
| 03_exploratory_analysis | EDA grounded in industrial & statistical reasoning | Not yet verified | — | — | — |
| 04_baseline_anomaly_detection | Three baseline methods | Not yet verified | — | — | — |
| 05_lstm_autoencoder | LSTM Autoencoder experiment | Not yet verified | — | — | — |
| 06_traditional_ml_anomaly_detection | Isolation Forest, OCSVM, LOF | Not yet verified | — | — | — |
| 07_deep_learning_anomaly_detection | TCN Autoencoder & USAD | Not yet verified | — | — | — |
| 08_threshold_and_evaluation | Unified protocol for all nine methods | Not yet verified | — | — | — |
| 09_error_and_event_analysis | Error & event analysis | Not yet verified | — | — | — |
| 10_robustness_analysis | Sensitivity & robustness | Not yet verified | — | — | — |
| 11_final_model | Evidence-based selection | Not yet verified | — | — | — |
| 12_reproducibility | Reproducibility record | Not yet verified | — | — | — |

Status vocabulary: **Not started**, **In progress**, **Awaiting review**, **Completed and verified**, **Blocked**, **Not yet verified**.

A stage is marked complete only when concrete evidence (executed code, reviewed outputs, recorded findings) supports that claim.

### Project-State Record Template

At the close of every notebook the following concise record is written:

1. Current notebook  
2. Current stage  
3. Objective  
4. Actions completed  
5. Commands or code executed  
6. Actual outputs reviewed  
7. Verified findings  
8. Decisions made and their rationale  
9. Unresolved questions  
10. Known limitations  
11. Next action  
12. Conditions required before the next stage may begin  

Work always resumes from the recorded current stage. Completed work is not repeated unnecessarily; unresolved dependencies are not skipped.

---

## 19. Collaboration and Execution Protocol

The working process is strictly incremental:

1. Inspect the current project files and the primary reference notebook.  
2. Explain the relevant code and methodology.  
3. Identify potential errors, assumptions, and leakage risks.  
4. Agree on the next small action.  
5. Run only the necessary code.  
6. Review the actual output.  
7. Interpret the evidence.  
8. Record verified conclusions and outstanding questions.  
9. Update the project-state record.  
10. Proceed only when the current stage is sufficiently complete.

Rules:

- Never fabricate output or claim that code has been executed when it has not.  
- Never silently alter the nine-method selection, the twelve-notebook workflow, or previously agreed decisions.  
- If a change is genuinely required, explain the reason, identify the impact, and obtain explicit authorisation before modifying the plan.  
- Prefer clarity and correctness over unnecessary complexity.

---

## 20. Final Deliverables

By the end of the project the repository must contain:

- A documented audit of the primary reference notebook.  
- A defensible account of dataset provenance, version uncertainty, structure, and limitations.  
- The twelve notebooks in the fixed order, each with its project-state record.  
- Reproducible data-quality checks and chronological split definitions.  
- Evidence-based exploratory analysis with industrial context.  
- Implementations of all nine selected methods.  
- A unified, leakage-safe threshold and evaluation protocol.  
- Point-level and event-level results for every method.  
- Error, event, and robustness analyses.  
- An evidence-based final-model selection with explicit trade-offs.  
- A reproducibility record (environment, seeds, paths, configurations).  
- A concise final summary of findings, limitations, and the statements that the evidence does and does not support.

---

## 21. Definition of Success

The project succeeds when:

- Every conclusion is traceable to verified data and reproducible experimental results.  
- Methods respect temporal structure and avoid leakage.  
- Mathematical and industrial reasoning is explained at the point of use.  
- Evaluation includes false-alarm behaviour and event-level metrics, not accuracy alone.  
- Limitations are stated explicitly.  
- Another practitioner can open the repository, understand the current state, and continue the work without guessing.

The objective is **not** to prove in advance that any particular model (LSTM Autoencoder, TCN, USAD, or otherwise) is best. The objective is to determine, through a transparent and technically sound investigation, which approaches are useful for the verified SWaT data and under what limitations.

---

*End of project specification.*