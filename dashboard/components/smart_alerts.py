from typing import List, Dict
import pandas as pd
import streamlit as st

def generate_alerts(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Scan the latest 24 hours of the dataset for operational anomalies.
    Returns a list of alert dictionaries: {"level": "error|warning|info", "message": "..."}
    """
    alerts = []
    
    if df.empty or "Timestamp" not in df.columns:
        return alerts

    # Get the latest 24 hours
    last_ts = df["Timestamp"].max()
    recent_df = df[df["Timestamp"] >= last_ts - pd.Timedelta(hours=24)]
    
    if recent_df.empty:
        return alerts

    # Check 1: High Congestion
    # Determine the router with highest congestion in recent period
    if "Congestion Index" in recent_df.columns and "Route" in recent_df.columns:
        max_congestion_idx = recent_df["Congestion Index"].idxmax()
        peak_row = recent_df.loc[max_congestion_idx]
        if peak_row["Congestion Index"] > 85:
            alerts.append({
                "level": "error",
                "message": f"🚨 High Congestion Detected! {peak_row['Route']} reached a Congestion Index of {peak_row['Congestion Index']}% at {peak_row['Timestamp'].strftime('%H:%M')}."
            })
            
    # Check 2: Unusual No-show Spike (Redemptions significantly lower than Sales)
    # Total sales vs redemptions in last 12 hours
    last_12h = df[df["Timestamp"] >= last_ts - pd.Timedelta(hours=12)]
    total_sales = last_12h["Sales Count"].sum()
    total_redemptions = last_12h.get("Redemption Count", pd.Series([0])).sum()
    
    if total_sales > 100:  # Base threshold
        no_show_rate = 1.0 - (total_redemptions / total_sales)
        if no_show_rate > 0.40:
            alerts.append({
                "level": "warning",
                "message": f"⚠️ High No-Show Rate: Over the last 12 hours, {no_show_rate*100:.1f}% of tickets went unredeemed (Potential weather impact or event cancellation)."
            })

    # Check 3: Demand imbalance by route 
    if "Route" in recent_df.columns:
        route_vols = recent_df.groupby("Route")["Sales Count"].sum()
        total_vol = route_vols.sum()
        if total_vol > 0:
            for route, vol in route_vols.items():
                if (vol / total_vol) < 0.10: # Less than 10% of traffic
                    alerts.append({
                        "level": "info",
                        "message": f"ℹ️ Underutilization Alert: {route} only carried {(vol/total_vol)*100:.1f}% of total recent traffic. Consider rebalancing ferry allocation."
                    })

    return alerts

def render_smart_alerts(df: pd.DataFrame):
    """Render alerts using Streamlit components."""
    alerts = generate_alerts(df)
    for alert in alerts:
        if alert["level"] == "error":
            st.error(alert["message"], icon="🚨")
        elif alert["level"] == "warning":
            st.warning(alert["message"], icon="⚠️")
        else:
            st.info(alert["message"], icon="💡")
