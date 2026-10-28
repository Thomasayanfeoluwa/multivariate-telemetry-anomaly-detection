"""
Convert SWaT CSVs to per-partition parquet files.

Output:
    data/parquet/threshold.parquet
    data/parquet/validation.parquet
    data/parquet/attack.parquet

Only the three replay partitions are produced — the train and monitor
partitions are not used by the application and are not needed on the
deployed server.

Run from the project root:
    python scripts/convert_to_parquet.py

Requires: pyarrow (pip install pyarrow)
"""

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = PROJECT_ROOT / "data" / "raw"
OUT_ROOT = PROJECT_ROOT / "data" / "parquet"

TRAIN_ROWS      = 221_366
MONITOR_ROWS    = 47_435
THRESHOLD_ROWS  = 47_437
VALIDATION_ROWS = 79_060

ATTACK_ROWS = 54_621

PARSE_FORMAT = "%d/%m/%Y %I:%M:%S %p"
TIMESTAMP_COL = "Timestamp"
LABEL_COL = "Normal/Attack"


def _load_csv(path: Path, parse_timestamps: bool = True) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")
    print(f"  Loading {path.name} ({path.stat().st_size / 1024**2:.1f} MB)...")
    df = pd.read_csv(path, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    if parse_timestamps:
        df[TIMESTAMP_COL] = pd.to_datetime(
            df[TIMESTAMP_COL].astype("string").str.strip(),
            format=PARSE_FORMAT,
            errors="raise",
        )
    print(f"  Loaded {len(df):,} rows, "
          f"memory footprint {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    return df


def _save_parquet(df: pd.DataFrame, name: str) -> None:
    path = OUT_ROOT / f"{name}.parquet"
    df.to_parquet(path, compression="snappy", index=False)
    size_mb = path.stat().st_size / 1024**2
    print(f"    → {path.name} ({size_mb:.2f} MB, {len(df):,} rows)")


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Converting SWaT CSVs → per-partition parquet")
    print("=" * 72)

    print("\n[1/3] Loading normal.csv...")
    normal = _load_csv(CSV_ROOT / "normal.csv")

    threshold_start = TRAIN_ROWS + MONITOR_ROWS
    threshold_end   = threshold_start + THRESHOLD_ROWS
    validation_end  = threshold_end   + VALIDATION_ROWS

    print("\n[2/3] Slicing + writing threshold & validation...")
    _save_parquet(normal.iloc[threshold_start:threshold_end].reset_index(drop=True), "threshold")
    _save_parquet(normal.iloc[threshold_end:validation_end].reset_index(drop=True), "validation")

    del normal  # free ~400 MB RAM before loading attack

    print("\n[3/3] Loading attack.csv...")
    attack = _load_csv(CSV_ROOT / "attack.csv")
    _save_parquet(attack, "attack")

    del attack

    print("\n" + "=" * 72)
    print("Done.")
    print("=" * 72)
    print(f"  Output directory: {OUT_ROOT}")
    total_mb = sum(p.stat().st_size for p in OUT_ROOT.glob("*.parquet")) / 1024**2
    print(f"  Total parquet size: {total_mb:.2f} MB")
    print()
    print("  Next steps:")
    print("    1. Verify the sizes with:")
    print("       Get-ChildItem data\\parquet\\*.parquet | Select-Object Name, Length")
    print("    2. Keep the Kaggle source and its stated CC0 listing documented")
    print("       alongside the derived dataset.")
    return 0


if __name__ == "__main__":
    sys.exit(main())