from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd


def _configure_stdout_utf8() -> None:
    """Force UTF-8 output so the checkmark prints reliably on Windows."""

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        # If reconfigure isn't available, continue without it.
        pass


def _project_root() -> Path:
    """Return repository root based on this script's location."""

    return Path(__file__).resolve().parent


def _featured_path() -> Path:
    """Return the deploy-time path to the featured dataset."""

    return _project_root() / "data" / "processed" / "ferry_featured.csv"


def _size_mb(path: Path) -> float:
    """Return file size in megabytes."""

    return path.stat().st_size / (1024 * 1024)


def main() -> None:
    """Shrink the featured dataset if needed for Streamlit Cloud deployment."""

    _configure_stdout_utf8()

    path = _featured_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Expected featured data at '{path}'. "
            f"Generate it first, then copy it to 'data/processed/ferry_featured.csv'."
        )

    original_size = _size_mb(path)
    print(f"Featured file: {path}")
    print(f"Current size: {original_size:.2f} MB")

    df = pd.read_csv(path)
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    if "year" not in df.columns and "Timestamp" in df.columns:
        df["year"] = df["Timestamp"].dt.year

    if original_size > 90:
        print("File is over 90MB. Filtering to keep only years 2020–2025.")
        if "year" not in df.columns:
            raise ValueError("Cannot filter by year because the 'year' column is missing.")
        df = df.loc[(df["year"] >= 2020) & (df["year"] <= 2025)].copy()
        df.to_csv(path, index=False)

    final_size = _size_mb(path)
    print(f"Final shape: {df.shape}")
    print(f"Final size: {final_size:.2f} MB")
    print("✅ Ready to deploy!")


if __name__ == "__main__":
    main()

