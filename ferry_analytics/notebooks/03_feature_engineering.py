from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def project_root() -> Path:
    """Return the `ferry_analytics/` root directory based on this file's location."""

    return Path(__file__).resolve().parents[1]


def cleaned_data_path() -> Path:
    """Build the relative path to the cleaned CSV input."""

    return project_root() / "data" / "processed" / "ferry_cleaned.csv"


def featured_data_path() -> Path:
    """Build the relative path to the featured CSV output."""

    return project_root() / "data" / "processed" / "ferry_featured.csv"


def month_to_season(month: int) -> str:
    """Map a month number (1-12) to a meteorological season label."""

    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Fall"


def hour_to_time_of_day(hour: int) -> str:
    """Bucket hour-of-day into Morning/Afternoon/Evening/Night."""

    if 6 <= hour <= 11:
        return "Morning"
    if 12 <= hour <= 17:
        return "Afternoon"
    if 18 <= hour <= 21:
        return "Evening"
    return "Night"


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-based features and net passenger movement."""

    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"]).copy()

    ts = df["Timestamp"]
    df["hour"] = ts.dt.hour.astype("int64")
    df["day_of_week"] = ts.dt.dayofweek.astype("int64")  # 0=Mon ... 6=Sun
    df["day_name"] = ts.dt.day_name()
    df["month"] = ts.dt.month.astype("int64")
    df["month_name"] = ts.dt.month_name()
    df["year"] = ts.dt.year.astype("int64")
    df["is_weekend"] = df["day_of_week"].isin([5, 6])

    df["season"] = df["month"].map(month_to_season)
    df["time_of_day"] = df["hour"].map(hour_to_time_of_day)

    for col in ["Redemption Count", "Sales Count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    df["net_passenger_movement"] = (df["Sales Count"] - df["Redemption Count"]).astype(
        "int64"
    )

    desired_time_of_day = ["Morning", "Afternoon", "Evening", "Night"]
    df["time_of_day"] = pd.Categorical(df["time_of_day"], categories=desired_time_of_day, ordered=True)

    desired_seasons = ["Winter", "Spring", "Summer", "Fall"]
    df["season"] = pd.Categorical(df["season"], categories=desired_seasons, ordered=True)

    return df.sort_values("Timestamp", ascending=True).reset_index(drop=True)


def main() -> None:
    """Load cleaned data, engineer features, and save featured dataset."""

    in_path = cleaned_data_path()
    out_path = featured_data_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise FileNotFoundError(
            f"Cleaned CSV not found at: {in_path}. "
            f"Run '02_data_cleaning.py' first to generate it."
        )

    df = pd.read_csv(in_path)
    print(f"Loaded cleaned data from: {in_path}")
    print(f"Input shape: {df.shape}")

    featured = add_features(df)
    print(f"Featured shape: {featured.shape}")
    print(f"Featured columns: {list(featured.columns)}")

    featured.to_csv(out_path, index=False)
    print(f"Saved featured data to: {out_path}")


if __name__ == "__main__":
    main()

