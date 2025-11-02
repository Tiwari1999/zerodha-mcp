#!/usr/bin/env python3
"""
Scrape Moneycontrol 'Markets' sections:
- Markets, Stocks, IPO, Commodities, Currencies
- Extract article metadata + content from each article page
- Extract stock tickers from content
- Save JSON and CSV
"""

from __future__ import annotations

import re
import time
import json
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import pandas as pd

# Import stock mapper for comprehensive ticker extraction
try:
    from .stock_mapper import get_stock_mapper
    STOCK_MAPPER_AVAILABLE = True
except ImportError:
    STOCK_MAPPER_AVAILABLE = False
    print("[WARN] stock_mapper not available, using limited stock list")

BASE = "https://www.moneycontrol.com"

SECTIONS = [
    "/news/business/markets/",
    "/news/business/stocks/",
    "/news/business/ipo/",
    "/news/business/commodities/",
]

# Scrape window / limits
HOURS_BACK = 24
MAX_PAGES_PER_SECTION = 5  # Reduced for faster scraping
SLEEP_LISTING_SEC = 0.5  # Reduced delay
SLEEP_ARTICLE_SEC = 0.3  # Reduced delay
MAX_ARTICLES_PER_SECTION = 50  # Limit articles per section

# HTTP settings - Browser-like headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.moneycontrol.com/",
    "Sec-CH-UA": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1",
}

# Cookies from actual browser session
COOKIES = {
    "__utma": "1.928815072.1762027831.1762027831.1762027831.1",
    "__utmc": "1",
    "__utmz": "1.1762027831.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
    "PHPSESSID": "57lkgc1nq0k2a8ebg75qbui1e5",
    "token-normal": "q5dCVMPH3xoNPJ7oITXGn7h7DiFQljXN0Jbv2qtgvB7sgPXqBziv7kD0omTeS4JRdwugnS4boQ_qiT9JRWO-ww",
    "_medium": "web",
    "_mode": "otp",
    "__token__": "st=1762027989~exp=1762031589~acl=/*~data=Zse48HkZA2__1__1783362599~hmac=30140af27a021e07fb9f68425d23717ff26df95c56d321c550f138e7e80268d0",
    "mcpro": "1",
    "_ga": "GA1.1.928815072.1762027831",
}

# URL pattern for articles: /news/...-123456.html
ARTICLE_RE = re.compile(r"^https?://www\.moneycontrol\.com/news/.+-(\d+)\.html(?:\?.*)?$")

# Initialize stock mapper for comprehensive ticker extraction
if STOCK_MAPPER_AVAILABLE:
    _stock_mapper = get_stock_mapper()
    KNOWN_STOCKS = _stock_mapper.get_all_tickers()
else:
    # Fallback: Limited stock list if mapper not available
    KNOWN_STOCKS = {
        'TCS', 'INFY', 'RELIANCE', 'HDFCBANK', 'HDFC', 'ICICIBANK', 'BHARTIARTL',
        'SBIN', 'BAJFINANCE', 'ITC', 'LICI', 'KOTAKBANK', 'LT', 'HCLTECH',
        'AXISBANK', 'ASIANPAINT', 'MARUTI', 'TITAN', 'TATAMOTORS', 'NTPC',
        'INDUSINDBK', 'POWERGRID', 'ULTRACEMCO', 'TATACONSUM', 'WIPRO', 'TECHM',
        'NESTLEIND', 'ADANIENT', 'TATAPOWER', 'COALINDIA', 'BPCL', 'ONGC',
        'HINDALCO', 'VEDL', 'JSWSTEEL', 'TATASTEEL', 'HINDUNILVR', 'DABUR',
        'BRITANNIA', 'GODREJCP', 'MARICO', 'GAIL', 'IOC', 'IRCTC', 'IDEA',
        'SUZLON', 'BEL', 'HYUNDAI', 'BHEL', 'HPCL', 'MTAR', 'LENSKART',
        'SHADOWFAX', 'SWIGGY', 'GROWW', 'ORKLA', 'STUDDS', 'PINE', 'TENNECO',
        'SAFECURE', 'CURIS', 'PICCADIL', 'DLF', 'BANDHAN', 'UNION', 'POLYCAB',
        'ECLERX', 'NBCC', 'HUDCO', 'HINDPETRO', 'CANARA', 'BOSCH', 'CIPLA',
        'COGNIZANT', 'DRREDDY', 'CONCOR', 'SAGILITY', 'IXIGO', 'PBFINTECH',
        'NUVAMA', 'MOTILAL', 'OSWAL', 'HDFCAMC', 'DYNAMATIC', 'PORINJU',
        'ADITYA', 'BIRLA', 'BHEL', 'AMS', 'ADANI', 'BANDHAN', 'VODAFONE'
    }

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def get_soup(session: requests.Session, url: str) -> BeautifulSoup | None:
    """Get HTML content with appropriate headers."""
    try:
        # Remove Accept-Encoding to avoid compression issues
        html_headers = HEADERS.copy()
        html_headers.pop("Accept-Encoding", None)
        
        r = session.get(url, headers=html_headers, cookies=COOKIES, timeout=20, allow_redirects=True)
        r.raise_for_status()
        
        # Ensure proper encoding
        if r.encoding is None or r.encoding == 'ISO-8859-1':
            r.encoding = 'utf-8'
        
        if not r.text or len(r.text) < 100:
            print(f"[WARN] Response too short for {url}")
            return None
        
        # Check if we got HTML
        if "<html" not in r.text.lower() and "<body" not in r.text.lower():
            print(f"[WARN] Response doesn't appear to be HTML for {url}")
            return None
            
        return BeautifulSoup(r.text, "html.parser")
    except requests.exceptions.HTTPError as e:
        print(f"[WARN] HTTP Error {e.response.status_code} for {url}")
        return None
    except Exception as e:
        print(f"[WARN] GET failed {url}: {e}")
        return None

def parse_listing_links(soup: BeautifulSoup) -> list[str]:
    """Extract article links from Moneycontrol listing page."""
    links = set()
    
    # Find all anchor tags
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href:
            continue
        
        # Make absolute URL
        if not href.startswith("http"):
            href = urljoin(BASE, href)
        
        # Must be a Moneycontrol news article URL
        if not href.startswith("https://www.moneycontrol.com/news/"):
            continue
        
        # Skip navigation/category links (don't have .html or article IDs)
        if href.endswith("/") or "/news/" in href and href.count("/") <= 4:
            continue
        
        # Must match article pattern (ends with number.html)
        if ARTICLE_RE.match(href):
            # Check if it's from markets/stocks/ipo/commodities sections
            if any(seg in href for seg in (
                "/news/business/markets/",
                "/news/business/stocks/",
                "/news/business/ipo/",
                "/news/business/commodities/",
            )):
                links.add(href)
        # Also check for .html links with numbers (article IDs)
        elif ".html" in href and any(char.isdigit() for char in href):
            # Check if it's from our target sections
            if any(seg in href for seg in (
                "/news/business/markets/",
                "/news/business/stocks/",
                "/news/business/ipo/",
                "/news/business/commodities/",
            )):
                links.add(href)
    
    return list(links)

def extract_stock_tickers(content: str, title: str = "") -> list[str]:
    """Extract stock tickers from content using comprehensive stock mapper."""
    if STOCK_MAPPER_AVAILABLE:
        # Use comprehensive stock mapper with fuzzy matching
        return _stock_mapper.extract_tickers_from_text(content, title)
    else:
        # Fallback to simple pattern matching
        tickers = set()
        full_text = f"{title} {content}".upper()
        
        # Pattern 1: Known stocks only (most reliable)
        for stock in KNOWN_STOCKS:
            if stock in full_text:
                tickers.add(stock)
        
        # Pattern 2: Stock mentions with context (e.g., "TCS shares", "Reliance IPO")
        stock_context = re.findall(r'\b([A-Z]{3,10})\s+(?:shares|share|stock|stocks|IPO|Ltd|Limited|Corp|Corporation)\b', full_text)
        for stock in stock_context:
            if stock in KNOWN_STOCKS or (len(stock) >= 3 and stock.isalpha()):
                tickers.add(stock)
        
        return sorted(list(tickers))

def parse_article(session: requests.Session, url: str) -> dict:
    """Parse individual article page."""
    soup = get_soup(session, url)
    if not soup:
        return {"url": url, "error": "fetch_failed"}

    # Title
    title = None
    if soup.title:
        title = soup.title.get_text(strip=True)
    mt = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "title"})
    if mt and mt.get("content"):
        title = mt["content"].strip()

    # Published time
    published_dt = None
    cand = (
        soup.find("meta", {"property": "article:published_time"})
        or soup.find("meta", {"name": "pubdate"})
        or soup.find("meta", {"name": "publish-date"})
    )
    if cand and cand.get("content"):
        try:
            published_dt = date_parser.parse(cand["content"])
            if not published_dt.tzinfo:
                published_dt = published_dt.replace(tzinfo=timezone.utc)
        except Exception:
            published_dt = None

    published_iso = published_dt.astimezone(timezone.utc).isoformat() if published_dt else None

    # Section
    section = None
    sec_meta = soup.find("meta", {"property": "article:section"})
    if sec_meta and sec_meta.get("content"):
        section = sec_meta["content"].strip()

    # Author
    author = None
    ma = soup.find("meta", {"name": "author"}) or soup.find("meta", {"property": "article:author"})
    if ma and ma.get("content"):
        author = ma["content"].strip()

    # Content
    content = None
    selectors = [
        "div[itemprop=articleBody]",
        "div.article-content",
        "div.articleDetail",
        "div#content-body",
        "article",
        "main",
    ]
    for sel in selectors:
        node = soup.select_one(sel)
        if node and node.get_text(strip=True):
            content = node.get_text("\n", strip=True)
            break

    # Extract tickers
    tickers = extract_stock_tickers(content or "", title or "")
    
    # Article ID
    m = ARTICLE_RE.match(url)
    article_id = m.group(1) if m else None
    
    return {
        "id": article_id,
        "url": url,
        "title": title,
        "published_at": published_iso,
        "section": section,
        "author": author,
        "tickers": tickers,
        "ticker_count": len(tickers),
        "content": (content[:20000] if content else None),
    }

def page_url(section_url: str, page: int) -> str:
    """Get paginated URL."""
    if page <= 1:
        return urljoin(BASE, section_url)
    join = urljoin(BASE, section_url)
    if not join.endswith("/"):
        join += "/"
    return f"{join}?page={page}"

def scrape_markets_news():
    """Scrape Moneycontrol markets news and extract stock tickers."""
    session = requests.Session()
    session.cookies.update(COOKIES)

    all_items = []
    seen_ids = set()
    cutoff = now_utc() - timedelta(hours=HOURS_BACK)
    total_articles_scraped = 0

    for section in SECTIONS:
        section_articles = 0
        
        for p in range(1, MAX_PAGES_PER_SECTION + 1):
            url = page_url(section, p)
            soup = get_soup(session, url)
            if not soup:
                break

            links = parse_listing_links(soup)
            if not links:
                break

            stop_due_to_time = False
            for link in sorted(set(links)):
                # Limit articles per section
                if section_articles >= MAX_ARTICLES_PER_SECTION:
                    print(f"    Reached max articles ({MAX_ARTICLES_PER_SECTION}) for this section")
                    break
                    
                key = link.split("/")[-1].replace(".html", "") if ".html" in link else link
                if key in seen_ids:
                    continue
                seen_ids.add(key)
                
                time.sleep(SLEEP_ARTICLE_SEC)
                art = parse_article(session, link)
                
                # Only add if article was successfully parsed
                if art and not art.get("error"):
                    # Time filter
                    published_iso = art.get("published_at")
                    if published_iso:
                        try:
                            dt = date_parser.parse(published_iso)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            if dt < cutoff:
                                stop_due_to_time = True
                        except Exception:
                            pass

                    all_items.append(art)
                    section_articles += 1
                    total_articles_scraped += 1

            time.sleep(SLEEP_LISTING_SEC)

            if stop_due_to_time or section_articles >= MAX_ARTICLES_PER_SECTION:
                break

    # Aggregate tickers
    ticker_count = {}
    ticker_articles = {}
    
    for item in all_items:
        for ticker in item.get("tickers", []):
            ticker_count[ticker] = ticker_count.get(ticker, 0) + 1
            if ticker not in ticker_articles:
                ticker_articles[ticker] = []
            ticker_articles[ticker].append({
                "title": item.get("title"),
                "url": item.get("url"),
                "published_at": item.get("published_at")
            })

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"moneycontrol_markets_{timestamp}.json"
    json_data = {
        "scrape_date": datetime.now().isoformat(),
        "scrape_status": "success" if all_items else "no_articles_found",
        "total_articles": len(all_items),
        "articles_with_tickers": sum(1 for item in all_items if item.get('tickers')),
        "unique_stocks": len(ticker_count),
        "articles": all_items,
        "ticker_summary": ticker_count,
        "ticker_articles": ticker_articles
    }
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    csv_file = None
    if all_items:
        df = pd.DataFrame(all_items)
        csv_file = f"moneycontrol_markets_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
    
    # Return tickers sorted by mention count
    sorted_tickers = sorted(ticker_count.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "articles": all_items,
        "tickers": [t[0] for t in sorted_tickers],
        "ticker_counts": dict(sorted_tickers),
        "ticker_articles": ticker_articles,
        "files": {"json": json_file, "csv": csv_file}
    }

if __name__ == "__main__":
    scrape_markets_news()
