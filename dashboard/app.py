from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Toronto Island Ferry Analytics Command Center",
    page_icon="⛴️",
    layout="wide",
)

# #region agent log
def _debug_log(message: str, data: dict, *, run_id: str, hypothesis_id: str) -> None:
    """Append a single NDJSON debug line (no secrets)."""

    payload = {
        "sessionId": "e6e343",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": "dashboard/app.py",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open("debug-e6e343.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass


_debug_log(
    "module_import_context",
    {
        "cwd": os.getcwd(),
        "__file__": __file__,
        "sys_path_head": sys.path[:5],
        "has_repo_dashboard_dir": Path("dashboard").exists(),
        "has_components_dir": Path(__file__).resolve().parent.joinpath("components").exists(),
        "has_utils_dir": Path(__file__).resolve().parent.joinpath("utils").exists(),
    },
    run_id="pre-fix",
    hypothesis_id="H1_import_path",
)
# #endregion


def main() -> None:
    """Run the Toronto Island Ferry Analytics Streamlit dashboard."""

    # Import from sibling modules so this works when Streamlit runs `dashboard/app.py`
    from components.filters import apply_filters
    from components.kpi_cards import render_kpis
    from components.time_series import (
        build_hour_vs_dow_heatmap,
        build_hourly_average_bar,
        build_time_series,
        build_route_congestion_heatmap,
        build_forecast_chart
    )
    from components.smart_alerts import render_smart_alerts
    from components.insights_engine import get_demand_insight, get_route_insight, get_redemption_insight, render_insight_panel
    from components.executive_summary import render_executive_summary
    from components.forecasting import generate_forecast
    from utils.data_loader import load_data

    # Header styling
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2rem;
            max-width: 95%;
        }
        h1 {
            color: #1a365d;
            font-weight: 800;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("⛴️ Toronto Island Ferry Command Center")
    st.caption("Operational Intelligence & Decision Support Platform")

    try:
        df = load_data()
    except Exception as exc:
        st.error(f"Failed to load data: {exc}")
        st.stop()
        
    # Render Smart Alerts (always visible at top if triggered)
    render_smart_alerts(df)

    filtered = apply_filters(df)
    
    st.divider()

    if filtered.empty:
        st.warning("No data to display. Adjust the filters in the sidebar.")
    else:
        # TABS ARCHITECTURE
        tab_exec, tab_ops, tab_pred = st.tabs([
            "📊 Executive Briefing", 
            "⚙️ Operational Demand", 
            "🔮 Predictive Analytics"
        ])
        
        # TAB 1: EXECUTIVE
        with tab_exec:
            render_executive_summary(filtered)
            st.divider()
            render_kpis(filtered)
            
            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.plotly_chart(build_time_series(filtered), use_container_width=True)
                render_insight_panel(get_demand_insight(filtered))
            with c2:
                st.plotly_chart(build_hourly_average_bar(filtered), use_container_width=True)
                render_insight_panel(get_redemption_insight(filtered))
                
        # TAB 2: OPERATIONAL
        with tab_ops:
            st.markdown("### Route Congestion & Activity Matrix")
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(build_route_congestion_heatmap(filtered), use_container_width=True)
                render_insight_panel(get_route_insight(filtered))
                
            with col2:
                st.plotly_chart(build_hour_vs_dow_heatmap(filtered), use_container_width=True)

        # TAB 3: PREDICTIVE
        with tab_pred:
            st.markdown("### Next 6-Hour Demand Forecast")
            st.info("Uses Exponential Weighted Moving Average augmented with temporal scaling factors to forecast incoming passenger flow.")
            
            # Use raw un-filtered data for better temporal forecasting to avoid gaps
            forecast_df = generate_forecast(df, periods=24) # 24 periods = 6 hours
            st.plotly_chart(build_forecast_chart(filtered, forecast_df), use_container_width=True)
            
            # Show data table
            with st.expander("View Forecast Data Matrix"):
                st.dataframe(forecast_df, use_container_width=True)

    st.divider()
    st.caption("Intelligence provided by Unified Mentor Ferry Analytics Platform | Internal Use Only")


if __name__ == "__main__":
    main()

