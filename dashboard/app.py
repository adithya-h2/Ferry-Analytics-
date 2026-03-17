from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Toronto Island Ferry Analytics",
    page_icon="⛴️",
    layout="wide",
)


def main() -> None:
    """Run the Toronto Island Ferry Analytics Streamlit dashboard."""

    from dashboard.components.filters import apply_filters
    from dashboard.components.kpi_cards import render_kpis
    from dashboard.components.time_series import (
        build_hour_vs_dow_heatmap,
        build_hourly_average_bar,
        build_time_series,
    )
    from dashboard.utils.data_loader import load_data

    st.title("Toronto Island Ferry Analytics Dashboard")
    st.caption("Real-time-style analytics on 15-minute intervals (2015–2025).")

    try:
        df = load_data()
    except Exception as exc:
        st.error(f"Failed to load data: {exc}")
        st.stop()

    filtered = apply_filters(df)

    render_kpis(filtered)
    st.divider()

    if filtered.empty:
        st.warning("No data to display. Adjust the filters in the sidebar.")
    else:
        st.plotly_chart(build_time_series(filtered), use_container_width=True)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.plotly_chart(build_hourly_average_bar(filtered), use_container_width=True)
        with c2:
            st.plotly_chart(build_hour_vs_dow_heatmap(filtered), use_container_width=True)

    st.divider()
    st.caption("Data source: Toronto Open Data | 2015–2025")


if __name__ == "__main__":
    main()

