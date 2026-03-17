from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


def _project_root() -> Path:
    """Return repository root based on this module's location."""

    return Path(__file__).resolve().parents[2]


def _processed_featured_path() -> Path:
    """Return the expected deploy-time path to the featured dataset."""

    return _project_root() / "data" / "processed" / "ferry_featured.csv"


def _raw_csv_path() -> Path:
    """Return the expected local path to the raw dataset."""

    return _project_root() / "data" / "raw" / "Toronto Island Ferry Tickets.csv"


def _generate_sample_data() -> pd.DataFrame:
    """Generate small sample data with the same column structure as the featured dataset."""

    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    timestamps = pd.date_range(now - timedelta(days=7), periods=7 * 24 * 4, freq="15min")

    df = pd.DataFrame(
        {
            "_id": np.arange(1, len(timestamps) + 1, dtype=np.int64),
            "Timestamp": timestamps,
        }
    )

    # Create plausible demand patterns (higher daytime, lower overnight).
    hours = df["Timestamp"].dt.hour
    base = np.where((hours >= 9) & (hours <= 18), 12, 3).astype(float)
    noise = np.random.default_rng(42).normal(0, 2.5, size=len(df))

    sales = np.clip(base + noise, 0, None).round().astype(int)
    redemptions = np.clip(sales - np.random.default_rng(7).integers(0, 4, size=len(df)), 0, None).astype(int)

    df["Sales Count"] = sales
    df["Redemption Count"] = redemptions

    ts = df["Timestamp"]
    df["hour"] = ts.dt.hour.astype("int64")
    df["day_of_week"] = ts.dt.dayofweek.astype("int64")
    df["day_name"] = ts.dt.day_name()
    df["month"] = ts.dt.month.astype("int64")
    df["month_name"] = ts.dt.month_name()
    df["year"] = ts.dt.year.astype("int64")
    df["is_weekend"] = df["day_of_week"].isin([5, 6])

    def month_to_season(month: int) -> str:
        if month in (12, 1, 2):
            return "Winter"
        if month in (3, 4, 5):
            return "Spring"
        if month in (6, 7, 8):
            return "Summer"
        return "Fall"

    def hour_to_time_of_day(hour: int) -> str:
        if 6 <= hour <= 11:
            return "Morning"
        if 12 <= hour <= 17:
            return "Afternoon"
        if 18 <= hour <= 21:
            return "Evening"
        return "Night"

    df["season"] = df["month"].map(month_to_season)
    df["time_of_day"] = df["hour"].map(hour_to_time_of_day)
    df["net_passenger_movement"] = (df["Sales Count"] - df["Redemption Count"]).astype(
        "int64"
    )

    return df


@st.cache_data(show_spinner="Loading ferry analytics dataset...")
def load_data() -> pd.DataFrame:
    """Load featured data if available; otherwise show a helpful error and fall back to sample data."""

    featured_path = _processed_featured_path()
    raw_path = _raw_csv_path()

    featured_exists = os.path.exists(featured_path)
    raw_exists = os.path.exists(raw_path)

    if not featured_exists and not raw_exists:
        st.error(
            "No dataset files found.\n\n"
            "Expected one of:\n"
            "- `data/processed/ferry_featured.csv` (recommended for Streamlit Cloud)\n"
            "- `data/raw/Toronto Island Ferry Tickets.csv` (local development)\n\n"
            "The app will load **sample data** so it can still run. "
            "To deploy real data, commit a size-safe `data/processed/ferry_featured.csv`."
        )
        return _generate_sample_data()

    if featured_exists:
        df = pd.read_csv(featured_path)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        df = (
            df.dropna(subset=["Timestamp"])
            .sort_values("Timestamp")
            .reset_index(drop=True)
        )
        return df

    st.error(
        "Found the raw CSV but not the featured dataset.\n\n"
        "Please run the pipeline locally to generate `data/processed/ferry_featured.csv` "
        "or upload a prepared version for deployment."
    )
    return _generate_sample_data()

