#!/usr/bin/env python3
"""
Live Holdings Analysis with Pattern Recognition
Uses real-time data from Kite MCP and applies pattern analysis
"""

from smart_portfolio_analyzer import SmartPortfolioAnalyzer

# Live holdings data from Kite MCP (just fetched)
live_holdings_raw = [
    {"tradingsymbol":"ARKADE","exchange":"NSE","quantity":40,"average_price":137.228,"last_price":174.38,"pnl":1857.6},
    {"tradingsymbol":"ATHERENERG","exchange":"NSE","quantity":20,"average_price":306,"last_price":691.95,"pnl":7719},
    {"tradingsymbol":"AXISBANK","exchange":"BSE","quantity":6,"average_price":795.69,"last_price":1233,"pnl":3061.2},
    {"tradingsymbol":"BANKBARODA","exchange":"NSE","quantity":10,"average_price":259.76,"last_price":278.4,"pnl":466},
    {"tradingsymbol":"CDSL","exchange":"NSE","quantity":4,"average_price":537.675,"last_price":1587.2,"pnl":4198.1},
    {"tradingsymbol":"ETERNAL","exchange":"BSE","quantity":80,"average_price":130.74,"last_price":317.75,"pnl":17765.5},
    {"tradingsymbol":"GAIL","exchange":"BSE","quantity":108,"average_price":119.66,"last_price":182.8,"pnl":6819.25},
    {"tradingsymbol":"GODREJAGRO","exchange":"NSE","quantity":20,"average_price":552.205,"last_price":663.25,"pnl":2220.9},
    {"tradingsymbol":"GOLDBEES","exchange":"NSE","quantity":165,"average_price":74.63,"last_price":100.02,"pnl":5458.8},
    {"tradingsymbol":"HCLTECH","exchange":"NSE","quantity":11,"average_price":1179.46,"last_price":1541.5,"pnl":3982.45},
    {"tradingsymbol":"HINDPETRO","exchange":"BSE","quantity":28,"average_price":249.68,"last_price":476,"pnl":8600.25},
    {"tradingsymbol":"INFY","exchange":"BSE","quantity":6,"average_price":1722.67,"last_price":1482.5,"pnl":-1441},
    {"tradingsymbol":"IOC","exchange":"BSE","quantity":18,"average_price":118.08,"last_price":165.9,"pnl":860.75},
    {"tradingsymbol":"IRCTC","exchange":"BSE","quantity":79,"average_price":892.13,"last_price":719.25,"pnl":-13657.7},
    {"tradingsymbol":"JUNIORBEES","exchange":"NSE","quantity":19,"average_price":725.08,"last_price":750.95,"pnl":957.08},
    {"tradingsymbol":"KALAMANDIR","exchange":"NSE","quantity":67,"average_price":222,"last_price":182.2,"pnl":-2666.6},
    {"tradingsymbol":"LIQUIDCASE","exchange":"BSE","quantity":62,"average_price":109.42,"last_price":111.19,"pnl":154.19},
    {"tradingsymbol":"MARUTI","exchange":"BSE","quantity":1,"average_price":6785.75,"last_price":16191.9,"pnl":9406.15},
    {"tradingsymbol":"NIFTYBEES","exchange":"BSE","quantity":68,"average_price":237.16,"last_price":291.1,"pnl":3667.72},
    {"tradingsymbol":"PAYTM","exchange":"NSE","quantity":8,"average_price":1611,"last_price":1303.2,"pnl":-2462.4},
    {"tradingsymbol":"PICCADIL","exchange":"BSE","quantity":6,"average_price":63.575,"last_price":680.25,"pnl":3700.05},
    {"tradingsymbol":"POLICYBZR","exchange":"BSE","quantity":9,"average_price":794.79,"last_price":1792,"pnl":8974.9},
    {"tradingsymbol":"POWERGRID","exchange":"BSE","quantity":37,"average_price":192.9,"last_price":288.15,"pnl":3524.25},
    {"tradingsymbol":"SAGILITY","exchange":"BSE","quantity":100,"average_price":41.286,"last_price":52.55,"pnl":1126.4},
    {"tradingsymbol":"SBIN","exchange":"BSE","quantity":37,"average_price":553.32,"last_price":937,"pnl":14196},
    {"tradingsymbol":"TATAPOWER","exchange":"BSE","quantity":133,"average_price":241.57,"last_price":405.05,"pnl":21742.2},
    {"tradingsymbol":"TCS","exchange":"NSE","quantity":4,"average_price":4030.41,"last_price":3058,"pnl":-3889.65},
    {"tradingsymbol":"TECHM","exchange":"BSE","quantity":12,"average_price":1498.6,"last_price":1426.35,"pnl":-867},
    {"tradingsymbol":"TMPV","exchange":"BSE","quantity":79,"average_price":378.2,"last_price":410.1,"pnl":2520.35},
    {"tradingsymbol":"VEDL","exchange":"BSE","quantity":18,"average_price":340.51,"last_price":493.6,"pnl":4286.6},
    {"tradingsymbol":"WIPRO","exchange":"NSE","quantity":6,"average_price":0,"last_price":240.67,"pnl":1444.02}
]

def format_holdings(raw_data):
    """Format MCP holdings data for analyzer"""
    holdings = []
    for holding in raw_data:
        # Calculate P&L percentage
        avg_price = holding['average_price']
        last_price = holding['last_price']
        pnl = holding['pnl']
        
        if avg_price > 0:
            pnl_percent = ((last_price - avg_price) / avg_price) * 100
        else:
            pnl_percent = 0
            
        holdings.append({
            'tradingsymbol': holding['tradingsymbol'],
            'exchange': holding['exchange'],
            'quantity': holding['quantity'],
            'average_price': avg_price,
            'last_price': last_price,
            'pnl': pnl,
            'pnl_percent': round(pnl_percent, 2)
        })
    return holdings

def main():
    """Run complete analysis with pattern recognition"""
    print("🚀 LIVE PORTFOLIO ANALYSIS WITH PATTERN RECOGNITION")
    print("=" * 80)
    
    # Format holdings data
    holdings_data = format_holdings(live_holdings_raw)
    
    print(f"📊 Loaded {len(holdings_data)} holdings from Kite MCP")
    print(f"💰 Analyzing with pattern detection enabled...\n")
    
    # Initialize analyzer (pattern analysis is automatically enabled)
    analyzer = SmartPortfolioAnalyzer(holdings_data)
    
    # Run complete analysis with pattern recognition
    results = analyzer.run_complete_analysis()
    
    print("\n✅ Pattern analysis complete!")
    print("   - Chart patterns detected (Head & Shoulders, Double Tops, etc.)")
    print("   - Technical indicators calculated (RSI, MACD, Bollinger Bands)")
    print("   - Buy/sell recommendations generated")
    
    return results

if __name__ == "__main__":
    main()

