# Notebook 13. Feasibility Report

**Decision: GO**

All seven tests (A. model load, B. score parity, C. chronological replay, D. full alert record, E. event parity, F. inference performance, G. input handling) passed their required checks. The replay workflow is functionally equivalent to the frozen NB08 scoring path at every measured level, and the CPU inference performance fits the SWaT 1 Hz cadence with substantial headroom. The remaining limitations do not block FastAPI and React application development.

## Test summary

| Test | What it verified | Verdict |
|---|---|---|
| A | Load exact selected TCN checkpoint with strict=True | **PASS** |
| B | Score parity against frozen NB08 scores (all 181,031) | **PASS** |
| C | Stateful chronological replay (warm-up, boundary, timestamps) | **PASS** |
| D | Full alert record (parquet, cross-check vs evaluation_summary) | **PASS** |
| E | Event detection parity against NB09 corrected reference | **PASS** |
| F | Inference performance (CPU latency, throughput, 1 Hz cadence) | **PASS** |
| G | Input handling validation (10 malformed/valid fixtures) | **PASS** |

## What the replay workflow establishes

### Model and scoring equivalence

- **Test A**: the checkpoint loads with `strict=True` into a freshly rebuilt `TCNAutoencoder(n_features=42, channels=[32,32,32,32], kernel_size=3, dilations=[1,2,4,8])`, produces finite, correctly shaped output, and reports 40,554 parameters.
- **Test B**: scoring all 181,031 sequences reproduces the frozen NB08 scores with max absolute difference **5.215e-08** across all three partitions, and **0** binary flag disagreements at the frozen threshold (`0.003906734725460411`).

### Chronological replay

- **Test C**: a stateful `deque(maxlen=30)` buffer, warm-up exclusion (first scored end-index = 29), and partition-boundary reset all behave correctly. Stateful replay scores match frozen scores with max absolute difference **6.403e-10** and **0** flag disagreements across the 500-window replay slice per partition.
- Per-window replay latency in Test C: median **3.43 ms** (threshold) and **3.22 ms** (validation).

### Full alert record and event parity

- **Test D**: produces a 181,031-row parquet record with columns `partition, seq_index, end_index, timestamp, score, threshold, alert, label`. Validation false-positive count = **2,528** and attack true-positive count = **43,345**, matching `evaluation_summary.csv` exactly. Zero flag disagreements with frozen scores across all three partitions.
- **Test E**: NB13's alert record reproduces NB09's corrected TCN reference exactly: **28/36 scenarios detected**, **8** missed, **median delay 0.00 s**, **p90 delay 22.80 s**, **max delay 1489.00 s**, **2,528** validation false-positive observations, and **73** false-alarm periods. All 36 per-scenario detection booleans match.

### Inference performance

- **Test F** (CPU-only, 2.6.0+cpu on Windows-10-10.0.22000-SP0):
  - Batch=1 per-observation median latency: **2.64 ms**; throughput **378.3 seq/s**; utilization at SWaT 1 Hz cadence: **0.264%**.
  - Batch=512 per-batch median latency: **52.13 ms**; throughput **9821.3 seq/s**.
  - The 1 Hz SWaT sampling cadence is comfortably met on this CPU with over two orders of magnitude of headroom in the batch=1 deployment-realistic case.

### Input safety

- **Test G**: ten fixtures exercised. Missing features, unexpected feature names, wrong feature order, wrong sequence length, non-numeric values, NaN, infinity, duplicate timestamps, and out-of-order timestamps are all **rejected** with a non-empty diagnostic. The well-formed control case is **accepted**. No malformed input was silently accepted.

## What the replay workflow does not establish

- **Production readiness.** All tests were run in-process on a laptop CPU. FastAPI/HTTP serving costs (parsing, Pydantic validation, JSON serialization, network) are not measured here.
- **Cross-dataset generalization.** The model was evaluated on the SWaT attack partition, whose physical time window overlaps the training and validation windows. The reported metrics describe in-window detection, not future-data behaviour (limitation inherited from NB08, documented in NB08 L1 and restated in NB12).
- **Live-plant behaviour.** The dataset is a recorded testbed. No live industrial-process data was scored. Concept drift, sensor failures, and process-state changes that occur in a real plant are outside the measured evidence.
- **Multi-tenant API safety.** The stateful buffer and timestamp validator were tested in isolation, not under concurrent FastAPI requests.
- **Retraining reproducibility.** The frozen checkpoint was verified as-loaded. It was not retrained. Whether an independent practitioner on other hardware could reproduce the training itself is not verified by NB13.

## Non-blocking issues carried forward to FastAPI implementation

- **G2 diagnostic-message clarity.** G2 detail message says 'match the expected set but are in a different order' when the actual mutation was an unexpected feature name. Fix before FastAPI deployment by splitting the validator into separate 'same set, different order' and 'different set' branches.
- **FastAPI-specific error responses.** HTTP status codes, response body schemas, and per-session state handling are decisions for the FastAPI implementation, not measured here.
- **Serving throughput.** Test F measured in-process throughput. Real HTTP serving throughput depends on request batching, worker count, and serialization overhead. The 1 Hz cadence fits inside Test F's measured per-observation latency with ~99.4% headroom, which is a large enough margin that HTTP-serving overhead is very unlikely to exhaust it — but the application layer must be measured separately.

## Recommended next step

Proceed to **FastAPI model inference backend** and **React.js monitoring dashboard**. Load the frozen TCN checkpoint, reuse the scaler and threshold exactly as verified by NB13, and apply the validation policy from Test G at the FastAPI request boundary. Split the G2 diagnostic into 'same set, different order' versus 'different set' branches before exposing the validator over HTTP.

---

**Notebook 13 status:** This report was generated automatically from the seven test result artifacts in `nb13_artifacts/`. Each verdict in the summary table was recomputed from the stored `verdict_checks` rather than trusting the top-level `overall_verdict` string. No model was retrained, retuned, or modified during NB13. No frozen artifact in `nb08_artifacts/` or `nb09_artifacts/` was overwritten.
