"""
Triangle Pattern Detection
==========================

Detects Ascending, Descending, and Symmetrical triangle patterns.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks


def detect_triangle_patterns(df, lookback=40, min_touches=3):
    """
    Detect triangle patterns (Ascending, Descending, Symmetrical).

    Args:
        df: DataFrame with OHLC data
        lookback: Number of periods to analyze
        min_touches: Minimum touches required for trendline validation

    Returns:
        dict: Pattern detection results
    """
    if len(df) < lookback:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Insufficient data",
        }

    # Get recent data
    recent_df = df.tail(lookback).copy()
    highs = recent_df["High"].values
    lows = recent_df["Low"].values
    closes = recent_df["Close"].values
    dates = np.arange(len(recent_df))

    # Find peaks and valleys
    peaks, _ = find_peaks(highs, distance=5)
    valleys, _ = find_peaks(-lows, distance=5)

    if len(peaks) < min_touches or len(valleys) < min_touches:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Not enough peaks/valleys for triangle",
        }

    # Calculate trendlines
    peak_slope, peak_r_squared = calculate_trendline(dates[peaks], highs[peaks])
    valley_slope, valley_r_squared = calculate_trendline(dates[valleys], lows[valleys])

    # Require good trendline fit
    if peak_r_squared < 0.6 or valley_r_squared < 0.6:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Trendlines not well-defined",
        }

    # Determine triangle type
    current_price = closes[-1]

    # Ascending Triangle: Flat resistance, rising support
    if abs(peak_slope) < 0.1 and valley_slope > 0.1:
        resistance_level = np.mean(highs[peaks[-3:]])  # Average of recent peaks
        pattern_type = "Ascending Triangle"
        signal = "BUY" if current_price > resistance_level * 0.98 else "HOLD"
        confidence = min(80, 50 + valley_r_squared * 30)
        description = f"Ascending Triangle: Bullish continuation. Resistance at ₹{resistance_level:.2f}"

    # Descending Triangle: Declining resistance, flat support
    elif peak_slope < -0.1 and abs(valley_slope) < 0.1:
        support_level = np.mean(lows[valleys[-3:]])  # Average of recent valleys
        pattern_type = "Descending Triangle"
        signal = "SELL" if current_price < support_level * 1.02 else "HOLD"
        confidence = min(80, 50 + peak_r_squared * 30)
        description = f"Descending Triangle: Bearish continuation. Support at ₹{support_level:.2f}"

    # Symmetrical Triangle: Converging trendlines
    elif peak_slope < -0.05 and valley_slope > 0.05:
        # Find convergence point
        peak_line_start = highs[peaks[0]]
        valley_line_start = lows[valleys[0]]

        # Calculate where lines would meet
        convergence_x = (valley_line_start - peak_line_start) / (
            peak_slope - valley_slope
        )
        convergence_price = peak_line_start + peak_slope * convergence_x

        pattern_type = "Symmetrical Triangle"

        # Signal based on which trendline might break
        upper_line = peak_line_start + peak_slope * len(recent_df)
        lower_line = valley_line_start + valley_slope * len(recent_df)

        if current_price > upper_line * 0.98:
            signal = "BUY"
        elif current_price < lower_line * 1.02:
            signal = "SELL"
        else:
            signal = "HOLD"

        confidence = min(75, 40 + (peak_r_squared + valley_r_squared) * 25)
        description = f"Symmetrical Triangle: Breakout pattern. Watch for break above ₹{upper_line:.2f} or below ₹{lower_line:.2f}"

    else:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "No clear triangle pattern",
        }

    # Calculate pattern reliability based on volume (if available)
    volume_confirmation = check_volume_confirmation(recent_df)
    if volume_confirmation:
        confidence = min(85, confidence + 10)

    return {
        "pattern": pattern_type,
        "signal": signal,
        "confidence": confidence,
        "description": description,
        "key_levels": {
            "peak_slope": peak_slope,
            "valley_slope": valley_slope,
            "peak_r_squared": peak_r_squared,
            "valley_r_squared": valley_r_squared,
        },
    }


def calculate_trendline(x_vals, y_vals):
    """Calculate trendline slope and R-squared."""
    if len(x_vals) < 2:
        return 0, 0

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
    r_squared = r_value**2

    return slope, r_squared


def check_volume_confirmation(df):
    """Check if volume supports the pattern (declining volume in triangle)."""
    if "Volume" not in df.columns:
        return False

    volumes = df["Volume"].values
    if len(volumes) < 10:
        return False

    # Check for declining volume trend
    recent_volume = np.mean(volumes[-10:])
    earlier_volume = (
        np.mean(volumes[-20:-10]) if len(volumes) >= 20 else np.mean(volumes[:-10])
    )

    return recent_volume < earlier_volume * 0.9  # 10% decline in volume
