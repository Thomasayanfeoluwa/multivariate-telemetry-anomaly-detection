"""
Stateful historical-replay runner for one SWaT partition.

Replays a validated DataFrame row-by-row, maintaining a deque(maxlen=30)
buffer. Emits one (timestamp, score, alert) result per arriving observation
once the warm-up period has passed.

Faithful to NB13 Cell 4:
    - Warm-up: first scored observation is at end-index 29 (the 30th row).
      Rows 0..28 fill the buffer only.
    - Boundary reset: a fresh ReplayRunner starts with an empty buffer and
      no last-timestamp. It never chains state from any prior runner. This
      is how NB13 verified partition isolation.
    - Strict chronological order: timestamps must strictly increase.
    - Label isolation: the DataFrame must not carry a label column
      (enforced upstream by src.data.validation.validate_partition).
    - Score parity: scores are produced by FrozenBundle.predict, the
      exact same path used by POST /predict. NB13 verified this path
      reproduces the frozen NB08 scores within 5.215e-08 max abs diff.

The runner does NOT load CSVs and does NOT validate dataset invariants.
Its contract is: caller supplies a DataFrame that validate_partition has
already accepted. Its job is one thing — replay it chronologically.
"""

from __future__ import annotations

import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

# Make `src` importable whether this file is run as a script
# (`python src/replay/runner.py`) or as a module (`python -m src.replay.runner`).
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.inference.frozen_bundle import FrozenBundle


SUPPORTED_PARTITIONS = ("threshold", "validation", "attack")


class ReplayError(RuntimeError):
    """Raised on misuse of ReplayRunner (bad partition, malformed df)."""


@dataclass
class ReplayResult:
    """One advance() result. All fields JSON-safe."""
    advanced: bool
    finished: bool
    position: int          # 0-based row index of the just-consumed row
    end_index: int         # same as position; named for parity with NB13 alert record
    timestamp: Optional[str]
    score: Optional[float]  # None during warm-up
    alert: Optional[bool]   # None during warm-up
    window_filled: bool
    warmup_remaining: int
    threshold: float
    observation: Optional[dict[str, float]] = None  # current row's feature values

    def as_dict(self) -> dict[str, Any]:
        return {
            "advanced": self.advanced,
            "finished": self.finished,
            "position": self.position,
            "end_index": self.end_index,
            "timestamp": self.timestamp,
            "score": self.score,
            "alert": self.alert,
            "window_filled": self.window_filled,
            "warmup_remaining": self.warmup_remaining,
            "threshold": self.threshold,
            "observation": self.observation,
        }


class ReplayRunner:
    """
    Stateful, single-partition replay. Not thread-safe; use one instance per
    (session, partition). Call reset() to restart from row 0.
    """

    def __init__(self, bundle: FrozenBundle, df: pd.DataFrame, partition: str):
        if partition not in SUPPORTED_PARTITIONS:
            raise ReplayError(
                f"Unsupported partition {partition!r}. "
                f"Must be one of {SUPPORTED_PARTITIONS}."
            )
        if not isinstance(df, pd.DataFrame) or len(df) == 0:
            raise ReplayError("df must be a non-empty pandas DataFrame.")

        expected_cols = ["timestamp"] + list(bundle.feature_names)
        actual_cols = list(df.columns)
        if actual_cols != expected_cols:
            raise ReplayError(
                f"df columns do not match bundle.feature_names in order. "
                f"Expected ['timestamp', <{len(bundle.feature_names)} features>], "
                f"got {actual_cols[:3]}{'...' if len(actual_cols) > 3 else ''}."
            )
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            raise ReplayError("df['timestamp'] must be datetime64 dtype.")

        self._bundle = bundle
        self._df = df
        self._partition = partition
        self._features = list(bundle.feature_names)
        self._n_rows = len(df)
        self._window_size = bundle.window_size
        self._threshold = bundle.threshold

        # Pre-extract the feature block as float32 for fast per-row access.
        self._features_np = df[self._features].to_numpy(dtype=np.float32)

        self._reset_state()

    def _reset_state(self) -> None:
        self._buf: deque[np.ndarray] = deque(maxlen=self._window_size)
        self._pos: int = 0
        self._last_ts: Optional[pd.Timestamp] = None
        self._alerts_emitted: int = 0
        self._total_scored: int = 0
        self._last_score: Optional[float] = None
        self._last_alert: Optional[bool] = None
        self._peak_score: Optional[float] = None

    # ---- public API ---------------------------------------------------

    def advance(self) -> ReplayResult:
        """
        Consume the next row and return one result.

        - During warm-up (buffer has fewer than window_size rows),
          score and alert are None.
        - Once window_size rows are buffered, one score is produced via
          FrozenBundle.predict.
        - When the partition is exhausted, returns advanced=False,
          finished=True and last-known context; does not raise.
        """
        if self._pos >= self._n_rows:
            last_row = self._features_np[self._n_rows - 1]
            return ReplayResult(
                advanced=False,
                finished=True,
                position=self._n_rows - 1,
                end_index=self._n_rows - 1,
                timestamp=str(self._last_ts) if self._last_ts is not None else None,
                score=self._last_score,
                alert=self._last_alert,
                window_filled=len(self._buf) == self._window_size,
                warmup_remaining=max(0, self._window_size - len(self._buf)),
                threshold=self._threshold,
                observation={
                    name: float(last_row[i])
                    for i, name in enumerate(self._features)
                },
            )
        ts = pd.Timestamp(self._df["timestamp"].iloc[self._pos])
        if self._last_ts is not None and ts <= self._last_ts:
            raise ReplayError(
                f"Timestamp {ts!r} at row {self._pos} is not strictly "
                f"later than last consumed {self._last_ts!r}. "
                f"DataFrame violates the chronological contract."
            )

        row = self._features_np[self._pos]
        self._buf.append(row)

        score: Optional[float] = None
        alert: Optional[bool] = None
        if len(self._buf) == self._window_size:
            window = np.stack(self._buf, axis=0)
            score, alert = self._bundle.predict(window)
            self._total_scored += 1
            if alert:
                self._alerts_emitted += 1
            if self._peak_score is None or score > self._peak_score:
                self._peak_score = score

        self._last_score = score
        self._last_alert = alert
        self._last_ts = ts
        position = self._pos
        self._pos += 1

        return ReplayResult(
            advanced=True,
            finished=(self._pos >= self._n_rows),
            position=position,
            end_index=position,
            timestamp=str(ts),
            score=score,
            alert=alert,
            window_filled=len(self._buf) == self._window_size,
            warmup_remaining=max(0, self._window_size - len(self._buf)),
            threshold=self._threshold,
            observation={
                name: float(row[i])
                for i, name in enumerate(self._features)
            },
        )

    def reset(self) -> None:
        """Discard buffer, position, and counters. Same partition."""
        self._reset_state()

    def status(self) -> dict[str, Any]:
        return {
            "partition": self._partition,
            "total_rows": self._n_rows,
            "position": self._pos,
            "rows_consumed": self._pos,
            "window_size": self._window_size,
            "window_filled": len(self._buf) == self._window_size,
            "warmup_remaining": max(0, self._window_size - len(self._buf)),
            "total_scored": self._total_scored,
            "alerts_emitted": self._alerts_emitted,
            "last_timestamp": str(self._last_ts) if self._last_ts is not None else None,
            "last_score": self._last_score,
            "last_alert": self._last_alert,
            "peak_score": self._peak_score,
            "threshold": self._threshold,
            "finished": self._pos >= self._n_rows,
        }


# --- Standalone smoke test -----------------------------------------------
#
# Run from the project root:
#     python src/replay/runner.py
#
# Loads the threshold and validation partitions via src.data.ingestion,
# validates them via src.data.validation, and checks:
#   T1  fresh runner starts with empty buffer (warm-up pending)
#   T2  first scored result is at position 29 (end of warm-up)
#   T3  first 500 scored results match frozen NB08 scores within 1e-6,
#       with 0 flag disagreements (NB13 score-parity contract)
#   T4  reset() restores initial state
#   T5  after reset(), re-advance yields the identical first score
#   T6  a fresh runner on validation starts with empty buffer (boundary reset)

if __name__ == "__main__":
    from src.data.ingestion import load_partition
    from src.data.validation import validate_partition
    from src.inference.frozen_bundle import load_frozen_bundle

    print("=" * 72)
    print("runner.py — standalone smoke test")
    print("=" * 72)

    csv_root = _PROJECT_ROOT / "data" / "raw"

    print("\n  Loading frozen bundle ...")
    bundle = load_frozen_bundle(_PROJECT_ROOT)
    print(f"    threshold:   {bundle.threshold!r}")
    print(f"    window:      {bundle.window_size}")
    print(f"    features:    {bundle.n_features}")

    print("\n  Loading + validating threshold partition ...")
    thr_df = load_partition(csv_root, "threshold", bundle.feature_names)
    validate_partition(thr_df, "threshold", bundle.feature_names,
                       expected_rows=47_437)
    print(f"    rows: {len(thr_df):,}")

    print("\n  Loading + validating validation partition ...")
    val_df = load_partition(csv_root, "validation", bundle.feature_names)
    validate_partition(val_df, "validation", bundle.feature_names,
                       expected_rows=79_060)
    print(f"    rows: {len(val_df):,}")

    with np.load(_PROJECT_ROOT / "nb08_artifacts" / "final_sequence_scores.npz") as f:
        frozen_thr = f["tcn_threshold_seq_scores"].copy()

    N_ADVANCE = 500
    overall = True

    # --- T1 ---
    print("\n" + "-" * 72)
    print("T1 — fresh runner initial state (warm-up pending)")
    print("-" * 72)
    runner = ReplayRunner(bundle, thr_df, "threshold")
    st = runner.status()
    t1_ok = (
        st["position"] == 0
        and st["window_filled"] is False
        and st["warmup_remaining"] == bundle.window_size
        and st["last_timestamp"] is None
        and st["rows_consumed"] == 0
    )
    print(f"  position:          {st['position']}")
    print(f"  window_filled:     {st['window_filled']}")
    print(f"  warmup_remaining:  {st['warmup_remaining']}")
    print(f"  last_timestamp:    {st['last_timestamp']}")
    print(f"  status_ok:         {'PASS' if t1_ok else 'ISSUE'}")
    overall = overall and t1_ok

    # --- T2 ---
    print("\n" + "-" * 72)
    print(f"T2 — advance {N_ADVANCE} rows; first score must land at position 29")
    print("-" * 72)
    results = [runner.advance() for _ in range(N_ADVANCE)]
    first_scored_idx = next(
        (i for i, r in enumerate(results) if r.score is not None), None
    )
    t2_ok = (
        first_scored_idx == 29
        and results[29].position == 29
        and results[29].end_index == 29
        and results[29].window_filled is True
    )
    print(f"  first scored result index: {first_scored_idx}")
    print(f"  results[29].position:      {results[29].position}")
    print(f"  results[29].timestamp:     {results[29].timestamp}")
    print(f"  first_scored_ok:           {'PASS' if t2_ok else 'ISSUE'}")
    overall = overall and t2_ok

    # --- T3 ---
    print("\n" + "-" * 72)
    print(f"T3 — score parity vs frozen NB08 (first {N_ADVANCE} scored)")
    print("-" * 72)
    scored = [r for r in results if r.score is not None]
    scores = np.array([r.score for r in scored], dtype=np.float64)
    flags = np.array([bool(r.alert) for r in scored], dtype=bool)
    frozen = frozen_thr[:len(scores)].astype(np.float64)
    frozen_flags = frozen > bundle.threshold
    diff = np.abs(scores - frozen)
    max_diff = float(diff.max())
    mean_diff = float(diff.mean())
    n_flag_mismatch = int((flags != frozen_flags).sum())
    t3_ok = (max_diff < 1e-6) and (n_flag_mismatch == 0)
    print(f"  n scored:         {len(scored)}")
    print(f"  max |diff|:       {max_diff:.3e}")
    print(f"  mean |diff|:      {mean_diff:.3e}")
    print(f"  flag mismatches:  {n_flag_mismatch}")
    print(f"  parity_ok:        {'PASS' if t3_ok else 'ISSUE'}")
    overall = overall and t3_ok

    # --- T4 ---
    print("\n" + "-" * 72)
    print("T4 — reset() restores initial state")
    print("-" * 72)
    runner.reset()
    st = runner.status()
    t4_ok = (
        st["position"] == 0
        and st["window_filled"] is False
        and st["last_timestamp"] is None
        and st["rows_consumed"] == 0
        and st["alerts_emitted"] == 0
        and st["total_scored"] == 0
    )
    print(f"  position:          {st['position']}")
    print(f"  window_filled:     {st['window_filled']}")
    print(f"  last_timestamp:    {st['last_timestamp']}")
    print(f"  total_scored:      {st['total_scored']}")
    print(f"  reset_ok:          {'PASS' if t4_ok else 'ISSUE'}")
    overall = overall and t4_ok

    # --- T5 ---
    print("\n" + "-" * 72)
    print("T5 — after reset, re-advance yields identical first score (determinism)")
    print("-" * 72)
    first_after_reset: Optional[float] = None
    for _ in range(N_ADVANCE):
        r = runner.advance()
        if r.score is not None and first_after_reset is None:
            first_after_reset = r.score
    t5_ok = (
        first_after_reset is not None
        and abs(first_after_reset - float(scores[0])) < 1e-12
    )
    print(f"  first score (original):    {float(scores[0])!r}")
    print(f"  first score (after reset): {first_after_reset!r}")
    print(f"  determinism_ok:            {'PASS' if t5_ok else 'ISSUE'}")
    overall = overall and t5_ok

    # --- T6 ---
    print("\n" + "-" * 72)
    print("T6 — boundary reset: fresh runner on validation does not chain")
    print("-" * 72)
    val_runner = ReplayRunner(bundle, val_df, "validation")
    st = val_runner.status()
    t6_ok = (
        st["position"] == 0
        and st["window_filled"] is False
        and st["last_timestamp"] is None
    )
    print(f"  validation position:  {st['position']}")
    print(f"  validation last_ts:   {st['last_timestamp']}")
    print(f"  boundary_ok:          {'PASS' if t6_ok else 'ISSUE'}")
    overall = overall and t6_ok

    print("\n" + "=" * 72)
    print(f"Overall: {'PASS' if overall else 'ISSUE'}")
    print("=" * 72)
    sys.exit(0 if overall else 1)