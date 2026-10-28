# Project audit

Generated from `C:\Users\ADEGOKE\Desktop\SWATS`.

## Summary

| Category | Count |
|---|---:|
| Total files | 444 |
| Meaningful (>1 KB) | 349 |
| Small (100 B – 1 KB) | 55 |
| Stub (1 – 100 B) | 4 |
| Empty (0 B) | 36 |
| Empty folders | 0 |

## Empty and stub files

| Directory | File | Size | Category |
|---|---|---:|---|
| `./` | `.env.example` | 0 B | empty |
| `./` | `docker-compose.yml` | 0 B | empty |
| `.github/workflows/` | `ci.yml` | 0 B | empty |
| `backend/` | `Dockerfile` | 0 B | empty |
| `configs/` | `evaluation.yaml` | 0 B | empty |
| `configs/` | `project.yaml` | 0 B | empty |
| `configs/` | `robustness.yaml` | 0 B | empty |
| `database/migrations/` | `001_initial_schema.sql` | 0 B | empty |
| `frontend/` | `.env.example` | 0 B | empty |
| `frontend/src/` | `App.test.tsx` | 0 B | empty |
| `frontend/src/` | `index.css` | 99 B | stub |
| `frontend/src/components/` | `NotificationHost.tsx` | 0 B | empty |
| `frontend/src/hooks/` | `useRunNotifier.ts` | 0 B | empty |
| `frontend/src/test/` | `setup.ts` | 0 B | empty |
| `frontend/src/types/` | `notifications.ts` | 0 B | empty |
| `models/isolation_forest/` | `reproducibility.json` | 0 B | empty |
| `nb08_artifacts/isolation_forest/` | `reproducibility.json` | 0 B | empty |
| `src/api/` | `detector_service.py` | 0 B | empty |
| `src/data/` | `preprocessing.py` | 0 B | empty |
| `src/detection/` | `event_detection.py` | 0 B | empty |
| `src/detection/` | `isolation_forest.py` | 0 B | empty |
| `src/detection/` | `rolling_statistical.py` | 0 B | empty |
| `src/detection/` | `rule_based.py` | 0 B | empty |
| `src/evaluation/` | `detection_delay.py` | 0 B | empty |
| `src/evaluation/` | `drift.py` | 0 B | empty |
| `src/evaluation/` | `event_metrics.py` | 0 B | empty |
| `src/evaluation/` | `point_metrics.py` | 0 B | empty |
| `src/evaluation/` | `robustness.py` | 0 B | empty |
| `src/inference/` | `__init__.py` | 65 B | stub |
| `src/monitoring/` | `logger.py` | 0 B | empty |
| `src/monitoring/` | `schemas.py` | 0 B | empty |
| `src/replay/` | `__init__.py` | 63 B | stub |
| `src/utils/` | `__init__.py` | 78 B | stub |
| `swat-artifacts/isolation_forest/` | `reproducibility.json` | 0 B | empty |
| `tests/` | `test_api.py` | 0 B | empty |
| `tests/` | `test_data_validation.py` | 0 B | empty |
| `tests/` | `test_detectors.py` | 0 B | empty |
| `tests/` | `test_evaluation.py` | 0 B | empty |
| `tests/` | `test_event_detection.py` | 0 B | empty |
| `tests/` | `test_monitoring.py` | 0 B | empty |

## Meaningful files

### `./`

- `.gitignore` — 3,251 B
- `DEPLOYMENT_PLAN.md` — 23,077 B
- `PROJECT_SPEC.md` — 41,331 B
- `PROJECT_STATE.md` — 5,840 B
- `README.md` — 16,939 B

### `frontend/`

- `package-lock.json` — 41,484 B
- `README.md` — 1,278 B

### `frontend/pages/`

- `Dashboard.tsx` — 10,094 B
- `Home.tsx` — 1,561 B

### `frontend/src/`

- `App.css` — 24,405 B
- `App.tsx` — 1,309 B

### `frontend/src/api/`

- `apiClient.ts` — 5,684 B

### `frontend/src/assets/`

- `hero.png` — 13,057 B
- `react.svg` — 4,126 B
- `vite.svg` — 8,709 B

### `frontend/src/components/`

- `AlertRateChart.tsx` — 4,106 B
- `AlertTable.tsx` — 2,774 B
- `AnimatedPreviewChart.tsx` — 3,876 B
- `ConfusionMatrix.tsx` — 1,543 B
- `EvaluationSummary.tsx` — 5,601 B
- `FeatureAttribution.tsx` — 3,465 B
- `ReplayControls.tsx` — 9,422 B
- `ScoreChart.tsx` — 5,421 B
- `ScoreDistribution.tsx` — 5,572 B
- `SensorChart.tsx` — 7,675 B
- `SessionSummary.tsx` — 5,040 B

### `frontend/src/hooks/`

- `useAlertSound.ts` — 2,664 B

### `frontend/src/pages/`

- `Dashboard.tsx` — 12,079 B
- `Home.tsx` — 1,561 B

### `frontend/src/types/`

- `api.ts` — 5,222 B

### `models/`

- `attack_evaluation_sequences.npz` — 3,954,752 B
- `attack_traditional_ml_scores.npz` — 1,171,679 B
- `evaluation_sequences.npz` — 10,735,316 B
- `isolation_forest.joblib` — 2,378,237 B
- `lof_model.joblib` — 56,670,578 B
- `lstm_autoencoder.pth` — 534,475 B
- `lstm_autoencoder_scores.npz` — 652,775 B
- `scaler.joblib` — 2,127 B
- `sgd_one_class_svm.joblib` — 1,078 B
- `tcn_autoencoder_scores.npz` — 653,299 B
- `traditional_ml_model_metadata.json` — 1,204 B
- `traditional_ml_scores.npz` — 1,708,401 B
- `usad_preliminary_scores.npz` — 633,444 B
- `validation_rolling_z_scores_notebook04_export.npz` — 12,872,153 B

### `models/tcn_preliminary/`

- `tcn_autoencoder_best.pth` — 172,469 B
- `tcn_training_history.csv` — 4,689 B
- `tcn_training_mae.png` — 69,056 B
- `tcn_training_mse.png` — 58,905 B

### `models/usad_preliminary/`

- `usad_best.pth` — 2,001,059 B
- `usad_training_history.csv` — 1,489 B
- `usad_training_mae.png` — 48,512 B
- `usad_training_metadata.json` — 1,021 B
- `usad_training_mse.png` — 44,864 B

### `nb08_artifacts/`

- `_inventory.csv` — 5,597 B
- `_nb08_checksums.csv` — 13,014 B
- `attack_deep_learning_scores.npz` — 726,467 B
- `attack_deep_learning_scores_progress.npz` — 557,204 B
- `attack_evaluation_sequences.npz` — 3,954,752 B
- `attack_traditional_ml_scores.npz` — 467,350 B
- `baseline_attack_scores.npz` — 321,656 B
- `baseline_attack_sequence_scores.npz` — 103,506 B
- `baseline_normal_scores.npz` — 58,739 B
- `baseline_normal_sequence_scores.npz` — 250,635 B
- `evaluation_roc_and_prc_curves.png` — 373,177 B
- `evaluation_sequences.npz` — 10,735,316 B
- `evaluation_summary.csv` — 1,872 B
- `final_observation_scores.npz` — 2,927,982 B
- `final_sequence_scores.npz` — 5,063,919 B
- `frozen_thresholds.json` — 1,347 B
- `isolation_forest.joblib` — 2,378,237 B
- `lof_model.joblib` — 89,894,128 B
- `lstm_attack_scores.npz` — 462,560 B
- `lstm_autoencoder.pth` — 534,475 B
- `lstm_autoencoder_scores.npz` — 652,874 B
- `scaler.joblib` — 2,127 B
- `score_distributions_comparison.png` — 72,229 B
- `sgd_one_class_svm.joblib` — 1,078 B
- `tcn_attack_scores.npz` — 474,220 B
- `tcn_autoencoder_scores.npz` — 653,299 B
- `traditional_ml_model_metadata.json` — 1,204 B
- `traditional_ml_scores.npz` — 1,711,184 B
- `traditional_ml_sequence_scores.npz` — 2,452,151 B
- `usad_attack_scores.npz` — 464,312 B
- `usad_preliminary_scores.npz` — 633,456 B
- `validation_rolling_z_scores_notebook04_export.npz` — 12,872,153 B

### `nb08_artifacts/tcn_preliminary/`

- `tcn_autoencoder_best.pth` — 172,469 B
- `tcn_training_history.csv` — 4,689 B
- `tcn_training_mae.png` — 69,056 B
- `tcn_training_mse.png` — 58,905 B

### `nb08_artifacts/tuning/isolation_forest/`

- `new_checkpoint.joblib` — 8,108,221 B
- `results.csv` — 1,465 B

### `nb08_artifacts/tuning/lof/monitor_scores/`

- `n30.npy` — 189,868 B
- `n50.npy` — 189,868 B
- `n70.npy` — 189,868 B

### `nb08_artifacts/tuning/lstm_autoencoder/`

- `results.csv` — 1,916 B

### `nb08_artifacts/tuning/lstm_autoencoder/checkpoints/`

- `h32_b16_lr0.0003.pth` — 157,597 B
- `h32_b16_lr0.001.pth` — 157,569 B
- `h32_b8_lr0.0003.pth` — 155,457 B
- `h32_b8_lr0.001.pth` — 155,429 B
- `h64_b16_lr0.0003.pth` — 536,861 B
- `h64_b16_lr0.001.pth` — 536,833 B
- `h64_b8_lr0.0003.pth` — 532,673 B
- `h64_b8_lr0.001.pth` — 532,645 B

### `nb08_artifacts/tuning/lstm_autoencoder/histories/`

- `h32_b16_lr0.0003.json` — 1,835 B
- `h32_b16_lr0.001.json` — 3,049 B
- `h32_b8_lr0.0003.json` — 1,826 B
- `h32_b8_lr0.001.json` — 3,043 B
- `h64_b16_lr0.0003.json` — 3,047 B
- `h64_b16_lr0.001.json` — 3,073 B
- `h64_b8_lr0.0003.json` — 3,056 B
- `h64_b8_lr0.001.json` — 2,922 B

### `nb08_artifacts/tuning/sgd_one_class_svm/`

- `new_checkpoint.joblib` — 1,222 B
- `results.csv` — 1,790 B

### `nb08_artifacts/tuning/tcn_autoencoder/`

- `results.csv` — 1,917 B

### `nb08_artifacts/tuning/tcn_autoencoder/checkpoints/`

- `cw16_ks3_lr0.0003.pth` — 59,221 B
- `cw16_ks3_lr0.001.pth` — 59,189 B
- `cw16_ks5_lr0.0003.pth` — 90,453 B
- `cw16_ks5_lr0.001.pth` — 90,421 B
- `cw32_ks3_lr0.0003.pth` — 170,965 B
- `cw32_ks3_lr0.001.pth` — 170,933 B
- `cw32_ks5_lr0.0003.pth` — 274,389 B
- `cw32_ks5_lr0.001.pth` — 274,357 B

### `nb08_artifacts/tuning/tcn_autoencoder/histories/`

- `cw16_ks3_lr0.0003.json` — 3,056 B
- `cw16_ks3_lr0.001.json` — 3,083 B
- `cw16_ks5_lr0.0003.json` — 3,063 B
- `cw16_ks5_lr0.001.json` — 2,158 B
- `cw32_ks3_lr0.0003.json` — 3,104 B
- `cw32_ks3_lr0.001.json` — 3,107 B
- `cw32_ks5_lr0.0003.json` — 3,089 B
- `cw32_ks5_lr0.001.json` — 3,104 B

### `nb08_artifacts/tuning/usad/`

- `results.csv` — 3,408 B

### `nb08_artifacts/tuning/usad/checkpoints/`

- `lr0.0001_h128_l16.pth` — 1,976,243 B
- `lr0.0001_h128_l32.pth` — 2,000,883 B
- `lr0.0001_h64_l16.pth` — 995,489 B
- `lr0.0001_h64_l32.pth` — 1,007,841 B
- `lr1e-05_h128_l16.pth` — 1,976,225 B
- `lr1e-05_h128_l32.pth` — 2,000,865 B
- `lr1e-05_h64_l16.pth` — 995,471 B
- `lr1e-05_h64_l32.pth` — 1,007,823 B
- `lr5e-05_h128_l16.pth` — 1,976,225 B
- `lr5e-05_h128_l32.pth` — 2,000,865 B
- `lr5e-05_h64_l16.pth` — 995,471 B
- `lr5e-05_h64_l32.pth` — 1,007,823 B

### `nb08_artifacts/tuning/usad/histories/`

- `lr1e-05_h64_l16.json` — 1,141 B

### `nb08_artifacts/usad_preliminary/`

- `usad_best.pth` — 2,001,059 B
- `usad_training_history.csv` — 1,489 B
- `usad_training_mae.png` — 48,512 B
- `usad_training_metadata.json` — 1,021 B
- `usad_training_mse.png` — 44,864 B

### `nb09_artifacts/`

- `all_predictions.parquet` — 22,061,823 B
- `attack_scenarios_matching_dates.csv` — 7,081 B
- `attack_scenarios_normalized.csv` — 7,081 B
- `attack_sequences_with_scenarios.parquet` — 2,227,041 B
- `coverage_histograms.png` — 84,358 B
- `derived_timestamps.npz` — 1,012,048 B
- `detection_delays.csv` — 15,121 B
- `error_inventory.csv` — 1,192 B
- `event_vs_point.csv` — 1,373 B
- `fn_timeline.png` — 49,710 B
- `fp_sensor_attribution.csv` — 1,281 B
- `fp_timeline.png` — 57,969 B
- `scenario_coverage_matrix.csv` — 4,117 B
- `scenario_detail.csv` — 43,302 B
- `scenario_detection.csv` — 9,923 B
- `scenario_detection_matrix.csv` — 1,918 B
- `scenario_detection_results.csv` — 35,547 B
- `simple_tcn_lstm_scenario_comparison.csv` — 3,001 B
- `validation_false_alarm_periods.csv` — 620,301 B
- `validation_false_alarms_vs_scenario_detection.csv` — 1,220 B

### `nb10_artifacts/`

- `_inventory.csv` — 5,323 B
- `_nb10_checksums.csv` — 4,876 B
- `_verification_report.md` — 1,469 B
- `available_source.json` — 1,915 B
- `pre_run_hashes.json` — 23,580 B

### `nb10_artifacts/batch_scoring/`

- `seed_stability_summary.csv` — 1,687 B
- `threshold_invariant_reference.csv` — 1,289 B
- `threshold_sensitivity_summary.csv` — 3,663 B
- `window_sensitivity_summary.csv` — 1,609 B

### `nb10_artifacts/nb10_artifacts/`

- `_inventory.csv` — 5,542 B
- `_nb10_checksums.csv` — 5,249 B
- `_verification_report.md` — 1,469 B
- `available_source.json` — 1,915 B
- `pre_run_hashes.json` — 23,580 B

### `nb10_artifacts/nb10_artifacts/batch_scoring/`

- `seed_stability_summary.csv` — 1,687 B
- `threshold_invariant_reference.csv` — 1,289 B
- `threshold_sensitivity_summary.csv` — 3,663 B
- `window_sensitivity_summary.csv` — 1,609 B

### `nb10_artifacts/nb10_artifacts/pilot/`

- `lstm_window30_minmax_seed1.pth` — 537,205 B
- `lstm_window30_minmax_seed1_history.csv` — 3,115 B
- `lstm_window30_minmax_seed1_metadata.json` — 2,101 B
- `lstm_window30_minmax_seed2.pth` — 537,205 B
- `lstm_window30_minmax_seed2_history.csv` — 2,941 B
- `lstm_window30_minmax_seed2_metadata.json` — 2,231 B
- `lstm_window30_std_history.csv` — 3,892 B
- `lstm_window30_std_metadata.json` — 2,431 B
- `lstm_window30_std_scaler.joblib` — 2,231 B
- `lstm_window30_std_seed42.pth` — 537,149 B
- `lstm_window60_history.csv` — 4,093 B
- `lstm_window60_metadata.json` — 2,173 B
- `lstm_window60_seed42_minmax.pth` — 537,233 B
- `lstm_window90_history.csv` — 5,932 B
- `lstm_window90_metadata.json` — 2,040 B
- `lstm_window90_seed42_minmax.pth` — 537,233 B
- `tcn_window30_minmax_seed1.pth` — 171,285 B
- `tcn_window30_minmax_seed1_history.csv` — 3,000 B
- `tcn_window30_minmax_seed1_metadata.json` — 2,111 B
- `tcn_window30_minmax_seed2.pth` — 171,285 B
- `tcn_window30_minmax_seed2_history.csv` — 2,996 B
- `tcn_window30_minmax_seed2_metadata.json` — 2,240 B
- `tcn_window30_std_history.csv` — 2,872 B
- `tcn_window30_std_metadata.json` — 2,437 B
- `tcn_window30_std_scaler.joblib` — 2,231 B
- `tcn_window30_std_seed42.pth` — 171,221 B
- `tcn_window60_history.csv` — 2,959 B
- `tcn_window60_metadata.json` — 2,180 B
- `tcn_window60_seed42_minmax.pth` — 171,317 B
- `tcn_window90_history.csv` — 2,991 B
- `tcn_window90_metadata.json` — 2,227 B
- `tcn_window90_seed42_minmax.pth` — 171,317 B

### `nb10_artifacts/nb10_artifacts/plots/`

- `frozen_baseline_comparison.png` — 84,702 B
- `retraining_axis_stability.png` — 65,352 B
- `threshold_f1_sensitivity.png` — 54,570 B
- `threshold_fpr_sensitivity.png` — 109,188 B

### `nb10_artifacts/nb10_artifacts/synthesis/`

- `nb10_cross_axis_summary.csv` — 1,808 B
- `nb10_threshold_swing.csv` — 1,025 B

### `nb10_artifacts/nb10_artifacts/window_scores/`

- `window_scores.npz` — 3,617,478 B
- `window_scores_metadata.json` — 1,661 B

### `nb10_artifacts/pilot/`

- `lstm_window30_minmax_seed1.pth` — 537,205 B
- `lstm_window30_minmax_seed1_history.csv` — 3,115 B
- `lstm_window30_minmax_seed1_metadata.json` — 2,101 B
- `lstm_window30_minmax_seed2.pth` — 537,205 B
- `lstm_window30_minmax_seed2_history.csv` — 2,941 B
- `lstm_window30_minmax_seed2_metadata.json` — 2,231 B
- `lstm_window30_std_history.csv` — 3,892 B
- `lstm_window30_std_metadata.json` — 2,431 B
- `lstm_window30_std_scaler.joblib` — 2,231 B
- `lstm_window30_std_seed42.pth` — 537,149 B
- `lstm_window60_history.csv` — 4,093 B
- `lstm_window60_metadata.json` — 2,173 B
- `lstm_window60_seed42_minmax.pth` — 537,233 B
- `lstm_window90_history.csv` — 5,932 B
- `lstm_window90_metadata.json` — 2,040 B
- `lstm_window90_seed42_minmax.pth` — 537,233 B
- `tcn_window30_minmax_seed1.pth` — 171,285 B
- `tcn_window30_minmax_seed1_history.csv` — 3,000 B
- `tcn_window30_minmax_seed1_metadata.json` — 2,111 B
- `tcn_window30_minmax_seed2.pth` — 171,285 B
- `tcn_window30_minmax_seed2_history.csv` — 2,996 B
- `tcn_window30_minmax_seed2_metadata.json` — 2,240 B
- `tcn_window30_std_history.csv` — 2,872 B
- `tcn_window30_std_metadata.json` — 2,437 B
- `tcn_window30_std_scaler.joblib` — 2,231 B
- `tcn_window30_std_seed42.pth` — 171,221 B
- `tcn_window60_history.csv` — 2,959 B
- `tcn_window60_metadata.json` — 2,180 B
- `tcn_window60_seed42_minmax.pth` — 171,317 B
- `tcn_window90_history.csv` — 2,991 B
- `tcn_window90_metadata.json` — 2,227 B
- `tcn_window90_seed42_minmax.pth` — 171,317 B

### `nb10_artifacts/plots/`

- `frozen_baseline_comparison.png` — 84,702 B
- `retraining_axis_stability.png` — 65,352 B
- `threshold_f1_sensitivity.png` — 54,570 B
- `threshold_fpr_sensitivity.png` — 109,188 B

### `nb10_artifacts/synthesis/`

- `nb10_cross_axis_summary.csv` — 1,808 B
- `nb10_threshold_swing.csv` — 1,025 B

### `nb10_artifacts/window_scores/`

- `window_scores.npz` — 3,618,439 B
- `window_scores_metadata.json` — 1,549 B

### `nb11_artifacts/`

- `_inventory.csv` — 1,396 B
- `_nb11_checksums.csv` — 1,153 B
- `_verification_report.md` — 2,750 B
- `cell1_artifact_inventory.csv` — 2,607 B
- `NB11_FINAL_REPORT.md` — 11,108 B
- `NB11_STAGE_B_COMPARABILITY_STATE.md` — 5,721 B

### `nb11_artifacts/alignment/`

- `NB11_STAGE_B_WINDOW_ALIGNMENT.md` — 3,217 B

### `nb11_artifacts/comparison/`

- `NB11_STAGE_C_UNIFIED_COMPARISON.md` — 5,806 B
- `NB11_STAGE_D6_COMPUTATIONAL_COST.md` — 2,609 B
- `nine_method_comparison.csv` — 3,143 B

### `nb12_artifacts/`

- `_inventory.csv` — 1,487 B
- `_nb12_checksums.csv` — 1,401 B
- `_verification_report.md` — 2,242 B
- `cell1_project_inventory.csv` — 1,113 B
- `cell2_dataset_provenance.json` — 2,739 B
- `cell4_configuration_register.csv` — 6,005 B
- `cell4_configuration_register.json` — 14,284 B
- `cell5_temporal_splits.json` — 2,349 B
- `cell6_artifact_inventory.csv` — 5,132 B
- `cell7b_portability_check.json` — 2,187 B
- `cell8_reproducibility_checks.json` — 1,960 B
- `NB12_FINAL_REPORT.md` — 8,687 B

### `nb13_artifacts/`

- `attack_alert_records_with_scenarios.parquet` — 1,490,379 B
- `cell1_artifact_inventory.csv` — 1,368 B
- `cell2_test_a.json` — 1,577 B
- `cell3_test_b.json` — 2,383 B
- `cell4_test_c.json` — 2,977 B
- `cell5_alert_records.parquet` — 4,017,193 B
- `cell5_test_d.json` — 1,341 B
- `cell6_test_e.json` — 1,167 B
- `cell7_test_f.json` — 1,971 B
- `cell8_test_g.json` — 3,489 B
- `cell9_final_verdict.json` — 2,331 B
- `NB13_FEASIBILITY_REPORT.md` — 6,644 B

### `notebooks/`

- `01_data_and_process_understanding.ipynb` — 9,642 B
- `02-data-quality-and-temporal-split.ipynb` — 148,881 B
- `03-exploratory-analysis.ipynb` — 1,016,780 B
- `04-baseline-anomaly-detection.ipynb` — 174,003 B
- `05-lstm-autoencoder.ipynb` — 225,973 B
- `06-traditional-ml-anomaly-detection.ipynb` — 670,020 B
- `07-deep-learning-anomaly-detection.ipynb` — 336,719 B
- `08-hyperparameter-tuning-threshold-calibration.ipynb` — 839,115 B
- `09_error_and_event_analysis.ipynb` — 385,688 B
- `10-robustness-Analysis.ipynb` — 852,075 B
- `11_final_model.ipynb` — 50,488 B
- `12_reproducibility.ipynb` — 232,874 B
- `13_deployment_feasibility_and_historical_replay_rest.ipynb` — 250,666 B

### `reports/`

- `NOTEBOOK_13_COMPLIANCE_AND_COMPLETION_REPORT.md` — 14,438 B

### `reports/figures/`

- `frozen-baseline-comparison.png` — 84,702 B

### `scripts/`

- `audit_project.py` — 7,125 B
- `convert_to_parquet.py` — 3,413 B

### `src/api/`

- `main.py` — 27,716 B
- `schemas.py` — 17,280 B

### `src/data/`

- `ingestion.py` — 6,387 B
- `validation.py` — 10,703 B

### `src/inference/`

- `frozen_bundle.py` — 13,653 B
- `validate.py` — 11,900 B

### `src/replay/`

- `runner.py` — 16,459 B

### `src/utils/`

- `paths.py` — 5,148 B

### `swat-artifacts/`

- `attack_evaluation_sequences.npz` — 3,954,752 B
- `attack_traditional_ml_scores.npz` — 1,171,679 B
- `evaluation_sequences.npz` — 10,735,316 B
- `isolation_forest.joblib` — 2,378,237 B
- `lof_model.joblib` — 56,670,578 B
- `lstm_autoencoder.pth` — 534,475 B
- `lstm_autoencoder_scores.npz` — 652,775 B
- `scaler.joblib` — 2,127 B
- `sgd_one_class_svm.joblib` — 1,078 B
- `tcn_autoencoder_scores.npz` — 653,299 B
- `traditional_ml_model_metadata.json` — 1,204 B
- `traditional_ml_scores.npz` — 1,708,401 B
- `usad_preliminary_scores.npz` — 633,444 B
- `validation_rolling_z_scores_notebook04_export.npz` — 12,872,153 B

### `swat-artifacts/tcn_preliminary/`

- `tcn_autoencoder_best.pth` — 172,469 B
- `tcn_training_history.csv` — 4,689 B
- `tcn_training_mae.png` — 69,056 B
- `tcn_training_mse.png` — 58,905 B

### `swat-artifacts/usad_preliminary/`

- `usad_best.pth` — 2,001,059 B
- `usad_training_history.csv` — 1,489 B
- `usad_training_mae.png` — 48,512 B
- `usad_training_metadata.json` — 1,021 B
- `usad_training_mse.png` — 44,864 B
