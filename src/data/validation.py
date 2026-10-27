"""
Dataset-level invariant enforcement for loaded replay partitions.

Three kinds of validation live in this project, intentionally separated:

    src/data/validation.py      <- this file.
                                    Dataset invariants on a DataFrame
                                    (schema, monotonicity, dtype, NaN,
                                    no-label column). Consumed by the
                                    replay runner and by tests.

    src/inference/validate.py   HTTP request-payload validation at the
                                    FastAPI boundary (feature order,
                                    window shape, finiteness, timestamps
                                    in a stateful buffer). Maps to 422.

    src/data/ingestion.py       CSV I/O. Does not assert data integrity
                                    beyond what is required to read the
                                    file.

The runner MUST call validate_partition on every loaded slice — whether
the slice came from a CSV (via ingestion.py) or from a cached parquet.
This module is the single guarantee that a DataFrame is safe to score.

Invariants enforced (each verified against NB13):
    - Column order equals ['timestamp', *expected_features].
    - Row count matches expected_rows (if supplied).
    - timestamp column is datetime64 dtype and not NaT anywhere.
    - Timestamps are strictly increasing (no duplicates).
    - Every feature column has numeric dtype.
    - Every feature value is finite (no NaN, no inf).
    - No label column ('Normal/Attack' or 'label') is present.

Invariants NOT enforced here, deliberately:
    - 1 Hz cadence regularity. NB13 did not assert it, and doing so
      would over-reject legitimate data. Strict monotonicity is the
      correct guarantee.
    - Value ranges. The scaler handles distribution; no operating limits
      are known for the SWaT testbed, and inventing them would violate
      the deployment-plan constraints.
"""

from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pandas as pd


TIMESTAMP_COL = "timestamp"
FORBIDDEN_COLUMNS = ("Normal/Attack", "label")


class DataIntegrityError(ValueError):
    """Raised when a loaded partition violates a dataset invariant."""


def validate_partition(
    df: pd.DataFrame,
    partition: str,
    expected_features: Iterable[str],
    expected_rows: Optional[int] = None,
) -> pd.DataFrame:
    """Validate df as a replayable partition. Returns df unchanged on success.

    Parameters
    ----------
    df : pandas.DataFrame
        A DataFrame produced by ingestion.load_partition (or any other
        loader that promises the same schema).
    partition : str
        Label used in error messages ('threshold', 'validation', 'attack').
    expected_features : iterable of str
        The 42 feature names in scaler order (from FrozenBundle.feature_names).
    expected_rows : int, optional
        If supplied, len(df) must equal this value exactly.

    Raises
    ------
    DataIntegrityError
        On the first invariant violation, with a specific message.
    """
    expected_features = list(expected_features)
    if not expected_features:
        raise DataIntegrityError(
            f"{partition}: expected_features is empty."
        )

    if not isinstance(df, pd.DataFrame):
        raise DataIntegrityError(
            f"{partition}: expected a pandas DataFrame, got {type(df).__name__}."
        )

    if len(df) == 0:
        raise DataIntegrityError(f"{partition}: DataFrame is empty.")


    # 1. Forbidden (label) columns — check by name, not by position,
    #    because a caller may have accidentally retained them.
    actual_cols = list(df.columns)
    for forbidden in FORBIDDEN_COLUMNS:
        if forbidden in actual_cols:
            raise DataIntegrityError(
                f"{partition}: label column '{forbidden}' must not be "
                f"present in inference input."
            )
    # 2. Column set and order
    expected_cols = [TIMESTAMP_COL] + expected_features
    if actual_cols != expected_cols:
        missing = [c for c in expected_cols if c not in actual_cols]
        extra   = [c for c in actual_cols if c not in expected_cols]
        if not missing and not extra and set(actual_cols) == set(expected_cols):
            # Same set, wrong order
            for i, (got, want) in enumerate(zip(actual_cols, expected_cols)):
                if got != want:
                    raise DataIntegrityError(
                        f"{partition}: column order is wrong. "
                        f"First difference at position {i}: "
                        f"expected '{want}', got '{got}'."
                    )
        raise DataIntegrityError(
            f"{partition}: expected columns ['timestamp', <{len(expected_features)} "
            f"features>] in scaler order. "
            f"Missing: {missing[:5]}{'...' if len(missing) > 5 else ''}. "
            f"Extra:   {extra[:5]}{'...' if len(extra) > 5 else ''}."
        )

    # 3. Row count
    if expected_rows is not None and len(df) != expected_rows:
        raise DataIntegrityError(
            f"{partition}: row count {len(df):,} != expected {expected_rows:,}."
        )

    # 4. Timestamp dtype and null
    ts = df[TIMESTAMP_COL]
    if not pd.api.types.is_datetime64_any_dtype(ts):
        raise DataIntegrityError(
            f"{partition}: timestamp column dtype is {ts.dtype}, "
            f"expected a datetime64 type."
        )
    if ts.isna().any():
        first_na = int(ts.isna().to_numpy().argmax())
        raise DataIntegrityError(
            f"{partition}: timestamp is NaT at row {first_na}."
        )

    # 5. Strictly increasing timestamps
    ts_np = ts.to_numpy()
    diffs = np.diff(ts_np)
    if (diffs <= np.timedelta64(0, "ns")).any():
        bad = int(np.argmax(diffs <= np.timedelta64(0, "ns")))
        raise DataIntegrityError(
            f"{partition}: timestamps are not strictly increasing. "
            f"First violation between rows {bad} and {bad + 1} "
            f"({ts_np[bad]!s} -> {ts_np[bad + 1]!s})."
        )

    # 6. Numeric dtype for all feature columns
    for col in expected_features:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise DataIntegrityError(
                f"{partition}: feature '{col}' has non-numeric dtype "
                f"{df[col].dtype}."
            )

    # 7. No NaN / inf anywhere in features
    feature_block = df[expected_features].to_numpy(dtype=np.float64)
    finite = np.isfinite(feature_block)
    if not finite.all():
        i, j = np.argwhere(~finite)[0]
        raise DataIntegrityError(
            f"{partition}: non-finite value at row {int(i)}, "
            f"feature '{expected_features[int(j)]}': "
            f"{feature_block[int(i), int(j)]!r}."
        )

    return df


# --- Standalone smoke test -----------------------------------------------
#
# Run from the project root:
#     python src/data/validation.py
#
# (1) Loads the real threshold partition via src.data.ingestion and
#     asserts validate_partition accepts it.
# (2) Constructs six deliberately corrupted copies of a small synthetic
#     DataFrame and asserts each is rejected with the expected message.
#
# The synthetic fixtures are NOT SWaT observations. They exist only to
# exercise rejection paths.

if __name__ == "__main__":
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))

    from src.data.ingestion import load_partition

    print("=" * 72)
    print("validation.py — standalone smoke test")
    print("=" * 72)

    csv_root = project_root / "data" / "raw"

    # Feature names read from the scaler, not hardcoded
    import joblib
    scaler = joblib.load(project_root / "nb08_artifacts" / "scaler.joblib")
    features = list(scaler.feature_names_in_)
    print(f"  Features (from scaler): {len(features)}")
    print(f"  CSV root:               {csv_root}")

    # --- Real partition: accept ---
    print("\n  [R1] real threshold partition -> ACCEPT")
    df_real = load_partition(csv_root, "threshold", features)
    validate_partition(df_real, "threshold", features, expected_rows=47_437)
    print(f"    rows: {len(df_real):,}")
    print(f"    verdict: PASS")

    # --- Synthetic corruptions: reject ---
    # Small in-memory DataFrame with valid schema
    base = pd.DataFrame(
        np.zeros((10, len(features)), dtype=np.float32),
        columns=features,
    )
    base.insert(0, "timestamp",
                pd.date_range("2016-01-01 00:00:00", periods=10, freq="1s"))

    def _expect_reject(label: str, description: str, df: pd.DataFrame,
                       expected_rows: Optional[int] = None) -> bool:
        try:
            validate_partition(df, label, features, expected_rows=expected_rows)
        except DataIntegrityError as e:
            print(f"\n  [{label}] {description} -> REJECTED")
            print(f"    detail: {e}")
            print(f"    verdict: PASS")
            return True
        print(f"\n  [{label}] {description} -> ACCEPTED (unexpected)")
        print(f"    verdict: ISSUE")
        return False

    overall = True

    # V1: wrong row count
    v = base.iloc[:-1].reset_index(drop=True)
    overall &= _expect_reject(
        "V1", "row count mismatch", v, expected_rows=10,
    )

    # V2: duplicate timestamp
    v = base.copy()
    v.loc[3, "timestamp"] = v.loc[2, "timestamp"]
    overall &= _expect_reject("V2", "duplicate timestamp", v)

    # V3: NaN in a feature
    v = base.copy()
    v.loc[4, features[7]] = np.nan
    overall &= _expect_reject("V3", "NaN feature value", v)

    # V4: inf in a feature
    v = base.copy()
    v.loc[5, features[11]] = np.inf
    overall &= _expect_reject("V4", "infinite feature value", v)

    # V5: forbidden label column present
    v = base.copy()
    v["Normal/Attack"] = 0
    overall &= _expect_reject("V5", "label column present", v)

    # V6: columns reordered
    v = base.copy()
    swapped = list(v.columns)
    swapped[1], swapped[2] = swapped[2], swapped[1]
    v = v[swapped]
    overall &= _expect_reject("V6", "feature order swapped", v)

    print("\n" + "=" * 72)
    print(f"Overall: {'PASS' if overall else 'ISSUE'}")
    print("=" * 72)
    sys.exit(0 if overall else 1)