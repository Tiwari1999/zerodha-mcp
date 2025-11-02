"""
News Analysis Module
Contains scraper, stock mapper, and news-based stock recommender
"""

from .moneycontrol_scraper import scrape_markets_news
from .news_based_stock_recommender import NewsBasedStockRecommender
from .stock_mapper import StockMapper, get_stock_mapper

__all__ = [
    'scrape_markets_news',
    'NewsBasedStockRecommender',
    'StockMapper',
    'get_stock_mapper',
]

