"""
SWaT parquet ingestion for the historical replay engine.

Loads one replay partition (threshold, validation, or attack) from a
per-partition parquet file and returns a DataFrame with columns:
    ['timestamp', <42 scaler features in scaler order>]

The parquet files are produced by scripts/convert_to_parquet.py and are
committed to the repository. Total parquet size: ~4.65 MB.

Parquet row counts (verified against NB13):
    threshold    47,437
    validation   79,060
    attack       54,621

Does NOT:
    - Modify the parquet files.
    - Impute missing values.
    - Scale. FrozenBundle owns the scaler.
    - Score. ReplayRunner + FrozenBundle own inference.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


TIMESTAMP_COL = "Timestamp"
LABEL_COL = "Normal/Attack"

PARQUET_ROW_COUNTS = {
    "threshold":  47_437,
    "validation": 79_060,
    "attack":     54_621,
}

SUPPORTED_PARTITIONS = ("threshold", "validation", "attack")


class IngestionError(RuntimeError):
    """Raised on any parquet-integrity problem that would prevent replay."""


def _require_features(columns: list[str], features: list[str], source: str) -> None:
    missing = [f for f in features if f not in columns]
    if missing:
        raise IngestionError(
            f"{source} is missing required feature columns: {missing[:5]}"
            f"{'...' if len(missing) > 5 else ''}."
        )


def load_partition(
    parquet_root: Path | str,
    partition: str,
    features: Iterable[str],
) -> pd.DataFrame:
    """Load one replay partition as a DataFrame with columns [timestamp, *features].

    Parameters
    ----------
    parquet_root : Path or str
        Directory containing threshold.parquet, validation.parquet, attack.parquet.
        Configured by the caller; never accepts a client-supplied path.
    partition : {"threshold", "validation", "attack"}
    features : iterable of str
        The 42 feature names in scaler order (from FrozenBundle.feature_names).

    Raises
    ------
    IngestionError
        If the parquet file is missing, malformed, wrong row count,
        non-monotonic, or missing required features.
    """
    if partition not in SUPPORTED_PARTITIONS:
        raise IngestionError(
            f"Unsupported partition {partition!r}. "
            f"Must be one of {SUPPORTED_PARTITIONS}."
        )
    parquet_root = Path(parquet_root).resolve()
    features = list(features)
    if not features:
        raise IngestionError("features list is empty.")

    path = parquet_root / f"{partition}.parquet"
    if not path.is_file():
        raise IngestionError(
            f"Parquet file not found: {path}. "
            "Run scripts/convert_to_parquet.py with a permitted SWaT copy."
        )

    try:
        df = pd.read_parquet(path)
    except Exception as e:
        raise IngestionError(f"Failed to read {path}: {e}") from e

    df.columns = [c.strip() for c in df.columns]
    _require_features(list(df.columns), features, path.name)

    if TIMESTAMP_COL not in df.columns:
        raise IngestionError(f"{path.name} is missing the {TIMESTAMP_COL!r} column.")

    if not pd.api.types.is_datetime64_any_dtype(df[TIMESTAMP_COL]):
        df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL], errors="raise")

    expected = PARQUET_ROW_COUNTS[partition]
    if len(df) != expected:
        raise IngestionError(
            f"{partition} parquet has {len(df):,} rows, expected {expected:,}. "
            "Do not replay."
        )

    if not df[TIMESTAMP_COL].is_monotonic_increasing:
        raise IngestionError(f"{partition} timestamps are not monotonic.")

    out = df[[TIMESTAMP_COL] + features].copy()
    out.columns = ["timestamp"] + list(features)
    return out


# --- Standalone smoke test ----------------------------------------------
#
# Run from the project root:
#     python src/data/ingestion.py
#
# Verifies each parquet loads with the exact row count and boundary
# timestamps NB13 recorded. Uses the scaler only for feature names —
# feature order is NOT hardcoded.

if __name__ == "__main__":
    import sys
    import joblib

    project_root = Path(__file__).resolve().parents[2]
    parquet_root = project_root / "data" / "parquet"

    if not parquet_root.is_dir():
        print(f"ERROR: {parquet_root} does not exist.")
        print("Run scripts/convert_to_parquet.py first.")
        sys.exit(1)

    scaler = joblib.load(project_root / "nb08_artifacts" / "scaler.joblib")
    features = list(scaler.feature_names_in_)

    EXPECTED = {
        "threshold":  {"rows": 47_437, "first": "2016-01-01 02:23:18",
                       "last": "2016-01-01 15:51:19"},
        "validation": {"rows": 79_060, "first": "2016-01-01 15:51:20",
                       "last": "2016-01-02 14:59:59"},
        "attack":     {"rows": 54_621, "first": None, "last": None},
    }

    print("=" * 72)
    print("ingestion.py — parquet smoke test")
    print("=" * 72)
    print(f"  Features (from scaler): {len(features)}")
    print(f"  Parquet root:           {parquet_root}")

    ok = True
    for partition in SUPPORTED_PARTITIONS:
        print(f"\n  Loading {partition} ...")
        df = load_partition(parquet_root, partition, features)
        exp = EXPECTED[partition]
        first = str(df["timestamp"].iloc[0])
        last = str(df["timestamp"].iloc[-1])
        rows_ok = len(df) == exp["rows"]
        first_ok = exp["first"] is None or first.startswith(exp["first"])
        last_ok = exp["last"] is None or last.startswith(exp["last"])
        checks_ok = rows_ok and first_ok and last_ok
        ok = ok and checks_ok
        print(f"    rows:   {len(df):>7,}  expected {exp['rows']:>7,}  "
              f"{'PASS' if rows_ok else 'ISSUE'}")
        print(f"    first:  {first}")
        print(f"    last:   {last}")
        if exp["first"]:
            print(f"    first_ts match: {'PASS' if first_ok else 'ISSUE'}")
        if exp["last"]:
            print(f"    last_ts match:  {'PASS' if last_ok else 'ISSUE'}")

    print("\n" + "=" * 72)
    print(f"Overall: {'PASS' if ok else 'ISSUE'}")
    print("=" * 72)
    sys.exit(0 if ok else 1)