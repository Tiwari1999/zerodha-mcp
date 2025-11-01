"""
Head and Shoulders Pattern Detection
===================================

Detects Head and Shoulders (bearish reversal) and Inverse Head and Shoulders (bullish reversal) patterns.
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, find_peaks_cwt


def detect_head_and_shoulders(df, lookback=20, tolerance=0.02):
    """
    Detect Head and Shoulders pattern.

    Args:
        df: DataFrame with OHLC data
        lookback: Number of periods to look back for pattern
        tolerance: Price tolerance for pattern validation (2% default)

    Returns:
        dict: Pattern detection results
    """
    if len(df) < lookback * 2:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Insufficient data",
        }

    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values

    # Find peaks and valleys
    peaks, _ = find_peaks(highs, distance=5)
    valleys, _ = find_peaks(-lows, distance=5)

    if len(peaks) < 3:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Not enough peaks found",
        }

    # Get recent peaks for pattern analysis
    recent_peaks = peaks[-5:] if len(peaks) >= 5 else peaks
    recent_peak_values = highs[recent_peaks]

    # Head and Shoulders: Left Shoulder < Head > Right Shoulder
    # Look for three consecutive peaks where middle is highest
    for i in range(len(recent_peaks) - 2):
        left_idx = recent_peaks[i]
        head_idx = recent_peaks[i + 1]
        right_idx = recent_peaks[i + 2]

        left_peak = highs[left_idx]
        head_peak = highs[head_idx]
        right_peak = highs[right_idx]

        # Check if head is higher than both shoulders
        if head_peak > left_peak and head_peak > right_peak:
            # Check if shoulders are approximately equal (within tolerance)
            shoulder_diff = abs(left_peak - right_peak) / max(left_peak, right_peak)

            if shoulder_diff <= tolerance:
                # Calculate neckline (support level between shoulders)
                neckline_level = min(lows[left_idx : right_idx + 1])
                current_price = closes[-1]

                # Pattern strength based on head prominence
                head_prominence = (head_peak - max(left_peak, right_peak)) / head_peak
                confidence = min(85, 50 + head_prominence * 100)

                # Signal generation
                if current_price < neckline_level * 1.01:  # Below neckline
                    signal = "SELL"
                    description = f"Head and Shoulders: Bearish reversal pattern. Head at ₹{head_peak:.2f}, Neckline at ₹{neckline_level:.2f}"
                else:
                    signal = "HOLD"
                    description = f"Head and Shoulders forming: Watch for neckline break at ₹{neckline_level:.2f}"

                return {
                    "pattern": "Head and Shoulders",
                    "signal": signal,
                    "confidence": confidence,
                    "description": description,
                    "key_levels": {
                        "head": head_peak,
                        "left_shoulder": left_peak,
                        "right_shoulder": right_peak,
                        "neckline": neckline_level,
                    },
                }

    return {
        "pattern": None,
        "signal": "HOLD",
        "confidence": 0,
        "description": "No Head and Shoulders pattern detected",
    }


def detect_inverse_head_and_shoulders(df, lookback=20, tolerance=0.02):
    """
    Detect Inverse Head and Shoulders pattern (bullish reversal).
    """
    if len(df) < lookback * 2:
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
    valleys, _ = find_peaks(-lows, distance=5)

    if len(valleys) < 3:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Not enough valleys found",
        }

    # Get recent valleys for pattern analysis
    recent_valleys = valleys[-5:] if len(valleys) >= 5 else valleys

    # Inverse Head and Shoulders: Left Shoulder > Head < Right Shoulder
    for i in range(len(recent_valleys) - 2):
        left_idx = recent_valleys[i]
        head_idx = recent_valleys[i + 1]
        right_idx = recent_valleys[i + 2]

        left_valley = lows[left_idx]
        head_valley = lows[head_idx]
        right_valley = lows[right_idx]

        # Check if head is lower than both shoulders
        if head_valley < left_valley and head_valley < right_valley:
            # Check if shoulders are approximately equal
            shoulder_diff = abs(left_valley - right_valley) / max(
                left_valley, right_valley
            )

            if shoulder_diff <= tolerance:
                # Calculate neckline (resistance level)
                neckline_level = max(highs[left_idx : right_idx + 1])
                current_price = closes[-1]

                # Pattern strength
                head_prominence = (
                    min(left_valley, right_valley) - head_valley
                ) / head_valley
                confidence = min(85, 50 + head_prominence * 100)

                # Signal generation
                if current_price > neckline_level * 0.99:  # Above neckline
                    signal = "BUY"
                    description = f"Inverse Head and Shoulders: Bullish reversal pattern. Head at ₹{head_valley:.2f}, Neckline at ₹{neckline_level:.2f}"
                else:
                    signal = "HOLD"
                    description = f"Inverse Head and Shoulders forming: Watch for neckline break above ₹{neckline_level:.2f}"

                return {
                    "pattern": "Inverse Head and Shoulders",
                    "signal": signal,
                    "confidence": confidence,
                    "description": description,
                    "key_levels": {
                        "head": head_valley,
                        "left_shoulder": left_valley,
                        "right_shoulder": right_valley,
                        "neckline": neckline_level,
                    },
                }

    return {
        "pattern": None,
        "signal": "HOLD",
        "confidence": 0,
        "description": "No Inverse Head and Shoulders pattern detected",
    }
