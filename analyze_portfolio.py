#!/usr/bin/env python3
"""
Portfolio/Holdings Analysis
============================

Analyzes your portfolio holdings with pattern recognition and technical analysis.
Supports multiple input methods:
1. JSON file (live_holdings.json or command line argument)
2. Hardcoded data (for testing)

Usage:
    python analyze_portfolio.py
    python analyze_portfolio.py holdings.json
"""

import json
import os
import sys
from smart_portfolio_analyzer import SmartPortfolioAnalyzer


def format_holdings(holdings_data):
    """Format holdings data for analyzer."""
    formatted = []
    for holding in holdings_data:
        try:
            avg_price = holding.get('average_price', 0) or holding.get('avg_price', 0)
            last_price = holding.get('last_price', 0) or holding.get('current_price', 0)
            
            pnl_percent = 0
            if avg_price > 0:
                pnl_percent = ((last_price - avg_price) / avg_price) * 100
            
            formatted.append({
                'tradingsymbol': holding.get('tradingsymbol', '') or holding.get('symbol', ''),
                'exchange': holding.get('exchange', 'NSE'),
                'quantity': holding.get('quantity', 0),
                'average_price': avg_price,
                'last_price': last_price,
                'pnl': holding.get('pnl', 0),
                'pnl_percent': round(pnl_percent, 2)
            })
        except Exception as e:
            print(f"⚠️  Skipping invalid holding: {e}")
            continue
    return formatted


def load_holdings():
    """
    Load holdings from multiple sources.
    Priority: 
    1. Command line argument (if provided)
    2. live_holdings.json file
    3. Hardcoded sample data (for testing)
    
    Note: MCP tools can't be called from Python code.
    To use live data:
    1. Get holdings using MCP tools in Cursor chat
    2. Save them to 'live_holdings.json' 
    3. Run: python analyze_portfolio.py
    """
    # Option 1: Command line argument
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded holdings from {sys.argv[1]}")
                return data
        except Exception as e:
            print(f"⚠️  Error reading {sys.argv[1]}: {e}")
    
    # Option 2: Check for live_holdings.json
    holdings_file = 'live_holdings.json'
    if os.path.exists(holdings_file):
        try:
            with open(holdings_file, 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded holdings from {holdings_file}")
                return data
        except Exception as e:
            print(f"⚠️  Error reading {holdings_file}: {e}")
    
    # Option 3: Return None (will show usage instructions)
    return None


def main():
    """Main entry point for portfolio analysis."""
    print("=" * 80)
    print("📊 PORTFOLIO/HOLDINGS ANALYSIS")
    print("=" * 80)
    
    # Load holdings
    holdings_data = load_holdings()
    
    if not holdings_data:
        print("\n❌ No holdings data found!")
        print("\n💡 Usage:")
        print("   1. Save your holdings to 'live_holdings.json'")
        print("   2. Or: python analyze_portfolio.py holdings.json")
        print("\n   Holdings format:")
        print("   [")
        print('     {"tradingsymbol": "RELIANCE", "exchange": "NSE", "quantity": 10,')
        print('      "average_price": 2500, "last_price": 2600, "pnl": 1000},')
        print('     {"tradingsymbol": "TCS", "exchange": "NSE", "quantity": 5,')
        print('      "average_price": 3500, "last_price": 3400, "pnl": -500}')
        print("   ]")
        print("\n   💡 Tip: Use MCP tools in chat to fetch live holdings from Zerodha Kite")
        return
    
    # Format holdings
    formatted_holdings = format_holdings(holdings_data)
    
    if not formatted_holdings:
        print("❌ No valid holdings found in data")
        return
    
    print(f"\n✅ Loaded {len(formatted_holdings)} stocks")
    print("🚀 Running analysis with pattern detection and technical indicators...\n")
    
    # Run analysis
    analyzer = SmartPortfolioAnalyzer(formatted_holdings)
    results = analyzer.run_complete_analysis()
    
    if results:
        print("\n✅ Portfolio analysis complete!")
        print("   - Chart patterns detected (Head & Shoulders, Double Tops, etc.)")
        print("   - Technical indicators calculated (RSI, MACD, Bollinger Bands)")
        print("   - Buy/sell/hold recommendations generated")
        return results
    else:
        print("\n⚠️  Analysis completed but no results returned")
        return None


if __name__ == "__main__":
    main()

