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
        
        try:
            # Download stock data
            yahoo_symbol = self.get_yahoo_symbol(ticker)
            stock_data = self.analyzer.download_enhanced_stock_data(ticker, period="1y", exchange="NSE")
            
            if not stock_data or "daily" not in stock_data or stock_data["daily"].empty:
                return None
            
            daily_data = self.analyzer.calculate_advanced_indicators(stock_data["daily"])
            
            if daily_data is None or daily_data.empty:
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
                except Exception:
                    pattern_analysis = None
            
            # Fundamental screening
            info = stock_data.get("info", {})
            market_cap = info.get("marketCap", 0)
            avg_volume = daily_data["Volume"].mean() if not daily_data.empty else 0
            
            if market_cap > 0 and market_cap < 5e9:
                return None
            
            if avg_volume < 100000:
                return None
            
            signals = self.analyzer.generate_enhanced_signals(stock_data, None)
            
            if signals.get("signal") == "HOLD" and signals.get("confidence") == 0:
                return None
            
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
            
            # Calculate stop loss (7% below entry or below pattern support)
            atr = latest.get("ATR", None) if "ATR" in daily_data.columns else None
            stop_loss = round(current_price * 0.93, 2)  # Default 7% stop
            
            if pattern_analysis and pattern_analysis.get("top_3_patterns"):
                # Use pattern support if available
                for pattern in pattern_analysis["top_3_patterns"]:
                    if pattern.get("signal") == "BUY" and pattern.get("support_level"):
                        pattern_stop = pattern.get("support_level", stop_loss)
                        stop_loss = min(stop_loss, round(pattern_stop * 0.98, 2))
            
            # Simple news sentiment (keyword-based)
            # Note: For ML models later, use article.get("content") instead of just title
            positive_keywords = ["rise", "gain", "up", "bullish", "strong", "beat", "growth", "profit", "win", "positive"]
            negative_keywords = ["fall", "drop", "down", "bearish", "weak", "miss", "loss", "decline", "warn", "negative"]
            
            sentiment_score = 0
            for article in news_articles[:5]:  # Check top 5 articles
                title = article.get("title", "").upper()
                # TODO: When ML model added, analyze article.get("content") for deeper sentiment
                pos_count = sum(1 for kw in positive_keywords if kw.upper() in title)
                neg_count = sum(1 for kw in negative_keywords if kw.upper() in title)
                sentiment_score += (pos_count - neg_count)
            
            news_sentiment = "POSITIVE" if sentiment_score > 0 else "NEGATIVE" if sentiment_score < 0 else "NEUTRAL"
            
            # Adjust news score based on sentiment
            if news_sentiment == "NEGATIVE":
                news_score = max(0, news_score - 10)
            elif news_sentiment == "POSITIVE":
                news_score = min(30, news_score + 5)
            
            total_score = news_score + signal_score + pattern_score
            
            recommendation = {
                "ticker": ticker,
                "yahoo_symbol": yahoo_symbol,
                "current_price": round(current_price, 2),
                "stop_loss": stop_loss,
                "risk_reward": round((current_price - stop_loss) / stop_loss, 2) if stop_loss > 0 else None,
                "news_count": news_count,
                "news_sentiment": news_sentiment,
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
            
            return recommendation
            
        except Exception as e:
            return None
    
    def load_json_data(self, json_file):
        """Load news data from existing JSON file."""
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON structure to format expected by recommend_stocks
        articles = data.get("articles", [])
        ticker_summary = data.get("ticker_summary", {})
        ticker_articles = data.get("ticker_articles", {})
        
        # Sort tickers by count
        sorted_tickers = sorted(ticker_summary.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "articles": articles,
            "tickers": [t[0] for t in sorted_tickers],
            "ticker_counts": dict(sorted_tickers),
            "ticker_articles": ticker_articles,
            "files": {"json": json_file}
        }
    
    def recommend_stocks(self, max_stocks=20, top_recommendations=3, json_file=None):
        """Main function: Scrape news, analyze stocks, recommend top buys.
        
        Args:
            max_stocks: Maximum number of stocks to analyze
            top_recommendations: Number of top recommendations to return
            json_file: Optional path to existing JSON file (skips scraping if provided)
        """
        if json_file:
            print(f"📂 Loading news data from {json_file}...")
            news_data = self.load_json_data(json_file)
        else:
            print("🔍 Scraping news and analyzing stocks...")
            news_data = scrape_markets_news()
        
        if not news_data or not news_data.get("tickers"):
            return None
        
        top_tickers = news_data["tickers"][:max_stocks]
        ticker_counts = news_data["ticker_counts"]
        ticker_articles = news_data["ticker_articles"]
        
        recommendations = []
        for ticker in top_tickers:
            news_count = ticker_counts.get(ticker, 0)
            news_articles = ticker_articles.get(ticker, [])
            
            rec = self.analyze_stock_from_news(ticker, news_count, news_articles)
            if rec:
                recommendations.append(rec)
        
        if not recommendations:
            return None
        
        recommendations.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Filter: Only BUY recommendations with positive sentiment
        buy_recommendations = [
            r for r in recommendations 
            if r["recommendation"] == "BUY" and r.get("news_sentiment") != "NEGATIVE"
        ]
        
        if not buy_recommendations:
            buy_recommendations = [r for r in recommendations if r.get("news_sentiment") != "NEGATIVE"][:top_recommendations]
        
        print(f"\n🎯 TOP {top_recommendations} BUY RECOMMENDATIONS:")
        print("=" * 80)
        
        for i, rec in enumerate(buy_recommendations[:top_recommendations], 1):
            print(f"\n#{i} {rec['ticker']} | ₹{rec['current_price']:,.2f} | Stop: ₹{rec.get('stop_loss', 0):,.0f}")
            print(f"   Score: {rec['total_score']:.1f}/100 | News: {rec['news_count']} ({rec.get('news_sentiment', 'N/A')}) | Signal: {rec['signal']} ({rec['signal_confidence']:.0f}%)")
            if rec.get('rsi'):
                print(f"   RSI: {rec['rsi']:.1f}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"stock_recommendations_{timestamp}.csv"
        df = pd.DataFrame(recommendations)
        df.to_csv(csv_file, index=False)
        
        return {
            "top_recommendations": buy_recommendations[:top_recommendations],
            "all_recommendations": recommendations,
            "news_data": news_data,
            "csv_file": csv_file
        }


def main():
    """Main entry point."""
    recommender = NewsBasedStockRecommender()
    result = recommender.recommend_stocks(max_stocks=200, top_recommendations=3)
    return result


if __name__ == "__main__":
    main()

