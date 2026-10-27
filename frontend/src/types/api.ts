/**
 * TypeScript mirror of src/api/schemas.py.
 *
 * One interface per Pydantic model, field names and nullability matching
 * FastAPI's JSON serialization exactly. If you change a field here, change
 * the corresponding model in schemas.py first — this file follows the
 * server contract, not the other way around.
 *
 * Notes on JSON serialization:
 *   - Python Optional[X] serializes to `X | null` (the key is present
 *     with value null; FastAPI does not omit it). Encode that as
 *     `X | null`, not `X | undefined`.
 *   - Python datetime serializes to an ISO 8601 string.
 *   - Python tuple[int, int] serializes to a 2-element JSON array.
 *
 * Neutral wording (required by the deployment plan):
 *   `alert` means the anomaly score exceeded the frozen threshold.
 *   It is NOT a confirmed attack, equipment failure, or safety event.
 *   Every response carries `alert_interpretation` stating this.
 */

// --- Shared discriminants ------------------------------------------------

export type Partition = "threshold" | "validation" | "attack";

export type HealthStatus = "ok" | "degraded" | "not_ready";

// --- Health --------------------------------------------------------------

export interface HealthResponse {
  status: HealthStatus;
  model_ready: boolean;
  message: string;
}

// --- Model info ----------------------------------------------------------

export interface ModelInfoResponse {
  method: string;
  window_size: number;
  n_features: number;
  feature_names: string[];
  threshold: number;
  threshold_source: string;
  threshold_procedure: string;
  score_convention: string;
  warmup_observations: number;
  checkpoint_size_bytes: number;
  param_count: number;
  device: string;
  model_id: string;
  alert_interpretation: string;
}

// --- Predict -------------------------------------------------------------

export interface PredictRequest {
  feature_names: string[];
  values: number[][];
  /** ISO 8601. Optional. Echoed back; never used for inference. */
  timestamp?: string | null;
}

export interface PredictResponse {
  score: number;
  threshold: number;
  alert: boolean;
  timestamp: string | null;
  /** Tuple serialized as a 2-element array, e.g. [30, 42]. */
  window_shape: [number, number];
  interpretation: string;
}

// --- Replay --------------------------------------------------------------

export interface ReplayStartRequest {
  partition: Partition;
}

export interface ReplayStatus {
  partition: string | null;
  total_rows: number;
  position: number;
  window_filled: boolean;
  warmup_remaining: number;
  total_scored: number;
  alerts_emitted: number;
  last_timestamp: string | null;
  last_score: number | null;
  last_alert: boolean | null;
  peak_score: number | null;
  threshold: number;
  finished: boolean;
  alert_interpretation: string;
  warmup_interpretation: string;
}

export interface ReplayAdvanceResponse {
  advanced: boolean;
  finished: boolean;
  position: number;
  end_index: number;
  timestamp: string | null;
  score: number | null;
  alert: boolean | null;
  window_filled: boolean;
  warmup_remaining: number;
  threshold: number;
  status: ReplayStatus;
  alert_interpretation: string;
  warmup_interpretation: string;
}

export interface ReplayResetResponse {
  reset: boolean;
  status: ReplayStatus;
}