from __future__ import annotations

from pathlib import Path

import pandas as pd


def project_root() -> Path:
    """Return the `ferry_analytics/` root directory based on this file's location."""

    return Path(__file__).resolve().parents[1]


def raw_data_path() -> Path:
    """Build the relative path to the raw CSV file."""

    return project_root() / "data" / "raw" / "Toronto Island Ferry Tickets.csv"


def load_raw_csv(path: Path) -> pd.DataFrame:
    """Load the raw ferry ticket CSV and parse timestamps."""

    df = pd.read_csv(path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    return df


def main() -> None:
    """Run basic ingestion checks and print dataset diagnostics."""

    path = raw_data_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Raw CSV not found at: {path}. "
            f"Expected it at 'ferry_analytics/data/raw/Toronto Island Ferry Tickets.csv'."
        )

    df = load_raw_csv(path)

    print(f"Loaded raw data from: {path}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nDtypes:")
    print(df.dtypes)

    print("\nHead (first 5 rows):")
    print(df.head())

    ts_min = df["Timestamp"].min()
    ts_max = df["Timestamp"].max()
    print(f"\nDate range (Timestamp): {ts_min} -> {ts_max}")

    print("\nMissing values per column:")
    print(df.isna().sum().sort_values(ascending=False))

    missing_ts = df["Timestamp"].isna().sum()
    print(f"\nMissing/invalid timestamps after parsing: {missing_ts}")


if __name__ == "__main__":
    main()

