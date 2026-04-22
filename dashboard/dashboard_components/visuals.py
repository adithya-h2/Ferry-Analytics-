import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def build_advanced_time_series(df: pd.DataFrame, window_size: int = 4) -> go.Figure:
    """Creates a high-fidelity time series with plotted anomaly overlay events."""
    plot_df = df.sort_values("Timestamp").copy()
    
    # Calculate rolling averages
    plot_df["Sales Rolling Avg"] = plot_df["Sales Count"].rolling(window=window_size, min_periods=1).mean()

    fig = go.Figure()
    
    # Raw Data (Transparent)
    fig.add_trace(go.Scatter(x=plot_df["Timestamp"], y=plot_df["Sales Count"], mode="lines", name="Sales Volatility", line=dict(color="rgba(31, 119, 180, 0.2)")))
    
    # Smoothed Trend
    fig.add_trace(go.Scatter(x=plot_df["Timestamp"], y=plot_df["Sales Rolling Avg"], mode="lines", name="EMA Trend Core", line=dict(color="rgba(15, 23, 42, 1)", width=2)))

    # Identify and plot statistical anomalies if they exist
    if "is_anomaly" in plot_df.columns:
        anomalies = plot_df[plot_df["is_anomaly"]]
        if not anomalies.empty:
            fig.add_trace(go.Scatter(
                x=anomalies["Timestamp"], 
                y=anomalies["Sales Count"],
                mode="markers",
                name="Stat. Anomaly (>2.5σ)",
                marker=dict(color="red", size=10, symbol="x"),
                hovertext=anomalies["z_score"].apply(lambda z: f"Z-Score: +{z:.1f}σ"),
                hoverinfo="text+x+y"
            ))

    fig.update_layout(
        title="Macro Volatility & Mathematical Congestion Events",
        xaxis_title="Timeline",
        yaxis_title="Headcount Throughput",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        margin=dict(l=10, r=10, t=60, b=10),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=12)
    )
    fig.update_yaxes(gridcolor="rgba(200,200,200,0.2)", zeroline=False)
    fig.update_xaxes(showgrid=False)
    return fig


def build_forecast_chart(df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    """Plots predictive boundaries spanning empirical vs modeled futures."""
    fig = go.Figure()

    if not df.empty:
        hist_df = df.sort_values("Timestamp").tail(96) # Last 24 hours
        fig.add_trace(go.Scatter(
            x=hist_df["Timestamp"], 
            y=hist_df["Sales Count"], 
            mode="lines", 
            name="Empirical Reality", 
            line=dict(color="#0f172a", width=2)
        ))

    if not forecast_df.empty:
        # Confidence Band polygon
        fig.add_trace(go.Scatter(
            x=forecast_df["Timestamp"].tolist() + forecast_df["Timestamp"].tolist()[::-1],
            y=forecast_df["Upper Bound"].tolist() + forecast_df["Lower Bound"].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(59, 130, 246, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name="Variance Bounds"
        ))
        
        # Predicted Extrapolation Line
        fig.add_trace(go.Scatter(
            x=forecast_df["Timestamp"], 
            y=forecast_df["Predicted Demand"], 
            mode="lines+markers", 
            name="EMA Vector Prediction",
            line=dict(color="#3b82f6", width=2, dash='dot')
        ))

    fig.update_layout(
        title="Forward Vector Analytics (Next 6 Hours)",
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=12)
    )
    fig.update_yaxes(gridcolor="rgba(200,200,200,0.2)", zeroline=False)
    return fig


def build_network_efficiency_heatmap(df: pd.DataFrame) -> go.Figure:
    """Builds spatial matrices for route performance."""
    if df.empty or "Route" not in df.columns or "Congestion Index" not in df.columns:
        return go.Figure()

    pivot = df.pivot_table(
        index="Route",
        columns="hour",
        values="Congestion Index",
        aggfunc="mean"
    ).reindex(columns=list(range(0, 24))).fillna(0)

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        labels=dict(x="Hour of Day", y="Terminal Routing", color="Thermal Congestion (%)"),
        title="Spatial Density Matrix"
    )
    
    fig.update_layout(
        height=350, 
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=12)
    )
    fig.update_xaxes(dtick=2)
    return fig
