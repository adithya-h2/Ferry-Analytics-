from __future__ import annotations

from pathlib import Path

import pandas as pd


def project_root() -> Path:
    """Return the `ferry_analytics/` root directory based on this file's location."""

    return Path(__file__).resolve().parents[1]


def raw_data_path() -> Path:
    """Build the relative path to the raw CSV file."""

    return project_root() / "data" / "raw" / "Toronto Island Ferry Tickets.csv"


def processed_dir() -> Path:
    """Return the processed data directory path."""

    return project_root() / "data" / "processed"


def cleaned_data_path() -> Path:
    """Build the relative path to the cleaned CSV output."""

    return processed_dir() / "ferry_cleaned.csv"


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw dataset by deduplicating, filling missing counts, and filtering empty intervals."""

    df = df.copy()

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"])

    df = df.drop_duplicates()

    for col in ["Redemption Count", "Sales Count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(0).astype("int64")

    df = df.loc[~((df["Redemption Count"] == 0) & (df["Sales Count"] == 0))].copy()

    df = df.sort_values("Timestamp", ascending=True).reset_index(drop=True)
    return df


def main() -> None:
    """Load raw CSV, apply cleaning rules, and save cleaned output."""

    in_path = raw_data_path()
    out_path = cleaned_data_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise FileNotFoundError(
            f"Raw CSV not found at: {in_path}. "
            f"Expected it at 'ferry_analytics/data/raw/Toronto Island Ferry Tickets.csv'."
        )

    raw_df = pd.read_csv(in_path)
    print(f"Loaded raw data from: {in_path}")
    print(f"Raw shape: {raw_df.shape}")

    cleaned_df = clean_data(raw_df)
    print(f"Cleaned shape: {cleaned_df.shape}")
    print(f"Removed rows: {raw_df.shape[0] - cleaned_df.shape[0]}")

    cleaned_df.to_csv(out_path, index=False)
    print(f"Saved cleaned data to: {out_path}")


if __name__ == "__main__":
    main()

