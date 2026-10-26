# SWaT Industrial Anomaly Detection

An experimental study of anomaly detection on multivariate telemetry from the Secure Water Treatment (SWaT) testbed. The project compares nine detection methods, evaluates false alarms and event detection, and selects a model from recorded evidence.

> **Project status:** Notebooks 01–13 are complete. Notebook 13's replay tests support a **GO to build a historical-monitoring prototype** using the frozen TCN. FastAPI, React, database, and hosting work are next; no live-plant integration or production readiness has been established.

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
13. [13 — Deployment feasibility and historical replay](notebooks/13_deployment_feasibility_and_historical_replay_rest.ipynb)

The root [`PROJECT_SPEC.md`](PROJECT_SPEC.md) defines the research methodology. [`PROJECT_STATE.md`](PROJECT_STATE.md) records the verified project state.
The repository layout, hosting choices, database, notifications, Docker setup, and test plan are in [`DEPLOYMENT_PLAN.md`](DEPLOYMENT_PLAN.md). Current target: the React/Vite frontend on Vercel, FastAPI and frozen-TCN inference on Modal, and PostgreSQL run/alert history on Neon. Application files are still placeholders; the app is not implemented or deployed.

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
Notebook 13's results are summarized in the [feasibility report](nb13_artifacts/NB13_FEASIBILITY_REPORT.md) and [completion/compliance report](reports/NOTEBOOK_13_COMPLIANCE_AND_COMPLETION_REPORT.md).

## Notebook 13 feasibility result

Notebook 13 tested chronological replay using the **frozen Notebook 11 TCN**, its scaler, feature order, window, and threshold. Across 181,031 sequences, scores matched the frozen results with maximum absolute difference `5.215e-08` and zero alert-flag disagreements. The test also reproduced 28/36 detected scenarios, 8 missed scenarios, and 73 validation false-alarm periods. Median delay was 0 seconds among detected scenarios only; p90 was 22.8 seconds and maximum delay was 1,489 seconds. The saved report records all seven feasibility tests passing.

On the tested Windows CPU, model-only single-sequence inference had a median latency of 2.64 ms, well below the dataset's 1-second sampling interval. This is encouraging for a prototype, but it does not measure FastAPI, network, or Modal latency.

**Conclusion: GO to build and test the portfolio prototype—not to claim production readiness.** The next stage is local FastAPI integration and API/parity tests, followed by Neon-backed run reports and episode-level `HookNotifier` events, a React human-review UI, Docker integration, and staged hosting (**Modal API/model → Neon PostgreSQL → Vercel frontend**). Notebook 13 rejected malformed inputs, but its G2 diagnostic needs a wording fix before that validation is exposed through the API. The real HTTP path, concurrent sessions, hosted performance, data-sharing permissions, and real-plant behavior still require verification.

## Known limitations

- SWaT release provenance for the local copy remains unresolved.
- A large tail of `normal.csv` has missing data and timestamp discontinuities and is outside the evaluated prefix.
- The evaluation uses a single historical split with temporal overlap between attack and normal partitions.
- Only TCN and LSTM were tested across the selected robustness perturbations; robustness is not established for all methods or all operating conditions.
- USAD did not meet its intended training specification; its result is not a fair estimate of a fully trained USAD model.
- The model detects statistical deviations. It does not establish attack intent, physical failure, cause, safety impact, or real-plant effectiveness.
- No production service, frontend, live-data integration, or user study has been completed.
