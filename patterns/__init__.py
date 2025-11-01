"""
Chart Pattern Detection Package
===============================

This package contains modules for detecting various chart patterns
that help predict stock price movements.

Available Patterns:
- Trend Reversal Patterns (head_and_shoulders, double_top_bottom)
- Continuation Patterns (triangles, flags_pennants)
- Candlestick Patterns (single_candle, multiple_candle)
- Support/Resistance Patterns (breakouts, consolidation)
"""

from .head_and_shoulders import detect_head_and_shoulders
from .double_patterns import detect_double_top, detect_double_bottom
from .triangles import detect_triangle_patterns
from .flags_pennants import detect_flag_patterns, detect_pennant_patterns
from .candlestick_patterns import detect_candlestick_patterns
from .support_resistance import detect_breakout_patterns

__all__ = [
    "detect_head_and_shoulders",
    "detect_double_top",
    "detect_double_bottom",
    "detect_triangle_patterns",
    "detect_flag_patterns",
    "detect_pennant_patterns",
    "detect_candlestick_patterns",
    "detect_breakout_patterns",
]
