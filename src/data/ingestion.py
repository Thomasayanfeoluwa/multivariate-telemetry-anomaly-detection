"""
SWaT CSV ingestion for the historical replay engine.

Loads one partition (threshold, validation, or attack) of the permitted
local SWaT CSVs into a DataFrame with columns:
    ['timestamp', <42 scaler features in scaler order>]

Faithful to NB13 Cell 4 (51-sensor eligibility filter, partition row
boundaries) and NB13 Cell 5 (raw-CSV row positioning via skiprows/nrows).

Partition row counts (verified by NB13 Cell 1 / Cell 4):
    train       221,366
    monitor      47,435
    threshold    47,437
    validation   79,060
    attack       54,621

Does NOT:
    - Modify the CSVs.
    - Impute missing values. If the 51-sensor filter drops any row, the
      row count assertion raises — NB13 verified the filter is a no-op
      on this dataset, and any drop would signal a data-integrity issue.
    - Scale. The scaler is loaded frozen by FrozenBundle.
    - Score. Replay runner and FrozenBundle do that.

Default CSV location: <project_root>/data/raw/{normal,attack}.csv.
No caller may pass an arbitrary filesystem path or client-supplied path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


TIMESTAMP_COL = "Timestamp"
LABEL_COL     = "Normal/Attack"

PARTITION_ROWS = {
    "train":      221_366,
    "monitor":     47_435,
    "threshold":   47_437,
    "validation":  79_060,
}
ATTACK_ROWS = 54_621

NORMAL_TOTAL = sum(PARTITION_ROWS.values())  # 395,298 — matches NB13 Cell 4

# Cumulative starting offset of each normal partition in the raw CSV,
# counting data rows only (header excluded). Cell 5 used the same idea.
PARTITION_OFFSETS = {
    "train":      0,
    "monitor":    PARTITION_ROWS["train"],
    "threshold":  PARTITION_ROWS["train"] + PARTITION_ROWS["monitor"],
    "validation": PARTITION_ROWS["train"] + PARTITION_ROWS["monitor"]
                  + PARTITION_ROWS["threshold"],
}

SUPPORTED_PARTITIONS = ("threshold", "validation", "attack")


class IngestionError(RuntimeError):
    """Raised on any CSV-integrity problem that would prevent replay."""


def _read_header(csv_path: Path) -> pd.DataFrame:
    if not csv_path.is_file():
        raise IngestionError(f"CSV not found: {csv_path}")
    header = pd.read_csv(csv_path, nrows=0)
    header.columns = [c.strip() for c in header.columns]
    return header


def _require_features(header_columns: list[str], features: Iterable[str], source: str) -> None:
    features = list(features)
    missing = [f for f in features if f not in header_columns]
    if missing:
        raise IngestionError(
            f"{source} is missing required feature columns: {missing[:5]}"
            f"{'...' if len(missing) > 5 else ''}."
        )


def _parse_normal_timestamps(series: pd.Series) -> pd.Series:
    # SWaT normal.csv uses `d/m/yyyy h:mm:ss AM/PM` (no zero-padding).
    # Declaring the format explicitly makes parsing deterministic and
    # removes pandas' per-element dateutil fallback. NB13 Cell 5 already
    # used this exact format for attack.csv; normal.csv uses the same one.
    return pd.to_datetime(
        series.astype("string").str.strip(),
        format="%d/%m/%Y %I:%M:%S %p",
        errors="raise",
    )


def _parse_attack_timestamps(series: pd.Series) -> pd.Series:
    # attack.csv uses an explicit 12-hour format, per NB13 Cell 5.
    return pd.to_datetime(
        series.astype("string").str.strip(),
        format="%d/%m/%Y %I:%M:%S %p",
        errors="raise",
    )


def _load_normal_partition(
    csv_root: Path,
    partition: str,
    features: list[str],
) -> pd.DataFrame:
    csv_path = csv_root / "normal.csv"
    header = _read_header(csv_path)
    all_cols = list(header.columns)
    _require_features(all_cols, features, "normal.csv")

    sensor_cols_51 = [c for c in all_cols if c not in (TIMESTAMP_COL, LABEL_COL)]
    if len(sensor_cols_51) != 51:
        raise IngestionError(
            f"normal.csv has {len(sensor_cols_51)} sensor columns, expected 51. "
            "This may not be the SWaT file expected by NB08/NB13."
        )

    first_data_row = PARTITION_OFFSETS[partition]
    n_rows         = PARTITION_ROWS[partition]

    # skiprows=range(1, first_data_row + 1): line 0 is the header (read
    # normally); lines 1..first_data_row are data rows 0..first_data_row-1,
    # which we skip. Reading then starts at data row `first_data_row`.
    df = pd.read_csv(
        csv_path,
        header=0,
        skiprows=range(1, first_data_row + 1),
        nrows=n_rows,
        low_memory=False,
    )
    df.columns = [c.strip() for c in df.columns]

    df[TIMESTAMP_COL] = _parse_normal_timestamps(df[TIMESTAMP_COL])

    # NB13 Cell 4 eligibility filter — should be a no-op on this dataset;
    # any dropped row means the CSV on this machine differs from the one
    # NB13 verified, so refuse rather than silently replay short.
    keep = df[TIMESTAMP_COL].notna() & df[sensor_cols_51].notna().all(axis=1)
    df = df.loc[keep].reset_index(drop=True)
    if len(df) != n_rows:
        raise IngestionError(
            f"After 51-sensor eligibility filter, {partition} partition "
            f"has {len(df):,} rows, expected {n_rows:,}. Do not replay."
        )

    if not df[TIMESTAMP_COL].is_monotonic_increasing:
        raise IngestionError(
            f"{partition} partition timestamps are not monotonic."
        )

    out = df[[TIMESTAMP_COL] + features].copy()
    out.columns = ["timestamp"] + list(features)
    return out


def _load_attack_partition(
    csv_root: Path,
    features: list[str],
) -> pd.DataFrame:
    csv_path = csv_root / "attack.csv"
    header = _read_header(csv_path)
    _require_features(list(header.columns), features, "attack.csv")

    df = pd.read_csv(csv_path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    df[TIMESTAMP_COL] = _parse_attack_timestamps(df[TIMESTAMP_COL])

    if len(df) != ATTACK_ROWS:
        raise IngestionError(
            f"attack.csv has {len(df):,} rows, expected {ATTACK_ROWS:,}. "
            "Do not replay."
        )

    if not df[TIMESTAMP_COL].is_monotonic_increasing:
        raise IngestionError("attack partition timestamps are not monotonic.")

    out = df[[TIMESTAMP_COL] + features].copy()
    out.columns = ["timestamp"] + list(features)
    return out


def load_partition(
    csv_root: Path | str,
    partition: str,
    features: Iterable[str],
) -> pd.DataFrame:
    """Load one replay partition as a DataFrame with columns [timestamp, *features].

    Parameters
    ----------
    csv_root : Path or str
        Directory containing normal.csv and attack.csv. Must be configured
        by the caller; never accept a client-supplied path.
    partition : {"threshold", "validation", "attack"}
    features : iterable of str
        The 42 feature names in scaler order (from FrozenBundle.feature_names).

    Raises
    ------
    IngestionError
        If the CSV is missing, malformed, wrong row count, non-monotonic,
        or missing required features.
    """
    if partition not in SUPPORTED_PARTITIONS:
        raise IngestionError(
            f"Unsupported partition {partition!r}. "
            f"Must be one of {SUPPORTED_PARTITIONS}."
        )
    csv_root = Path(csv_root).resolve()
    features = list(features)
    if not features:
        raise IngestionError("features list is empty.")

    if partition == "attack":
        return _load_attack_partition(csv_root, features)
    return _load_normal_partition(csv_root, partition, features)


# --- Standalone smoke test ------------------------------------------------
#
# Run from the project root:
#     python src/data/ingestion.py
#
# Loads each partition and checks the row counts and first/last timestamps
# against the values recorded by NB13 Cell 4 / Cell 5. Uses the scaler
# (via joblib) only to obtain the feature-name list — the feature order
# is NOT hardcoded here.

if __name__ == "__main__":
    import sys
    import joblib

    root = Path.cwd()
    if not (root / "data" / "raw" / "normal.csv").is_file():
        print(f"ERROR: {root} does not contain data/raw/normal.csv.")
        sys.exit(1)

    scaler = joblib.load(root / "nb08_artifacts" / "scaler.joblib")
    features = list(scaler.feature_names_in_)
    csv_root = root / "data" / "raw"

    EXPECTED = {
        "threshold":  {"rows": 47_437,
                       "first": "2016-01-01 02:23:18",
                       "last":  "2016-01-01 15:51:19"},
        "validation": {"rows": 79_060,
                       "first": "2016-01-01 15:51:20",
                       "last":  "2016-01-02 14:59:59"},
        "attack":     {"rows": 54_621,
                       "first": None,
                       "last":  None},
    }

    print("=" * 72)
    print("ingestion.py — standalone smoke test")
    print("=" * 72)
    print(f"  Features (from scaler): {len(features)}")
    print(f"  CSV root:               {csv_root}")

    ok = True
    for partition in SUPPORTED_PARTITIONS:
        print(f"\n  Loading {partition} ...")
        df = load_partition(csv_root, partition, features)
        exp = EXPECTED[partition]
        first = str(df["timestamp"].iloc[0])
        last  = str(df["timestamp"].iloc[-1])
        rows_ok = len(df) == exp["rows"]
        first_ok = exp["first"] is None or first.startswith(exp["first"])
        last_ok  = exp["last"]  is None or last.startswith(exp["last"])
        checks_ok = rows_ok and first_ok and last_ok
        ok = ok and checks_ok
        print(f"    rows:   {len(df):>7,}  expected {exp['rows']:>7,}  "
              f"{'PASS' if rows_ok else 'ISSUE'}")
        print(f"    first:  {first}")
        print(f"    last:   {last}")
        if exp["first"]:
            print(f"    first_ts match: {'PASS' if first_ok else 'ISSUE'}  "
                  f"(expected startswith {exp['first']!r})")
        if exp["last"]:
            print(f"    last_ts match:  {'PASS' if last_ok else 'ISSUE'}  "
                  f"(expected startswith {exp['last']!r})")

    print("\n" + "=" * 72)
    print(f"Overall: {'PASS' if ok else 'ISSUE'}")
    print("=" * 72)
    sys.exit(0 if ok else 1)