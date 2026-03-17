from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Toronto Island Ferry Analytics",
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
    # with `dashboard/` as the first entry on `sys.path`.
    from components.filters import apply_filters
    from components.kpi_cards import render_kpis
    from components.time_series import (
        build_hour_vs_dow_heatmap,
        build_hourly_average_bar,
        build_time_series,
    )
    from utils.data_loader import load_data

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

