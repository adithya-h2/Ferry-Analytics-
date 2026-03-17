from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return a filtered copy of the dataset."""

    if df.empty:
        st.sidebar.warning("No data available to filter.")
        return df

    min_ts = df["Timestamp"].min()
    max_ts = df["Timestamp"].max()

    st.sidebar.header("Filters")

    # Date range picker
    start_default = min_ts.date() if pd.notna(min_ts) else date.today()
    end_default = max_ts.date() if pd.notna(max_ts) else date.today()

    start_date, end_date = st.sidebar.date_input(
        "Date range",
        value=(start_default, end_default),
        min_value=start_default,
        max_value=end_default,
    )

    if isinstance(start_date, (list, tuple)) and len(start_date) == 2:
        # Streamlit can return a tuple in some versions
        start_date, end_date = start_date

    # Year multiselect
    years = sorted(df["year"].dropna().unique().tolist()) if "year" in df.columns else []
    selected_years = st.sidebar.multiselect("Year", options=years, default=years)

    # Season multiselect
    seasons = (
        [s for s in df["season"].dropna().unique().tolist()]
        if "season" in df.columns
        else []
    )
    seasons_sorted = sorted(seasons, key=lambda x: ["Winter", "Spring", "Summer", "Fall"].index(x) if x in ["Winter", "Spring", "Summer", "Fall"] else 99)
    selected_seasons = st.sidebar.multiselect(
        "Season", options=seasons_sorted, default=seasons_sorted
    )

    # Time-of-day multiselect
    tod = (
        [t for t in df["time_of_day"].dropna().unique().tolist()]
        if "time_of_day" in df.columns
        else []
    )
    tod_order = ["Morning", "Afternoon", "Evening", "Night"]
    tod_sorted = sorted(tod, key=lambda x: tod_order.index(x) if x in tod_order else 99)
    selected_tod = st.sidebar.multiselect(
        "Time of day", options=tod_sorted, default=tod_sorted
    )

    filtered = df.copy()

    # Apply date filter
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered = filtered.loc[(filtered["Timestamp"] >= start_ts) & (filtered["Timestamp"] <= end_ts)]

    # Apply categorical filters
    if selected_years and "year" in filtered.columns:
        filtered = filtered.loc[filtered["year"].isin(selected_years)]
    if selected_seasons and "season" in filtered.columns:
        filtered = filtered.loc[filtered["season"].isin(selected_seasons)]
    if selected_tod and "time_of_day" in filtered.columns:
        filtered = filtered.loc[filtered["time_of_day"].isin(selected_tod)]

    return filtered.reset_index(drop=True)

