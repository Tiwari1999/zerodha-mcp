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
    import sys
    import glob
    import os
    
    recommender = NewsBasedStockRecommender()
    
    # Check if JSON file provided as argument or find latest
    json_file = None
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # Find latest moneycontrol JSON file
        json_files = glob.glob("news_analysis/moneycontrol_markets_*.json")
        if json_files:
            json_file = max(json_files, key=lambda x: os.path.getmtime(x))
            print(f"📂 Using existing JSON file: {json_file}")
    
    result = recommender.recommend_stocks(
        max_stocks=20, 
        top_recommendations=3,
        json_file=json_file
    )
    return result

if __name__ == "__main__":
    main()

