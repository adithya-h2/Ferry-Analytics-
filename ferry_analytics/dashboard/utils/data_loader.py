from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


def project_root() -> Path:
    """Return the `ferry_analytics/` root directory from this module's location."""

    return Path(__file__).resolve().parents[2]


def featured_data_path() -> Path:
    """Build the relative path to the featured CSV file used by the dashboard."""

    return project_root() / "data" / "processed" / "ferry_featured.csv"


@st.cache_data(show_spinner="Loading ferry demand dataset...")
def load_data() -> pd.DataFrame:
    """Load the featured ferry dataset and return a clean DataFrame for the dashboard."""

    path = featured_data_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Featured dataset not found at: {path}. "
            f"Run 'ferry_analytics/notebooks/03_feature_engineering.py' to generate it."
        )

    df = pd.read_csv(path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)

    for col in ["Redemption Count", "Sales Count", "net_passenger_movement"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in ["hour", "day_of_week", "month", "year"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    if "is_weekend" in df.columns:
        df["is_weekend"] = df["is_weekend"].astype(bool)

    return df

