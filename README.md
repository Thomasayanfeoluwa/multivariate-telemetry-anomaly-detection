# SWaT Industrial Anomaly Detection

An experimental study of anomaly detection on multivariate telemetry from the Secure Water Treatment (SWaT) testbed. The project compares nine detection methods, evaluates false alarms and event detection, and selects a model from recorded evidence.

> **Project status:** the 12-notebook research and reproducibility workflow is complete. The next step is Notebook 13, a feasibility test that replays historical SWaT data through the frozen TCN. FastAPI and React are later steps only if replay validates; no live-plant integration or production deployment has been completed.

## What the project asks

Can a detector identify unusual patterns in the available SWaT observations while keeping missed events, false alarms, and detection delay visible to a human reviewer?

The intended eventual use is a **human-reviewed monitoring aid**: display a timestamped anomaly score and relevant telemetry so an operator can investigate. An alert is not proof of an attack, equipment failure, unsafe water, or root cause.

## Dataset and scope

- **Dataset:** a local copy of the SWaT industrial control-system testbed data.
- **Provenance:** the exact upstream release of the local copy has not been established. The dataset must not be described as verified against a particular official release.
- **Files:** `normal.csv`, `attack.csv`, and `List_of_attacks_Final.xlsx`; `merged.csv` is a derived concatenation used for analysis.
- **Schema:** the raw CSVs contain 53 columns. The deep-learning pipeline uses 42 selected telemetry features.
- **Important data-quality limitation:** `normal.csv` contains 1,387,098 rows, but the experiments use only its first 395,298 rows. The remaining 991,800 rows contain missing values in seven variables and include backward timestamp transitions. Raw data were preserved; the project did not repair or reorder this tail.
- **Scenario coverage:** 49 annotation rows are present, while 36 scenarios are represented in the evaluated attack partition.
- **Evaluation limitation:** results are from one fixed historical split, not a prospective test on future plant operations. The attack and normal partitions overlap in calendar time.

Do not commit restricted dataset files. Consult the [iTrust dataset access process](https://www.sutd.edu.sg/itrust/request-for-datasets/) and [terms of use](https://www.sutd.edu.sg/itrust/itrust-labs/datasets/terms-of-usage/). The source/version uncertainty and local file checksums are recorded in Notebook 12's audit artifacts.

## Methods

| Family | Methods |
|---|---|
| Baselines | Rule-Based, Rolling Statistical, Simple Statistical Threshold |
| Traditional ML | Isolation Forest, One-Class SVM, Local Outlier Factor (novelty mode) |
| Deep learning | LSTM Autoencoder, TCN Autoencoder, USAD |

All models use the project's documented feature selection and temporal evaluation protocol. Thresholds are frozen before evaluation; attack labels are not used for training or threshold selection.

## Main result

Notebook 11 selected the **TCN Autoencoder** (30-step window, MinMaxScaler, seed 42, frozen threshold `0.0039067`) as the preferred method among the nine evaluated under this protocol.

| Measure | TCN Autoencoder | LSTM Autoencoder | Simple Statistical |
|---|---:|---:|---:|
| pAUC@FPR≤0.05 | 0.7597 | 0.7289 | 0.6434 |
| F1 at frozen threshold | 0.8629 | 0.8386 | 0.8144 |
| Precision | 0.9449 | 0.9478 | 0.8059 |
| Recall | 0.7940 | 0.7519 | 0.8231 |
| False-positive rate | 3.20% | 2.86% | 13.69% |
| Scenarios detected | 28 / 36 | 30 / 36 | 33 / 36 |
| Median delay among detected scenarios | 0.0 s | 1.5 s | 2.0 s |
| False-alarm periods in validation | 73 | 180 | 232 |

The TCN also had 43,345 TP, 2,528 FP, 76,503 TN, and 11,247 FN under the recorded point-level evaluation protocol. Its 0-second median delay applies only to the scenarios it detected; its 90th-percentile delay was 22.8 seconds and its maximum was about 24.8 minutes.

![Notebook 10 comparison of the frozen models](reports/figures/frozen-baseline-comparison.png)

These are offline benchmark measurements, **not production guarantees**. Precision depends on the evaluation mix of normal and attack-labelled observations and should not be interpreted as the expected precision in a real plant. The 73 validation false-alarm periods are a recorded count, not a claim that the burden is acceptable to an operator. Scenario detection does not establish that an incident was prevented or that the model is ready for plant use.

## Notebook workflow

Run notebooks in numeric order, subject to the data and environment limitations documented in Notebook 12:

1. [01 — Data and process understanding](notebooks/01_data_and_process_understanding.ipynb)
2. [02 — Data quality and temporal split](notebooks/02-data-quality-and-temporal-split.ipynb)
3. [03 — Exploratory analysis](notebooks/03-exploratory-analysis.ipynb)
4. [04 — Baseline anomaly detection](notebooks/04-baseline-anomaly-detection.ipynb)
5. [05 — LSTM autoencoder](notebooks/05-lstm-autoencoder.ipynb)
6. [06 — Traditional ML anomaly detection](notebooks/06-traditional-ml-anomaly-detection.ipynb)
7. [07 — Deep-learning anomaly detection](notebooks/07-deep-learning-anomaly-detection.ipynb)
8. [08 — Hyperparameter tuning and threshold calibration](notebooks/08-hyperparameter-tuning-threshold-calibration.ipynb)
9. [09 — Error and event analysis](notebooks/09_error_and_event_analysis.ipynb)
10. [10 — Robustness analysis](notebooks/10-robustness-Analysis.ipynb)
11. [11 — Final model selection](notebooks/11_final_model.ipynb)
12. [12 — Reproducibility and final audit](notebooks/12_reproducibility.ipynb)

The root [`PROJECT_SPEC.md`](PROJECT_SPEC.md) defines the research methodology. [`PROJECT_STATE.md`](PROJECT_STATE.md) records the verified project state.
The proposed application structure, hosting choices, database, notifications, Docker setup, and test plan are in [`DEPLOYMENT_PLAN.md`](DEPLOYMENT_PLAN.md). Current target: the React/Vite frontend on Vercel, FastAPI and frozen-TCN inference on Modal, and PostgreSQL run/alert history on Neon. These are plans only; the application is not deployed.

## Reproduce the audit

Use Python 3.11 and the recorded dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab
```

Place permitted source files under `data/raw/` before running data-dependent notebooks. Notebook 12 records the required files, hashes, partition boundaries, frozen artifact inventory, and reproducibility checks.

**Portability caveat:** Notebook 12 found that notebooks 02–08 and 10 contain Kaggle-specific paths that need portability edits before a complete local re-run. The frozen results and saved evaluation artifacts support the reported selection; a clean, from-scratch local run has not been demonstrated.

## Reports and evidence

The project keeps the detailed, evidence-based summaries in the tracked [Notebook 11 model-selection report](nb11_artifacts/NB11_FINAL_REPORT.md) and [Notebook 12 reproducibility report](nb12_artifacts/NB12_FINAL_REPORT.md). The comparison figure above is the saved Notebook 10 visualization. Some large or run-specific intermediate artifacts may be excluded from a Git checkout.

## Next step: Notebook 13 feasibility test

Notebook 13 is the next planned step: replay historical SWaT data chronologically through the **frozen Notebook 11 TCN**, using its saved scaler, feature order, window, and threshold. Do not retrain or retune the model. Check that replay matches the saved scoring procedure, handles sequence warm-up and boundaries correctly, produces timestamped scores and alert episodes, and records inference performance. Evaluate event coverage, detection delay, and false-alarm episodes offline; labels must not be model inputs.

This test asks whether the selected model can support a practical historical-monitoring workflow. It does not establish real-plant effectiveness. If the replay is sound, the next stage can expose the verified inference flow through FastAPI and present scores, alert history, and relevant telemetry in a React interface for human review. Keep the prototype advisory: no live-plant connection or equipment control.

The intended portfolio architecture after a successful feasibility test is **Vercel (React UI) → Modal (FastAPI + frozen TCN) → Neon PostgreSQL (run reports and alert episodes)**. A backend `HookNotifier` is planned for run-start/completion/failure events and each new alert episode; continuous anomalous samples are grouped into episodes to avoid notification floods. Notebook 13 tests the frozen model and does not need an experiment-tracking service.

## Known limitations

- SWaT release provenance for the local copy remains unresolved.
- A large tail of `normal.csv` has missing data and timestamp discontinuities and is outside the evaluated prefix.
- The evaluation uses a single historical split with temporal overlap between attack and normal partitions.
- Only TCN and LSTM were tested across the selected robustness perturbations; robustness is not established for all methods or all operating conditions.
- USAD did not meet its intended training specification; its result is not a fair estimate of a fully trained USAD model.
- The model detects statistical deviations. It does not establish attack intent, physical failure, cause, safety impact, or real-plant effectiveness.
- No production service, frontend, live-data integration, or user study has been completed.
