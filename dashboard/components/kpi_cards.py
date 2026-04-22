from __future__ import annotations

import pandas as pd
import streamlit as st


def render_kpis(df: pd.DataFrame) -> None:
    """Render top-level KPI metric cards for the filtered dataset."""
    if df.empty:
        st.info("No data matches the current filters.")
        return

    # Advanced Calculations
    total_sold = int(pd.to_numeric(df["Sales Count"], errors="coerce").fillna(0).sum())
    total_redeemed = int(pd.to_numeric(df.get("Redemption Count", pd.Series([0])), errors="coerce").fillna(0).sum())
    
    net_movement = int(pd.to_numeric(df.get("net_passenger_movement"), errors="coerce").fillna(0).sum())

    # Peak hour and route
    peak_hour = "N/A"
    if "hour" in df.columns:
        hourly_mean_sales = df.groupby("hour", as_index=False)["Sales Count"].mean().sort_values("Sales Count", ascending=False)
        if not hourly_mean_sales.empty:
            peak_hour = f"{int(hourly_mean_sales.iloc[0]['hour'])}:00"

    congestion = "N/A"
    if "Congestion Index" in df.columns:
        congestion = f"{df['Congestion Index'].mean():.1f}%"

    redemption_rate = 100.0 if total_sold == 0 else (total_redeemed / total_sold) * 100
    
    st.markdown("### Core Performance Indicators")
    
    # Custom CSS to improve KPI cards layout in Streamlit
    st.markdown(
        """
        <style>
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #1E3A8A;
        }
        [data-testid="stMetricLabel"] {
            font-size: 1rem;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="Total Tickets Sold", 
            value=f"{total_sold:,}", 
            help="Total cumulative volume of tickets purchased during the selected timeframe."
        )
    with c2:
        st.metric(
            label="Redemption Rate", 
            value=f"{redemption_rate:.1f}%", 
            delta=None if redemption_rate >= 90 else f"{redemption_rate-100:.1f}% (Below Optimal)",
            delta_color="normal",
            help="Percentage of sold tickets that were actively redeemed at the ferry terminal. Target is >90%."
        )
    with c3:
        st.metric(
            label="Net Movement", 
            value=f"{net_movement:,}",
            help="Difference between tickets sold and redeemed. Indicates queue buildup or system lag."
        )
        
    with c4:
        st.metric(
            label="Avg Route Congestion", 
            value=congestion,
            help="Average estimated traffic density compared to maximum historical throughput."
        )

