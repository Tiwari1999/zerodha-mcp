#!/usr/bin/env python3
"""
Comprehensive Stock Mapper for Indian Markets (NSE/BSE)
Maps company names to stock ticker symbols using fuzzy matching
"""

import re
import json
import csv
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from difflib import SequenceMatcher
from collections import defaultdict

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class StockMapper:
    """Maps company names to stock ticker symbols for Indian markets."""
    
    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize stock mapper.
        
        Args:
            mapping_file: Path to JSON file with stock mappings (optional)
        """
        self.company_to_ticker: Dict[str, str] = {}
        self.ticker_to_companies: Dict[str, Set[str]] = defaultdict(set)
        self.ticker_aliases: Dict[str, str] = {}
        
        # Load mappings
        if mapping_file and Path(mapping_file).exists():
            self.load_from_file(mapping_file)
        else:
            self.load_default_mappings()
    
    def load_default_mappings(self):
        """Load comprehensive default mappings for Indian stocks."""
        # Comprehensive NSE/BSE stock mappings
        # Format: {ticker: [company_name_variations]}
        stock_mappings = {
            # Large Cap Stocks
            'RELIANCE': ['Reliance Industries', 'Reliance', 'RIL', 'Reliance Industries Limited'],
            'TCS': ['Tata Consultancy Services', 'TCS', 'Tata CS'],
            'HDFCBANK': ['HDFC Bank', 'HDFC Bank Limited', 'HDFC'],
            'INFY': ['Infosys', 'Infosys Limited', 'Infosys Technologies'],
            'ICICIBANK': ['ICICI Bank', 'ICICI Bank Limited', 'ICICI'],
            'HDFC': ['Housing Development Finance Corporation', 'HDFC Ltd'],
            'BHARTIARTL': ['Bharti Airtel', 'Airtel', 'Bharti', 'Airtel Limited'],
            'SBIN': ['State Bank of India', 'SBI', 'State Bank'],
            'BAJFINANCE': ['Bajaj Finance', 'Bajaj Finserv', 'Bajaj Finance Limited'],
            'ITC': ['ITC Limited', 'ITC', 'ITC Ltd'],
            'LICI': ['LIC', 'Life Insurance Corporation', 'LIC India', 'LIC of India'],
            'KOTAKBANK': ['Kotak Mahindra Bank', 'Kotak Bank', 'Kotak', 'Kotak Mahindra'],
            'LT': ['Larsen & Toubro', 'L&T', 'L and T', 'Larsen Toubro', 'Larsen and Toubro', 'L&T Limited', 'Larsen & Toubro Limited'],
            'INFY': ['Infosys', 'Infosys Limited', 'Infosys Technologies', 'Infosys Ltd'],
            'HCLTECH': ['HCL Technologies', 'HCL', 'HCL Tech', 'HCL Technologies Limited'],
            'AXISBANK': ['Axis Bank', 'Axis Bank Limited'],
            'ASIANPAINT': ['Asian Paints', 'Asian Paint', 'Asian Paints Limited'],
            'MARUTI': ['Maruti Suzuki', 'Maruti', 'Maruti Suzuki India'],
            'TITAN': ['Titan Company', 'Titan', 'Titan Industries'],
            'TATAMOTORS': ['Tata Motors', 'Tata Motors Limited', 'TML'],
            'NTPC': ['NTPC Limited', 'NTPC', 'National Thermal Power Corporation'],
            'INDUSINDBK': ['IndusInd Bank', 'IndusInd Bank Limited', 'IndusInd'],
            'POWERGRID': ['Power Grid Corporation', 'PowerGrid', 'PGCIL', 'Power Grid Corp'],
            'ULTRACEMCO': ['UltraTech Cement', 'UltraTech', 'UltraTech Cement Limited'],
            'TATACONSUM': ['Tata Consumer Products', 'Tata Global Beverages', 'Tata Consumer'],
            'WIPRO': ['Wipro Limited', 'Wipro', 'Wipro Technologies'],
            'TECHM': ['Tech Mahindra', 'Tech Mahindra Limited', 'TechM'],
            'NESTLEIND': ['Nestle India', 'Nestle', 'Nestle India Limited'],
            'ADANIENT': ['Adani Enterprises', 'Adani Enterprise', 'Adani Enterprises Limited'],
            'TATAPOWER': ['Tata Power', 'Tata Power Company', 'Tata Power Limited'],
            'COALINDIA': ['Coal India', 'Coal India Limited', 'CIL'],
            'BPCL': ['Bharat Petroleum', 'BPCL', 'Bharat Petroleum Corporation'],
            'ONGC': ['Oil and Natural Gas Corporation', 'ONGC', 'Oil & Natural Gas Corp'],
            'HINDALCO': ['Hindalco Industries', 'Hindalco', 'Hindalco Industries Limited'],
            'VEDL': ['Vedanta Limited', 'Vedanta', 'Vedanta Resources'],
            'JSWSTEEL': ['JSW Steel', 'JSW Steel Limited', 'JSW'],
            'TATASTEEL': ['Tata Steel', 'Tata Steel Limited', 'Tata Steel Ltd'],
            'HINDUNILVR': ['Hindustan Unilever', 'HUL', 'Hindustan Unilever Limited'],
            'DABUR': ['Dabur India', 'Dabur', 'Dabur India Limited'],
            'BRITANNIA': ['Britannia Industries', 'Britannia', 'Britannia Industries Limited'],
            'GODREJCP': ['Godrej Consumer Products', 'Godrej CP', 'Godrej Consumer'],
            'MARICO': ['Marico Limited', 'Marico', 'Marico Ltd'],
            'GAIL': ['GAIL India', 'GAIL', 'Gas Authority of India', 'GAIL India Limited'],
            'IOC': ['Indian Oil Corporation', 'IOC', 'Indian Oil', 'IOCL'],
            'IRCTC': ['Indian Railway Catering and Tourism Corporation', 'IRCTC', 'Indian Railways'],
            'IDEA': ['Vodafone Idea', 'Idea Cellular', 'Idea', 'Vodafone Idea Limited'],
            'SUZLON': ['Suzlon Energy', 'Suzlon', 'Suzlon Energy Limited'],
            'BEL': ['Bharat Electronics', 'BEL', 'Bharat Electronics Limited'],
            'HYUNDAI': ['Hyundai Motor India', 'Hyundai', 'Hyundai Motor'],
            'BHEL': ['Bharat Heavy Electricals', 'BHEL', 'Bharat Heavy Electricals Limited'],
            'HPCL': ['Hindustan Petroleum', 'HPCL', 'Hindustan Petroleum Corporation'],
            'MTAR': ['MTAR Technologies', 'MTAR', 'MTAR Tech'],
            'DLF': ['DLF Limited', 'DLF', 'DLF Ltd'],
            'BANDHAN': ['Bandhan Bank', 'Bandhan Bank Limited', 'Bandhan'],
            'UNION': ['Union Bank of India', 'Union Bank', 'UBI'],
            'POLYCAB': ['Polycab India', 'Polycab', 'Polycab India Limited'],
            'ECLERX': ['eClerx Services', 'eClerx', 'eClerx Services Limited'],
            'NBCC': ['NBCC India', 'NBCC', 'National Buildings Construction Corporation'],
            'HUDCO': ['Housing and Urban Development Corporation', 'HUDCO', 'HUDCO Limited'],
            'HINDPETRO': ['Hindustan Petroleum', 'HPCL', 'Hindustan Petroleum Corporation'],
            'CANARA': ['Canara Bank', 'Canara Bank Limited', 'Canara'],
            'BOSCH': ['Bosch Limited', 'Bosch', 'Robert Bosch'],
            'CIPLA': ['Cipla Limited', 'Cipla', 'Cipla Ltd'],
            'COGNIZANT': ['Cognizant Technology Solutions', 'Cognizant', 'CTS'],
            'DRREDDY': ['Dr. Reddy\'s Laboratories', 'Dr Reddy\'s', 'Dr Reddy', 'DR Reddy'],
            'CONCOR': ['Container Corporation of India', 'CONCOR', 'Container Corp'],
            'SAGILITY': ['Sagility', 'Sagility Limited', 'Sagility India'],
            'IXIGO': ['ixigo', 'Ixigo', 'Ixigo Limited'],
            'PBFINTECH': ['PB Fintech', 'Policybazaar', 'PB Fintech Limited'],
            'NUVAMA': ['Nuvama Wealth', 'Nuvama', 'Nuvama Wealth Management'],
            'MOTILAL': ['Motilal Oswal', 'Motilal Oswal Financial Services', 'MOFSL'],
            'OSWAL': ['Motilal Oswal', 'Motilal Oswal Financial Services'],
            'HDFCAMC': ['HDFC Asset Management Company', 'HDFC AMC', 'HDFC Mutual Fund'],
            'ADANI': ['Adani Group', 'Adani Enterprises', 'Adani Ports', 'Adani Green'],
            'VODAFONE': ['Vodafone Idea', 'Vodafone', 'Vodafone Idea Limited'],
            'SWIGGY': ['Swiggy', 'Swiggy Limited', 'Bundl Technologies'],
            'LENSKART': ['Lenskart', 'Lenskart Solutions', 'Lenskart Limited'],
            'GROWW': ['Groww', 'Groww Fintech', 'Groww Investment Platform'],
            'SHADOWFAX': ['Shadowfax', 'Shadowfax Technologies', 'Shadowfax Logistics'],
            'TENNECO': ['Tenneco Clean Air India', 'Tenneco', 'Tenneco India'],
            'SAFECURE': ['Safecure Services', 'Safecure', 'Safecure Limited'],
            'CURIS': ['Curis Lifesciences', 'Curis', 'Curis Lifesciences Limited'],
            'PICCADIL': ['Piccadily Agro Industries', 'Piccadily', 'Piccadily Industries'],
            'ORKLA': ['Orkla India', 'Orkla', 'Orkla ASA India'],
            'STUDDS': ['Studds Accessories', 'Studds', 'Studds Accessories Limited'],
            'PINE': ['Pine Labs', 'Pine Labs Private', 'Pine Labs Limited'],
        }
        
        # Build mappings
        for ticker, names in stock_mappings.items():
            self.ticker_to_companies[ticker].add(ticker)
            for name in names:
                # Normalize company name
                normalized = self._normalize_company_name(name)
                self.company_to_ticker[normalized] = ticker
                self.ticker_to_companies[ticker].add(name)
                self.ticker_to_companies[ticker].add(normalized)
    
    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for matching."""
        name = name.upper().strip()
        # Normalize special characters and abbreviations
        name = name.replace('&', 'AND')
        name = name.replace('+', 'AND')
        name = name.replace('@', 'AT')
        # Remove common suffixes
        name = re.sub(r'\s+(LIMITED|LTD|LTD\.|INC|INC\.|CORP|CORPORATION|CORP\.)$', '', name)
        # Remove extra spaces
        name = re.sub(r'\s+', ' ', name)
        return name.strip()
    
    def find_ticker(self, text: str, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        """
        Find stock tickers mentioned in text using fuzzy matching.
        
        Args:
            text: Text to search for stock mentions
            threshold: Minimum similarity score (0-1)
        
        Returns:
            List of (ticker, matched_company_name, confidence_score) tuples
        """
        text_upper = text.upper()
        found_tickers = []
        seen_tickers = set()
        
        # Method 1: Direct ticker match
        for ticker in self.ticker_to_companies.keys():
            if ticker in text_upper:
                if ticker not in seen_tickers:
                    found_tickers.append((ticker, ticker, 1.0))
                    seen_tickers.add(ticker)
        
        # Method 2: Company name fuzzy matching (improved)
        # Extract words and phrases more carefully
        text_words = re.findall(r'\b[A-Z][A-Za-z0-9]{1,20}\b', text_upper)
        text_phrases = []
        for i in range(len(text_words)):
            # Single word (only if it's substantial)
            if len(text_words[i]) >= 3:
                text_phrases.append(text_words[i])
            # Two-word phrases
            if i < len(text_words) - 1:
                phrase = f"{text_words[i]} {text_words[i+1]}"
                text_phrases.append(phrase)
            # Three-word phrases
            if i < len(text_words) - 2:
                phrase = f"{text_words[i]} {text_words[i+1]} {text_words[i+2]}"
                text_phrases.append(phrase)
        
        # First pass: Direct matches (high confidence)
        for phrase in text_phrases:
            normalized = self._normalize_company_name(phrase)
            if normalized in self.company_to_ticker:
                ticker = self.company_to_ticker[normalized]
                if ticker not in seen_tickers:
                    # Check if it's a meaningful match (not just a substring)
                    if len(phrase) >= 3 and phrase in text_upper:
                        found_tickers.append((ticker, phrase, 1.0))
                        seen_tickers.add(ticker)
        
        # Second pass: Fuzzy matches (only if no direct match found)
        for phrase in text_phrases:
            if len(phrase) < 4:  # Skip very short phrases
                continue
            normalized = self._normalize_company_name(phrase)
            # Skip if already matched directly
            if normalized in self.company_to_ticker:
                continue
            
            # Fuzzy match with stricter requirements
            best_match = None
            best_score = 0.0
            for company_name, ticker in self.company_to_ticker.items():
                # Skip if ticker already found
                if ticker in seen_tickers:
                    continue
                
                # Use better similarity metric (require word boundary match for better accuracy)
                if phrase in company_name or company_name in phrase:
                    score = 0.95  # High score for substring match
                else:
                    score = SequenceMatcher(None, normalized, company_name).ratio()
                
                # Require higher threshold and better match quality
                if score > best_score and score >= max(threshold, 0.85):
                    # Additional check: ensure phrase length similarity
                    if abs(len(phrase) - len(company_name)) / max(len(phrase), len(company_name)) < 0.5:
                        best_score = score
                        best_match = (ticker, phrase, score)
            
            if best_match and best_match[0] not in seen_tickers:
                found_tickers.append(best_match)
                seen_tickers.add(best_match[0])
        
        # Method 3: Look for "X shares", "X stock", "X IPO" patterns
        patterns = [
            r'\b([A-Z][A-Z0-9]{2,15})\s+(?:SHARES?|STOCK|STOCKS|IPO|LIMITED|LTD)\b',
            r'\b([A-Z][A-Z0-9]{2,15})\s+(?:SHARES?|STOCK|STOCKS|IPO)\s+(?:OF|TO)\b',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text_upper)
            for match in matches:
                ticker = self._normalize_company_name(match)
                if ticker in self.company_to_ticker:
                    actual_ticker = self.company_to_ticker[ticker]
                    if actual_ticker not in seen_tickers:
                        found_tickers.append((actual_ticker, match, 0.9))
                        seen_tickers.add(actual_ticker)
        
        # Sort by confidence (descending)
        found_tickers.sort(key=lambda x: x[2], reverse=True)
        return found_tickers
    
    def extract_tickers_from_text(self, text: str, title: str = "") -> List[str]:
        """
        Extract stock tickers from text (simple interface).
        
        Args:
            text: Article content
            title: Article title (optional)
        
        Returns:
            List of unique ticker symbols found
        """
        full_text = f"{title} {text}"
        matches = self.find_ticker(full_text, threshold=0.75)  # Higher threshold to reduce false positives
        
        # Prioritize high-confidence matches and exact matches
        ticker_scores = {}
        for ticker, matched_text, score in matches:
            # Exact ticker match gets highest priority
            if matched_text.upper() == ticker:
                ticker_scores[ticker] = max(ticker_scores.get(ticker, 0), 1.0)
            # High confidence matches
            elif score >= 0.85:
                ticker_scores[ticker] = max(ticker_scores.get(ticker, 0), score)
            # Lower confidence matches only if not already found with higher confidence
            elif score >= 0.75 and ticker not in ticker_scores:
                ticker_scores[ticker] = score
        
        # Return tickers sorted by confidence
        return [ticker for ticker, _ in sorted(ticker_scores.items(), key=lambda x: x[1], reverse=True)]
    
    def save_to_file(self, filepath: str):
        """Save mappings to JSON file."""
        data = {
            'company_to_ticker': self.company_to_ticker,
            'ticker_to_companies': {k: list(v) for k, v in self.ticker_to_companies.items()}
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """Load mappings from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.company_to_ticker = data.get('company_to_ticker', {})
            ticker_to_companies = data.get('ticker_to_companies', {})
            self.ticker_to_companies = {k: set(v) for k, v in ticker_to_companies.items()}
    
    def get_company_name(self, ticker: str) -> Optional[str]:
        """Get primary company name for a ticker."""
        companies = self.ticker_to_companies.get(ticker)
        if companies:
            # Return the longest name (usually the full name)
            return max(companies, key=len)
        return None
    
    def get_all_tickers(self) -> Set[str]:
        """Get all known ticker symbols."""
        return set(self.ticker_to_companies.keys())


# Global instance for easy access
_stock_mapper = None

def get_stock_mapper() -> StockMapper:
    """Get global stock mapper instance."""
    global _stock_mapper
    if _stock_mapper is None:
        _stock_mapper = StockMapper()
    return _stock_mapper

if __name__ == "__main__":
    # Test the mapper
    mapper = StockMapper()
    
    test_texts = [
        "Reliance Industries shares rise 5%",
        "TCS announces new project",
        "L&T wins major contract",
        "Infosys reported strong Q2 results",
        "HDFC Bank announces dividend",
    ]
    
    print("Testing Stock Mapper:")
    print("=" * 80)
    for text in test_texts:
        tickers = mapper.extract_tickers_from_text(text)
        print(f"\nText: {text}")
        print(f"Found tickers: {tickers}")
    
    print(f"\n\nTotal tickers loaded: {len(mapper.get_all_tickers())}")
    print(f"Total company name mappings: {len(mapper.company_to_ticker)}")

