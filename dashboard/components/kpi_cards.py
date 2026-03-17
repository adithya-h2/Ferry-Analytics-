from __future__ import annotations

import pandas as pd
import streamlit as st


def render_kpis(df: pd.DataFrame) -> None:
    """Render top-level KPI metric cards for the filtered dataset."""

    if df.empty:
        st.info("No data matches the current filters.")
        return

    total_sold = int(pd.to_numeric(df["Sales Count"], errors="coerce").fillna(0).sum())
    total_redeemed = int(
        pd.to_numeric(df["Redemption Count"], errors="coerce").fillna(0).sum()
    )
    net_movement = int(
        pd.to_numeric(df.get("net_passenger_movement"), errors="coerce")
        .fillna(0)
        .sum()
    )

    peak_hour = None
    if "hour" in df.columns:
        hourly_mean_sales = (
            df.groupby("hour", as_index=False)["Sales Count"].mean().sort_values(
                "Sales Count", ascending=False
            )
        )
        if not hourly_mean_sales.empty:
            peak_hour = int(hourly_mean_sales.iloc[0]["hour"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Tickets Sold", f"{total_sold:,}")
    with c2:
        st.metric("Total Tickets Redeemed", f"{total_redeemed:,}")
    with c3:
        st.metric("Net Passenger Movement", f"{net_movement:,}")
    with c4:
        st.metric("Peak Hour", f"{peak_hour}:00" if peak_hour is not None else "N/A")

