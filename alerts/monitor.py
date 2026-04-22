from typing import List, Dict
import pandas as pd
import streamlit as st

def detect_passive_anomalies(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Scan the latest data block for critical operational events.
    Returns structurally quantified alerts.
    """
    alerts = []
    
    if df.empty or "Timestamp" not in df.columns:
        return alerts

    last_ts = df["Timestamp"].max()
    recent_df = df[df["Timestamp"] >= last_ts - pd.Timedelta(hours=24)]
    if recent_df.empty: return alerts

    # Anomaly mathematical check
    if "is_anomaly" in recent_df.columns:
        recent_anoms = recent_df[recent_df["is_anomaly"]]
        if not recent_anoms.empty:
            peak = recent_anoms.loc[recent_anoms["z_score"].idxmax()]
            alerts.append({
                "level": "error",
                "message": f"🚨 **Z-Score Anomaly Triggered**: Load detected at +{peak['z_score']:.1f}σ above structural moving average. Prepare for immediate physical terminal congestion."
            })

    # Capacity Limit check via Congestion Index
    if "Congestion Index" in recent_df.columns and "Route" in recent_df.columns:
        max_idx = recent_df["Congestion Index"].idxmax()
        peak_row = recent_df.loc[max_idx]
        if peak_row["Congestion Index"] > 90:
            alerts.append({
                "level": "warning",
                "message": f"⚠️ **Capacity Breach**: {peak_row['Route']} reached a theoretical thermal congestion of {peak_row['Congestion Index']:.1f}%. Recommend immediate vessel diversion."
            })
            
    # Efficiency Check
    sales = recent_df["Sales Count"].sum()
    reds = recent_df.get("Redemption Count", pd.Series([0])).sum()
    if sales > 200:
        eff = reds / sales
        if eff < 0.60:
             alerts.append({
                 "level": "info",
                 "message": f"💡 **Efficiency Drag**: Redemption efficiency collapsed to {eff*100:.1f}%. High rate of ghost tickets detected in the network."
             })

    return alerts

def render_system_alerts(df: pd.DataFrame):
    """Displays structural alerts inside the UI frame."""
    alerts = detect_passive_anomalies(df)
    for alert in alerts:
        if alert["level"] == "error":
            st.error(alert["message"])
        elif alert["level"] == "warning":
            st.warning(alert["message"])
        else:
            st.info(alert["message"])
