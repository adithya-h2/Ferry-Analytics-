from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def build_time_series(df: pd.DataFrame, window_size: int = 4) -> go.Figure:
    """Create a line chart of Sales Count and Redemption Count over time with rolling averages."""

    plot_df = df.sort_values("Timestamp").copy()
    
    # Calculate rolling averages for smoother trend lines
    plot_df["Sales Rolling Avg"] = plot_df["Sales Count"].rolling(window=window_size, min_periods=1).mean()
    plot_df["Redemption Rolling Avg"] = plot_df["Redemption Count"].rolling(window=window_size, min_periods=1).mean()

    fig = go.Figure()
    
    # Raw Data (Lighter, transparent)
    fig.add_trace(go.Scatter(x=plot_df["Timestamp"], y=plot_df["Sales Count"], mode="lines", name="Sales (Raw)", line=dict(color="rgba(31, 119, 180, 0.3)")))
    fig.add_trace(go.Scatter(x=plot_df["Timestamp"], y=plot_df["Redemption Count"], mode="lines", name="Redemptions (Raw)", line=dict(color="rgba(255, 127, 14, 0.3)")))
    
    # Smoothed Data
    fig.add_trace(go.Scatter(x=plot_df["Timestamp"], y=plot_df["Sales Rolling Avg"], mode="lines", name="Sales (Rolling Trend)", line=dict(color="rgba(31, 119, 180, 1)", width=3)))
    fig.add_trace(go.Scatter(x=plot_df["Timestamp"], y=plot_df["Redemption Rolling Avg"], mode="lines", name="Redemptions (Rolling Trend)", line=dict(color="rgba(255, 127, 14, 1)", width=3)))

    fig.update_layout(
        title="Demand Volatility & Smoothed Trends",
        xaxis_title="Timestamp",
        yaxis_title="Volume",
        legend_title_text="Metric",
        height=450,
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(gridcolor="rgba(200,200,200,0.2)")
    return fig


def build_forecast_chart(df: pd.DataFrame, forecast_df: pd.DataFrame) -> go.Figure:
    """Create a chart showing recent actual demand vs forecasted demand with confidence bands."""
    fig = go.Figure()

    if not df.empty:
        # Show last 100 points
        hist_df = df.sort_values("Timestamp").tail(100)
        fig.add_trace(go.Scatter(
            x=hist_df["Timestamp"], 
            y=hist_df["Sales Count"], 
            mode="lines", 
            name="Actual Historical", 
            line=dict(color="#1f77b4", width=2)
        ))

    if not forecast_df.empty:
        # Confidence Band
        fig.add_trace(go.Scatter(
            x=forecast_df["Timestamp"].tolist() + forecast_df["Timestamp"].tolist()[::-1],
            y=forecast_df["Upper Bound"].tolist() + forecast_df["Lower Bound"].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(255, 0, 0, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name="Confidence Interval"
        ))
        
        # Predicted Line
        fig.add_trace(go.Scatter(
            x=forecast_df["Timestamp"], 
            y=forecast_df["Predicted Demand"], 
            mode="lines+markers", 
            name="Forecasted Demand",
            line=dict(color="#d62728", width=2, dash='dot')
        ))

    fig.update_layout(
        title="Demand Forecast (Next 6 Hours)",
        xaxis_title="Timestamp",
        yaxis_title="Predicted Passenger Volume",
        height=450,
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_yaxes(gridcolor="rgba(200,200,200,0.2)")
    return fig


def build_route_congestion_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create a heatmap showing congestion index across routes over the day."""
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
        color_continuous_scale="Reds",
        labels=dict(x="Hour of Day", y="Route", color="Congestion (%)"),
        title="Operational Heatmap: Route Congestion"
    )
    
    fig.update_layout(
        height=350, 
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(dtick=2)
    return fig


def build_hourly_average_bar(df: pd.DataFrame) -> go.Figure:
    """Create a bar chart of hourly average demand (sales and redemptions)."""

    hourly = (
        df.groupby("hour", as_index=False)[["Sales Count", "Redemption Count"]].mean()
        if "hour" in df.columns
        else pd.DataFrame(columns=["hour", "Sales Count", "Redemption Count"])
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(x=hourly["hour"], y=hourly["Sales Count"], name="Sales (avg)", marker_color="#1f77b4"))
    fig.add_trace(
        go.Bar(
            x=hourly["hour"],
            y=hourly["Redemption Count"],
            name="Redemptions (avg)",
            marker_color="#ff7f0e"
        )
    )
    fig.update_layout(
        barmode="group",
        title="Hourly Demand Profile",
        xaxis_title="Hour of day",
        yaxis_title="Average count",
        height=360,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(gridcolor="rgba(200,200,200,0.2)")
    return fig


def build_hour_vs_dow_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create a heatmap of average sales by hour and day-of-week."""

    if not {"hour", "day_name"}.issubset(df.columns):
        return go.Figure()

    pivot = df.pivot_table(
        index="hour",
        columns="day_name",
        values="Sales Count",
        aggfunc="mean",
    ).reindex(index=list(range(0, 24)))

    day_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]
    existing_days = [d for d in day_order if d in pivot.columns]
    pivot = pivot[existing_days]

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Viridis",
        labels=dict(x="Day of week", y="Hour", color="Avg Volume"),
        title="Macroscopic Heatmap: Weekly Demand Patterns",
    )
    fig.update_layout(
        height=420, 
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

