import pandas as pd
import streamlit as st
import sys
from pathlib import Path

# Fix relative imports depending on sys.path
try:
    from dashboard.forecasting.model import extract_next_peak, generate_forecast
    from dashboard.analytics.anomaly_detection import calculate_health_score
except ImportError:
    from forecasting.model import extract_next_peak, generate_forecast
    from analytics.anomaly_detection import calculate_health_score

def render_executive_brief(df: pd.DataFrame):
    """Render a rigorous C-level operational health dashboard."""
    if df.empty:
        st.warning("Insufficient data.")
        return

    health_metrics = calculate_health_score(df)
    score = health_metrics["score"]
    status = health_metrics["status"]
    
    status_colors = {"Stable": "🟢", "At Risk": "🟡", "Critical": "🔴"}
    icon = status_colors.get(status, "⚪")

    forecast = generate_forecast(df, periods=24)
    next_peak = extract_next_peak(forecast)

    st.markdown("## 📊 Executive Reliability Report")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown(f"### System Health: {icon} **{score:.1f}/100** ({status})")
        
        st.markdown("#### Structural Assessment")
        if score > 80:
            st.success("**Operations Running Nominally.** Capacity balances match throughput and passenger friction is statistically insignificant.")
        elif score > 60:
             st.warning("**Operational Friction Detected.** Moderate system drag due to anomalous volume spikes or ticket inefficiencies.")
        else:
             st.error("**System Risk Critical.** Redemptions drastically mismatched with sales and rolling variance limits severely breached.")
             
        # Anomaly text
        if health_metrics["recent_anomalies"] > 0:
            st.markdown(f"- ⚠️ **{health_metrics['recent_anomalies']}** Volatility spikes (>2.5 std dev) flagged in recent block.")
            
    with col2:
        st.markdown("### 🔭 Forward Predictive Intelligence")
        
        if next_peak:
            peak_time = next_peak["timestamp"].strftime("%I:%M %p")
            peak_vol = next_peak["volume"]
            st.markdown(f"- **Target Congestion Window**: The models forecast the next major demand cluster occurring around **{peak_time}**.")
            st.markdown(f"- **Expected Load**: Projected interval volume of **{peak_vol:.0f}** passengers.")
            vessel_needs = int(peak_vol // 250) + 1
            st.markdown(f"**Automated Decision Support**: Given load bounds, system recommends preemptive orchestration of **{vessel_needs} vessel(s)** directly prior to {peak_time}.")
        else:
            st.markdown("- No definitive forecast extracted.")

    st.markdown("---")
