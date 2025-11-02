#!/usr/bin/env python3
"""
Main Entry Point for News-Based Stock Recommendation System
============================================================

This is the main script to run news-based stock recommendations.
It scrapes Moneycontrol news, extracts stocks, and provides buy/sell recommendations.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from news_analysis.news_based_stock_recommender import NewsBasedStockRecommender

def main():
    """Main entry point for news-based stock recommender."""
    print("🚀 Starting News-Based Stock Recommendation System")
    print("=" * 80)
    
    recommender = NewsBasedStockRecommender()
    result = recommender.recommend_stocks(max_stocks=20, top_recommendations=3)
    
    if result:
        print("\n✅ Analysis complete!")
        return result
    else:
        print("\n❌ Analysis failed or no stocks found.")
        return None

if __name__ == "__main__":
    main()

