import pandas as pd
import numpy as np

def generate_forecast(df: pd.DataFrame, periods: int = 24) -> pd.DataFrame:
    """
    Generate a simple exponential weighted moving average forecast 
    for the next 'periods' intervals based on historical Sales Count.
    Assumes 15-minute intervals.
    """
    if df.empty or "Timestamp" not in df.columns or "Sales Count" not in df.columns:
        return pd.DataFrame()

    df_sorted = df.copy().sort_values("Timestamp").reset_index(drop=True)
    
    # We will compute an EMA to smooth the data, and use it plus a diurnal seasonal component
    # For a 15-min interval dataset, a day is 96 periods.
    
    # Fast path if not enough data
    if len(df_sorted) < 96:
        last_ts = df_sorted["Timestamp"].iloc[-1]
        future_ts = [last_ts + pd.Timedelta(minutes=15 * i) for i in range(1, periods + 1)]
        mean_sales = df_sorted["Sales Count"].mean()
        forecast = pd.DataFrame({"Timestamp": future_ts, "Predicted Demand": [mean_sales]*periods})
        forecast["Lower Bound"] = np.maximum(0, forecast["Predicted Demand"] - df_sorted["Sales Count"].std())
        forecast["Upper Bound"] = forecast["Predicted Demand"] + df_sorted["Sales Count"].std()
        return forecast

    # Extract historical hourly/daily distributions for a naive seasonal factor
    # Group by hour to get average relative load
    global_mean = df_sorted["Sales Count"].mean()
    hourly_means = df_sorted.groupby("hour")["Sales Count"].mean()
    seasonal_factors = (hourly_means / global_mean).fillna(1.0).to_dict()

    # EMA for trend
    df_sorted["EMA"] = df_sorted["Sales Count"].ewm(span=96, adjust=False).mean()
    last_trend = df_sorted["EMA"].iloc[-1]
    last_std = df_sorted["Sales Count"].std()

    last_ts = df_sorted["Timestamp"].iloc[-1]
    future_ts = [last_ts + pd.Timedelta(minutes=15 * i) for i in range(1, periods + 1)]
    
    predictions = []
    upper_bounds = []
    lower_bounds = []

    for ts in future_ts:
        h = ts.hour
        factor = seasonal_factors.get(h, 1.0)
        
        pred = max(0, last_trend * factor)
        predictions.append(pred)
        
        # Apply confidence bands with heteroskedastic assumption (wider bands during high demand)
        variance_scalar = max(1.0, factor)
        upper_bounds.append(pred + (last_std * 1.5 * variance_scalar))
        lower_bounds.append(max(0, pred - (last_std * 1.5 * variance_scalar)))

    forecast = pd.DataFrame({
        "Timestamp": future_ts,
        "Predicted Demand": np.round(predictions).astype(int),
        "Upper Bound": np.round(upper_bounds).astype(int),
        "Lower Bound": np.round(lower_bounds).astype(int)
    })

    return forecast
