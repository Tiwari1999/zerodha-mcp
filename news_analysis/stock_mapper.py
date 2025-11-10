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


# Blacklist of common words that should never be matched as tickers
BLACKLIST = {
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT',
    'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO',
    'WAY', 'USE', 'MAN', 'MEN', 'HAD', 'THEY', 'THEM', 'THIS', 'THAT', 'THESE', 'THOSE', 'WAS', 'WERE',
    'WHAT', 'WHEN', 'WHERE', 'WHICH', 'WHILE', 'WITH', 'WITHIN', 'WITHOUT', 'WOULD', 'YOUR', 'YOURS',
    'CRORE', 'LAKH', 'LAKHS', 'CRORES', 'RUPEES', 'RS', 'INR', 'USD', 'EURO', 'EUROS',
    'SME', 'QIB', 'NII', 'IPO', 'NSE', 'BSE', 'SEBI', 'RBI', 'GST', 'PAN', 'AADHAAR',
    'IST', 'GMT', 'UTC', 'AM', 'PM', 'HR', 'HRS', 'MIN', 'MINS', 'SEC', 'SECS',
    'NOV', 'DEC', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT',
    'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN',
    'LTD', 'LIMITED', 'CORP', 'CORPORATION', 'INC', 'INCORPORATED',
    'SHARES', 'SHARE', 'STOCK', 'STOCKS', 'EQUITY', 'EQUITIES',
    'INVESTOR', 'INVESTORS', 'INVESTMENT', 'INVESTMENTS',
    'ACCOUNT', 'ACCOUNTS', 'DEMAT', 'BANK', 'BANKS',
    'THEIR', 'THERE', 'THEN', 'THAN',
}


class StockMapper:
    """Maps company names to stock ticker symbols for Indian markets."""

    def __init__(self, mapping_file: Optional[str] = None):
        """Initialize stock mapper."""
        self.company_to_ticker: Dict[str, str] = {}
        self.ticker_to_companies: Dict[str, Set[str]] = defaultdict(set)

        if mapping_file and Path(mapping_file).exists():
            self.load_from_file(mapping_file)
        else:
            self.load_default_mappings()

    def load_default_mappings(self):
        """Load mappings. Prefer NSE EQUITY_L.csv if available, else use minimal seed map."""
        repo_root = Path(__file__).resolve().parents[1]
        csv_path = next((p for p in [repo_root / "EQUITY_L.csv", Path.cwd() / "EQUITY_L.csv"] 
                        if p.exists()), None)
        
        if csv_path:
            try:
                self._load_from_equity_csv(csv_path)
                return
            except Exception:
                pass

        # Seed mappings (fallback if CSV not found)
        stock_mappings = {
            # Large Cap Stocks
            'RELIANCE': ['Reliance Industries', 'Reliance', 'RIL', 'Reliance Industries Limited'],
            'TCS': ['Tata Consultancy Services', 'TCS', 'Tata CS'],
            'HDFCBANK': ['HDFC Bank', 'HDFC Bank Limited', 'HDFC'],
            'ICICIBANK': ['ICICI Bank', 'ICICI Bank Limited', 'ICICI'],
            'HDFC': ['Housing Development Finance Corporation', 'HDFC Ltd'],
            'BHARTIARTL': ['Bharti Airtel', 'Airtel', 'Bharti', 'Airtel Limited'],
            'SBIN': ['State Bank of India', 'SBI', 'State Bank'],
            'BAJFINANCE': ['Bajaj Finance', 'Bajaj Finserv', 'Bajaj Finance Limited'],
            'ITC': ['ITC Limited', 'ITC', 'ITC Ltd'],
            'LICI': ['LIC', 'Life Insurance Corporation', 'LIC India', 'LIC of India'],
            'KOTAKBANK': ['Kotak Mahindra Bank', 'Kotak Bank', 'Kotak', 'Kotak Mahindra'],
            'LT': ['Larsen & Toubro', 'L&T', 'L and T', 'Larsen Toubro', 'Larsen and Toubro', 'L&T Limited',
                   'Larsen & Toubro Limited'],
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

        # Build mappings from seed
        for ticker, names in stock_mappings.items():
            self._add_mapping_entries(ticker, names)

    def _add_mapping_entries(self, ticker: str, names: List[str]):
        """Add a ticker and its company name variations into internal maps."""
        self.ticker_to_companies[ticker].add(ticker)
        self.company_to_ticker[ticker] = ticker
        for name in names:
            normalized = self._normalize_company_name(name)
            self.company_to_ticker[normalized] = ticker
            self.ticker_to_companies[ticker].add(name)
            self.ticker_to_companies[ticker].add(normalized)

    def _load_from_equity_csv(self, csv_path: Path):
        """Load tickers and names from NSE EQUITY_L.csv (SYMBOL, NAME OF COMPANY, SERIES).

        Only include series EQ (main trading) to avoid special series noise.
        """
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = (row.get("SYMBOL") or "").strip().upper()
                name = (row.get("NAME OF COMPANY") or "").strip()
                series = (row.get(" SERIES") or row.get("SERIES") or "").strip().upper()
                if not symbol or not name:
                    continue
                # Prefer EQ series; if SERIES column absent or empty, still include
                if series and series not in {"EQ", "BE", "BZ"}:
                    # Keep common series too (BE/BZ often appear in news); skip others
                    continue

                # Build variations
                variations = [name, re.sub(r"\b(LIMITED|LTD\.?|PVT\.?|PRIVATE|COMPANY|CO\.?|INDIA)\b", "", name,
                                           flags=re.I).strip(), symbol]
                # Keep ticker itself as a mention

                # Special case: replace & with AND and vice-versa
                if "&" in name or " AND " in name.upper():
                    variations.append(name.replace("&", "AND"))
                    variations.append(name.replace("AND", "&"))

                # Add entries
                self._add_mapping_entries(symbol, [v for v in variations if v])

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
        """Find stock tickers mentioned in text using strict matching with context."""
        text_upper = text.upper()
        found_tickers = []
        seen_tickers = set()

        # Method 1: Direct ticker match with context
        for ticker in self.ticker_to_companies.keys():
            if ticker in BLACKLIST or len(ticker) <= 2:
                continue
            
            # Pattern 1: Ticker with financial context (highest priority)
            if re.search(r'\b' + re.escape(ticker) + r'\s+(?:SHARES?|STOCK|STOCKS|IPO|LIMITED|LTD|CORP|CORPORATION)\b', text_upper):
                if ticker not in seen_tickers:
                    found_tickers.append((ticker, ticker, 1.0))
                    seen_tickers.add(ticker)
                    continue
            
            # Pattern 2: Ticker as standalone word
            if len(ticker) >= 3 and re.search(r'(?:^|[^A-Z0-9])' + re.escape(ticker) + r'(?:[^A-Z0-9]|$)', text_upper):
                if ticker not in seen_tickers:
                    found_tickers.append((ticker, ticker, 0.9))
                    seen_tickers.add(ticker)

        # Method 2: Company name matching with context
        patterns = [
            r'\b([A-Z][A-Za-z0-9\s&]{4,40}?)\s+(?:SHARES?|STOCK|STOCKS|IPO|LIMITED|LTD|CORP|CORPORATION|ANNOUNCES?|REPORTS?|RISES?|FALLS?|GAINS?|DROPS?)\b',
            r'\b(?:SHARES?|STOCK|STOCKS)\s+OF\s+([A-Z][A-Za-z0-9\s&]{4,40}?)\b',
        ]
        
        for pattern in patterns:
            for match in re.findall(pattern, text_upper):
                match = match.strip()
                if len(match) < 4 or any(w in BLACKLIST for w in match.split()):
                    continue
                normalized = self._normalize_company_name(match)
                if normalized in self.company_to_ticker:
                    ticker = self.company_to_ticker[normalized]
                    if ticker not in BLACKLIST and ticker not in seen_tickers:
                        found_tickers.append((ticker, match, 0.9))
                        seen_tickers.add(ticker)

        # Method 3: 2-3 word phrases
        text_words = re.findall(r'\b[A-Z][A-Za-z0-9]{2,15}\b', text_upper)
        for i in range(len(text_words) - 1):
            for word_count in [2, 3]:
                if i + word_count > len(text_words):
                    continue
                phrase = ' '.join(text_words[i:i+word_count])
                if any(w in BLACKLIST for w in text_words[i:i+word_count]) or len(phrase) < 5:
                    continue
                normalized = self._normalize_company_name(phrase)
                if normalized in self.company_to_ticker:
                    ticker = self.company_to_ticker[normalized]
                    if ticker not in BLACKLIST and ticker not in seen_tickers:
                        found_tickers.append((ticker, phrase, 0.85))
                        seen_tickers.add(ticker)

        # Filter and sort
        filtered = [(t, m, s) for t, m, s in found_tickers if t not in BLACKLIST]
        filtered.sort(key=lambda x: x[2], reverse=True)
        return filtered

    def extract_tickers_from_text(self, text: str, title: str = "", max_tickers: int = 5) -> List[str]:
        """Extract stock tickers from text (simple interface)."""
        matches = self.find_ticker(f"{title} {text}", threshold=0.85)
        
        ticker_scores = {}
        for ticker, matched_text, score in matches:
            priority = 1.0 if matched_text.upper() == ticker else score
            ticker_scores[ticker] = max(ticker_scores.get(ticker, 0), priority)
        
        return [t for t, _ in sorted(ticker_scores.items(), key=lambda x: x[1], reverse=True)][:max_tickers]

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
        return max(companies, key=len) if companies else None

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
