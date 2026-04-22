from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Toronto Island Ferry Operational Control",
    page_icon="⛴️",
    layout="wide",
)

def main() -> None:
    """Run the Toronto Ferry Decision Support Platform."""

    # Core Utility
    from dashboard.components.filters import apply_filters
    from dashboard.utils.data_loader import load_data
    
    # Analytics & Logic
    from dashboard.analytics.anomaly_detection import detect_anomalies
    from dashboard.forecasting.model import generate_forecast
    
    # UI Components
    from dashboard.alerts.monitor import render_system_alerts
    from dashboard.dashboard_components.kpis import render_kpis
    from dashboard.dashboard_components.executive_brief import render_executive_brief
    from dashboard.dashboard_components.visuals import (
        build_advanced_time_series, 
        build_forecast_chart, 
        build_network_efficiency_heatmap
    )
    from dashboard.insights.generator import (
        get_demand_insight, 
        get_route_insight, 
        get_anomaly_insight, 
        render_insight_panel
    )

    # CSS Injection for Premium Framework
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            max-width: 98%;
        }
        h1 { font-family: 'Inter', sans-serif; color: #0f172a; font-weight: 800; }
        h2, h3 { font-family: 'Inter', sans-serif; color: #1e293b; font-weight: 700; }
        hr { transform: scaleY(0.5); opacity: 0.2; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("⛴️ Ferry Operations & Predictive Control")
    st.caption("Active Intelligence & Decision Support Platform")

    try:
        raw_df = load_data()
        # Compute anomalies on the full dataset before filtering
        df = detect_anomalies(raw_df)
    except Exception as exc:
        st.error(f"System Load Failure: {exc}")
        st.stop()
        
    # Render passive threshold alerts
    render_system_alerts(df)

    filtered = apply_filters(df)
    
    st.divider()

    if filtered.empty:
        st.warning("Data Matrix Empty. Select wider temporal parameters.")
        return

    # ENTERPRISE LAYOUT
    tab_exec, tab_ops, tab_pred = st.tabs([
        "📋 C-Suite Briefing", 
        "⚙️ Thermal Ops & Network", 
        "🔮 Variance & Extrapolation"
    ])
    
    # TAB 1: EXECUTIVE BRIEFING
    with tab_exec:
        render_executive_brief(filtered)
        render_kpis(filtered)
        
        st.markdown("---")
        st.markdown("### Temporal Volatility Profiling")
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.plotly_chart(build_advanced_time_series(filtered), use_container_width=True)
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            render_insight_panel(get_demand_insight(filtered))
            render_insight_panel(get_anomaly_insight(filtered))
            
    # TAB 2: OPERATIONAL NETWORKS
    with tab_ops:
        st.markdown("### Route Congestion & Efficiency")
        c1, c2 = st.columns([1.2, 1])
        
        with c1:
            st.plotly_chart(build_network_efficiency_heatmap(filtered), use_container_width=True)
            
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            render_insight_panel(get_route_insight(filtered))

    # TAB 3: PREDICTIVE MODELS
    with tab_pred:
        st.markdown("### Projected Demand (EMA-Z Model)")
        st.info("System executes structural moving average paired with historically weighted homoscedastic variance bonds to map future state timelines.")
        
        # Forecast utilizes RAW un-filtered data array to preserve spatial contiguity.
        f_df = generate_forecast(df, periods=24) 
        st.plotly_chart(build_forecast_chart(filtered, f_df), use_container_width=True)


if __name__ == "__main__":
    main()

