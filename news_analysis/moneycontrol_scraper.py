#!/usr/bin/env python3
"""
Scrape Moneycontrol 'Markets' sections:
- Markets, Stocks, IPO, Commodities, Currencies
- Extract article metadata + content from each article page
- Extract stock tickers from content
- Save JSON and CSV
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

# Import stock mapper for comprehensive ticker extraction
try:
    from news_analysis import get_stock_mapper

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
HOURS_BACK = 48
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

# Lazy initialization of stock mapper
_stock_mapper = None

def _get_stock_mapper():
    """Lazy initialization of stock mapper."""
    global _stock_mapper
    if _stock_mapper is None and STOCK_MAPPER_AVAILABLE:
        try:
            _stock_mapper = get_stock_mapper()
        except Exception:
            pass
    return _stock_mapper


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def get_soup(session: requests.Session, url: str) -> BeautifulSoup | None:
    """Get HTML content with appropriate headers."""
    try:
        html_headers = {k: v for k, v in HEADERS.items() if k != "Accept-Encoding"}
        r = session.get(url, headers=html_headers, cookies=COOKIES, timeout=15, allow_redirects=True)
        r.raise_for_status()
        
        if r.encoding in (None, 'ISO-8859-1'):
            r.encoding = 'utf-8'
        
        if not r.text or len(r.text) < 100 or "<html" not in r.text.lower() and "<body" not in r.text.lower():
            return None
        
        return BeautifulSoup(r.text, "html.parser")
    except Exception:
        return None


def parse_listing_links(soup: BeautifulSoup) -> list[str]:
    """Extract article links from Moneycontrol listing page."""
    target_sections = ("/news/business/markets/", "/news/business/stocks/", 
                      "/news/business/ipo/", "/news/business/commodities/")
    links = set()
    
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        if not href:
            continue
        
        if not href.startswith("http"):
            href = urljoin(BASE, href)
        
        if (not href.startswith("https://www.moneycontrol.com/news/") or
            href.endswith("/") or (href.count("/") <= 4) or
            not any(seg in href for seg in target_sections) or
            not (ARTICLE_RE.match(href) or (".html" in href and any(c.isdigit() for c in href)))):
            continue
        
        links.add(href)
    
    return list(links)


def extract_stock_tickers(content: str, title: str = "") -> list[str]:
    """Extract stock tickers from content using comprehensive stock mapper."""
    mapper = _get_stock_mapper()
    if mapper:
        return mapper.extract_tickers_from_text(content, title, max_tickers=5)
    return []


def parse_article(session: requests.Session, url: str) -> dict:
    """Parse individual article page."""
    soup = get_soup(session, url)
    if not soup:
        return {"url": url, "error": "fetch_failed"}

    # Title
    title = None
    if soup.title:
        title = soup.title.get_text(strip=True)
    if not title:
        meta = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "title"})
        title = meta.get("content", "").strip() if meta else None

    # Published time
    published_iso = None
    pub_meta = (soup.find("meta", {"property": "article:published_time"}) or
                soup.find("meta", {"name": "pubdate"}) or
                soup.find("meta", {"name": "publish-date"}))
    if pub_meta and pub_meta.get("content"):
        try:
            dt = date_parser.parse(pub_meta["content"])
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)
            published_iso = dt.astimezone(timezone.utc).isoformat()
        except Exception:
            pass

    # Section
    sec_meta = soup.find("meta", {"property": "article:section"})
    section = str(sec_meta.get("content", "")).strip() if sec_meta and sec_meta.get("content") else None

    # Author
    author_meta = soup.find("meta", {"name": "author"}) or soup.find("meta", {"property": "article:author"})
    author = str(author_meta.get("content", "")).strip() if author_meta and author_meta.get("content") else None

    # Content extraction - try multiple methods
    skip_words = ['cookie', 'privacy', 'follow us', 'trending', 'powered by', 
                  'see the top', 'invest now', 'my account', 'search quotes', 'mutual fund']
    
    def extract_paragraphs(container):
        """Extract valid paragraphs from container."""
        paras = container.find_all('p') if hasattr(container, 'find_all') else []
        valid = [str(p.get_text(strip=True)) for p in paras 
                if len(str(p.get_text(strip=True))) > 50 and
                not any(skip in str(p.get_text(strip=True)).lower() for skip in skip_words)]
        return '\n\n'.join(valid) if valid else None
    
    content = None
    # Method 1: disBdy div
    content_div = soup.find('div', class_=lambda x: x and 'disBdy' in ' '.join(x) if x else False)
    if content_div:
        content = str(content_div.get_text("\n", strip=True))
        if len(content) < 200:
            content = None
    
    # Method 2: section tag
    if not content or len(content) < 200:
        section_tag = soup.find('section')
        if section_tag:
            content = extract_paragraphs(section_tag)
    
    # Method 3: all paragraphs
    if not content or len(content) < 200:
        content = extract_paragraphs(soup)
    
    # Method 4: other selectors
    if not content or len(content) < 200:
        for sel in ["div[itemprop=articleBody]", "div.article-content", 
                   "div.articleDetail", "div#content-body", "article"]:
            node = soup.select_one(sel)
            if node:
                text = str(node.get_text("\n", strip=True))
                if len(text) > 200:
                    content = text
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
        "content": (content[:2000] if content else None),
    }


def page_url(section_url: str, page: int) -> str:
    """Get paginated URL."""
    url = urljoin(BASE, section_url)
    return url if page <= 1 else f"{url.rstrip('/')}/?page={page}"


def scrape_markets_news():
    """Scrape Moneycontrol markets news and extract stock tickers."""
    print(f"🚀 Starting scraper... (max {MAX_PAGES_PER_SECTION} pages/section, {MAX_ARTICLES_PER_SECTION} articles/section)")
    
    session = requests.Session()
    session.cookies.update(COOKIES)

    all_items = []
    seen_ids = set()
    cutoff = now_utc() - timedelta(hours=HOURS_BACK)
    total_articles_scraped = 0

    for section_idx, section in enumerate(SECTIONS, 1):
        print(f"\n📰 Section {section_idx}/{len(SECTIONS)}: {section}")
        section_articles = 0

        for p in range(1, MAX_PAGES_PER_SECTION + 1):
            url = page_url(section, p)
            print(f"  📄 Page {p}: {url}")
            soup = get_soup(session, url)
            if not soup:
                print(f"  ⚠️  Failed to fetch page {p}, stopping section")
                break

            links = parse_listing_links(soup)
            print(f"  ✅ Found {len(links)} article links")
            if not links:
                print(f"  ⚠️  No links found on page {p}, stopping section")
                break

            stop_due_to_time = False
            for link_idx, link in enumerate(sorted(set(links)), 1):
                # Limit articles per section
                if section_articles >= MAX_ARTICLES_PER_SECTION:
                    print(f"  ⏹️  Reached max articles ({MAX_ARTICLES_PER_SECTION}) for this section")
                    break

                key = link.split("/")[-1].replace(".html", "") if ".html" in link else link
                if key in seen_ids:
                    continue
                seen_ids.add(key)

                print(f"    [{link_idx}/{len(links)}] Scraping: {link[:80]}...")
                time.sleep(SLEEP_ARTICLE_SEC)
                art = parse_article(session, link)

                if not art or art.get("error"):
                    continue
                
                # Time filter
                if art.get("published_at"):
                    try:
                        dt = date_parser.parse(art["published_at"])
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        if dt < cutoff:
                            stop_due_to_time = True
                            break
                    except Exception:
                        pass
                
                all_items.append(art)
                section_articles += 1
                total_articles_scraped += 1
                if art.get("tickers"):
                    print(f"      ✅ Found {len(art['tickers'])} tickers: {', '.join(art['tickers'][:5])}")

            time.sleep(SLEEP_LISTING_SEC)

            if stop_due_to_time or section_articles >= MAX_ARTICLES_PER_SECTION:
                break
        
        print(f"  ✅ Section complete: {section_articles} articles scraped")

    print(f"\n✅ Scraping complete! Total articles: {total_articles_scraped}")
    
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
    json_file = f"news_analysis/moneycontrol_markets_{timestamp}.json"
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

    # Ensure directory exists
    Path(json_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved JSON: {json_file}")

    csv_file = None
    if all_items:
        csv_file = f"news_analysis/moneycontrol_markets_{timestamp}.csv"
        pd.DataFrame(all_items).to_csv(csv_file, index=False)
        print(f"💾 Saved CSV: {csv_file}")

    # Return tickers sorted by mention count
    sorted_tickers = sorted(ticker_count.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n📊 Summary:")
    print(f"   - Total articles: {len(all_items)}")
    print(f"   - Articles with tickers: {sum(1 for item in all_items if item.get('tickers'))}")
    print(f"   - Unique stocks found: {len(ticker_count)}")
    if sorted_tickers:
        print(f"   - Top 5 stocks: {', '.join([f'{t[0]}({t[1]})' for t in sorted_tickers[:5]])}")

    return {
        "articles": all_items,
        "tickers": [t[0] for t in sorted_tickers],
        "ticker_counts": dict(sorted_tickers),
        "ticker_articles": ticker_articles,
        "files": {"json": json_file, "csv": csv_file}
    }


if __name__ == "__main__":
    scrape_markets_news()
