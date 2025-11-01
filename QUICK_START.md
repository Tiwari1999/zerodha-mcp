# Quick Start Guide - Smart Portfolio Analyzer

## Overview
This tool analyzes your stock portfolio using advanced technical analysis and provides actionable buy/sell recommendations.

## Simple 4-Step Process

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get Your Portfolio Data
In your MCP-enabled chat (like Claude with Kite MCP), ask:
```
Can you get my current holdings from Kite?
```

You'll get data like:
```json
[
  {
    "tradingsymbol": "ARKADE",
    "quantity": 40,
    "average_price": 128.00,
    "last_price": 183.64,
    "pnl": 2225.60,
    "pnl_percent": 43.47
  },
  // ... more holdings
]
```

### Step 3: Update the Analysis Script
Open `run_analysis.py` and replace the `holdings_data` list with your actual data.

### Step 4: Run Analysis
```bash
python run_analysis.py
```

## What You'll Get

✅ **Technical Analysis** for each stock with confidence scores
✅ **Buy/Sell/Hold recommendations** with detailed reasoning  
✅ **Risk alerts** for positions with significant losses
✅ **Profit booking suggestions** for high-gain stocks
✅ **Portfolio diversification analysis**
✅ **CSV report** with all details

## Sample Output

```
🚀 HIGH-CONFIDENCE RECOMMENDATIONS:
   📈 STRONG BUY SIGNALS:
      🟢 BPCL: 95.0% confidence
         💰 Investment: ₹3,465 | P&L: +27.9%
         📊 RSI oversold, strong uptrend

   📉 STRONG SELL SIGNALS:
      🔴 ARKADE: 95.0% confidence
         💰 Investment: ₹5,120 | P&L: +43.5%
         📊 RSI overbought, consider profit booking

🛑 URGENT - STOP-LOSS REVIEW:
   • COALINDIA: -23.5% loss
```

## Technical Indicators Used

- **RSI**: Overbought/oversold conditions
- **MACD**: Trend direction changes
- **Moving Averages**: Trend strength (20, 50, 200-day)
- **Bollinger Bands**: Price volatility bands
- **ADX**: Trend strength indicator
- **Volume Analysis**: Trading activity patterns

## Tips

1. **Run regularly**: Markets change, analyze weekly or bi-weekly
2. **Don't rely solely**: Use as one input in your decision-making
3. **Consider risk tolerance**: High-confidence signals aren't guarantees
4. **Track results**: Keep the CSV files to track recommendation accuracy

## Troubleshooting

**Error downloading data**: Some stocks might not be available on Yahoo Finance. The tool will still analyze available stocks.

**No MCP access**: You can manually format your holdings data by looking at the structure in `run_analysis.py`.

---

*Always do your own research before making investment decisions!* 