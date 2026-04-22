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

    return df

def _enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """Add synthetic operational fields like Route, temporal splits, and advanced KPIs."""
    df = df.copy()
    
    if "Timestamp" not in df.columns:
        return df

    ts = df["Timestamp"]
    df["hour"] = ts.dt.hour.astype("int64")
    df["day_of_week"] = ts.dt.dayofweek.astype("int64")
    df["day_name"] = ts.dt.day_name()
    df["month"] = ts.dt.month.astype("int64")
    df["month_name"] = ts.dt.month_name()
    df["year"] = ts.dt.year.astype("int64")
    df["is_weekend"] = df["day_of_week"].isin([5, 6])

    def month_to_season(month: int) -> str:
        if month in (12, 1, 2): return "Winter"
        if month in (3, 4, 5): return "Spring"
        if month in (6, 7, 8): return "Summer"
        return "Fall"

    def hour_to_time_of_day(hour: int) -> str:
        if 6 <= hour <= 11: return "Morning"
        if 12 <= hour <= 17: return "Afternoon"
        if 18 <= hour <= 21: return "Evening"
        return "Night"

    df["season"] = df["month"].map(month_to_season)
    df["time_of_day"] = df["hour"].map(hour_to_time_of_day)
    
    # Calculate net movements
    df["net_passenger_movement"] = (df["Sales Count"] - df.get("Redemption Count", 0)).astype("int64")

    # Inject Synthetic Route data probabilistically based on temporal patterns
    routes = ["Centre Island", "Hanlan's Point", "Ward's Island"]
    np.random.seed(42)
    
    def assign_route(row):
        # Center Island is most popular on weekends and afternoons
        if row["is_weekend"] or row["time_of_day"] in ["Afternoon", "Morning"]:
            probs = [0.65, 0.20, 0.15]
        else:
            probs = [0.40, 0.35, 0.25]
        return np.random.choice(routes, p=probs)
        
    df["Route"] = df.apply(assign_route, axis=1)

    # Calculate Route Congestion Index (Synthetic formula)
    # Using Sales Count / baseline max per hour per route to get a 0-100 index
    # We'll approximate this by scaling Sales count 
    max_sales = df["Sales Count"].max() if df["Sales Count"].max() > 0 else 1
    df["Congestion Index"] = (df["Sales Count"] / max_sales * 100).round(1)

    return df


@st.cache_data(show_spinner="Loading operational analytics dataset...")
def load_data() -> pd.DataFrame:
    """Load data and enrich with operational metrics."""

    featured_path = _processed_featured_path()
    raw_path = _raw_csv_path()

    featured_exists = os.path.exists(featured_path)
    raw_exists = os.path.exists(raw_path)

    raw_df = None

    if not featured_exists and not raw_exists:
        st.error(
            "No dataset files found.\n\n"
            "The app will load **sample data** so it can still run."
        )
        raw_df = _generate_sample_data()

    elif featured_exists:
        df = pd.read_csv(featured_path)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        raw_df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)

    else:
        # Load raw dataset directly if featured not available
        try:
            df = pd.read_csv(raw_path)
            df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
            raw_df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)
        except Exception as e:
            st.error(f"Failed to load raw data: {e}")
            raw_df = _generate_sample_data()

    # Enrich whatever dataframe we successfully loaded
    return _enrich_data(raw_df)

