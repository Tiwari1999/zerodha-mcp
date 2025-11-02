#!/usr/bin/env python3
"""
News-Based Stock Recommender
============================

This script:
1. Scrapes Moneycontrol news from last 24 hours
2. Extracts stock tickers mentioned in news
3. Runs pattern analysis on those stocks
4. Recommends top 3 stocks to buy based on:
   - News frequency (how often mentioned)
   - Pattern analysis (technical signals)
   - Technical indicators (RSI, MACD, etc.)
"""

from datetime import datetime
import sys
from pathlib import Path

from news_analysis import scrape_markets_news

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from same package (news_analysis)


# Import from parent directory
from smart_portfolio_analyzer import SmartPortfolioAnalyzer

import pandas as pd
import warnings

warnings.filterwarnings("ignore")


class NewsBasedStockRecommender:
    """Recommends stocks based on news mentions and technical analysis."""
    
    def __init__(self):
        self.analyzer = SmartPortfolioAnalyzer()
        self.recommendations = []
        
    def get_yahoo_symbol(self, ticker, exchange="NSE"):
        """Convert Indian stock ticker to Yahoo Finance symbol."""
        # Common mappings
        stock_mapping = {
            "TCS": "TCS.NS",
            "INFY": "INFY.NS",
            "RELIANCE": "RELIANCE.NS",
            "HDFCBANK": "HDFCBANK.NS",
            "HDFC": "HDFC.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "BHARTIARTL": "BHARTIARTL.NS",
            "SBIN": "SBIN.NS",
            "BAJFINANCE": "BAJFINANCE.NS",
            "ITC": "ITC.NS",
            "LICI": "LICI.NS",
            "KOTAKBANK": "KOTAKBANK.NS",
            "LT": "LT.NS",
            "HCLTECH": "HCLTECH.NS",
            "AXISBANK": "AXISBANK.NS",
            "ASIANPAINT": "ASIANPAINT.NS",
            "MARUTI": "MARUTI.NS",
            "TITAN": "TITAN.NS",
            "TATAMOTORS": "TATAMOTORS.NS",
            "NTPC": "NTPC.NS",
            "INDUSINDBK": "INDUSINDBK.NS",
            "POWERGRID": "POWERGRID.NS",
            "ULTRACEMCO": "ULTRACEMCO.NS",
            "TATACONSUM": "TATACONSUM.NS",
            "WIPRO": "WIPRO.NS",
            "TECHM": "TECHM.NS",
            "NESTLEIND": "NESTLEIND.NS",
            "ADANIENT": "ADANIENT.NS",
            "TATAPOWER": "TATAPOWER.NS",
            "COALINDIA": "COALINDIA.NS",
            "BPCL": "BPCL.NS",
            "ONGC": "ONGC.NS",
            "HINDALCO": "HINDALCO.NS",
            "VEDL": "VEDL.NS",
            "JSWSTEEL": "JSWSTEEL.NS",
            "TATASTEEL": "TATASTEEL.NS",
            "HINDUNILVR": "HINDUNILVR.NS",
            "DABUR": "DABUR.NS",
            "BRITANNIA": "BRITANNIA.NS",
            "GODREJCP": "GODREJCP.NS",
            "MARICO": "MARICO.NS",
        }
        
        if ticker in stock_mapping:
            return stock_mapping[ticker]
        else:
            # Default: try NSE
            return f"{ticker}.NS"
    
    def analyze_stock_from_news(self, ticker, news_count, news_articles):
        """Analyze a stock mentioned in news using pattern analysis."""
        print(f"\n📊 Analyzing {ticker}...")
        print(f"   📰 Mentioned in {news_count} articles")
        
        try:
            # Download stock data
            yahoo_symbol = self.get_yahoo_symbol(ticker)
            stock_data = self.analyzer.download_enhanced_stock_data(ticker, period="1y", exchange="NSE")
            
            if not stock_data or "daily" not in stock_data or stock_data["daily"].empty:
                print(f"   ⚠️ No data available for {ticker}")
                return None
            
            # Calculate indicators
            daily_data = self.analyzer.calculate_advanced_indicators(stock_data["daily"])
            
            if daily_data is None or daily_data.empty:
                print(f"   ⚠️ Error calculating indicators for {ticker}")
                return None
            
            # Get current price
            latest = daily_data.iloc[-1]
            current_price = latest["Close"]
            
            # Run pattern analysis
            pattern_analysis = None
            if self.analyzer.pattern_analysis_enabled and self.analyzer.pattern_analyzer:
                try:
                    pattern_analysis = self.analyzer.pattern_analyzer.analyze_patterns(
                        daily_data, ticker
                    )
                except Exception as e:
                    print(f"   ⚠️ Pattern analysis error: {e}")
                    pattern_analysis = None
            
            # Generate trading signals
            signals = self.analyzer.generate_enhanced_signals(stock_data, None)
            
            # Calculate recommendation score
            score = 0
            
            # News factor (0-30 points)
            if news_count >= 10:
                news_score = 30
            elif news_count >= 5:
                news_score = 20
            elif news_count >= 3:
                news_score = 15
            else:
                news_score = news_count * 3
            
            # Signal factor (0-40 points)
            signal = signals.get("signal", "HOLD")
            confidence = signals.get("confidence", 0)
            
            if signal == "BUY":
                signal_score = min(40, confidence * 0.4)
            elif signal == "SELL":
                signal_score = 0
            else:
                signal_score = min(20, confidence * 0.2)
            
            # Pattern factor (0-30 points)
            pattern_score = 0
            if pattern_analysis:
                pattern_signal = pattern_analysis.get("overall_signal", "HOLD")
                pattern_confidence = pattern_analysis.get("overall_confidence", 0)
                
                if pattern_signal == "BUY":
                    pattern_score = min(30, pattern_confidence * 0.3)
                elif pattern_signal == "SELL":
                    pattern_score = 0
                else:
                    pattern_score = min(15, pattern_confidence * 0.15)
            
            total_score = news_score + signal_score + pattern_score
            
            # Get technical indicators
            rsi = latest.get("RSI", None) if "RSI" in daily_data.columns else None
            macd = latest.get("MACD", None) if "MACD" in daily_data.columns else None
            
            recommendation = {
                "ticker": ticker,
                "yahoo_symbol": yahoo_symbol,
                "current_price": round(current_price, 2),
                "news_count": news_count,
                "news_articles": news_articles,
                "signal": signal,
                "signal_confidence": round(confidence, 1),
                "pattern_signal": pattern_analysis.get("overall_signal", "HOLD") if pattern_analysis else "N/A",
                "pattern_confidence": round(pattern_analysis.get("overall_confidence", 0), 1) if pattern_analysis else 0,
                "top_patterns": pattern_analysis.get("top_3_patterns", []) if pattern_analysis else [],
                "rsi": round(rsi, 2) if rsi else None,
                "macd": round(macd, 4) if macd else None,
                "total_score": round(total_score, 2),
                "news_score": round(news_score, 2),
                "signal_score": round(signal_score, 2),
                "pattern_score": round(pattern_score, 2),
                "recommendation": "BUY" if signal == "BUY" and total_score >= 50 else "HOLD",
                "reasons": signals.get("reasons", [])
            }
            
            print(f"   ✅ Analysis complete | Score: {total_score:.1f} | Signal: {signal} ({confidence:.1f}%)")
            
            return recommendation
            
        except Exception as e:
            print(f"   ❌ Error analyzing {ticker}: {e}")
            return None
    
    def recommend_stocks(self, max_stocks=20, top_recommendations=3):
        """Main function: Scrape news, analyze stocks, recommend top buys."""
        print("🚀 NEWS-BASED STOCK RECOMMENDATION SYSTEM")
        print("=" * 80)
        
        # Step 1: Scrape Moneycontrol news
        print("\n📰 Step 1: Scraping Moneycontrol Markets News...")
        print("-" * 80)
        
        news_data = scrape_markets_news()
        
        if not news_data or not news_data.get("tickers"):
            print("\n❌ Failed to scrape news or no stocks found in articles.")
            print("   Cannot provide recommendations without real data.")
            return None
        
        # Step 2: Get top mentioned stocks
        print(f"\n📊 Step 2: Found {len(news_data['tickers'])} unique stocks mentioned in news")
        print(f"   Analyzing top {max_stocks} most mentioned stocks...")
        
        top_tickers = news_data["tickers"][:max_stocks]
        ticker_counts = news_data["ticker_counts"]
        ticker_articles = news_data["ticker_articles"]
        
        # Step 3: Analyze each stock
        print(f"\n🔍 Step 3: Running Technical Analysis & Pattern Detection...")
        print("-" * 80)
        
        recommendations = []
        for ticker in top_tickers:
            news_count = ticker_counts.get(ticker, 0)
            news_articles = ticker_articles.get(ticker, [])
            
            rec = self.analyze_stock_from_news(ticker, news_count, news_articles)
            if rec:
                recommendations.append(rec)
        
        if not recommendations:
            print("\n❌ No valid stock analysis completed. Cannot provide recommendations.")
            return None
        
        # Step 4: Rank and recommend
        print(f"\n🎯 Step 4: Ranking Stocks & Generating Recommendations...")
        print("-" * 80)
        
        # Sort by total score (highest first)
        recommendations.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Filter to BUY recommendations only
        buy_recommendations = [r for r in recommendations if r["recommendation"] == "BUY"]
        
        if not buy_recommendations:
            buy_recommendations = [r for r in recommendations[:top_recommendations]]
        
        # Step 5: Generate report
        print("\n" + "=" * 80)
        print("📈 TOP STOCK RECOMMENDATIONS FROM NEWS ANALYSIS")
        print("=" * 80)
        
        print(f"\n🎯 TOP {top_recommendations} BUY RECOMMENDATIONS:")
        print("-" * 80)
        
        for i, rec in enumerate(buy_recommendations[:top_recommendations], 1):
            print(f"\n🏆 #{i}: {rec['ticker']}")
            print(f"   💰 Current Price: ₹{rec['current_price']:,.2f}")
            print(f"   📊 Total Score: {rec['total_score']:.1f}/100")
            print(f"      📰 News Score: {rec['news_score']:.1f}/30 (Mentioned in {rec['news_count']} articles)")
            print(f"      📈 Signal Score: {rec['signal_score']:.1f}/40 (Signal: {rec['signal']} @ {rec['signal_confidence']}%)")
            print(f"      🎨 Pattern Score: {rec['pattern_score']:.1f}/30 (Pattern: {rec['pattern_signal']} @ {rec['pattern_confidence']}%)")
            
            if rec.get('rsi'):
                print(f"   📊 RSI: {rec['rsi']:.2f}")
            if rec.get('macd'):
                print(f"   📊 MACD: {rec['macd']:.4f}")
            
            if rec['top_patterns']:
                print(f"   🎨 Top Patterns Detected:")
                for pattern in rec['top_patterns'][:2]:
                    pattern_name = pattern.get('pattern', 'Unknown')
                    confidence = pattern.get('confidence', 0)
                    signal = pattern.get('signal', 'HOLD')
                    emoji = "📈" if signal == "BUY" else "📉" if signal == "SELL" else "⚖️"
                    print(f"      {emoji} {pattern_name}: {confidence}% confidence ({signal})")
            
            if rec['reasons']:
                print(f"   📝 Key Reasons:")
                for reason in rec['reasons'][:3]:
                    print(f"      • {reason}")
            
            print(f"   📰 Latest News Articles:")
            for article in rec['news_articles'][:3]:
                title = article.get('title', 'No title')
                if len(title) > 70:
                    title = title[:70] + "..."
                print(f"      • {title}")
        
        print(f"\n📋 ALL ANALYZED STOCKS:")
        print("-" * 80)
        
        df = pd.DataFrame(recommendations)
        print(df[['ticker', 'current_price', 'news_count', 'signal', 'signal_confidence', 
                  'pattern_signal', 'pattern_confidence', 'total_score', 'recommendation']].to_string(index=False))
        
        # Save recommendations
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"stock_recommendations_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
        
        print(f"\n💾 Recommendations saved to: {csv_file}")
        print("\n" + "=" * 80)
        print("✅ Analysis Complete!")
        print("=" * 80)
        
        return {
            "top_recommendations": buy_recommendations[:top_recommendations],
            "all_recommendations": recommendations,
            "news_data": news_data,
            "csv_file": csv_file
        }


def main():
    """Main entry point."""
    recommender = NewsBasedStockRecommender()
    result = recommender.recommend_stocks(max_stocks=20, top_recommendations=3)
    return result


if __name__ == "__main__":
    main()

