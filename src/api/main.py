"""
FastAPI application for the SWaT historical-replay monitoring prototype.

Single-file application (deliberately): the entire HTTP surface — health,
model-info, predict, replay start/status/advance/reset — lives here so the
whole API can be read in one pass. If we later need multiple routers, split
into `src/api/routes.py` and mount from here.

Design commitments (see DEPLOYMENT_PLAN.md and NB13):

    - FrozenBundle is loaded ONCE at startup via the FastAPI lifespan.
      If it fails to load, /health returns status='not_ready',
      model_ready=False, and every other endpoint returns 503.
      The API never falsely claims readiness.

    - One ReplayManager holds one active ReplayRunner. The lock serialises
      /replay/advance so concurrent callers cannot interleave the buffer.
      Single-session by design; multi-session is out of scope for this
      prototype and can be added by keying runners on a session id.

    - Replay partitions are allowlisted by name ('threshold', 'validation',
      'attack'). No endpoint accepts an arbitrary filesystem path.

    - Label columns never reach inference. src.data.validation rejects
      them upstream; src.inference.validate rejects any request that does
      not name exactly the scaler's features in order.

    - Neutral wording: 'alert' means "score > frozen threshold". Every
      response that exposes 'alert' carries ALERT_INTERPRETATION.

Run:
    uvicorn src.api.main:app --host 127.0.0.1 --port 8000

    or for the standalone smoke test (no separate terminal needed):
    python src/api/main.py
"""

from __future__ import annotations
import json
import sys
import os
import pandas as pd
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
from typing import Optional

# Make `src` importable whether this file is run as a script
# (`python src/api/main.py`) or as a module
# (`uvicorn src.api.main:app`). Running a script adds the script's own
# directory to sys.path — not the project root — so we insert it here.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import (
    ALERT_INTERPRETATION,
    EVALUATION_DISCLAIMER,
    GROUND_TRUTH_DISCLAIMER,
    EvaluationEventLevel,
    EvaluationParity,
    EvaluationPerformance,
    EvaluationPointLevel,
    EvaluationSummaryResponse,
    GroundTruthResponse,
    GroundTruthWindow,
    HealthResponse,
    ModelInfoResponse,
    PredictRequest,
    PredictResponse,
    ReplayAdvanceBatchResponse,
    ReplayAdvanceResponse,
    ReplayResetResponse,
    ReplayStartRequest,
    ReplayStatus,
)
from src.data.ingestion import IngestionError, load_partition
from src.data.validation import DataIntegrityError, validate_partition
from src.inference.frozen_bundle import (
    FrozenBundle,
    FrozenBundleError,
    load_frozen_bundle,
)
from src.inference.validate import ValidationError, validate_inference_request
from src.replay.runner import ReplayError, ReplayRunner


PARQUET_ROOT = PROJECT_ROOT / "data" / "parquet"
MODEL_ID = "tcn_autoencoder_nb08_frozen"
NB13_VERDICT_JSON = PROJECT_ROOT / "nb13_artifacts" / "cell9_final_verdict.json"
NB13_PARITY_JSON  = PROJECT_ROOT / "nb13_artifacts" / "cell3_test_b.json"
NB09_SCENARIOS_CSV = PROJECT_ROOT / "nb09_artifacts" / "attack_scenarios_matching_dates.csv"


# --- App state -----------------------------------------------------------

class _AppState:
    """Holds the loaded bundle and the single active replay runner."""

    def __init__(self) -> None:
        self.bundle: Optional[FrozenBundle] = None
        self.bundle_error: Optional[str] = None
        self.runner: Optional[ReplayRunner] = None
        self.lock = Lock()


_state = _AppState()


# --- Lifespan: load the frozen bundle exactly once -----------------------

@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        _state.bundle = load_frozen_bundle(PROJECT_ROOT)
        _state.bundle_error = None
    except FrozenBundleError as e:
        _state.bundle = None
        _state.bundle_error = str(e)
    yield
    # No teardown: the bundle is read-only and short-lived per process.


app = FastAPI(
    title="SWaT Process Anomaly Monitoring Prototype",
    description=(
        "Historical-replay inference API for the frozen TCN Autoencoder. "
        "Alerts are model outputs that require human review; they are "
        "not confirmed attacks, equipment failures, or safety events."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# Localhost dev origins only. The frontend's dev server will call this API.
# No credentials, no wildcard, no production domain until we deploy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    # Render-hosted frontends: match any *.onrender.com subdomain so
    # preview builds and the production site both work without a second
    # backend redeploy every time the frontend URL changes.
    allow_origin_regex=r"https://[\w-]+\.onrender\.com",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Helpers -------------------------------------------------------------

def _require_bundle() -> FrozenBundle:
    if _state.bundle is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model bundle not ready. "
                f"{_state.bundle_error or 'FrozenBundle failed to load.'}"
            ),
        )
    return _state.bundle


def _require_runner() -> ReplayRunner:
    if _state.runner is None:
        raise HTTPException(
            status_code=404,
            detail="No replay active. POST /replay/start first.",
        )
    return _state.runner


def _status_from_runner(runner: ReplayRunner) -> ReplayStatus:
    st = runner.status()
    return ReplayStatus(
        partition=st["partition"],
        total_rows=st["total_rows"],
        position=st["position"],
        window_filled=st["window_filled"],
        warmup_remaining=st["warmup_remaining"],
        total_scored=st["total_scored"],
        alerts_emitted=st["alerts_emitted"],
        last_timestamp=st["last_timestamp"],
        last_score=st["last_score"],
        last_alert=st["last_alert"],
        peak_score=st["peak_score"],
        threshold=st["threshold"],
        finished=st["finished"],
    )


# --- Endpoints -----------------------------------------------------------

@app.get("/")
def root() -> dict[str, str]:
    """Friendly pointer when the backend URL is visited in a browser.

    The dashboard UI is served from a separate frontend service.
    This route exists only so visiting the API root returns useful
    information instead of a bare 404.
    """
    return {
        "service": "SWaT Process Anomaly Monitor — backend API",
        "docs": "/docs",
        "health": "/health",
        "note": (
            "This is the backend API, not the dashboard. "
            "The dashboard is served from a separate frontend URL. "
            "Visit /docs for the interactive API explorer."
        ),
    }

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Reports whether the model is loaded. Never reports success on failure."""
    if _state.bundle is None:
        return HealthResponse(
            status="not_ready",
            model_ready=False,
            message=(
                f"Model bundle failed to load: "
                f"{_state.bundle_error or 'unknown error'}"
            ),
        )
    return HealthResponse(
        status="ok",
        model_ready=True,
        message="Frozen TCN bundle loaded and ready.",
    )


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    """Public metadata for the loaded model. No filesystem paths."""
    bundle = _require_bundle()
    return ModelInfoResponse(
        method="TCN Autoencoder",
        window_size=bundle.window_size,
        n_features=bundle.n_features,
        feature_names=list(bundle.feature_names),
        threshold=bundle.threshold,
        threshold_source=bundle.metadata["threshold_source"],
        threshold_procedure=bundle.metadata.get("threshold_procedure") or "",
        score_convention="mean over (T, F) of squared reconstruction error",
        warmup_observations=bundle.window_size - 1,
        checkpoint_size_bytes=bundle.metadata["checkpoint_bytes"],
        param_count=bundle.metadata["param_count"],
        device=bundle.metadata["device"],
        model_id=MODEL_ID,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    """Score one (window_size, n_features) window. Validates, scales, scores."""
    bundle = _require_bundle()
    try:
        window = validate_inference_request(
            feature_names=req.feature_names,
            values=req.values,
            expected_features=bundle.feature_names,
            window_size=bundle.window_size,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    score, alert = bundle.predict(window)
    return PredictResponse(
        score=score,
        threshold=bundle.threshold,
        alert=alert,
        timestamp=req.timestamp.isoformat() if req.timestamp else None,
        window_shape=(bundle.window_size, bundle.n_features),
        interpretation=ALERT_INTERPRETATION,
    )


@app.post("/replay/start", response_model=ReplayResetResponse)
def replay_start(req: ReplayStartRequest) -> ReplayResetResponse:
    """Create a fresh replay runner on the requested partition."""
    bundle = _require_bundle()
    with _state.lock:
        try:
            df = load_partition(PARQUET_ROOT, req.partition, bundle.feature_names)
            validate_partition(df, req.partition, bundle.feature_names)
        except (IngestionError, DataIntegrityError) as e:
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Replay data unavailable: {e} "
                    "The parquet files must be present at data/parquet/. "
                    "Run scripts/convert_to_parquet.py with a permitted "
                    "SWaT copy."
                ),
            )
        _state.runner = ReplayRunner(bundle, df, req.partition)
        return ReplayResetResponse(
            reset=True,
            status=_status_from_runner(_state.runner),
        )


@app.get("/replay/status", response_model=ReplayStatus)
def replay_status() -> ReplayStatus:
    """Current runner state, or 404 if no replay has been started."""
    with _state.lock:
        return _status_from_runner(_require_runner())


@app.post("/replay/advance", response_model=ReplayAdvanceResponse)
def replay_advance() -> ReplayAdvanceResponse:
    """Consume one row. Serialised by the lock to prevent buffer races."""
    bundle = _require_bundle()
    with _state.lock:
        runner = _require_runner()
        try:
            result = runner.advance()
        except ReplayError as e:
            raise HTTPException(status_code=500, detail=str(e))
        return ReplayAdvanceResponse(
            advanced=result.advanced,
            finished=result.finished,
            position=result.position,
            end_index=result.end_index,
            timestamp=result.timestamp,
            score=result.score,
            alert=result.alert,
            window_filled=result.window_filled,
            warmup_remaining=result.warmup_remaining,
            threshold=result.threshold,
            observation=result.observation,
            feature_residuals=result.residuals,
            status=_status_from_runner(runner),
        )

@app.get("/ground-truth-windows", response_model=GroundTruthResponse)
def ground_truth_windows() -> GroundTruthResponse:
    """Retrospective attack scenario windows, for visual overlay only.

    Labels are NOT used by inference. This endpoint exists solely so the
    frontend can shade known attack periods on the timeline. It is never
    called by /predict or /replay/advance, and the runner never sees it.
    """
    if not NB09_SCENARIOS_CSV.is_file():
        raise HTTPException(
            status_code=503,
            detail=(
                "Ground-truth scenario windows not available. "
                "Expected nb09_artifacts/attack_scenarios_matching_dates.csv."
            ),
        )

    try:
        df = pd.read_csv(NB09_SCENARIOS_CSV)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not read ground-truth scenario file: {e}",
        )

    required = {"start_time", "end_time", "attack_id"}
    missing = required - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Ground-truth scenario file missing columns: "
                f"{sorted(missing)}."
            ),
        )

    windows: list[GroundTruthWindow] = []
    for _, row in df.iterrows():
        start = pd.to_datetime(row["start_time"], errors="coerce")
        end = pd.to_datetime(row["end_time"], errors="coerce")
        sid = row["attack_id"]
        if pd.isna(start) or pd.isna(end) or pd.isna(sid) or end <= start:
            continue
        windows.append(
            GroundTruthWindow(
                scenario_id=int(sid),
                start=start.strftime("%Y-%m-%d %H:%M:%S"),
                end=end.strftime("%Y-%m-%d %H:%M:%S"),
            )
        )

    windows.sort(key=lambda w: w.start)

    return GroundTruthResponse(
        partition="attack",
        source="nb09_artifacts/attack_scenarios_matching_dates.csv",
        disclaimer=GROUND_TRUTH_DISCLAIMER,
        windows=windows,
    )

@app.post("/replay/advance-batch", response_model=ReplayAdvanceBatchResponse)
def replay_advance_batch(n: int = 5) -> ReplayAdvanceBatchResponse:
    """Consume up to n rows in one request. n is bounded to prevent abuse.

    Returns the full list of intermediate results so the frontend can
    accumulate every scored point. Stops early if the partition finishes.
    """
    if n < 1 or n > 100:
        raise HTTPException(
            status_code=422,
            detail="n must be between 1 and 100.",
        )
    _require_bundle()
    with _state.lock:
        runner = _require_runner()
        results: list[ReplayAdvanceResponse] = []
        for _ in range(n):
            try:
                result = runner.advance()
            except ReplayError as e:
                raise HTTPException(status_code=500, detail=str(e))
            results.append(
                ReplayAdvanceResponse(
                    advanced=result.advanced,
                    finished=result.finished,
                    position=result.position,
                    end_index=result.end_index,
                    timestamp=result.timestamp,
                    score=result.score,
                    alert=result.alert,
                    window_filled=result.window_filled,
                    warmup_remaining=result.warmup_remaining,
                    threshold=result.threshold,
                    observation=result.observation,
                    feature_residuals=result.residuals,
                    status=_status_from_runner(runner),
                )
            )
            if result.finished:
                break
        return ReplayAdvanceBatchResponse(
            advanced=len(results),
            finished=runner.status()["finished"],
            results=results,
        )

@app.get("/evaluation-summary", response_model=EvaluationSummaryResponse)
def evaluation_summary() -> EvaluationSummaryResponse:
    """Retrospective benchmark numbers, read from verified NB13 artifacts."""
    bundle = _require_bundle()

    if not NB13_VERDICT_JSON.is_file() or not NB13_PARITY_JSON.is_file():
        raise HTTPException(
            status_code=503,
            detail=(
                "Evaluation artifacts not available. "
                "Expected nb13_artifacts/cell9_final_verdict.json and "
                "nb13_artifacts/cell3_test_b.json."
            ),
        )

    try:
        verdict = json.loads(NB13_VERDICT_JSON.read_text(encoding="utf-8"))
        parity  = json.loads(NB13_PARITY_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not read evaluation artifacts: {e}",
        )

    pins = verdict.get("numeric_pins", {})
    partitions = parity.get("partitions", {})
    n_sequences = int(sum(
        int(p.get("n_sequences", 0)) for p in partitions.values()
    ))

    try:
        return EvaluationSummaryResponse(
            source_artifact="nb13_artifacts/cell9_final_verdict.json "
                          "+ nb13_artifacts/cell3_test_b.json",
            decision=str(verdict["decision"]),
            method="TCN Autoencoder",
            window_size=bundle.window_size,
            threshold=bundle.threshold,
            parity=EvaluationParity(
                n_sequences=n_sequences,
                max_abs_diff_score=float(pins["test_b_max_abs_diff_overall"]),
                flag_disagreements=int(pins["test_b_flag_disagreements_total"]),
            ),
            point_level=EvaluationPointLevel(
                validation_fp_count=int(pins["test_d_validation_fp"]),
                attack_tp_count=int(pins["test_d_attack_tp"]),
                validation_total=int(partitions["validation"]["n_sequences"]),
                attack_total=int(partitions["attack"]["n_sequences"]),
            ),
            event_level=EvaluationEventLevel(
                scenarios_total=36,
                scenarios_detected=int(pins["test_e_scenarios_detected"]),
                scenarios_missed=int(pins["test_e_scenarios_missed"]),
                median_delay_s=float(pins["test_e_median_delay_s"]),
                p90_delay_s=float(pins["test_e_p90_delay_s"]),
                max_delay_s=float(pins["test_e_max_delay_s"]),
                validation_fp_count=int(pins["test_e_validation_fp_count"]),
                validation_fp_periods=int(pins["test_e_validation_fp_periods"]),
                period_gap_limit_s=1.5,
            ),
            performance=EvaluationPerformance(
                batch1_median_ms=float(pins["test_f_batch1_median_ms"]),
                batch1_utilization_pct_1hz=float(
                    pins["test_f_batch1_utilization_pct_1hz"]
                ),
                batch1_throughput_seqs_per_s=float(
                    pins["test_f_batch1_throughput_seqs_per_s"]
                ),
                batch512_median_ms=float(pins["test_f_batch512_median_ms"]),
                batch512_throughput_seqs_per_s=float(
                    pins["test_f_batch512_throughput_seqs_per_s"]
                ),
            ),
            disclaimer=EVALUATION_DISCLAIMER,
        )
    except KeyError as e:
        raise HTTPException(
            status_code=503,
            detail=(
                f"NB13 artifact missing expected field {e!r}. "
                "Re-run the notebook's final report cell to regenerate "
                "cell9_final_verdict.json before serving /evaluation-summary."
            ),
        )


@app.post("/replay/reset", response_model=ReplayResetResponse)
def replay_reset() -> ReplayResetResponse:
    """Restart the current runner from row 0. Partition unchanged."""
    with _state.lock:
        runner = _require_runner()
        runner.reset()
        return ReplayResetResponse(
            reset=True,
            status=_status_from_runner(runner),
        )


# --- Standalone smoke test ----------------------------------------------
#
# Run from the project root with no uvicorn terminal needed:
#     python src/api/main.py
#
# Exercises every endpoint via FastAPI's TestClient. Verifies:
#   A1  GET  /health            -> 200, model_ready=True, status='ok'
#   A2  GET  /model-info        -> 200, threshold matches frozen bundle
#   A3  POST /predict (bad)     -> 422, validation error surfaced
#   A4  POST /predict (good)    -> 200, score in [0, ~], alert is bool
#   A5  POST /replay/start      -> 200, partition matches request
#   A6  POST /replay/advance    -> first 29 are warm-up (score=None),
#                                  the 30th produces a score matching NB13
#   A7  POST /replay/reset      -> position back to 0
#   A8  POST /replay/start bad  -> 422 for unsupported partition
#
# Uses synthetic fixtures only for /predict (labeled as such). Replay uses
# the real SWaT partitions, which is the point of the smoke test.

if __name__ == "__main__":
    try:
        from fastapi.testclient import TestClient
    except ImportError as e:
        print(f"ERROR: {e}")
        print("Install with: pip install 'httpx>=0.24'")
        sys.exit(1)

    import numpy as np

    print("=" * 72)
    print("main.py — standalone smoke test (via FastAPI TestClient)")
    print("=" * 72)

    ok = True

    def _check(label: str, condition: bool, detail: str = "") -> None:
        nonlocal_ok[0] = nonlocal_ok[0] and condition
        status = "PASS" if condition else "ISSUE"
        line = f"  [{label}] {status}"
        if detail:
            line += f"   {detail}"
        print(line)

    nonlocal_ok = [True]

    with TestClient(app) as client:
        # A1
        r = client.get("/health")
        j = r.json()
        _check(
            "A1", r.status_code == 200 and j["model_ready"] is True,
            f"status={r.status_code} model_ready={j.get('model_ready')}",
        )

        # A2
        r = client.get("/model-info")
        j = r.json()
        a2 = (
            r.status_code == 200
            and j["threshold"] == 0.003906734725460411
            and j["window_size"] == 30
            and j["n_features"] == 42
            and j["warmup_observations"] == 29
            and j["param_count"] == 40_554
        )
        _check(
            "A2", a2,
            f"threshold={j.get('threshold')} warmup={j.get('warmup_observations')}",
        )
        features = j["feature_names"]

        # A3: bad /predict — wrong feature list
        r = client.post("/predict", json={
            "feature_names": ["NOT_A_SENSOR"],
            "values": [[0.0]],
        })
        _check(
            "A3", r.status_code == 422,
            f"status={r.status_code} detail={r.json().get('detail', '')[:60]}",
        )

        # A4: good /predict — synthetic zero window (labeled synthetic)
        r = client.post("/predict", json={
            "feature_names": features,
            "values": [[0.0] * 42 for _ in range(30)],
            "timestamp": "2016-01-01T02:23:47",
        })
        j = r.json()
        a4 = (
            r.status_code == 200
            and isinstance(j.get("score"), float)
            and j["score"] >= 0.0
            and isinstance(j.get("alert"), bool)
            and j["threshold"] == 0.003906734725460411
            and j["timestamp"] == "2016-01-01T02:23:47"
        )
        _check(
            "A4", a4,
            f"score={j.get('score')!r} alert={j.get('alert')}",
        )

        # A5: replay start
        r = client.post("/replay/start", json={"partition": "threshold"})
        j = r.json()
        a5 = (
            r.status_code == 200
            and j["status"]["partition"] == "threshold"
            and j["status"]["position"] == 0
            and j["status"]["total_rows"] == 47_437
        )
        _check(
            "A5", a5,
            f"partition={j.get('status', {}).get('partition')} total={j.get('status', {}).get('total_rows')}",
        )

        # A6: advance 30 times; first 29 are warm-up, 30th scores
        warmup_scores_none = True
        score_30 = None
        timestamp_30 = None
        for i in range(30):
            r = client.post("/replay/advance")
            j = r.json()
            if i < 29:
                if j["score"] is not None:
                    warmup_scores_none = False
            else:
                score_30 = j["score"]
                timestamp_30 = j["timestamp"]
        a6 = (
            warmup_scores_none
            and score_30 is not None
            and abs(score_30 - 0.0007158350781537592) < 1e-9
            and timestamp_30 == "2016-01-01 02:23:47"
        )
        _check(
            "A6", a6,
            f"warmup_clean={warmup_scores_none} score_30={score_30!r} ts={timestamp_30}",
        )

        # A7: reset
        r = client.post("/replay/reset")
        j = r.json()
        a7 = (
            r.status_code == 200
            and j["status"]["position"] == 0
            and j["status"]["last_timestamp"] is None
            and j["status"]["total_scored"] == 0
        )
        _check(
            "A7", a7,
            f"position={j.get('status', {}).get('position')} total_scored={j.get('status', {}).get('total_scored')}",
        )

        # A8: bad replay start
        r = client.post("/replay/start", json={"partition": "train"})
        _check(
            "A8", r.status_code == 422,
            f"status={r.status_code}",
        )

        # A10: ground-truth windows (retrospective overlay data)
        r = client.get("/ground-truth-windows")
        j = r.json()
        a10 = (
            r.status_code == 503
            or (r.status_code == 200 and len(j.get("windows", [])) >= 1)
        )
        _check(
            "A10", a10,
            f"status={r.status_code} windows={len(j.get('windows', [])) if r.status_code == 200 else 0}",
        )


        # A9: evaluation summary reads from NB13 artifacts
        r = client.get("/evaluation-summary")
        j = r.json()
        a9 = (
            r.status_code == 200
            and j["decision"] == "GO"
            and j["parity"]["max_abs_diff_score"] <= 5.22e-8
            and j["parity"]["flag_disagreements"] == 0
            and j["point_level"]["validation_fp_count"] == 2528
            and j["point_level"]["attack_tp_count"] == 43345
            and j["event_level"]["scenarios_detected"] == 28
            and j["event_level"]["scenarios_missed"] == 8
            and j["event_level"]["validation_fp_periods"] == 73
            and j["threshold"] == 0.003906734725460411
        )
        _check(
            "A9", a9,
            f"decision={j.get('decision')} "
            f"scenarios={j.get('event_level', {}).get('scenarios_detected')}"
            f"/36 fp_periods={j.get('event_level', {}).get('validation_fp_periods')}",
        )

    print("\n" + "=" * 72)
    print(f"Overall: {'PASS' if nonlocal_ok[0] else 'ISSUE'}")
    print("=" * 72)
    sys.exit(0 if nonlocal_ok[0] else 1)