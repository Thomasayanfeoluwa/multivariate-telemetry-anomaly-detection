# SWaT Industrial Anomaly Detection — Project State

**Last updated:** 14 October 2026

## 1. Authoritative Documents

- `PROJECT_SPEC.md` — project objectives, fixed workflow, selected methods, methodology, and repository standards.
- `PROJECT_STATE.md` — current progress, verified findings, outstanding questions, and next action.
- `DEEPSEEK_REVIEW_PROMPT.md` — requirements for independent code review.

The project specification must not be silently changed. Any material inconsistency or required change must be identified and resolved explicitly.

## 2. Project Identity

Investigate anomaly detection in multivariate time-series data from the Secure Water Treatment (SWaT) industrial control-system testbed.

The project follows the fixed twelve-notebook workflow and the nine selected detection methods defined in `PROJECT_SPEC.md`.

All conclusions must be supported by verified data, documented methodology, or reproducible experimental evidence.

## 3. Current Position

**Current notebook:** `02_data_quality_and_temporal_split.ipynb`

**Current stage:** Initial structural inspection of the raw CSV files.

**Current status:** In progress.

### Notebook 01 — Data and Process Understanding

The revised Markdown content was supplied and the user reported applying it to Notebook 01.

The revised content documents the SWaT process stages, instrumentation, problem definition, scope, limitations, and dataset-specific questions to be verified later.

**Outstanding:** The saved notebook's final content and organization have not been independently inspected in this conversation. Do not describe Notebook 01 as fully verified until its completion criteria have been checked.

### Notebook 02 — Data Quality and Temporal Split

Completed:
- Inspected the raw-data directory.
- Identified the three available CSV files.
- Inspected their headers and first data rows.
- Confirmed that each observed header contains 53 columns.
- Confirmed that the header width matches the first data-row width in each file.
- Identified `Timestamp` and `Normal/Attack` as column names.
- Observed leading whitespace in some raw column names.

Not yet completed:
- Full record counts.
- Formal schema comparison after column-name normalization.
- Timestamp validity across the complete files.
- Full timestamp coverage and chronological-order verification.
- Label counts and label-distribution verification.
- Sampling intervals and temporal gaps.
- Duplicate timestamps and duplicate observations.
- Missing, infinite, constant, or otherwise invalid measurements.
- Dataset provenance and release/version verification.
- Chronological partition design.

## 4. Raw-Data Inventory

The initial file inventory reported:

| File | Size in bytes |
|---|---:|
| `normal.csv` | 402,374,633 |
| `attack.csv` | 15,162,438 |
| `merged.csv` | 426,855,390 |

Each file has 53 columns according to the initial header inspection.

The first inspected timestamps were:
- `normal.csv`: `28/12/2015 10:00:00 AM`, labelled `Normal`.
- `attack.csv`: `28/12/2015 10:29:14 AM`, labelled `Attack`.
- `merged.csv`: `28/12/2015 10:00:00 AM`, labelled `Normal`.

These are observations from the first data rows only. They do not establish the full time coverage, sampling cadence, chronology, or label distribution of any file.

The relationship between `merged.csv` and the two separate files has not been verified.

**Raw-data rule:** Do not overwrite, delete, or modify the original CSV files during inspection.

## 5. Fixed Project Decisions

The following decisions remain governed by `PROJECT_SPEC.md`:

- Preserve the twelve-notebook workflow and notebook order.
- Retain the selected nine detection methods.
- Preserve chronological ordering for the primary time-series evaluation.
- Prevent temporal, preprocessing, feature, and label leakage.
- Reserve final-test data for final evaluation.
- Use portable paths rather than machine-specific absolute paths in committed code.
- Explain relevant mathematical and statistical concepts in Markdown where they are introduced.
- Do not begin model training before the required data verification and exploratory-analysis stages are complete.
- Do not declare a stage complete without reviewing the evidence required by its objectives.

## 6. Current Next Action

Independently review the proposed structural-audit code for Notebook 02 using `DEEPSEEK_REVIEW_PROMPT.md`.

The proposed code is intended to inspect:
- Record counts.
- Timestamp parsing and validity.
- Timestamp ordering within and across chunks.
- Label distributions, including missing labels.
- Normalized schema consistency.
- Column names containing surrounding whitespace.

The proposed cell has not yet been reported as executed.

After the independent review:
1. Resolve any substantive review findings.
2. Execute the accepted version of the code.
3. Inspect and retain the actual output.
4. Record verified findings and remaining limitations.
5. Determine the next data-quality check from that evidence.

## 7. Outstanding Project Questions

- What is the exact source and identifiable release/version of the local dataset?
- Are the three CSV files structurally and temporally consistent?
- Does `merged.csv` contain the expected records from the separate files, without unintended duplication or ordering problems?
- What are the actual timestamp coverage, sampling intervals, and temporal gaps?
- What are the full label distribution and label semantics?
- What data-quality issues exist in the actual files?
- What chronological evaluation design is justified by the verified dataset?

These questions must be answered using the relevant files and supporting documentation, not inferred from filenames or expected SWaT characteristics.

## 8. Reference-Notebook Audit

The primary reference notebook identified in `PROJECT_SPEC.md` remains subject to a documented audit.

The audit must be supported by inspection of the actual reference implementation. Expectations about its contents must not be treated as completed findings.

The project specification requires this audit before the modelling stages begin. Its location and completion evidence must be recorded explicitly without silently changing the fixed twelve-notebook workflow.

## 9. Progress and Completion Rules

A task is complete only when its required code or documentation has been produced, its relevant evidence has been inspected, and its findings and limitations have been recorded.

The following distinctions must be preserved:

- **Completed:** The requested work has been performed.
- **Verified:** The relevant result or property has been checked against appropriate evidence.
- **Awaiting review:** The work exists but has not received the required independent review.
- **Blocked:** An unresolved issue prevents safe or valid progression.
- **Not started:** No implementation or investigation has yet been performed.

Do not equate successful execution with methodological correctness.

Do not claim that an entire notebook is complete merely because one cell or section has been completed.

## 10. Resume Instructions

Resume from the current position in Notebook 02.

Review the proposed structural-audit cell, resolve the review findings, execute the accepted code, and assess the observed output.

Do not repeat the completed header inventory unnecessarily. Do not skip the outstanding data checks, begin model training, or change the fixed project plan without justification and authorization.