# SWaT Reference Notebook Audit

## 1. Audit Status

**Status:** Not started  
**Audit type:** Independent review of a published reference implementation  
**Primary reference:** https://github.com/umairs5/swat-lstm-anomaly-detection/blob/main/notebook.ipynb  
**Project specification:** `PROJECT_SPEC.md`  
**Project state:** `PROJECT_STATE.md`

> This document is an audit record, not evidence that the reference notebook has already been inspected. Complete each section using the actual notebook cells and their outputs. Do not infer findings from the repository title, expected model list, or descriptions elsewhere.

## 2. Purpose and Boundaries

The purpose of this audit is to understand and critically evaluate the primary reference notebook before relying on it for methodological decisions in the SWaT project.

The reference is an object of inspection, not code to copy blindly. Record what it actually implements, what its evidence supports, what is uncertain, and which practices should or should not inform this project.

This audit does not authorize changes to the fixed twelve-notebook workflow or the selected nine detection methods in `PROJECT_SPEC.md`.

## 3. Inspection Record

Complete these fields when the notebook has been accessed and inspected.

| Item | Record |
|---|---|
| Date inspected | Not yet recorded |
| Reference URL | https://github.com/umairs5/swat-lstm-anomaly-detection/blob/main/notebook.ipynb |
| Commit or revision inspected | Not yet recorded |
| Local downloaded copy, if applicable | Not yet recorded |
| Inspection method | Not yet recorded |
| Cells reviewed | Not yet recorded |
| Were outputs available and inspected? | Not yet verified |
| Auditor notes | Not yet recorded |

If the inspected version cannot be tied to a commit or revision, record that limitation.

## 4. Evidence-Recording Rules

For each finding:

1. Reference the relevant cell number, heading, code fragment, or output. Record line numbers where the exported format supports them.
2. Quote only the minimum code or output needed to identify the evidence.
3. Separate direct observations from interpretations and recommendations.
4. Mark a question **Unverified** when the notebook or its outputs do not provide enough evidence.
5. Do not claim that a function, model, data split, metric, or result exists until it has been observed in the reference.
6. Do not treat a reported result as reproducible unless the data, preprocessing, split, threshold, and metric definitions have been examined.

### Finding statuses

- **Verified:** Directly supported by inspected code, outputs, or cited documentation.
- **Issue:** Evidence demonstrates a defect or a methodological concern.
- **Unverified:** The available notebook or evidence does not resolve the question.
- **Not applicable:** The item does not apply; explain why.

### Severity

- **Blocker:** Invalidates a major conclusion or creates serious leakage, integrity, or safety risk.
- **Major:** Material correctness or methodological issue that should be resolved before using the approach.
- **Minor:** Limited weakness that does not invalidate the overall finding.
- **Informational:** Context, limitation, or optional improvement.

## 5. Notebook Objective and Data Source

| Check | Status | Evidence (cell/heading/output) | Finding and implication |
|---|---|---|---|
| Stated objective is recorded accurately | Unverified | — | — |
| Dataset source is cited or described | Unverified | — | — |
| Dataset release/version is identifiable | Unverified | — | — |
| Data files and expected formats are identified | Unverified | — | — |
| Claims are distinguished from verified evidence | Unverified | — | — |

## 6. Data Loading and Provenance

Inspect and record:

- Exact file names and source paths.
- Whether paths are absolute, relative, or environment-specific.
- How normal and attack data are loaded.
- Whether files are concatenated, merged, or used separately.
- The row order after loading and combining files.
- Whether record counts are checked before and after combining files.
- Whether duplicate rows or overlapping time ranges are examined.
- Whether the code assumes a dataset version without evidence.
- Whether any raw file is modified or overwritten.

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| File-loading logic is understood | Unverified | — | — |
| Source paths and portability are assessed | Unverified | — | — |
| Normal/attack combination logic is assessed | Unverified | — | — |
| Record-count reconciliation is assessed | Unverified | — | — |
| Raw-data integrity is preserved | Unverified | — | — |
| Dataset provenance and version claims are assessed | Unverified | — | — |

## 7. Schema, Timestamps, and Data Quality

Inspect how the notebook handles:

- Column names and schema consistency.
- Numeric conversion and non-numeric values.
- Timestamp parsing, timezone assumptions, sorting, and chronological order.
- Sampling intervals and temporal gaps.
- Duplicate timestamps and duplicate observations.
- Missing values, infinite values, and invalid measurements.
- Constant or near-constant columns.
- Label encoding, label alignment, and unexpected label values.

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| Schema and data types are examined | Unverified | — | — |
| Timestamp parsing and ordering are correct | Unverified | — | — |
| Sampling cadence and gaps are considered | Unverified | — | — |
| Missing and non-finite values are handled appropriately | Unverified | — | — |
| Duplicates and constant columns are considered | Unverified | — | — |
| Label handling and alignment are correct | Unverified | — | — |

## 8. Feature Selection and Preprocessing

Record the exact features used and determine whether the implementation:

- Includes the timestamp as a model feature.
- Includes the `Normal/Attack` label or derived attack information in the feature matrix.
- Converts all features to suitable data types.
- Fits scaling, imputation, feature selection, or other learned transformations only on permitted training data.
- Applies fitted transformations consistently to validation and test data.
- Uses future information in feature construction.
- Handles non-finite values and zero-variance features.

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| Feature list is recorded | Unverified | — | — |
| Labels and post-event information are excluded from features | Unverified | — | — |
| Preprocessing steps are identified | Unverified | — | — |
| Preprocessing fit boundaries are leakage-safe | Unverified | — | — |
| Feature construction respects prediction-time availability | Unverified | — | — |

## 9. Train, Validation, and Test Design

Identify the exact split procedure, date boundaries, and record counts. Determine whether the implementation uses chronological partitions and whether each step respects the intended purpose of each partition.

Check for:

- Random shuffling of time-series rows.
- Scaling or imputation fitted on the whole dataset.
- Sequences or rolling windows crossing partition boundaries.
- Overlapping observations shared improperly across partitions.
- Validation or final-test information used during training or model selection.
- Threshold tuning using final-test labels.
- Repeated experimentation against the final test set.

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| Split procedure and exact boundaries are recorded | Unverified | — | — |
| Chronological ordering is preserved | Unverified | — | — |
| Train/validation/test roles are clear | Unverified | — | — |
| Preprocessing does not cross fit boundaries | Unverified | — | — |
| Sequence/window boundaries are leakage-safe | Unverified | — | — |
| Final-test data are protected from tuning | Unverified | — | — |

## 10. Models and Training Procedures Actually Present

Do not assume which methods the notebook contains. Inventory them from the actual code.

| Method as implemented | Cell/section evidence | Input representation | Training data | Hyperparameters | Output/score | Notes |
|---|---|---|---|---|---|---|
| Not yet inspected | — | — | — | — | — | — |

For each implemented method, inspect:

- Model class or architecture.
- Input features and shapes.
- Training data eligibility.
- Loss function or learning objective.
- Hyperparameters and random seeds.
- Sequence length, window stride, and boundary handling where applicable.
- Training loop, stopping criteria, and model-selection rule.
- How an anomaly score is calculated and oriented.
- Whether the implementation matches the method's stated purpose.

## 11. Threshold Selection and Metrics

Record the exact score-to-alert procedure. Determine whether thresholds are fixed in advance, derived from training data, calibrated on validation data, or optimized using labels. Identify all metrics and their definitions.

| Check | Status | Evidence | Finding and implication |
|---|---|---|---|
| Anomaly-score definition is explicit | Unverified | — | — |
| Higher/lower score interpretation is correct | Unverified | — | — |
| Threshold-selection data are identified | Unverified | — | — |
| Final-test labels are not used to choose thresholds | Unverified | — | — |
| Point-level metric definitions are recorded | Unverified | — | — |
| Event-level metrics and matching rules are recorded, if used | Unverified | — | — |
| False alarms and detection delay are considered, if relevant | Unverified | — | — |
| Nonstandard adjustments are identified and justified | Unverified | — | — |

## 12. Results and Interpretation

For each reported result, record the metric, evaluation period, threshold, data split, and supporting cell/output. Check whether the interpretation is justified by the evidence.

| Reported claim or result | Evidence | Split and threshold | Reproducibility concerns | Assessment |
|---|---|---|---|---|
| Not yet inspected | — | — | — | Unverified |

Determine whether the notebook:

- Distinguishes point-level detection from event-level detection.
- Reports false positives, false negatives, or false-alarm burden.
- Defines event boundaries and detection delay where claimed.
- Uses valid comparisons across models.
- Avoids unsupported claims of superiority.
- Distinguishes observed anomalies from confirmed attacks or physical faults.
- States relevant limitations.

## 13. Reference Audit Findings Register

Add one row for every substantive finding. Use stable IDs such as `REF-001`, `REF-002`, and so on.

| ID | Severity | Status | Evidence location | Finding | Why it matters | Required action | Relevance to our project |
|---|---|---|---|---|---|---|---|
| — | — | Unverified | — | Audit has not started | No conclusions about the reference are currently justified | Inspect the actual notebook | Establish a defensible implementation plan |

## 14. Comparison Against Our Project Requirements

Compare the reference with `PROJECT_SPEC.md`. The reference does not override our project requirements. Record whether each practice is reusable, requires modification, should be avoided, or remains uncertain.

| Topic | Reference implementation evidence | Project requirement | Assessment | Decision and rationale |
|---|---|---|---|---|
| Data loading and provenance | Not yet inspected | Verify data identity and preserve raw files | Unverified | — |
| Temporal split | Not yet inspected | Leakage-safe chronological partitions | Unverified | — |
| Preprocessing | Not yet inspected | Fit learned preprocessing on permitted training data | Unverified | — |
| Model implementations | Not yet inspected | Nine selected methods in the project specification | Unverified | — |
| Threshold selection | Not yet inspected | Do not tune using final-test labels | Unverified | — |
| Evaluation | Not yet inspected | Point-level and event-level assessment as defined in the specification | Unverified | — |
| Reproducibility | Not yet inspected | Portable paths and documented configuration | Unverified | — |

## 15. Final Audit Summary

Complete this section only after the notebook has been inspected.

### What the reference actually implements

Not yet established.

### Practices that are technically sound and potentially reusable

Not yet established.

### Defects or methodological weaknesses

Not yet established.

### Important methods or checks that are absent

Not yet established.

### Claims or results that cannot be independently substantiated

Not yet established.

### Decisions for our implementation

Not yet established. Decisions must be consistent with `PROJECT_SPEC.md` or explicitly authorized changes to it.

### Remaining uncertainties and limitations

The reference notebook has not yet been audited. No conclusions about its implementation quality or results should be drawn from this template.

### Audit completion decision

**Not yet reviewed.** Do not mark the reference audit complete until the evidence has been recorded and the final summary is supported by the inspected notebook.

## 16. Completion Criteria

The audit may be marked complete only when:

- The actual reference notebook version inspected is recorded as precisely as possible.
- Its relevant cells and available outputs have been examined.
- Data loading, preprocessing, splitting, models, thresholds, evaluation, and reported results have been assessed where present.
- Findings cite exact notebook locations or outputs.
- Verified facts are distinguished from unverified assumptions.
- Material issues have been recorded with severity and rationale.
- Implications for our own project are documented without silently changing the project specification.
- The summary and completion decision reflect the evidence actually collected.

**End of audit record.**
