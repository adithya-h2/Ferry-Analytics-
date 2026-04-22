import pandas as pd
import numpy as np

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies demand anomalies using a rolling Z-score over the trailing 24 hours.
    Anomalies are flagged if the demand spike is >2.5 standard deviations from the rolling mean.
    Returns the dataframe with an `is_anomaly` boolean column and `z_score`.
    """
    if df.empty or "Sales Count" not in df.columns:
        return df
        
    df = df.copy().sort_values("Timestamp")
    
    # 24 hours of 15-minute intervals = 96 periods
    window = 96
    
    rolling_mean = df["Sales Count"].rolling(window=window, min_periods=10).mean()
    rolling_std = df["Sales Count"].rolling(window=window, min_periods=10).std().fillna(1.0)
    
    # Avoid division by zero
    rolling_std = rolling_std.replace(0, 1.0)
    
    df["z_score"] = (df["Sales Count"] - rolling_mean) / rolling_std
    
    # +2.5 std dev is an anomaly spike
    df["is_anomaly"] = df["z_score"] > 2.5
    
    return df

def calculate_health_score(df: pd.DataFrame) -> dict:
    """
    Calculates an Operational Health Score (0-100) based on:
    - Redemption Efficiency (Target > 90%)
    - Congestion Index (Target < 80%)
    - Volatility / Anomalies penalty
    """
    if df.empty:
        return {"score": 100, "status": "Unknown", "details": "No data"}
        
    total_sales = df["Sales Count"].sum()
    total_redemptions = df.get("Redemption Count", pd.Series([0])).sum()
    
    redemption_rate = (total_redemptions / total_sales) if total_sales > 0 else 1.0
    redemption_penalty = max(0, (0.90 - redemption_rate) * 100) # Penalty for no-shows
    
    avg_congestion = df.get("Congestion Index", pd.Series([0])).mean()
    congestion_penalty = max(0, avg_congestion - 50) * 0.5 # Penalty if avg congestion > 50%
    
    # Penalty for anomalous spikes in the recent timeframe
    recently = df.tail(100)
    anomaly_count = recently.get("is_anomaly", pd.Series([False])).sum()
    volatility_penalty = anomaly_count * 2
    
    score = 100.0 - redemption_penalty - congestion_penalty - volatility_penalty
    score = max(0, min(100, score)) # Clamp 0-100
    
    status = "Stable"
    if score < 70:
        status = "At Risk"
    if score < 50:
        status = "Critical"
        
    return {
        "score": score,
        "status": status,
        "redemption_rate": redemption_rate,
        "avg_congestion": avg_congestion,
        "recent_anomalies": anomaly_count
    }
