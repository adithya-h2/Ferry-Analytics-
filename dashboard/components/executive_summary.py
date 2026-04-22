import pandas as pd
import streamlit as st

def render_executive_summary(df: pd.DataFrame):
    """Render a C-level executive dashboard briefing."""
    if df.empty:
        st.warning("Insufficient data to generate an Executive Summary. Please expand filters.")
        return

    # Main Metrics
    total_tickets = df["Sales Count"].sum()
    total_redemptions = df.get("Redemption Count", pd.Series([0])).sum()
    no_show_rate = 1.0 - (total_redemptions / max(total_tickets, 1))
    
    if "Congestion Index" in df.columns:
        max_congestion = df["Congestion Index"].max()
    else:
        max_congestion = 0

    st.markdown("## 📊 Executive Operational Briefing")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Key Findings")
        st.markdown(f"""
        - **Total Ticket Volume**: {total_tickets:,.0f} processed.
        - **System Efficiency**: Currently operating at a **{(1-no_show_rate)*100:.1f}%** redemption rate.
        - **Congestion Peak**: Reached a maximum congestion index of **{max_congestion:.1f}%** during the selected window.
        """)
        
        if max_congestion > 80:
            st.error("**Risk Indicator**: Critical congestion threshold exceeded during peaks.")
        else:
            st.success("**Risk Indicator**: Operations occurring within standard capacity limits.")
            
    with col2:
        st.markdown("### Operational Recommendations")
        # Generate dynamic recommendations
        if df["is_weekend"].any():
             st.markdown("- 🚢 **Fleet Alignment**: Ensure maximum fleet availability (3+ vessels) for weekend peak hours.")
             
        if no_show_rate > 0.25:
             st.markdown("- 📉 **Yield Management**: Investigate high no-show rate. Review cancellation and refund policies.")
             
        if "Route" in df.columns:
             busiest = df.groupby("Route")["Sales Count"].sum().idxmax()
             st.markdown(f"- 🗺️ **Routing**: Allocate primary high-capacity vessels to the **{busiest}** route.")

    st.markdown("---")
