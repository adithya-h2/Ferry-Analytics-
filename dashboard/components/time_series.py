from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_time_series(df: pd.DataFrame) -> go.Figure:
    """Create a line chart of Sales Count and Redemption Count over time."""

    plot_df = df.sort_values("Timestamp").copy()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=plot_df["Timestamp"],
            y=plot_df["Sales Count"],
            mode="lines",
            name="Sales Count",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=plot_df["Timestamp"],
            y=plot_df["Redemption Count"],
            mode="lines",
            name="Redemption Count",
        )
    )
    fig.update_layout(
        title="Tickets Sold vs Redeemed Over Time",
        xaxis_title="Timestamp",
        yaxis_title="Count",
        legend_title_text="Metric",
        height=420,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def build_hourly_average_bar(df: pd.DataFrame) -> go.Figure:
    """Create a bar chart of hourly average demand (sales and redemptions)."""

    hourly = (
        df.groupby("hour", as_index=False)[["Sales Count", "Redemption Count"]].mean()
        if "hour" in df.columns
        else pd.DataFrame(columns=["hour", "Sales Count", "Redemption Count"])
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(x=hourly["hour"], y=hourly["Sales Count"], name="Sales (avg)"))
    fig.add_trace(
        go.Bar(
            x=hourly["hour"],
            y=hourly["Redemption Count"],
            name="Redemptions (avg)",
        )
    )
    fig.update_layout(
        barmode="group",
        title="Hourly Average Demand",
        xaxis_title="Hour of day",
        yaxis_title="Average count",
        height=360,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(dtick=1)
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
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    existing_days = [d for d in day_order if d in pivot.columns]
    pivot = pivot[existing_days]

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels=dict(x="Day of week", y="Hour", color="Avg sales"),
        title="Heatmap: Average Sales (Hour vs Day of Week)",
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
    return fig

