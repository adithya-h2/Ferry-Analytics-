from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def project_root() -> Path:
    """Return the `ferry_analytics/` root directory based on this file's location."""

    return Path(__file__).resolve().parents[1]


def featured_data_path() -> Path:
    """Build the relative path to the featured CSV input."""

    return project_root() / "data" / "processed" / "ferry_featured.csv"


def figures_dir() -> Path:
    """Return the directory where EDA figures will be saved."""

    return project_root() / "reports" / "figures"


def save_figure(fig: plt.Figure, filename: str) -> Path:
    """Save a matplotlib figure to the figures directory."""

    out_dir = figures_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out_path


def load_featured(path: Path) -> pd.DataFrame:
    """Load featured dataset and parse Timestamp."""

    df = pd.read_csv(path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)
    return df


def main() -> None:
    """Generate EDA plots and print key operational insights."""

    in_path = featured_data_path()
    if not in_path.exists():
        raise FileNotFoundError(
            f"Featured CSV not found at: {in_path}. "
            f"Run '03_feature_engineering.py' first to generate it."
        )

    sns.set_theme(style="whitegrid")
    df = load_featured(in_path)

    print(f"Loaded featured data from: {in_path}")
    print(f"Shape: {df.shape}")
    print(f"Saving figures to: {figures_dir()}")

    # a) Hourly average Sales Count and Redemption Count (line chart)
    hourly_avg = (
        df.groupby("hour", as_index=False)[["Sales Count", "Redemption Count"]].mean()
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(hourly_avg["hour"], hourly_avg["Sales Count"], label="Sales (avg)", linewidth=2)
    ax.plot(
        hourly_avg["hour"],
        hourly_avg["Redemption Count"],
        label="Redemptions (avg)",
        linewidth=2,
    )
    ax.set_title("Hourly Average Tickets Sold vs Redeemed")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Average count")
    ax.set_xticks(range(0, 24, 1))
    ax.legend()
    a_path = save_figure(fig, "a_hourly_avg_sales_vs_redemptions.png")
    print(f"Saved: {a_path}")

    # b) Daily demand by day of week (bar chart)
    dow_avg = (
        df.groupby(["day_of_week", "day_name"], as_index=False)["Sales Count"].mean()
        .sort_values("day_of_week")
    )
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.barplot(data=dow_avg, x="day_name", y="Sales Count", ax=ax, color="#4C72B0")
    ax.set_title("Average Tickets Sold by Day of Week")
    ax.set_xlabel("Day of week")
    ax.set_ylabel("Average Sales Count")
    b_path = save_figure(fig, "b_day_of_week_avg_sales.png")
    print(f"Saved: {b_path}")

    # c) Monthly demand trends (bar chart)
    month_avg = (
        df.groupby(["month", "month_name"], as_index=False)["Sales Count"].mean()
        .sort_values("month")
    )
    fig, ax = plt.subplots(figsize=(11, 4))
    sns.barplot(data=month_avg, x="month_name", y="Sales Count", ax=ax, color="#55A868")
    ax.set_title("Average Tickets Sold by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Sales Count")
    ax.tick_params(axis="x", rotation=45)
    c_path = save_figure(fig, "c_monthly_avg_sales.png")
    print(f"Saved: {c_path}")

    # d) Yearly trend (line chart)
    yearly = df.groupby("year", as_index=False)[["Sales Count", "Redemption Count"]].sum()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(yearly["year"], yearly["Sales Count"], label="Sales (sum)", linewidth=2)
    ax.plot(yearly["year"], yearly["Redemption Count"], label="Redemptions (sum)", linewidth=2)
    ax.set_title("Yearly Ticket Sales & Redemptions (Total)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total count")
    ax.legend()
    d_path = save_figure(fig, "d_yearly_totals_sales_redemptions.png")
    print(f"Saved: {d_path}")

    # e) Peak vs off-peak hour heatmap (hour vs month)
    heat = (
        df.pivot_table(
            index="hour",
            columns="month",
            values="Sales Count",
            aggfunc="mean",
        )
        .sort_index()
        .sort_index(axis=1)
    )
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(heat, ax=ax, cmap="YlOrRd")
    ax.set_title("Heatmap: Average Tickets Sold (Hour vs Month)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Hour")
    e_path = save_figure(fig, "e_heatmap_hour_vs_month_avg_sales.png")
    print(f"Saved: {e_path}")

    # f) Net passenger movement over time
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df["Timestamp"], df["net_passenger_movement"], linewidth=0.8, color="#C44E52")
    ax.set_title("Net Passenger Movement Over Time (Sales - Redemptions)")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Net movement")
    f_path = save_figure(fig, "f_net_passenger_movement_over_time.png")
    print(f"Saved: {f_path}")

    # g) Season-wise distribution (boxplot)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=df, x="season", y="Sales Count", ax=ax)
    ax.set_title("Season-wise Distribution of Ticket Sales")
    ax.set_xlabel("Season")
    ax.set_ylabel("Sales Count")
    g_path = save_figure(fig, "g_season_wise_sales_distribution_boxplot.png")
    print(f"Saved: {g_path}")

    # Key insights
    peak_hours = (
        df.groupby("hour", as_index=False)["Sales Count"].mean().sort_values("Sales Count", ascending=False)
    )
    top3_hours = peak_hours.head(3)["hour"].tolist()

    busiest_month_row = month_avg.sort_values("Sales Count", ascending=False).head(1)
    busiest_month = busiest_month_row["month_name"].iloc[0]

    busiest_day_row = dow_avg.sort_values("Sales Count", ascending=False).head(1)
    busiest_day = busiest_day_row["day_name"].iloc[0]

    print("\nKey insights:")
    print(f"- Top 3 peak hours (by avg Sales Count): {top3_hours}")
    print(f"- Busiest month (by avg Sales Count): {busiest_month}")
    print(f"- Busiest day (by avg Sales Count): {busiest_day}")


if __name__ == "__main__":
    main()

