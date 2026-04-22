from __future__ import annotations

import pandas as pd
import streamlit as st


def render_kpis(df: pd.DataFrame) -> None:
    """Render top-level KPI metric cards accompanied by structural logic tooltips."""
    if df.empty:
        st.info("No data matches the current filters.")
        return

    # Advanced Calculations
    total_sold = int(pd.to_numeric(df["Sales Count"], errors="coerce").fillna(0).sum())
    total_redeemed = int(pd.to_numeric(df.get("Redemption Count", pd.Series([0])), errors="coerce").fillna(0).sum())
    
    net_movement = total_sold - total_redeemed

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
    
    st.markdown("### 🎯 Tier-1 Operational Health Indicators")
    
    st.markdown(
        """
        <style>
        [data-testid="stMetricValue"] { font-size: 1.8rem; color: #0f172a; font-family: 'Inter', sans-serif;}
        [data-testid="stMetricLabel"] { font-size: 1rem; font-weight: 600; color: #475569; }
        </style>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="Total Passenger Volume", 
            value=f"{total_sold:,}"
        )
        with st.expander("📖 Definition"):
            st.markdown("**Metric**: Absolute total of tickets sold.\n\n**Impact**: Dictates gross revenue and total physical human load expected within the terminal environment.")
    with c2:
        st.metric(
            label="Redemption Efficiency", 
            value=f"{redemption_rate:.1f}%", 
            delta=None if redemption_rate >= 90 else f"{redemption_rate-100:.1f}% (Sub-Optimal)",
            delta_color="normal"
        )
        with st.expander("📖 Logic"):
            st.markdown("**Computation**: `(Redeemed Tickets / Sold Tickets) * 100`.\n\n**Impact**: High gap (>10%) implies no-shows. Affects capacity planning as allocated vessels may sail empty.")
    with c3:
        st.metric(
            label="Net Passenger Lag", 
            value=f"{net_movement:,}"
        )
        with st.expander("📖 Alert Meaning"):
             st.markdown("**Computation**: `Total Sold - Total Redeemed`.\n\n**Impact**: A high positive integer indicates extreme queue buildup inside the waiting area before turnstiles.")
        
    with c4:
        st.metric(
            label="System Risk (Congestion)", 
            value=congestion
        )
        with st.expander("📖 Engine"):
             st.markdown("**Meaning**: The mathematical ratio of active passenger load relative to historical maximum load mapping (100%). High numbers mean physical terminal capacity is being overwhelmed.")
