from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


def ensure_import_paths() -> None:
    """Ensure imports work whether launched from repo root or within `ferry_analytics/`."""

    ferry_root = Path(__file__).resolve().parents[1]
    if str(ferry_root) not in sys.path:
        sys.path.insert(0, str(ferry_root))


def main() -> None:
    """Run the Toronto Island Ferry Analytics Streamlit dashboard."""

    ensure_import_paths()

    from dashboard.components.filters import apply_filters
    from dashboard.components.kpi_cards import render_kpis
    from dashboard.components.time_series import (
        build_hour_vs_dow_heatmap,
        build_hourly_average_bar,
        build_time_series,
    )
    from dashboard.utils.data_loader import load_data

    st.set_page_config(
        page_title="Toronto Island Ferry Analytics Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Toronto Island Ferry Analytics Dashboard")
    st.caption(
        "Real-time-style analytics on 15-minute ticket sales and redemptions (2015–2025)."
    )

    df = load_data()
    filtered = apply_filters(df)

    render_kpis(filtered)
    st.divider()

    if filtered.empty:
        st.warning("No data to display. Adjust the filters in the sidebar.")
        return

    st.plotly_chart(build_time_series(filtered), use_container_width=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(build_hourly_average_bar(filtered), use_container_width=True)
    with c2:
        st.plotly_chart(build_hour_vs_dow_heatmap(filtered), use_container_width=True)


if __name__ == "__main__":
    main()

