"""
Validation policy for inference requests.

Faithful port of Notebook 13 Test G (Cell 8), with the G2 diagnostic-message
fix flagged in NB13 Cell 8's result record: split "same set, different order"
from "different set" so the error message names the actual problem.

Policy (unchanged from NB13):
    1. feature_names must equal expected_features exactly, in order.
    2. values must be a 2D array of shape (window_size, n_features).
    3. Every cell must be numeric and finite (no NaN, no inf).
    4. In a stateful buffer context, the incoming timestamp must be
       strictly later than the last buffered timestamp.

Every rejection raises ValidationError with a non-empty, human-readable
message. The validator never imputes, reorders, or silently accepts
malformed input.

This module is bundle-agnostic: it takes expected_features and window_size
as parameters so it can be tested independently of the loaded model. The
FastAPI layer supplies these from FrozenBundle.

Synthetic fixtures used below are clearly identified as test data, not
SWaT observations.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd


class ValidationError(ValueError):
    """Raised on any malformed inference request. Maps to HTTP 422."""


def _format_list(items: Sequence[Any], limit: int = 5) -> str:
    items = list(items)
    if not items:
        return "[]"
    shown = items[:limit]
    suffix = "..." if len(items) > limit else ""
    return f"{shown}{suffix}"


def validate_features(
    feature_names: Any,
    expected_features: Iterable[str],
) -> None:
    """Reject anything that isn't exactly `expected_features`, in order.

    Branches, in order (fixes NB13 G2 message imprecision):
      1. Wrong type (not list/tuple)
      2. Wrong length
      3. Same set, wrong order   -> "wrong order" message
      4. Different set           -> "missing + unexpected names" message
    """
    if not isinstance(feature_names, (list, tuple)):
        raise ValidationError(
            f"feature_names must be a list or tuple, "
            f"got {type(feature_names).__name__}."
        )

    expected = list(expected_features)
    names = list(feature_names)

    if len(names) != len(expected):
        missing = [f for f in expected if f not in names]
        unexpected = [f for f in names if f not in expected]
        raise ValidationError(
            f"Expected {len(expected)} features, got {len(names)}. "
            f"Missing: {_format_list(missing)}. "
            f"Unexpected: {_format_list(unexpected)}."
        )

    if names == expected:
        return

    if set(names) == set(expected):
        # Same set, wrong order — report first differing position
        for i, (got, want) in enumerate(zip(names, expected)):
            if got != want:
                raise ValidationError(
                    f"Feature names match the expected set but are in the "
                    f"wrong order. First difference at position {i}: "
                    f"expected '{want}', got '{got}'. "
                    f"Order must equal the scaler's feature_names_in_."
                )
        raise ValidationError(
            "Feature names match the expected set but are in the wrong order."
        )

    # Different set
    missing = sorted(set(expected) - set(names))
    unexpected = sorted(set(names) - set(expected))
    raise ValidationError(
        f"Feature names do not match the expected set. "
        f"Missing: {_format_list(missing)}. "
        f"Unexpected: {_format_list(unexpected)}."
    )


def validate_sequence_shape(
    values: Any,
    window_size: int,
    n_features: int,
) -> np.ndarray:
    """Reject anything that isn't a 2D array of shape (window_size, n_features)."""
    arr = np.asarray(values)
    if arr.ndim != 2:
        raise ValidationError(
            f"Sequence must be a 2D array, got {arr.ndim}D."
        )
    expected_shape = (window_size, n_features)
    if arr.shape != expected_shape:
        raise ValidationError(
            f"Expected sequence shape {expected_shape}, got {arr.shape}."
        )
    return arr


def validate_numeric_finite(arr: np.ndarray) -> np.ndarray:
    """Reject if any cell is non-numeric, NaN, or infinite.

    Returns a float32 ndarray of the same shape on success.
    On failure, raises ValidationError identifying the first offending cell.
    """
    try:
        numeric = np.asarray(arr, dtype=np.float32)
    except (TypeError, ValueError):
        # Slow path: identify first non-numeric cell for a useful diagnostic
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                v = arr[i, j]
                try:
                    float(v)
                except (TypeError, ValueError):
                    raise ValidationError(
                        f"Non-numeric value at position ({i}, {j}): {v!r}."
                    )
        raise  # unreachable under normal conditions

    finite = np.isfinite(numeric)
    if not finite.all():
        i, j = np.argwhere(~finite)[0]
        raw = arr[int(i), int(j)]
        raise ValidationError(
            f"Non-finite value at position ({int(i)}, {int(j)}): {raw!r}."
        )
    return numeric


def validate_inference_request(
    feature_names: Any,
    values: Any,
    expected_features: Iterable[str],
    window_size: int,
) -> np.ndarray:
    """Full validation pipeline. Returns (window_size, n_features) float32."""
    expected = list(expected_features)
    validate_features(feature_names, expected)
    arr = validate_sequence_shape(values, window_size, len(expected))
    return validate_numeric_finite(arr)


def validate_incoming_timestamp(
    new_ts: Any,
    last_ts: Any = None,
) -> pd.Timestamp:
    """Reject duplicate or out-of-order timestamps in a stateful buffer."""
    try:
        new_dt = pd.Timestamp(new_ts)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Invalid timestamp {new_ts!r}: {e}.")
    if pd.isna(new_dt):
        raise ValidationError(f"Timestamp {new_ts!r} parsed as NaT.")

    if last_ts is None:
        return new_dt

    try:
        last_dt = pd.Timestamp(last_ts)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Invalid last_timestamp {last_ts!r}: {e}.")
    if pd.isna(last_dt):
        raise ValidationError(f"Last timestamp {last_ts!r} parsed as NaT.")

    if new_dt == last_dt:
        raise ValidationError(
            f"Duplicate timestamp {new_ts!r} — incoming observation must "
            f"have a strictly later timestamp than the last buffered one."
        )
    if new_dt < last_dt:
        raise ValidationError(
            f"Out-of-order timestamp {new_ts!r} precedes last buffered "
            f"timestamp {last_dt!r}."
        )
    return new_dt


# --- Standalone smoke test (mirrors NB13 Cell 8) --------------------------
#
# Run:
#     python src/inference/validate.py
#
# Fixtures below are SYNTHETIC. They are not SWaT observations. They exist
# only to exercise the validator's accept/reject behaviour. Genuine SWaT
# data must not be embedded in this file.

if __name__ == "__main__":
    TEST_FEATURES = tuple(f"FEAT_{i:02d}" for i in range(42))
    TEST_WINDOW = 30

    results: list[dict] = []

    def _run(label: str, description: str, expected: str, fn) -> None:
        try:
            fn()
            actual = "ACCEPTED"
            detail = ""
        except ValidationError as e:
            actual = "REJECTED"
            detail = str(e)
        passed = actual == expected
        results.append({
            "label": label,
            "description": description,
            "expected": expected,
            "actual": actual,
            "detail": detail,
            "pass": passed,
        })
        status = "PASS" if passed else "FAIL"
        print(f"\n  [{label}] {description}")
        print(f"    expected: {expected}")
        print(f"    actual:   {actual}")
        if detail:
            print(f"    detail:   {detail}")
        print(f"    verdict:  {status}")

    base_window = np.zeros((TEST_WINDOW, len(TEST_FEATURES)), dtype=np.float32)

    def case_missing_feature():
        names = list(TEST_FEATURES[:-1])
        vals = np.zeros((TEST_WINDOW, len(names)), dtype=np.float32)
        validate_inference_request(names, vals, TEST_FEATURES, TEST_WINDOW)

    def case_unexpected_feature():
        names = list(TEST_FEATURES)
        names[0] = "NOT_A_SENSOR"
        validate_inference_request(names, base_window, TEST_FEATURES, TEST_WINDOW)

    def case_wrong_order():
        names = list(TEST_FEATURES)
        names[0], names[1] = names[1], names[0]
        validate_inference_request(names, base_window, TEST_FEATURES, TEST_WINDOW)

    def case_wrong_window():
        bad = np.zeros((TEST_WINDOW - 1, len(TEST_FEATURES)), dtype=np.float32)
        validate_inference_request(TEST_FEATURES, bad, TEST_FEATURES, TEST_WINDOW)

    def case_non_numeric():
        bad = np.zeros((TEST_WINDOW, len(TEST_FEATURES)), dtype=object)
        bad[5, 3] = "not_a_number"
        validate_inference_request(TEST_FEATURES, bad, TEST_FEATURES, TEST_WINDOW)

    def case_nan_value():
        bad = np.zeros((TEST_WINDOW, len(TEST_FEATURES)), dtype=object)
        bad[10, 20] = np.nan
        validate_inference_request(TEST_FEATURES, bad, TEST_FEATURES, TEST_WINDOW)

    def case_inf_value():
        bad = np.zeros((TEST_WINDOW, len(TEST_FEATURES)), dtype=object)
        bad[15, 5] = np.inf
        validate_inference_request(TEST_FEATURES, bad, TEST_FEATURES, TEST_WINDOW)

    def case_duplicate_ts():
        validate_incoming_timestamp("2016-01-01 12:00:00", "2016-01-01 12:00:00")

    def case_out_of_order_ts():
        validate_incoming_timestamp("2016-01-01 11:59:59", "2016-01-01 12:00:00")

    def case_control():
        validate_inference_request(
            TEST_FEATURES, base_window, TEST_FEATURES, TEST_WINDOW
        )
        validate_incoming_timestamp("2016-01-01 12:00:00", None)
        validate_incoming_timestamp("2016-01-01 12:00:01", "2016-01-01 12:00:00")

    print("=" * 72)
    print("validate.py — standalone smoke test")
    print("=" * 72)
    print(f"  Synthetic features: {len(TEST_FEATURES)}")
    print(f"  Synthetic window:   {TEST_WINDOW}")
    print("\n" + "-" * 72)
    print("Validation test cases (synthetic fixtures — not SWaT data)")
    print("-" * 72)

    _run("G1",  "missing required feature",            "REJECTED", case_missing_feature)
    _run("G2",  "unexpected feature name",              "REJECTED", case_unexpected_feature)
    _run("G3",  "wrong feature order (same set)",       "REJECTED", case_wrong_order)
    _run("G4",  "incorrect sequence length (29 rows)",  "REJECTED", case_wrong_window)
    _run("G5",  "non-numeric sensor value",             "REJECTED", case_non_numeric)
    _run("G6",  "NaN sensor value",                     "REJECTED", case_nan_value)
    _run("G7",  "infinite sensor value",                "REJECTED", case_inf_value)
    _run("G8",  "duplicate timestamp in buffer",        "REJECTED", case_duplicate_ts)
    _run("G9",  "out-of-order timestamp in buffer",     "REJECTED", case_out_of_order_ts)
    _run("G10", "well-formed control case",             "ACCEPTED", case_control)

    passed = sum(r["pass"] for r in results)
    total = len(results)
    print("\n" + "=" * 72)
    print(f"Overall: {'PASS' if passed == total else 'ISSUE'} ({passed}/{total})")
    print("=" * 72)
    raise SystemExit(0 if passed == total else 1)