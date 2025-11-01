# Smart Portfolio Analyzer

An advanced portfolio analysis tool that provides **technical analysis**, **chart pattern recognition**, and actionable recommendations for your stock holdings.

## 🎯 Features

- **Technical Analysis**: RSI, MACD, Moving Averages, Bollinger Bands, ADX, and more
- **📊 Chart Pattern Recognition**: 15+ patterns including Head & Shoulders, Double Tops/Bottoms, Triangles, Flags, and Candlestick patterns
- **Multi-timeframe Analysis**: Daily, weekly, and monthly chart analysis
- **🎨 Pattern Confidence Scoring**: AI-powered pattern detection with confidence levels
- **Risk Assessment**: Stop-loss recommendations and profit booking alerts
- **Sector Diversification**: Portfolio composition analysis
- **Market Condition Assessment**: Overall market trend analysis
- **Automated Reports**: Comprehensive analysis reports with actionable insights

## 🆕 NEW: Chart Pattern Analysis

The analyzer now includes advanced pattern recognition that detects:

### Reversal Patterns
- **Head and Shoulders** / **Inverse Head and Shoulders**
- **Double Top** / **Double Bottom** 

### Continuation Patterns  
- **Ascending/Descending/Symmetrical Triangles**
- **Bull/Bear Flags and Pennants**

### Breakout Patterns
- **Resistance Breakouts** / **Support Breakdowns**
- **Support/Resistance Level Detection**

### Candlestick Patterns
- **Hammer, Hanging Man, Doji**
- **Bullish/Bearish Engulfing**
- **Morning/Evening Stars**

**Each pattern includes:**
- ✅ Confidence score (0-100%)  
- 📈 BUY/SELL/HOLD signal
- 📝 Detailed explanation
- 🎯 Key price levels

## How It Works

1. **Get Portfolio Data**: Use Zerodha Kite MCP tools in chat to fetch your holdings
2. **Update Data**: Copy your holdings data to `run_analysis.py`
3. **Run Analysis**: Execute the analysis script to get recommendations
4. **Review Results**: Get detailed buy/sell/hold recommendations with confidence scores **+ pattern analysis**

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Your Portfolio Data
In your MCP-enabled chat, use the Kite tools to get your holdings:
```
Can you get my current holdings from Kite?
```

### 3. Update Analysis Script
Copy your holdings data to the `holdings_data` list in `run_analysis.py`.

### 4. Run Analysis
```bash
python run_analysis.py
```

## 📊 Sample Output with Pattern Analysis

```
🚀 HIGH-CONFIDENCE RECOMMENDATIONS:
   📈 STRONG BUY SIGNALS:
      🟢 BPCL: 95.0% confidence
         💰 Investment: ₹3,465 | P&L: +27.9%
         🎨 Patterns: 5 detected
            📈 Double Bottom: 85% confidence
            📈 Resistance Breakout: 90% confidence
         📝 Pattern Summary: Primary: Resistance Breakout (90% confidence) | 📈 Bullish signals dominate

   📉 STRONG SELL SIGNALS:
      🔴 ARKADE: 95.0% confidence
         💰 Investment: ₹5,120 | P&L: +43.5%
         🎨 Patterns: 6 detected
            📉 Double Top: 85% confidence
            ⚖️ Hanging Man: 60% confidence
         📝 Pattern Summary: Primary: Double Top (85% confidence) | 📉 Bearish signals dominate
```

## Technical Indicators + Patterns

### Technical Analysis
- **RSI (Relative Strength Index)**: Momentum oscillator for overbought/oversold conditions
- **MACD**: Moving Average Convergence Divergence for trend changes
- **Bollinger Bands**: Volatility bands for price extremes
- **ADX**: Average Directional Index for trend strength
- **Moving Averages**: 20, 50, and 200-day trends
- **Volume Analysis**: Trading volume patterns

### NEW: Pattern Analysis
- **Algorithmic Detection**: Uses scipy for mathematical pattern recognition
- **Confidence Scoring**: 20-100% confidence levels based on pattern quality
- **Multi-Pattern Analysis**: Detects up to 15+ different pattern types per stock
- **Weighted Signals**: Patterns weighted by category (Reversal > Breakout > Continuation > Candlestick)
- **Volume Confirmation**: Breakout patterns confirmed with volume analysis

## Risk Management

- **Stop-loss Alerts**: For positions with significant losses
- **Profit Booking**: Recommendations for high-gain positions  
- **Pattern-Based Targets**: Price targets based on pattern measurements
- **Position Sizing**: Risk-adjusted recommendations
- **Sector Analysis**: Diversification assessment

## 🎨 Pattern Analysis Demo

To see pattern analysis in action on individual stocks:

   ```bash
python pattern_demo.py
```

This will analyze popular stocks and show detected patterns with confidence scores.

## Output Files

- CSV reports with detailed analysis for each stock
- **Pattern analysis data** included in reports
- Timestamped files for tracking analysis history
- Technical indicators and confidence scores
- **Top 3 patterns per stock** with explanations

## Requirements

- Python 3.7+
- pandas, numpy, yfinance, ta (technical analysis library)
- **scipy** (for pattern detection)
- Internet connection for fetching stock data

## Workflow Example

1. **In Chat**: "Get my Kite holdings"
2. **Copy Data**: Update `run_analysis.py` with your holdings
3. **Run**: `python run_analysis.py`
4. **Review**: Check recommendations **+ pattern insights** and take action

## 🔧 Advanced Usage

### Pattern Analysis Only
```python
from patterns.pattern_analyzer import analyze_stock_patterns
import yfinance as yf

# Download data
df = yf.Ticker("RELIANCE.NS").history(period="1y")

# Analyze patterns
result = analyze_stock_patterns(df, "RELIANCE")
print(f"Signal: {result['overall_signal']} ({result['overall_confidence']}%)")
```

### Custom Pattern Detection
Individual pattern detectors can be used separately - see `patterns/README.md` for details.

## Support

This tool provides recommendations based on technical analysis **and chart patterns**. Always do your own research and consider your risk tolerance before making investment decisions.

**Pattern analysis adds powerful insights but should be combined with fundamental analysis and market conditions.**

---

*Powered by Smart Portfolio Analyzer - Technical Analysis + **Chart Pattern Recognition** + Yahoo Finance Data*# zerodha-mcp
