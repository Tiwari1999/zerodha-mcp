"""
Candlestick Pattern Detection
============================

Detects key candlestick patterns for short-term trading signals.
"""


def detect_candlestick_patterns(df, lookback=10):
    """
    Detect major candlestick patterns.

    Returns the top 3 most relevant patterns found.
    """
    if len(df) < 5:
        return {"patterns": [], "top_signal": "HOLD", "confidence": 0}

    recent_df = df.tail(lookback).copy()
    patterns_found = []

    # Check for various patterns
    patterns_found.extend(detect_hammer_patterns(recent_df))
    patterns_found.extend(detect_doji_patterns(recent_df))
    patterns_found.extend(detect_engulfing_patterns(recent_df))
    patterns_found.extend(detect_star_patterns(recent_df))
    patterns_found.extend(detect_piercing_patterns(recent_df))

    # Sort by confidence and return top 3
    patterns_found.sort(key=lambda x: x["confidence"], reverse=True)
    top_patterns = patterns_found[:3]

    # Determine overall signal
    if top_patterns:
        signals = [p["signal"] for p in top_patterns]
        confidences = [p["confidence"] for p in top_patterns]

        # Weighted signal based on confidence
        buy_weight = sum(c for s, c in zip(signals, confidences) if s == "BUY")
        sell_weight = sum(c for s, c in zip(signals, confidences) if s == "SELL")

        if buy_weight > sell_weight + 20:
            top_signal = "BUY"
            overall_confidence = min(80, buy_weight)
        elif sell_weight > buy_weight + 20:
            top_signal = "SELL"
            overall_confidence = min(80, sell_weight)
        else:
            top_signal = "HOLD"
            overall_confidence = max(confidences) if confidences else 0
    else:
        top_signal = "HOLD"
        overall_confidence = 0

    return {
        "patterns": top_patterns,
        "top_signal": top_signal,
        "confidence": overall_confidence,
    }


def detect_hammer_patterns(df):
    """Detect Hammer and Hanging Man patterns."""
    patterns = []

    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i - 1]

        open_price = current["Open"]
        high_price = current["High"]
        low_price = current["Low"]
        close_price = current["Close"]

        # Calculate candle components
        body = abs(close_price - open_price)
        upper_shadow = high_price - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low_price
        total_range = high_price - low_price

        if total_range == 0:
            continue

        # Hammer criteria: small body, long lower shadow, small upper shadow
        body_ratio = body / total_range
        lower_shadow_ratio = lower_shadow / total_range
        upper_shadow_ratio = upper_shadow / total_range

        is_hammer = (
            body_ratio < 0.3 and lower_shadow_ratio > 0.6 and upper_shadow_ratio < 0.1
        )

        if is_hammer:
            # Determine if bullish hammer or bearish hanging man
            if close_price < prev["Close"]:  # In downtrend
                pattern_name = "Hammer"
                signal = "BUY"
                confidence = min(70, 40 + lower_shadow_ratio * 50)
                description = f"Hammer: Bullish reversal signal after decline"
            else:  # In uptrend
                pattern_name = "Hanging Man"
                signal = "SELL"
                confidence = min(65, 35 + lower_shadow_ratio * 40)
                description = f"Hanging Man: Bearish reversal signal after rise"

            patterns.append(
                {
                    "pattern": pattern_name,
                    "signal": signal,
                    "confidence": confidence,
                    "description": description,
                    "position": i,
                }
            )

    return patterns


def detect_doji_patterns(df):
    """Detect Doji patterns (indecision)."""
    patterns = []

    for i in range(len(df)):
        current = df.iloc[i]

        open_price = current["Open"]
        close_price = current["Close"]
        high_price = current["High"]
        low_price = current["Low"]

        total_range = high_price - low_price
        if total_range == 0:
            continue

        body = abs(close_price - open_price)
        body_ratio = body / total_range

        # Doji: very small body
        if body_ratio < 0.1:
            patterns.append(
                {
                    "pattern": "Doji",
                    "signal": "HOLD",
                    "confidence": min(60, 30 + (1 - body_ratio) * 30),
                    "description": "Doji: Market indecision, watch for direction",
                    "position": i,
                }
            )

    return patterns


def detect_engulfing_patterns(df):
    """Detect Bullish and Bearish Engulfing patterns."""
    patterns = []

    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i - 1]

        curr_open = current["Open"]
        curr_close = current["Close"]
        curr_body = abs(curr_close - curr_open)

        prev_open = prev["Open"]
        prev_close = prev["Close"]
        prev_body = abs(prev_close - prev_open)

        # Engulfing criteria: current body engulfs previous body
        if curr_body > prev_body * 1.2:  # Current candle significantly larger

            # Bullish Engulfing: prev bearish, current bullish and engulfs
            if (
                    curr_open < prev_close < prev_open < curr_close  # Previous bearish
                    and curr_close > curr_open
            ):  # Closes above prev open

                patterns.append(
                    {
                        "pattern": "Bullish Engulfing",
                        "signal": "BUY",
                        "confidence": min(75, 50 + (curr_body / prev_body - 1) * 25),
                        "description": "Bullish Engulfing: Strong reversal signal",
                        "position": i,
                    }
                )

            # Bearish Engulfing: prev bullish, current bearish and engulfs
            elif (
                    curr_open > prev_close > prev_open > curr_close  # Previous bullish
                    and curr_close < curr_open
            ):  # Closes below prev open

                patterns.append(
                    {
                        "pattern": "Bearish Engulfing",
                        "signal": "SELL",
                        "confidence": min(75, 50 + (curr_body / prev_body - 1) * 25),
                        "description": "Bearish Engulfing: Strong reversal signal",
                        "position": i,
                    }
                )

    return patterns


def detect_star_patterns(df):
    """Detect Morning Star and Evening Star patterns."""
    patterns = []

    for i in range(2, len(df)):
        first = df.iloc[i - 2]
        middle = df.iloc[i - 1]
        last = df.iloc[i]

        # Morning Star: bearish + small body + bullish
        if (
            first["Close"] < first["Open"]  # First bearish
            and abs(middle["Close"] - middle["Open"])
            < abs(first["Close"] - first["Open"]) * 0.3  # Small middle
            and last["Close"] > last["Open"]  # Last bullish
            and last["Close"] > (first["Open"] + first["Close"]) / 2
        ):  # Good recovery

            patterns.append(
                {
                    "pattern": "Morning Star",
                    "signal": "BUY",
                    "confidence": 70,
                    "description": "Morning Star: Three-candle bullish reversal",
                    "position": i,
                }
            )

        # Evening Star: bullish + small body + bearish
        elif (
            first["Close"] > first["Open"]  # First bullish
            and abs(middle["Close"] - middle["Open"])
            < abs(first["Close"] - first["Open"]) * 0.3  # Small middle
            and last["Close"] < last["Open"]  # Last bearish
            and last["Close"] < (first["Open"] + first["Close"]) / 2
        ):  # Good decline

            patterns.append(
                {
                    "pattern": "Evening Star",
                    "signal": "SELL",
                    "confidence": 70,
                    "description": "Evening Star: Three-candle bearish reversal",
                    "position": i,
                }
            )

    return patterns


def detect_piercing_patterns(df):
    """Detect Piercing Line and Dark Cloud Cover patterns."""
    patterns = []

    for i in range(1, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i - 1]

        curr_open = current["Open"]
        curr_close = current["Close"]
        prev_open = prev["Open"]
        prev_close = prev["Close"]

        prev_body = abs(prev_close - prev_open)
        midpoint = (prev_open + prev_close) / 2

        # Piercing Line: bearish + bullish that pierces above midpoint
        if (
            prev_open > prev_close > curr_open  # Previous bearish
            and curr_close > curr_open  # Opens below prev close
            and curr_close > midpoint
        ):  # Closes above midpoint

            penetration = (curr_close - midpoint) / prev_body

            patterns.append(
                {
                    "pattern": "Piercing Line",
                    "signal": "BUY",
                    "confidence": min(70, 40 + penetration * 40),
                    "description": "Piercing Line: Bullish reversal pattern",
                    "position": i,
                }
            )

        # Dark Cloud Cover: bullish + bearish that penetrates below midpoint
        elif (
                prev_open < prev_close < curr_open  # Previous bullish
                and curr_close < curr_open  # Opens above prev close
                and curr_close < midpoint
        ):  # Closes below midpoint

            penetration = (midpoint - curr_close) / prev_body

            patterns.append(
                {
                    "pattern": "Dark Cloud Cover",
                    "signal": "SELL",
                    "confidence": min(70, 40 + penetration * 40),
                    "description": "Dark Cloud Cover: Bearish reversal pattern",
                    "position": i,
                }
            )

    return patterns
