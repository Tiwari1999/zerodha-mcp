"""
Double Top and Double Bottom Pattern Detection
==============================================

Detects Double Top (bearish reversal) and Double Bottom (bullish reversal) patterns.
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def detect_double_top(df, lookback=30, tolerance=0.03):
    """
    Detect Double Top pattern (bearish reversal).

    Args:
        df: DataFrame with OHLC data
        lookback: Number of periods to look back
        tolerance: Price tolerance for pattern validation (3% default)

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

    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values

    # Find peaks
    peaks, properties = find_peaks(highs, distance=10, prominence=None)

    if len(peaks) < 2:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Not enough peaks found",
        }

    # Look for two peaks of similar height
    recent_peaks = peaks[-10:] if len(peaks) >= 10 else peaks

    for i in range(len(recent_peaks) - 1):
        for j in range(i + 1, len(recent_peaks)):
            first_peak_idx = recent_peaks[i]
            second_peak_idx = recent_peaks[j]

            first_peak = highs[first_peak_idx]
            second_peak = highs[second_peak_idx]

            # Check if peaks are similar in height (within tolerance)
            height_diff = abs(first_peak - second_peak) / max(first_peak, second_peak)

            if height_diff <= tolerance:
                # Find the valley between peaks
                valley_start = min(first_peak_idx, second_peak_idx)
                valley_end = max(first_peak_idx, second_peak_idx)
                valley_low = min(lows[valley_start: valley_end + 1])

                # Calculate pattern strength
                peak_avg = (first_peak + second_peak) / 2
                valley_depth = (peak_avg - valley_low) / peak_avg

                if valley_depth > 0.05:  # At least 5% retracement
                    current_price = closes[-1]
                    support_level = valley_low

                    # Pattern confidence based on valley depth and peak similarity
                    confidence = min(
                        85, 40 + valley_depth * 300 + (1 - height_diff) * 30
                    )

                    # Signal generation
                    if current_price < support_level * 1.02:  # Near support break
                        signal = "SELL"
                        description = f"Double Top: Bearish reversal. Peaks at ₹{first_peak:.2f} & ₹{second_peak:.2f}, Support at ₹{support_level:.2f}"
                    elif current_price < peak_avg * 0.95:  # Below peak average
                        signal = "HOLD"
                        description = f"Double Top forming: Watch for support break below ₹{support_level:.2f}"
                    else:
                        signal = "HOLD"
                        description = (
                            f"Double Top pattern detected but price still elevated"
                        )

                    return {
                        "pattern": "Double Top",
                        "signal": signal,
                        "confidence": confidence,
                        "description": description,
                        "key_levels": {
                            "first_peak": first_peak,
                            "second_peak": second_peak,
                            "support_level": support_level,
                            "target": support_level
                                      - (peak_avg - support_level),  # Measured move
                        },
                    }

    return {
        "pattern": None,
        "signal": "HOLD",
        "confidence": 0,
        "description": "No Double Top pattern detected",
    }


def detect_double_bottom(df, lookback=30, tolerance=0.03):
    """
    Detect Double Bottom pattern (bullish reversal).
    """
    if len(df) < lookback:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Insufficient data",
        }

    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values

    # Find valleys (inverted peaks)
    valleys, properties = find_peaks(-lows, distance=10, prominence=None)

    if len(valleys) < 2:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Not enough valleys found",
        }

    # Look for two valleys of similar depth
    recent_valleys = valleys[-10:] if len(valleys) >= 10 else valleys

    for i in range(len(recent_valleys) - 1):
        for j in range(i + 1, len(recent_valleys)):
            first_valley_idx = recent_valleys[i]
            second_valley_idx = recent_valleys[j]

            first_valley = lows[first_valley_idx]
            second_valley = lows[second_valley_idx]

            # Check if valleys are similar in depth
            depth_diff = abs(first_valley - second_valley) / max(
                first_valley, second_valley
            )

            if depth_diff <= tolerance:
                # Find the peak between valleys
                peak_start = min(first_valley_idx, second_valley_idx)
                peak_end = max(first_valley_idx, second_valley_idx)
                peak_high = max(highs[peak_start: peak_end + 1])

                # Calculate pattern strength
                valley_avg = (first_valley + second_valley) / 2
                peak_height = (peak_high - valley_avg) / valley_avg

                if peak_height > 0.05:  # At least 5% rally between valleys
                    current_price = closes[-1]
                    resistance_level = peak_high

                    # Pattern confidence
                    confidence = min(85, 40 + peak_height * 300 + (1 - depth_diff) * 30)

                    # Signal generation
                    if current_price > resistance_level * 0.98:  # Near resistance break
                        signal = "BUY"
                        description = f"Double Bottom: Bullish reversal. Valleys at ₹{first_valley:.2f} & ₹{second_valley:.2f}, Resistance at ₹{resistance_level:.2f}"
                    elif current_price > valley_avg * 1.03:  # Above valley average
                        signal = "HOLD"
                        description = f"Double Bottom forming: Watch for resistance break above ₹{resistance_level:.2f}"
                    else:
                        signal = "HOLD"
                        description = (
                            f"Double Bottom pattern detected but price still weak"
                        )

                    return {
                        "pattern": "Double Bottom",
                        "signal": signal,
                        "confidence": confidence,
                        "description": description,
                        "key_levels": {
                            "first_valley": first_valley,
                            "second_valley": second_valley,
                            "resistance_level": resistance_level,
                            "target": resistance_level
                                      + (resistance_level - valley_avg),  # Measured move
                        },
                    }

    return {
        "pattern": None,
        "signal": "HOLD",
        "confidence": 0,
        "description": "No Double Bottom pattern detected",
    }
