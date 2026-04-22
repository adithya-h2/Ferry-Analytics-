import pandas as pd
import streamlit as st

def get_demand_insight(df: pd.DataFrame) -> str:
    """Generate computed mathematical insight about demand."""
    if df.empty or "Sales Count" not in df.columns or "is_weekend" not in df.columns:
        return "Insufficient data."
        
    avg_demand = df["Sales Count"].mean()
    weekend_df = df[df["is_weekend"]]
    weekday_df = df[~df["is_weekend"]]
    
    if not weekend_df.empty and not weekday_df.empty:
        we_mean = weekend_df["Sales Count"].mean()
        wd_mean = weekday_df["Sales Count"].mean()
        
        diff_pct = ((we_mean - wd_mean) / wd_mean) * 100 if wd_mean > 0 else 0
        
        if diff_pct > 10:
            suggested_extra_vessels = max(1, int(we_mean // 350) - int(wd_mean // 350))
            return f"💡 **Demand Volatility**: Weekend demand exceeded weekday averages by **{diff_pct:.1f}%** ({we_mean:.0f} vs {wd_mean:.0f} average pass/interval). **Recommendation**: Temporary fleet expansion of **{suggested_extra_vessels}** additional vessel(s) during weekend peak periods to maintain stability."
        elif diff_pct < -10:
             return f"💡 **Demand Inefficiency**: Weekend demand underperformed weekdays by **{abs(diff_pct):.1f}%**. **Recommendation**: Reduce idle capacity; return 1 vessel to reserve."
            
    return f"💡 **Stable Demand**: Average throughput is {avg_demand:.0f} per interval. Volatility is within acceptable (+/- 10%) parameters."

def get_route_insight(df: pd.DataFrame) -> str:
    """Generate mathematical route distribution insights."""
    if df.empty or "Route" not in df.columns:
        return ""
    
    route_vols = df.groupby("Route")["Sales Count"].sum()
    total_vol = route_vols.sum()
    
    if total_vol == 0: return ""
    
    busiest_route = route_vols.idxmax()
    busiest_share = (route_vols.max() / total_vol) * 100
    
    quietest_route = route_vols.idxmin()
    quietest_share = (route_vols.min() / total_vol) * 100
    
    if busiest_share > 50:
         return f"💡 **Load Imbalance**: **{busiest_route}** represents a dominant **{busiest_share:.1f}%** of all traffic, while {quietest_route} holds only {quietest_share:.1f}%. **Action**: Shift 1 standby vessel from {quietest_route} terminal to support {busiest_route} operations."
    
    return f"💡 **Balanced Distribution**: Network distribution is healthy. Highest traffic share is {busiest_route} at {busiest_share:.1f}%."

def get_anomaly_insight(df: pd.DataFrame) -> str:
    """Generate text concerning statistical demand anomalies."""
    if df.empty or "is_anomaly" not in df.columns:
         return ""
         
    anomalies = df[df["is_anomaly"]]
    if not anomalies.empty:
        max_z = anomalies["z_score"].max()
        peak_anomaly_time = anomalies.loc[anomalies["z_score"].idxmax()]["Timestamp"]
        return f"🚨 **Statistical Event**: Passenger demand spike detected mathematically **{max_z:.1f}** standard deviations above baseline moving average occurring at {peak_anomaly_time.strftime('%Y-%m-%d %H:%M')}. Review external scheduling software for unregistered public events."
    return ""

def render_insight_panel(insight_text: str):
    """Render the insight box with consistent, premium UI scaling."""
    if insight_text:
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-top: 10px; color: #1e293b; font-size: 0.95rem;">
                {insight_text}
            </div>
            """, 
            unsafe_allow_html=True
        )
