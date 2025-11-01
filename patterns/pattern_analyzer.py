"""
Main Pattern Analyzer
=====================

Integrates all pattern detection modules and provides unified pattern analysis.
"""

import sys
import os

# Add patterns directory to path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from head_and_shoulders import (
        detect_head_and_shoulders,
        detect_inverse_head_and_shoulders,
    )
    from double_patterns import detect_double_top, detect_double_bottom
    from triangles import detect_triangle_patterns
    from flags_pennants import detect_flag_patterns, detect_pennant_patterns
    from candlestick_patterns import detect_candlestick_patterns
    from support_resistance import detect_breakout_patterns
except ImportError:
    # Fallback if imports fail
    def fallback_pattern(*args, **kwargs):
        return {
            "pattern": None,
            "signal": "HOLD",
            "confidence": 0,
            "description": "Pattern detection unavailable",
        }

    detect_head_and_shoulders = fallback_pattern
    detect_inverse_head_and_shoulders = fallback_pattern
    detect_double_top = fallback_pattern
    detect_double_bottom = fallback_pattern
    detect_triangle_patterns = fallback_pattern
    detect_flag_patterns = fallback_pattern
    detect_pennant_patterns = fallback_pattern
    detect_candlestick_patterns = fallback_pattern
    detect_breakout_patterns = fallback_pattern


class PatternAnalyzer:
    """
    Main pattern analyzer that detects and ranks chart patterns.
    """

    def __init__(self):
        self.pattern_detectors = [
            # Reversal Patterns (High Priority)
            ("Head and Shoulders", detect_head_and_shoulders),
            ("Inverse Head and Shoulders", detect_inverse_head_and_shoulders),
            ("Double Top", detect_double_top),
            ("Double Bottom", detect_double_bottom),
            # Continuation Patterns (Medium Priority)
            ("Triangle Patterns", detect_triangle_patterns),
            ("Flag Patterns", detect_flag_patterns),
            ("Pennant Patterns", detect_pennant_patterns),
            # Support/Resistance (High Priority)
            ("Breakout Patterns", detect_breakout_patterns),
            # Candlestick Patterns (Medium Priority)
            ("Candlestick Patterns", detect_candlestick_patterns),
        ]

    def analyze_patterns(self, df, symbol="UNKNOWN"):
        """
        Analyze all patterns for a given stock.

        Returns:
            dict: Complete pattern analysis with top 3 patterns
        """
        if df is None or df.empty:
            return {
                "symbol": symbol,
                "patterns_detected": [],
                "top_3_patterns": [],
                "overall_signal": "HOLD",
                "overall_confidence": 0,
                "pattern_summary": "No data available for pattern analysis",
            }

        all_patterns = []

        # Run all pattern detectors
        for pattern_name, detector_func in self.pattern_detectors:
            try:
                if pattern_name == "Candlestick Patterns":
                    # Candlestick patterns return multiple patterns
                    result = detector_func(df)
                    if result and result.get("patterns"):
                        for pattern in result["patterns"]:
                            pattern["category"] = "Candlestick"
                            all_patterns.append(pattern)
                else:
                    # Other patterns return single pattern
                    result = detector_func(df)
                    if result and result.get("pattern"):
                        result["category"] = self._get_pattern_category(pattern_name)
                        result["detector"] = pattern_name
                        all_patterns.append(result)
            except Exception as e:
                print(f"Error detecting {pattern_name} for {symbol}: {e}")
                continue

        # Filter valid patterns and sort by confidence
        valid_patterns = [p for p in all_patterns if p.get("confidence", 0) > 20]
        valid_patterns.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        # Get top 3 patterns
        top_3_patterns = valid_patterns[:3]

        # Calculate overall signal and confidence
        overall_signal, overall_confidence = self._calculate_overall_signal(
            valid_patterns
        )

        # Generate pattern summary
        pattern_summary = self._generate_pattern_summary(top_3_patterns, overall_signal)

        return {
            "symbol": symbol,
            "patterns_detected": len(valid_patterns),
            "top_3_patterns": top_3_patterns,
            "overall_signal": overall_signal,
            "overall_confidence": overall_confidence,
            "pattern_summary": pattern_summary,
            "all_patterns": valid_patterns,  # For detailed analysis
        }

    def _get_pattern_category(self, pattern_name):
        """Categorize patterns for better organization."""
        if pattern_name in [
            "Head and Shoulders",
            "Inverse Head and Shoulders",
            "Double Top",
            "Double Bottom",
        ]:
            return "Reversal"
        elif pattern_name in ["Triangle Patterns", "Flag Patterns", "Pennant Patterns"]:
            return "Continuation"
        elif pattern_name in ["Breakout Patterns"]:
            return "Breakout"
        else:
            return "Other"

    def _calculate_overall_signal(self, patterns):
        """Calculate overall signal from all detected patterns."""
        if not patterns:
            return "HOLD", 0

        # Weight patterns by confidence and category
        weighted_signals = {"BUY": 0, "SELL": 0, "HOLD": 0}
        total_weight = 0

        for pattern in patterns:
            signal = pattern.get("signal", "HOLD")
            confidence = pattern.get("confidence", 0)
            category = pattern.get("category", "Other")

            # Apply category multipliers
            category_multiplier = {
                "Reversal": 1.5,  # Higher weight for reversal patterns
                "Breakout": 1.3,  # High weight for breakouts
                "Continuation": 1.0,  # Normal weight for continuation
                "Candlestick": 0.8,  # Lower weight for candlestick patterns
                "Other": 0.5,
            }.get(category, 1.0)

            weight = confidence * category_multiplier
            weighted_signals[signal] += weight
            total_weight += weight

        # Determine overall signal
        if total_weight == 0:
            return "HOLD", 0

        # Normalize scores
        buy_score = weighted_signals["BUY"] / total_weight * 100
        sell_score = weighted_signals["SELL"] / total_weight * 100
        hold_score = weighted_signals["HOLD"] / total_weight * 100

        # Determine final signal with threshold
        if buy_score > sell_score + 15 and buy_score > 30:
            return "BUY", min(85, int(buy_score))
        elif sell_score > buy_score + 15 and sell_score > 30:
            return "SELL", min(85, int(sell_score))
        else:
            return "HOLD", min(70, int(max(buy_score, sell_score, hold_score)))

    def _generate_pattern_summary(self, top_patterns, overall_signal):
        """Generate a human-readable pattern summary."""
        if not top_patterns:
            return "No significant patterns detected"

        summary_parts = []

        # Describe top pattern
        top_pattern = top_patterns[0]
        summary_parts.append(
            f"Primary: {top_pattern.get('pattern', 'Unknown')} ({top_pattern.get('confidence', 0):.0f}% confidence)"
        )

        # Add signal interpretation
        signal_desc = {
            "BUY": "📈 Bullish signals dominate",
            "SELL": "📉 Bearish signals dominate",
            "HOLD": "⚖️ Mixed or neutral signals",
        }.get(overall_signal, "Unclear signals")

        summary_parts.append(signal_desc)

        # Add pattern count
        if len(top_patterns) > 1:
            summary_parts.append(f"Additional patterns: {len(top_patterns) - 1}")

        return " | ".join(summary_parts)

    def get_pattern_explanation(self, pattern_name):
        """Get detailed explanation of what a pattern means."""
        explanations = {
            "Head and Shoulders": "Bearish reversal pattern. Three peaks with middle highest. Suggests trend change from up to down.",
            "Inverse Head and Shoulders": "Bullish reversal pattern. Three valleys with middle lowest. Suggests trend change from down to up.",
            "Double Top": "Bearish reversal. Two peaks at similar levels suggest uptrend exhaustion.",
            "Double Bottom": "Bullish reversal. Two valleys at similar levels suggest downtrend exhaustion.",
            "Ascending Triangle": "Bullish continuation. Flat resistance, rising support. Expect upward breakout.",
            "Descending Triangle": "Bearish continuation. Declining resistance, flat support. Expect downward breakdown.",
            "Symmetrical Triangle": "Neutral breakout pattern. Converging trendlines. Direction depends on breakout.",
            "Bull Flag": "Bullish continuation. Tight consolidation after strong up move. Expect continued rise.",
            "Bear Flag": "Bearish continuation. Tight consolidation after strong down move. Expect continued fall.",
            "Resistance Breakout": "Bullish signal. Price breaks above key resistance level with volume.",
            "Support Breakdown": "Bearish signal. Price breaks below key support level with volume.",
            "Hammer": "Bullish reversal candlestick. Small body, long lower wick after decline.",
            "Hanging Man": "Bearish reversal candlestick. Small body, long lower wick after rise.",
            "Bullish Engulfing": "Bullish reversal. Large green candle engulfs previous red candle.",
            "Bearish Engulfing": "Bearish reversal. Large red candle engulfs previous green candle.",
        }

        return explanations.get(pattern_name, "Pattern explanation not available")


# Convenience function for easy integration
def analyze_stock_patterns(df, symbol="UNKNOWN"):
    """
    Main function to analyze patterns for a stock.

    Usage:
        from patterns.pattern_analyzer import analyze_stock_patterns
        result = analyze_stock_patterns(stock_dataframe, "RELIANCE")
    """
    analyzer = PatternAnalyzer()
    return analyzer.analyze_patterns(df, symbol)
