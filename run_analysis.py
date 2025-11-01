#!/usr/bin/env python3
"""
Single file that analyzes your stocks with pattern detection
Gives clear BUY/SELL/HOLD recommendations
"""

import json
import os
import sys
from smart_portfolio_analyzer import SmartPortfolioAnalyzer


def format_holdings(holdings_data):
    """Format holdings for analyzer"""
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
    Load holdings from file.
    Priority: live_holdings.json > command line argument
    
    Note: MCP tools can't be called from Python code.
    To use live data:
    1. Get holdings using MCP tools in Cursor chat
    2. Save them to 'live_holdings.json' 
    3. Run this script: python run_analysis.py
    """
    # Option 1: Check for live_holdings.json (created by MCP tools in chat)
    holdings_file = 'live_holdings.json'
    if os.path.exists(holdings_file):
        try:
            with open(holdings_file, 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded holdings from {holdings_file}")
                return data
        except Exception as e:
            print(f"⚠️  Error reading {holdings_file}: {e}")
    
    # Option 2: Check command line argument
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded holdings from {sys.argv[1]}")
                return data
        except Exception as e:
            print(f"⚠️  Error reading {sys.argv[1]}: {e}")
    
    return None


def main():
    print("=" * 80)
    print("📊 STOCK ANALYSIS WITH PATTERN DETECTION")
    print("=" * 80)
    
    # Load holdings
    holdings_data = load_holdings()
    
    if not holdings_data:
        print("\n❌ No holdings data found!")
        print("\n💡 Usage:")
        print("   1. Save your holdings to 'live_holdings.json'")
        print("   2. Or: python run_analysis.py holdings.json")
        print("\n   Holdings format:")
        print("   [")
        print('     {"tradingsymbol": "RELIANCE", "quantity": 10, "average_price": 2500, "last_price": 2600},')
        print('     {"tradingsymbol": "TCS", "quantity": 5, "average_price": 3500, "last_price": 3400}')
        print("   ]")
        return
    
    # Format holdings
    formatted_holdings = format_holdings(holdings_data)
    
    if not formatted_holdings:
        print("❌ No valid holdings found in data")
        return
    
    print(f"\n✅ Loaded {len(formatted_holdings)} stocks")
    print("\n🚀 Running analysis with pattern detection...\n")
    
    # Run analysis
    analyzer = SmartPortfolioAnalyzer(formatted_holdings)
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()
