"""
Pydantic v2 request/response models for the SWaT monitoring API.

Design boundaries (deliberate):

    This module enforces TRANSPORT-LEVEL types only:
        - Is feature_names a list of strings?
        - Is values a 2D list of floats?
        - Is the HTTP method well-formed?

    Content-level validation (exactly 42 features, exact names, exact
    order, exactly 30 window rows, finite numeric values, timestamp
    monotonicity) lives in src/inference/validate.py, called by the
    route handlers AFTER this schema passes. That preserves the exact
    NB13 Test G diagnostic messages over HTTP, and keeps the frozen
    constants declared only once (in src/inference/frozen_bundle.py).

Two layers, one set of constants. Do not add length-42 checks here —
that would duplicate EXPECTED_N_FEATURES and cause the two layers to
disagree if the frozen bundle is ever re-selected.

Neutral wording (required by the deployment plan):
    'alert' means the model's anomaly score exceeded the frozen
    threshold. It is NOT a confirmed attack, equipment failure, or
    safety event. Every response surface that exposes 'alert' includes
    that disclaimer via the interpretation field or a status field.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Shared disclaimer text (single source of truth) ---------------------

ALERT_INTERPRETATION = (
    "Alert indicates the model's anomaly score exceeded the frozen "
    "threshold. It is not a confirmed attack, equipment failure, or "
    "safety event. Human review is required."
)

WARMUP_INTERPRETATION = (
    "No anomaly score is produced during the first (window_size - 1) "
    "observations of a replay: the rolling window is still filling. "
    "The absence of a score during warm-up does not indicate normal "
    "behaviour."
)


# --- Health ---------------------------------------------------------------

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "not_ready"]
    model_ready: bool
    message: str = Field(
        description="Human-readable status. Never contains filesystem paths."
    )


# --- Model info -----------------------------------------------------------

class ModelInfoResponse(BaseModel):
    method: str = Field(description="e.g. 'TCN Autoencoder'.")
    window_size: int = Field(description="Observations per input window.")
    n_features: int = Field(description="Number of sensor features per row.")
    feature_names: list[str] = Field(
        description="Ordered feature names. Must match scaler.feature_names_in_."
    )
    threshold: float = Field(
        description="Frozen decision threshold (score > threshold -> alert)."
    )
    threshold_source: str = Field(
        description="Where the threshold was read from, as a repo-relative path."
    )
    threshold_procedure: str = Field(
        description="How the threshold was originally chosen (from NB08)."
    )
    score_convention: str = Field(
        description="How the anomaly score is computed."
    )
    warmup_observations: int = Field(
        description="Observations required before the first score is produced."
    )
    checkpoint_size_bytes: int = Field(
        description="TCN checkpoint file size in bytes, as a fingerprint."
    )
    param_count: int = Field(
        description="Total trainable parameters in the model."
    )
    device: str = Field(description="Torch device string, e.g. 'cpu'.")
    model_id: str = Field(
        description="Stable identifier for this frozen artifact, e.g. 'tcn_autoencoder_nb08_frozen'."
    )
    alert_interpretation: str = ALERT_INTERPRETATION


# --- Predict --------------------------------------------------------------

class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feature_names: list[str] = Field(
        description=(
            "Ordered feature names. The handler verifies this equals the "
            "scaler's feature_names_in_ exactly; a mismatch returns HTTP 422."
        )
    )
    values: list[list[float]] = Field(
        description=(
            "Sensor window of shape (window_size, n_features). The handler "
            "verifies the exact shape, finiteness, and numeric content."
        )
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        description=(
            "Optional informational timestamp (window-end). Echoed back to "
            "the caller for labeling. Never used for inference or state."
        ),
    )


class PredictResponse(BaseModel):
    score: float = Field(
        description="Reconstruction-error score for the supplied window."
    )
    threshold: float = Field(
        description="Frozen decision threshold applied to the score."
    )
    alert: bool = Field(
        description="True iff score > threshold. See alert_interpretation."
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="Echo of the request timestamp, if supplied."
    )
    window_shape: tuple[int, int] = Field(
        description="The validated window shape the model actually received."
    )
    interpretation: str = ALERT_INTERPRETATION


# --- Replay ---------------------------------------------------------------

Partition = Literal["threshold", "validation", "attack"]


class ReplayStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    partition: Partition = Field(
        description=(
            "Which SWaT partition to replay. Only these three are permitted; "
            "arbitrary filesystem paths are rejected at the schema layer."
        )
    )


class ReplayStatus(BaseModel):
    partition: Optional[str] = Field(
        description="Currently loaded partition, or null if no replay is active."
    )
    total_rows: int
    position: int = Field(description="0-based index of the next row to consume.")
    window_filled: bool
    warmup_remaining: int = Field(
        description="How many more observations are needed before scoring begins."
    )
    total_scored: int
    alerts_emitted: int = Field(
        description=(
            "Count of scored observations whose score exceeded the threshold. "
            "An alert is not a confirmed attack; see alert_interpretation."
        )
    )
    last_timestamp: Optional[str]
    last_score: Optional[float]
    last_alert: Optional[bool]
    peak_score: Optional[float] = Field(
        description="Highest score observed so far in this replay."
    )
    threshold: float
    finished: bool = Field(
        description="True once position == total_rows."
    )
    alert_interpretation: str = ALERT_INTERPRETATION
    warmup_interpretation: str = WARMUP_INTERPRETATION


class ReplayAdvanceResponse(BaseModel):
    advanced: bool = Field(
        description="True if a row was consumed. False at end-of-partition."
    )
    finished: bool
    position: int = Field(description="Index of the just-consumed row.")
    end_index: int = Field(
        description=(
            "Same value as position. Named for parity with NB13's alert-record "
            "column convention."
        )
    )
    timestamp: Optional[str] = Field(
        description="Timestamp of the just-consumed row (null before any row)."
    )
    score: Optional[float] = Field(
        description=(
            "Anomaly score if the window was full at this row; null during "
            "warm-up (the first window_size - 1 rows)."
        )
    )
    alert: Optional[bool] = Field(
        description=(
            "True iff score > threshold. Null during warm-up. See "
            "alert_interpretation."
        )
    )
    window_filled: bool
    warmup_remaining: int
    threshold: float
    status: ReplayStatus = Field(
        description="Snapshot of the runner state after this advance."
    )
    alert_interpretation: str = ALERT_INTERPRETATION
    warmup_interpretation: str = WARMUP_INTERPRETATION


class ReplayResetResponse(BaseModel):
    reset: bool = Field(description="Always true on success.")
    status: ReplayStatus


# --- Standalone smoke test -----------------------------------------------
#
# Run from the project root:
#     python src/api/schemas.py
#
# Verifies:
#   S1  Valid PredictRequest constructs
#   S2  PredictRequest rejects non-float values via Pydantic
#   S3  PredictRequest rejects extra fields (extra='forbid')
#   S4  HealthResponse + ModelInfoResponse construct from plausible values
#   S5  ReplayStatus + ReplayAdvanceResponse construct; JSON round-trips
#   S6  ReplayStartRequest rejects an unsupported partition name

if __name__ == "__main__":
    import json
    import sys

    from pydantic import ValidationError

    print("=" * 72)
    print("schemas.py — standalone smoke test")
    print("=" * 72)
    print(f"  Pydantic version: {__import__('pydantic').VERSION}")

    ok = True

    # --- S1: valid PredictRequest ---
    valid = PredictRequest(
        feature_names=[f"F{i:02d}" for i in range(42)],
        values=[[0.0] * 42 for _ in range(30)],
        timestamp="2024-01-01T00:00:00",
    )
    s1 = len(valid.feature_names) == 42 and len(valid.values) == 30
    print(f"\n  [S1] valid PredictRequest          -> {'PASS' if s1 else 'ISSUE'}")
    ok &= s1

    # --- S2: PredictRequest rejects non-float values ---
    try:
        PredictRequest(
            feature_names=["f"],
            values=[["not_a_number"]],
        )
        s2 = False
        detail = "accepted non-float value"
    except ValidationError as e:
        s2 = True
        detail = f"rejected ({e.error_count()} error(s))"
    print(f"  [S2] rejects non-float values      -> {'PASS' if s2 else 'ISSUE'}   {detail}")
    ok &= s2

    # --- S3: PredictRequest rejects extra fields ---
    try:
        PredictRequest.model_validate({
            "feature_names": ["f"],
            "values": [[0.0]],
            "extra_field": "nope",
        })
        s3 = False
        detail = "accepted extra field"
    except ValidationError as e:
        s3 = True
        detail = f"rejected ({e.error_count()} error(s))"
    print(f"  [S3] rejects extra fields          -> {'PASS' if s3 else 'ISSUE'}   {detail}")
    ok &= s3
    
    # --- S4: Health + ModelInfo ---
    h = HealthResponse(status="ok", model_ready=True, message="ready")
    mi = ModelInfoResponse(
        method="TCN Autoencoder",
        window_size=30,
        n_features=42,
        feature_names=[f"F{i:02d}" for i in range(42)],
        threshold=0.003906734725460411,
        threshold_source="nb08_artifacts/frozen_thresholds.json -> thresholds.tcn",
        threshold_procedure="99th pct of threshold partition (linear interpolation)",
        score_convention="mean over (T, F) of squared reconstruction error",
        warmup_observations=29,
        checkpoint_size_bytes=172_469,
        param_count=40_554,
        device="cpu",
        model_id="tcn_autoencoder_nb08_frozen",
    )
    s4 = (
        h.model_ready is True
        and mi.threshold == 0.003906734725460411
        and mi.warmup_observations == 29
    )
    print(f"  [S4] Health + ModelInfo construct  -> {'PASS' if s4 else 'ISSUE'}")
    ok &= s4

    # --- S5: Replay status + advance; JSON round-trip ---
    status = ReplayStatus(
        partition="threshold",
        total_rows=47_437,
        position=30,
        window_filled=True,
        warmup_remaining=0,
        total_scored=1,
        alerts_emitted=0,
        last_timestamp="2016-01-01 02:23:47",
        last_score=0.0007158350781537592,
        last_alert=False,
        peak_score=0.0007158350781537592,
        threshold=0.003906734725460411,
        finished=False,
    )
    adv = ReplayAdvanceResponse(
        advanced=True,
        finished=False,
        position=29,
        end_index=29,
        timestamp="2016-01-01 02:23:47",
        score=0.0007158350781537592,
        alert=False,
        window_filled=True,
        warmup_remaining=0,
        threshold=0.003906734725460411,
        status=status,
    )
    j = json.loads(adv.model_dump_json())
    s5 = (
        j["score"] == 0.0007158350781537592
        and j["status"]["threshold"] == 0.003906734725460411
        and j["status"]["partition"] == "threshold"
        and j["alert_interpretation"] == ALERT_INTERPRETATION
    )
    print(f"  [S5] Replay status/advance + JSON  -> {'PASS' if s5 else 'ISSUE'}")
    ok &= s5

    # --- S6: ReplayStartRequest rejects unsupported partition ---
    try:
        ReplayStartRequest(partition="train")  # type: ignore[arg-type]
        s6 = False
        detail = "accepted 'train'"
    except ValidationError as e:
        s6 = True
        detail = f"rejected ({e.error_count()} error(s))"
    print(f"  [S6] rejects unsupported partition -> {'PASS' if s6 else 'ISSUE'}   {detail}")
    ok &= s6

    print("\n" + "=" * 72)
    print(f"Overall: {'PASS' if ok else 'ISSUE'}")
    print("=" * 72)
    sys.exit(0 if ok else 1)