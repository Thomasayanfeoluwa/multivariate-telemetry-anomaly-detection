# SWaT Anomaly Detection — Project State

**Updated:** 27 October 2026

## Current status

The 12-notebook experimental workflow and Notebook 13's historical-replay feasibility test are complete. Notebook 13 passed all seven recorded checks and supports proceeding to build a portfolio monitoring prototype around the frozen TCN. This is not production authorization or a real-plant recommendation.

| Stage | Status |
|---|---|
| Notebooks 01–10 | Experiments, evaluation, event/error analysis, and robustness work recorded |
| Notebook 11 | TCN Autoencoder selected from the nine evaluated methods |
| Notebook 12 | Reproducibility audit complete; 10/10 checks passed |
| Notebook 13 | Completed; all 7 tests PASS (model load, score parity, replay, alerts, events, latency, validation); Decision: GO |
| FastAPI / inference / replay | Local implementation present; endpoint and parity tests remain |
| React application | Vite starter plus typed API client; SWaT dashboard not implemented |
| Database / notifications / hosting | Not implemented or deployed |
| Automated tests | Test files exist as empty placeholders; test coverage not implemented |

The detailed experimental specification remains in [`PROJECT_SPEC.md`](./PROJECT_SPEC.md). The main results and public-facing summary belong in [`README.md`](./README.md).
The approved next-phase scope and its remaining gates are in [`DEPLOYMENT_PLAN.md`](./DEPLOYMENT_PLAN.md). Some local inference/API implementation exists; database, full dashboard, deployment configuration, and hosted deployment remain future work.

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

1. Notebook 13 verified score parity across 181,031 sequences (maximum absolute difference `5.215e-08`, zero flag disagreements), reproduced event metrics (28/36 detected, 8 missed, 73 validation false-alarm periods), and measured 2.64 ms median model-only latency per sequence on its tested CPU.
2. Verify the G2 diagnostic fix now used by `/predict`; add API/parity tests and test request isolation, HTTP behavior, and end-to-end latency.
3. If local API checks pass, connect Neon for compact replay reports/alert episodes and implement `HookNotifier` at run and alert-episode boundaries. Then complete the React UI and Docker integration.
4. Deploy the API/model to Modal and the frontend to Vercel only after local end-to-end checks and data/model permission review. Re-measure the hosted HTTP path.
5. Keep the system advisory. No live-plant connection, equipment control, production-readiness claim, or financial benefit is established.

## Repository constraints for continuation

- Preserve raw data and scored/model artifacts; do not retrain or replace frozen results without an explicitly documented experiment.
- Keep notebooks 01–12 and their recorded results unchanged. Notebook 13 is a completed post-12 feasibility extension; do not treat it as evidence of deployment or real-plant validation.
- Do not treat a statistical anomaly as a confirmed attack, failure, cause, or safety event.
- The complete current file/folder tree is in `README.md`; deployment responsibilities and next-phase placement rules are in `DEPLOYMENT_PLAN.md`. The local inference/replay/API code is present, but database persistence, notification delivery, container configuration, CI, and automated tests are not implemented. The React screen remains the Vite starter.
- Keep notebook outputs, raw data, and model artifacts in their current root-level locations. Notebook code and reproducibility records refer to these paths; do not relocate or duplicate them during application work.
