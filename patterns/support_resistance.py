"""
Support and Resistance Breakout Pattern Detection
=================================================

Detects support/resistance levels and breakout patterns.
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def detect_breakout_patterns(df, lookback=50, min_touches=3):
    """
    Detect support and resistance breakout patterns.
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

    # Find support and resistance levels
    support_levels = find_support_levels(lows, min_touches)
    resistance_levels = find_resistance_levels(highs, min_touches)

    if not support_levels and not resistance_levels:
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "No clear S/R levels found",
        }

    current_price = closes[-1]

    # Check for breakouts
    resistance_breakout = check_resistance_breakout(
        current_price, resistance_levels, recent_df
    )
    support_breakdown = check_support_breakdown(
        current_price, support_levels, recent_df
    )

    if resistance_breakout:
        return resistance_breakout
    elif support_breakdown:
        return support_breakdown
    else:
        return check_approaching_levels(
            current_price, support_levels, resistance_levels
        )


def find_support_levels(lows, min_touches, tolerance=0.02):
    """Find significant support levels."""
    support_levels = []

    # Find valleys
    valleys, _ = find_peaks(-lows, distance=5)

    if len(valleys) < min_touches:
        return support_levels

    valley_prices = lows[valleys]

    # Group similar price levels
    for i, price in enumerate(valley_prices):
        touches = 1
        similar_prices = [price]

        for j, other_price in enumerate(valley_prices):
            if i != j and abs(price - other_price) / price <= tolerance:
                touches += 1
                similar_prices.append(other_price)

        if touches >= min_touches:
            avg_level = np.mean(similar_prices)
            support_levels.append(
                {
                    "level": avg_level,
                    "touches": touches,
                    "strength": touches * (1 - tolerance),
                }
            )

    # Remove duplicates and sort by strength
    unique_levels = []
    for level in support_levels:
        is_duplicate = False
        for existing in unique_levels:
            if abs(level["level"] - existing["level"]) / level["level"] <= tolerance:
                is_duplicate = True
                if level["strength"] > existing["strength"]:
                    unique_levels.remove(existing)
                    unique_levels.append(level)
                break
        if not is_duplicate:
            unique_levels.append(level)

    return sorted(unique_levels, key=lambda x: x["strength"], reverse=True)


def find_resistance_levels(highs, min_touches, tolerance=0.02):
    """Find significant resistance levels."""
    resistance_levels = []

    # Find peaks
    peaks, _ = find_peaks(highs, distance=5)

    if len(peaks) < min_touches:
        return resistance_levels

    peak_prices = highs[peaks]

    # Group similar price levels
    for i, price in enumerate(peak_prices):
        touches = 1
        similar_prices = [price]

        for j, other_price in enumerate(peak_prices):
            if i != j and abs(price - other_price) / price <= tolerance:
                touches += 1
                similar_prices.append(other_price)

        if touches >= min_touches:
            avg_level = np.mean(similar_prices)
            resistance_levels.append(
                {
                    "level": avg_level,
                    "touches": touches,
                    "strength": touches * (1 - tolerance),
                }
            )

    # Remove duplicates and sort by strength
    unique_levels = []
    for level in resistance_levels:
        is_duplicate = False
        for existing in unique_levels:
            if abs(level["level"] - existing["level"]) / level["level"] <= 0.02:
                is_duplicate = True
                if level["strength"] > existing["strength"]:
                    unique_levels.remove(existing)
                    unique_levels.append(level)
                break
        if not is_duplicate:
            unique_levels.append(level)

    return sorted(unique_levels, key=lambda x: x["strength"], reverse=True)


def check_resistance_breakout(current_price, resistance_levels, df):
    """Check for resistance breakout."""
    if not resistance_levels:
        return None

    strongest_resistance = resistance_levels[0]
    resistance_level = strongest_resistance["level"]

    # Check if price has broken above resistance
    if current_price > resistance_level * 1.005:  # 0.5% above resistance

        # Check volume confirmation
        volume_confirmed = check_breakout_volume(df)

        confidence = min(85, 50 + strongest_resistance["strength"] * 10)
        if volume_confirmed:
            confidence = min(90, confidence + 15)

        return {
            "pattern": "Resistance Breakout",
            "signal": "BUY",
            "confidence": confidence,
            "description": f"Breakout above resistance at ₹{resistance_level:.2f} (touched {strongest_resistance['touches']} times)",
            "key_levels": {
                "resistance_level": resistance_level,
                "touches": strongest_resistance["touches"],
                "volume_confirmed": volume_confirmed,
            },
        }

    # Check if approaching resistance
    elif current_price > resistance_level * 0.98:  # Within 2% of resistance
        return {
            "pattern": "Approaching Resistance",
            "signal": "HOLD",
            "confidence": 60,
            "description": f"Approaching resistance at ₹{resistance_level:.2f}. Watch for breakout or rejection.",
            "key_levels": {
                "resistance_level": resistance_level,
                "touches": strongest_resistance["touches"],
            },
        }

    return None


def check_support_breakdown(current_price, support_levels, df):
    """Check for support breakdown."""
    if not support_levels:
        return None

    strongest_support = support_levels[0]
    support_level = strongest_support["level"]

    # Check if price has broken below support
    if current_price < support_level * 0.995:  # 0.5% below support

        # Check volume confirmation
        volume_confirmed = check_breakout_volume(df)

        confidence = min(85, 50 + strongest_support["strength"] * 10)
        if volume_confirmed:
            confidence = min(90, confidence + 15)

        return {
            "pattern": "Support Breakdown",
            "signal": "SELL",
            "confidence": confidence,
            "description": f"Breakdown below support at ₹{support_level:.2f} (touched {strongest_support['touches']} times)",
            "key_levels": {
                "support_level": support_level,
                "touches": strongest_support["touches"],
                "volume_confirmed": volume_confirmed,
            },
        }

    # Check if approaching support
    elif current_price < support_level * 1.02:  # Within 2% of support
        return {
            "pattern": "Approaching Support",
            "signal": "HOLD",
            "confidence": 60,
            "description": f"Approaching support at ₹{support_level:.2f}. Watch for bounce or breakdown.",
            "key_levels": {
                "support_level": support_level,
                "touches": strongest_support["touches"],
            },
        }

    return None


def check_approaching_levels(current_price, support_levels, resistance_levels):
    """Check if price is approaching key S/R levels."""

    # Find closest levels
    closest_support = None
    closest_resistance = None

    if support_levels:
        for support in support_levels:
            if support["level"] < current_price:
                closest_support = support
                break

    if resistance_levels:
        for resistance in resistance_levels:
            if resistance["level"] > current_price:
                closest_resistance = resistance
                break

    # Check which level is closer
    if closest_support and closest_resistance:
        support_distance = (current_price - closest_support["level"]) / current_price
        resistance_distance = (
            closest_resistance["level"] - current_price
        ) / current_price

        if support_distance < resistance_distance and support_distance < 0.03:
            return {
                "pattern": "Near Support",
                "signal": "HOLD",
                "confidence": 50,
                "description": f"Price near support at ₹{closest_support['level']:.2f}. Potential bounce.",
                "key_levels": {"support_level": closest_support["level"]},
            }
        elif resistance_distance < 0.03:
            return {
                "pattern": "Near Resistance",
                "signal": "HOLD",
                "confidence": 50,
                "description": f"Price near resistance at ₹{closest_resistance['level']:.2f}. Watch for reaction.",
                "key_levels": {"resistance_level": closest_resistance["level"]},
            }

    return {
        "pattern": None,
        "signal": "HOLD",
        "confidence": 0,
        "description": "No significant S/R levels nearby",
    }


def check_breakout_volume(df, volume_multiplier=1.5):
    """Check if recent volume supports breakout."""
    if "Volume" not in df.columns or len(df) < 10:
        return False

    volumes = df["Volume"].values
    recent_volume = np.mean(volumes[-3:])  # Last 3 days average
    avg_volume = np.mean(volumes[-20:-3])  # Previous 17 days average

    return recent_volume > avg_volume * volume_multiplier
