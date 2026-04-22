import pandas as pd
import numpy as np
from datetime import timedelta

def generate_forecast(df: pd.DataFrame, periods: int = 24) -> pd.DataFrame:
    """
    Generate a simple exponential weighted moving average forecast 
    augmented with historical diurnal variance, predicting future passenger demand.
    Returns standard forecast DataFrame with explicit confidence bands.
    """
    if df.empty or "Timestamp" not in df.columns or "Sales Count" not in df.columns:
        return pd.DataFrame()

    df_sorted = df.copy().sort_values("Timestamp").reset_index(drop=True)
    
    global_mean = df_sorted["Sales Count"].mean()
    hourly_means = df_sorted.groupby("hour")["Sales Count"].mean()
    seasonal_factors = (hourly_means / global_mean).replace(0, 1.0).fillna(1.0).to_dict()

    df_sorted["EMA"] = df_sorted["Sales Count"].ewm(span=96, adjust=False).mean()
    last_trend = df_sorted["EMA"].iloc[-1]
    
    # Calculate localized variance for tighter bands
    last_std = df_sorted["Sales Count"].tail(96).std()
    if np.isnan(last_std) or last_std == 0:
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

def extract_next_peak(forecast_df: pd.DataFrame) -> dict:
    """
    Identifies the exact timestamp and volume of the next forecasted peak.
    """
    if forecast_df.empty:
        return None
        
    peak_idx = forecast_df["Predicted Demand"].idxmax()
    peak_row = forecast_df.loc[peak_idx]
    
    return {
        "timestamp": peak_row["Timestamp"],
        "volume": peak_row["Predicted Demand"],
        "upper_bound": peak_row["Upper Bound"]
    }
