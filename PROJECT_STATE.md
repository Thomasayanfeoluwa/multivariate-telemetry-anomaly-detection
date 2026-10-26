# SWaT Anomaly Detection — Project State

**Updated:** 26 October 2026

## Current status

The core 12-notebook experimental workflow is complete and Notebook 12's audit records 10/10 reproducibility checks passing. The preferred model is the frozen TCN Autoencoder selected in Notebook 11. This is an offline benchmark result, not a production recommendation.

| Stage | Status |
|---|---|
| Notebooks 01–10 | Experiments, evaluation, event/error analysis, and robustness work recorded |
| Notebook 11 | TCN Autoencoder selected from the nine evaluated methods |
| Notebook 12 | Reproducibility audit complete; 10/10 checks passed |
| Notebook 13 | Next planned step: test frozen-TCN historical replay and monitoring feasibility; not started |
| FastAPI / React application | Future work; not implemented |
| Tests / live integration | Future work; not implemented |

The detailed experimental specification remains in [`PROJECT_SPEC.md`](./PROJECT_SPEC.md). The main results and public-facing summary belong in [`README.md`](./README.md).
The proposed backend, frontend, Docker, storage, and testing sequence is documented in [`DEPLOYMENT_PLAN.md`](./DEPLOYMENT_PLAN.md); it is not implemented work.

## Selected model and measured results

- **Model:** TCN Autoencoder, 30-step window, MinMaxScaler, seed 42.
- **Frozen threshold:** `0.0039067347`, calibrated at the 99th percentile of the designated threshold partition.
- **Point-level:** pAUC@0.05 0.7597; F1 0.8629; precision 0.9449; recall 0.7940; FPR 3.20%.
- **Confusion counts:** TP 43,345; FP 2,528; TN 76,503; FN 11,247 under the recorded evaluation protocol.
- **Events:** 28 of 36 represented scenarios detected; median delay 0 seconds among detected scenarios, p90 22.8 seconds, maximum about 24.8 minutes.
- **False alarms:** 73 validation false-alarm periods.

The TCN is the selected model under the documented weighting, not the best choice for every criterion. LSTM and Simple Statistical have higher scenario recall (30/36 and 33/36 respectively). The measured precision depends on this benchmark's evaluation mix and is not an estimate of real-plant alert precision.

## Dataset and evaluation qualifications

- The project uses a local SWaT dataset copy; its exact upstream release is unresolved.
- The raw `normal.csv` has 1,387,098 rows. The model pipeline uses the ordered first 395,298 rows. The remainder contains a 991,800-row missing-value block in seven variables and backward timestamp transitions.
- Raw data were retained unchanged. No claim is made that the problematic tail was repaired or made suitable for evaluation.
- The attack annotation workbook has 49 rows; 36 scenarios are represented in the evaluated attack data.
- The normal-validation and attack partitions overlap in calendar time. The results are a fixed historical benchmark evaluation, not future-period generalization.
- The attack/normal ratio in the evaluated partitions affects precision and F1. Do not interpret them as expected production alert quality.
- Notebook 12 found that notebooks 02–08 and 10 require path portability edits for a complete local rerun. Frozen artifacts/checksums support the reported model-selection result, but a clean from-scratch local reproduction has not been demonstrated.
- Robustness perturbations were run for TCN and LSTM only. USAD did not meet its intended training specification.

## Planned direction after the core study

1. Use Notebook 13 to replay the frozen TCN chronologically and validate scoring parity, window warm-up/boundaries, alert episodes, event coverage and delay, and inference performance. Keep labels out of inference and use them only for offline evaluation.
2. Only if replay is verified, build the planned service: FastAPI and frozen-TCN inference on Modal, React on Vercel, and Neon PostgreSQL for run reports and alert episodes. `HookNotifier` is planned for run and alert-episode notifications. No experiment-tracking service is needed for this frozen-model feasibility work.
3. Keep the system advisory. No live-plant connection or equipment control is planned.
4. Report only what the historical replay and its measured evaluation support; do not present benchmark results as proof of real-plant outcomes.

## Repository constraints for continuation

- Preserve raw data and scored/model artifacts; do not retrain or replace frozen results without an explicitly documented experiment.
- Keep the core 12 notebooks unchanged in order. Notebook 13 is a separate planned extension, not part of the completed core workflow.
- Do not treat a statistical anomaly as a confirmed attack, failure, cause, or safety event.
- Backend, frontend, and tests remain unfinished and are intentionally outside the current documentation cleanup.
