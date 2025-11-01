"""
Flag and Pennant Pattern Detection
==================================

Detects Flag and Pennant patterns (short-term continuation patterns).
"""

import numpy as np
import pandas as pd
from scipy import stats


def detect_flag_patterns(df, lookback=30):
    """
    Detect Flag patterns (rectangular consolidation after strong move).
    """
    if len(df) < lookback:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Insufficient data",
        }

    recent_df = df.tail(lookback).copy()
    highs = recent_df["High"].values
    lows = recent_df["Low"].values
    closes = recent_df["Close"].values

    # Identify strong move (flagpole)
    price_change = (closes[-1] - closes[0]) / closes[0]

    if abs(price_change) < 0.10:  # Need at least 10% move
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "No significant prior move for flag",
        }

    # Check for consolidation in recent periods
    consolidation_periods = min(15, len(recent_df) // 2)
    consolidation_data = recent_df.tail(consolidation_periods)

    # Calculate consolidation range
    consolidation_high = consolidation_data["High"].max()
    consolidation_low = consolidation_data["Low"].min()
    consolidation_range = (consolidation_high - consolidation_low) / consolidation_low

    # Flag should have tight consolidation (< 8% range)
    if consolidation_range > 0.08:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Consolidation range too wide for flag",
        }

    # Determine flag direction
    is_bullish_flag = price_change > 0
    current_price = closes[-1]

    if is_bullish_flag:
        # Bull flag - expect upward breakout
        breakout_level = consolidation_high
        if current_price > breakout_level * 0.99:
            signal = "BUY"
            confidence = min(75, 50 + abs(price_change) * 100)
            description = (
                f"Bull Flag: Bullish continuation. Breakout above ₹{breakout_level:.2f}"
            )
        else:
            signal = "HOLD"
            confidence = min(60, 40 + abs(price_change) * 50)
            description = (
                f"Bull Flag forming: Watch for breakout above ₹{breakout_level:.2f}"
            )
    else:
        # Bear flag - expect downward breakout
        breakout_level = consolidation_low
        if current_price < breakout_level * 1.01:
            signal = "SELL"
            confidence = min(75, 50 + abs(price_change) * 100)
            description = f"Bear Flag: Bearish continuation. Breakdown below ₹{breakout_level:.2f}"
        else:
            signal = "HOLD"
            confidence = min(60, 40 + abs(price_change) * 50)
            description = (
                f"Bear Flag forming: Watch for breakdown below ₹{breakout_level:.2f}"
            )

    return {
        "pattern": "Bull Flag" if is_bullish_flag else "Bear Flag",
        "signal": signal,
        "confidence": confidence,
        "description": description,
        "key_levels": {
            "flagpole_move": price_change * 100,
            "consolidation_high": consolidation_high,
            "consolidation_low": consolidation_low,
            "breakout_level": breakout_level,
        },
    }


def detect_pennant_patterns(df, lookback=25):
    """
    Detect Pennant patterns (triangular consolidation after strong move).
    """
    if len(df) < lookback:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Insufficient data",
        }

    recent_df = df.tail(lookback).copy()
    closes = recent_df["Close"].values

    # Identify strong move (pennant pole)
    price_change = (closes[-1] - closes[0]) / closes[0]

    if abs(price_change) < 0.08:  # Need at least 8% move
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "No significant prior move for pennant",
        }

    # Check for triangular consolidation
    consolidation_periods = min(12, len(recent_df) // 2)
    consolidation_data = recent_df.tail(consolidation_periods)

    # Calculate if highs are declining and lows are rising (pennant shape)
    highs = consolidation_data["High"].values
    lows = consolidation_data["Low"].values
    dates = np.arange(len(consolidation_data))

    # Trendline analysis
    if len(dates) < 5:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Insufficient consolidation data",
        }

    high_slope, high_r2, _, _, _ = stats.linregress(dates, highs)
    low_slope, low_r2, _, _, _ = stats.linregress(dates, lows)

    # Pennant: declining highs, rising lows (converging)
    is_pennant = (
        high_slope < -0.1 and low_slope > 0.1 and high_r2 > 0.5 and low_r2 > 0.5
    )

    if not is_pennant:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "No converging trendlines for pennant",
        }

    # Determine pennant direction based on prior move
    is_bullish_pennant = price_change > 0
    current_price = closes[-1]

    # Calculate breakout levels
    recent_high = consolidation_data["High"].max()
    recent_low = consolidation_data["Low"].min()

    if is_bullish_pennant:
        breakout_level = recent_high
        if current_price > breakout_level * 0.99:
            signal = "BUY"
            confidence = min(80, 55 + abs(price_change) * 100)
            description = f"Bull Pennant: Bullish continuation. Breakout above ₹{breakout_level:.2f}"
        else:
            signal = "HOLD"
            confidence = min(65, 45 + abs(price_change) * 50)
            description = (
                f"Bull Pennant forming: Watch for breakout above ₹{breakout_level:.2f}"
            )
    else:
        breakout_level = recent_low
        if current_price < breakout_level * 1.01:
            signal = "SELL"
            confidence = min(80, 55 + abs(price_change) * 100)
            description = f"Bear Pennant: Bearish continuation. Breakdown below ₹{breakout_level:.2f}"
        else:
            signal = "HOLD"
            confidence = min(65, 45 + abs(price_change) * 50)
            description = (
                f"Bear Pennant forming: Watch for breakdown below ₹{breakout_level:.2f}"
            )

    return {
        "pattern": "Bull Pennant" if is_bullish_pennant else "Bear Pennant",
        "signal": signal,
        "confidence": confidence,
        "description": description,
        "key_levels": {
            "pole_move": price_change * 100,
            "high_slope": high_slope,
            "low_slope": low_slope,
            "breakout_level": breakout_level,
        },
    }
