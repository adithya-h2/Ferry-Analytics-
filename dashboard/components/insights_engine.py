import pandas as pd
import streamlit as st

def get_demand_insight(df: pd.DataFrame) -> str:
    """Generate insight about overall demand trends."""
    if df.empty or "Sales Count" not in df.columns:
        return "Not enough data to generate demand insights."
        
    avg_demand = df["Sales Count"].mean()
    max_demand = df["Sales Count"].max()
    
    if max_demand > avg_demand * 3:
        return f"💡 **Demand Volatility Recognized**: The dataset shows spikes up to {max_demand} tickets in a 15-minute window, significantly higher than the average {avg_demand:.0f}. **Recommendation**: Ensure flexible staffing during identified peak events."
    return f"💡 **Stable Demand**: Average throughput is {avg_demand:.0f} per 15-minute interval with manageable peak variations. No extraordinary capacity increases are immediately required based on this subset."

def get_route_insight(df: pd.DataFrame) -> str:
    """Generate insight regarding route congestion."""
    if df.empty or "Route" not in df.columns:
        return ""
    
    route_demand = df.groupby("Route")["Sales Count"].mean()
    busiest_route = route_demand.idxmax()
    quietest_route = route_demand.idxmin()
    
    return f"💡 **Route Intelligence**: **{busiest_route}** represents the most heavily trafficked destination in this timeframe. Conversely, **{quietest_route}** exhibits low demand. **Action**: Consider transitioning a vessel from {quietest_route} to {busiest_route} if congestion index exceeds 85%."

def get_redemption_insight(df: pd.DataFrame) -> str:
    """Generate insight about ticket redemptions (No-shows)."""
    if df.empty or "Redemption Count" not in df.columns:
        return ""
        
    total_sales = df["Sales Count"].sum()
    total_redemptions = df["Redemption Count"].sum()
    
    if total_sales == 0:
        return ""
        
    no_show_rate = 1 - (total_redemptions / total_sales)
    
    if no_show_rate > 0.20:
        return f"💡 **Operational Risk**: A {no_show_rate*100:.1f}% no-show rate is observed. This indicates tickets are being purchased but not used, leading to unpredictable vessel load factors. **Action**: Consider implementing 'use-it-or-lose-it' time-bound ticketing."
    return f"💡 **Healthy Redemption Flow**: The redemption rate sits at an optimal {(1-no_show_rate)*100:.1f}%. Passenger flow aligns well with pre-booked ticket expectations."

def render_insight_panel(insight_text: str):
    """Render the insight box with consistent styling."""
    if insight_text:
        st.info(insight_text)
