#!/usr/bin/env python3
"""
Smart Portfolio Analyzer
=========================

This is the main analysis engine that combines:
1. Portfolio data (provided manually or from external sources)
2. Historical stock data from Yahoo Finance
3. Advanced technical analysis with multiple indicators
4. Risk assessment and portfolio optimization
5. Actionable buy/sell recommendations

Features:
- Multi-timeframe technical analysis
- Risk-adjusted position sizing
- Sector diversification analysis
- Market condition assessment
- Automated report generation

Usage:
1. Get your portfolio data from Zerodha Kite (using MCP in chat)
2. Update the holdings_data in run_analysis.py
3. Run: python run_analysis.py

Author: AI Assistant
Created: 2025
"""

import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import ta
import yfinance as yf

from patterns.pattern_analyzer import PatternAnalyzer

warnings.filterwarnings("ignore")


class SmartPortfolioAnalyzer:
    """
    Advanced portfolio analyzer with technical analysis and pattern recognition.
    """

    def __init__(self, holdings_data=None):
        self.portfolio_data = {"holdings": holdings_data} if holdings_data else None
        self.analysis_results = []
        self.market_condition = "NEUTRAL"

        # Initialize pattern analyzer
        try:

            self.pattern_analyzer = PatternAnalyzer()
            self.pattern_analysis_enabled = True
            print("🎯 Pattern analysis enabled")
        except ImportError as e:
            print(f"⚠️ Pattern analysis disabled: {e}")
            self.pattern_analyzer = None
            self.pattern_analysis_enabled = False

        # Enhanced stock mapping with your portfolio stocks
        self.stock_mapping = {
            "ARKADE": "ARKADE.NS",
            "ATHERENERG": "ATHERENERG.NS",
            "AXISBANK": "AXISBANK.NS",
            "BANKBARODA": "BANKBARODA.NS",
            "BPCL": "BPCL.NS",
            "CDSL": "CDSL.NS",
            "COALINDIA": "COALINDIA.NS",
            "DALMIASUG": "DALMIASUG.BO",
            "DHANI": "DHANI.NS",
            "ETERNAL": "ETERNAL.BO",
            "GAIL": "GAIL.NS",
            "GODREJAGRO": "GODREJAGRO.NS",
            "GOLDBEES": "GOLDBEES.BO",
            "HCLTECH": "HCLTECH.NS",
            "HINDPETRO": "HINDPETRO.NS",
            "INFY": "INFY.NS",
            "IOC": "IOC.NS",
            "IRCTC": "IRCTC.NS",
            "JUNIORBEES": "JUNIORBEES.NS",
            "KALAMANDIR": "KALAMANDIR.NS",
            "LIQUIDCASE": "LIQUIDCASE.BO",
            "MARUTI": "MARUTI.NS",
            "NIFTYBEES": "NIFTYBEES.BO",
            "PAYTM": "PAYTM.NS",
            "PICCADIL": "PICCADIL.BO",
            "POLICYBZR": "POLICYBZR.NS",
            "POWERGRID": "POWERGRID.NS",
            "SAGILITY": "SAGILITY.NS",
            "SBIN": "SBIN.NS",
            "TATAPOWER": "TATAPOWER.NS",
            "TCS": "TCS.NS",
            "TECHM": "TECHM.NS",
            "TMPV": "TMPV.BO",
            "VEDL": "VEDL.NS",
            "WIPRO": "WIPRO.NS",
        }

        # Sector classification for your stocks
        self.sector_mapping = {
            "ARKADE": "Real Estate",
            "ATHERENERG": "Auto & EV",
            "AXISBANK": "Banking",
            "BANKBARODA": "Banking",
            "BPCL": "Oil & Gas",
            "CDSL": "Financial Services",
            "COALINDIA": "Mining",
            "DALMIASUG": "Sugar",
            "DHANI": "Financial Services",
            "ETERNAL": "Manufacturing",
            "GAIL": "Oil & Gas",
            "GODREJAGRO": "Agri",
            "GOLDBEES": "ETF",
            "HCLTECH": "IT Services",
            "HINDPETRO": "Oil & Gas",
            "INFY": "IT Services",
            "IOC": "Oil & Gas",
            "IRCTC": "Railways",
            "JUNIORBEES": "ETF",
            "KALAMANDIR": "Fashion",
            "LIQUIDCASE": "ETF",
            "MARUTI": "Auto",
            "NIFTYBEES": "ETF",
            "PAYTM": "Fintech",
            "PICCADIL": "FMCG",
            "POLICYBZR": "Fintech",
            "POWERGRID": "Power",
            "SAGILITY": "IT Services",
            "SBIN": "Banking",
            "TATAPOWER": "Power",
            "TCS": "IT Services",
            "TECHM": "IT Services",
            "TMPV": "FMCG",
            "VEDL": "Metals",
            "WIPRO": "IT Services",
        }

    def fetch_real_portfolio_data(self):
        """Fetch real portfolio data from Zerodha MCP."""
        print("🔄 Fetching portfolio data...")

        if self.portfolio_data and "holdings" in self.portfolio_data:
            print(f"📊 Analyzing {len(self.portfolio_data['holdings'])} holdings")
            return self.portfolio_data

        print("❌ No portfolio data available")
        return None

    def get_yahoo_symbol(self, zerodha_symbol, exchange="NSE"):
        """Convert Zerodha symbol to Yahoo Finance symbol."""
        clean_symbol = zerodha_symbol.replace("NSE:", "").replace("BSE:", "")

        # Check if we have a mapping
        if clean_symbol in self.stock_mapping:
            return self.stock_mapping[clean_symbol]

        # Default: NSE for .NS, BSE for .BO
        if exchange == "BSE":
            return f"{clean_symbol}.BO"
        else:
            return f"{clean_symbol}.NS"

    def download_enhanced_stock_data(self, symbol, period="1y", exchange="NSE"):
        """Download and enhance stock data with multiple timeframes."""
        try:
            yahoo_symbol = self.get_yahoo_symbol(symbol, exchange=exchange)
            stock = yf.Ticker(yahoo_symbol)

            # Get different timeframes
            data = {}
            data["1d"] = stock.history(period="5d", interval="1d")
            data["1w"] = stock.history(period="3mo", interval="1wk")
            data["1mo"] = stock.history(period="1y", interval="1mo")
            data["daily"] = stock.history(period=period)

            # Get stock info
            try:
                info = stock.info
                data["info"] = {
                    "sector": info.get("sector", "Unknown"),
                    "industry": info.get("industry", "Unknown"),
                    "marketCap": info.get("marketCap", 0),
                    "beta": info.get("beta", 1.0),
                    "pe_ratio": info.get("trailingPE", 0),
                    "pb_ratio": info.get("priceToBook", 0),
                    "div_yield": info.get("dividendYield", 0),
                }
            except:
                data["info"] = {}

            return data

        except Exception as e:
            print(f"Error downloading data for {symbol}: {e}")
            return None

    def calculate_advanced_indicators(self, df):
        """Calculate comprehensive technical indicators."""
        if df is None or df.empty:
            return None

        data = df.copy()

        try:
            # Trend Indicators
            data["SMA_20"] = ta.trend.sma_indicator(data["Close"], window=20)
            data["SMA_50"] = ta.trend.sma_indicator(data["Close"], window=50)
            data["SMA_200"] = ta.trend.sma_indicator(data["Close"], window=200)
            data["EMA_12"] = ta.trend.ema_indicator(data["Close"], window=12)
            data["EMA_26"] = ta.trend.ema_indicator(data["Close"], window=26)

            # MACD
            data["MACD"] = ta.trend.macd(data["Close"])
            data["MACD_signal"] = ta.trend.macd_signal(data["Close"])
            data["MACD_histogram"] = ta.trend.macd_diff(data["Close"])

            # Momentum Indicators
            data["RSI"] = ta.momentum.rsi(data["Close"], window=14)
            data["RSI_fast"] = ta.momentum.rsi(data["Close"], window=7)
            data["Stoch_K"] = ta.momentum.stoch(
                data["High"], data["Low"], data["Close"]
            )
            data["Stoch_D"] = ta.momentum.stoch_signal(
                data["High"], data["Low"], data["Close"]
            )
            data["Williams_R"] = ta.momentum.williams_r(
                data["High"], data["Low"], data["Close"]
            )

            # Volatility Indicators
            data["BB_upper"] = ta.volatility.bollinger_hband(data["Close"])
            data["BB_middle"] = ta.volatility.bollinger_mavg(data["Close"])
            data["BB_lower"] = ta.volatility.bollinger_lband(data["Close"])
            data["BB_width"] = data["BB_upper"] - data["BB_lower"]
            data["ATR"] = ta.volatility.average_true_range(
                data["High"], data["Low"], data["Close"]
            )
            data["Keltner_upper"] = ta.volatility.keltner_channel_hband(
                data["High"], data["Low"], data["Close"]
            )
            data["Keltner_lower"] = ta.volatility.keltner_channel_lband(
                data["High"], data["Low"], data["Close"]
            )

            # Volume Indicators - Fixed calculation
            data["Volume_SMA"] = data["Volume"].rolling(window=20).mean()
            data["Volume_weighted_price"] = ta.volume.volume_weighted_average_price(
                data["High"], data["Low"], data["Close"], data["Volume"]
            )
            data["OBV"] = ta.volume.on_balance_volume(data["Close"], data["Volume"])

            # Additional indicators
            data["CCI"] = ta.trend.cci(
                data["High"], data["Low"], data["Close"], window=20
            )
            data["ADX"] = ta.trend.adx(
                data["High"], data["Low"], data["Close"], window=14
            )

            return data

        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return data

    def assess_market_condition(self, nifty_data=None):
        """Assess overall market condition using Nifty data."""
        try:
            if nifty_data is None:
                nifty = yf.Ticker("^NSEI")
                nifty_data = nifty.history(period="3mo")

            if nifty_data.empty:
                return "NEUTRAL"

            # Calculate market indicators
            nifty_with_indicators = self.calculate_advanced_indicators(nifty_data)
            latest = nifty_with_indicators.iloc[-1]

            bullish_signals = 0
            bearish_signals = 0

            # RSI check
            if latest["RSI"] > 60:
                bullish_signals += 1
            elif latest["RSI"] < 40:
                bearish_signals += 1

            # Moving average trend
            if latest["Close"] > latest["SMA_20"] > latest["SMA_50"]:
                bullish_signals += 2
            elif latest["Close"] < latest["SMA_20"] < latest["SMA_50"]:
                bearish_signals += 2

            # MACD
            if latest["MACD"] > latest["MACD_signal"]:
                bullish_signals += 1
            else:
                bearish_signals += 1

            # Determine market condition
            if bullish_signals > bearish_signals + 1:
                self.market_condition = "BULLISH"
            elif bearish_signals > bullish_signals + 1:
                self.market_condition = "BEARISH"
            else:
                self.market_condition = "NEUTRAL"

            print(f"📊 Market Condition: {self.market_condition}")
            return self.market_condition

        except Exception as e:
            print(f"Error assessing market condition: {e}")
            self.market_condition = "NEUTRAL"
            return "NEUTRAL"

    def generate_enhanced_signals(self, stock_data, holding_info=None):
        """Generate enhanced trading signals with multiple confirmations including pattern analysis."""
        if not stock_data or "daily" not in stock_data or stock_data["daily"].empty:
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reasons": ["No data available"],
                "patterns": [],
            }

        daily_data = stock_data["daily"]
        latest = daily_data.iloc[-1]
        signals = []
        buy_score = 0
        sell_score = 0

        # Pattern Analysis (NEW)
        pattern_analysis = None
        if self.pattern_analysis_enabled and self.pattern_analyzer:
            try:
                symbol = (
                    holding_info.get("tradingsymbol", "UNKNOWN")
                    if holding_info
                    else "UNKNOWN"
                )
                pattern_analysis = self.pattern_analyzer.analyze_patterns(
                    daily_data, symbol
                )

                # Integrate pattern signals
                if pattern_analysis["overall_signal"] == "BUY":
                    buy_score += (
                            pattern_analysis["overall_confidence"] / 20
                    )  # Scale to 0-5
                    signals.append(
                        f"Pattern Analysis: {pattern_analysis['pattern_summary']}"
                    )
                elif pattern_analysis["overall_signal"] == "SELL":
                    sell_score += pattern_analysis["overall_confidence"] / 20
                    signals.append(
                        f"Pattern Analysis: {pattern_analysis['pattern_summary']}"
                    )

                # Add top pattern if significant
                if pattern_analysis["top_3_patterns"]:
                    top_pattern = pattern_analysis["top_3_patterns"][0]
                    if top_pattern["confidence"] > 60:
                        signals.append(
                            f"Key Pattern: {top_pattern['pattern']} ({top_pattern['confidence']:.0f}% confidence)"
                        )

            except Exception as e:
                print(f"Error in pattern analysis: {e}")
                pattern_analysis = {
                    "patterns_detected": 0,
                    "top_3_patterns": [],
                    "pattern_summary": "Pattern analysis failed",
                }

        # Multi-timeframe analysis
        timeframe_scores = {"buy": 0, "sell": 0}

        for timeframe, data in stock_data.items():
            if timeframe == "info" or data.empty:
                continue

            tf_latest = data.iloc[-1]

            # RSI analysis for this timeframe
            if "RSI" in data.columns and not pd.isna(tf_latest["RSI"]):
                if tf_latest["RSI"] < 30:
                    timeframe_scores["buy"] += 1
                elif tf_latest["RSI"] > 70:
                    timeframe_scores["sell"] += 1

        # Primary signal generation from daily data

        # 1. RSI Analysis
        if "RSI" in daily_data.columns and not pd.isna(latest["RSI"]):
            rsi = latest["RSI"]
            if rsi < 25:
                signals.append(f"RSI extremely oversold ({rsi:.1f}) - Strong BUY")
                buy_score += 3
            elif rsi < 35:
                signals.append(f"RSI oversold ({rsi:.1f}) - BUY signal")
                buy_score += 2
            elif rsi > 75:
                signals.append(f"RSI extremely overbought ({rsi:.1f}) - Strong SELL")
                sell_score += 3
            elif rsi > 65:
                signals.append(f"RSI overbought ({rsi:.1f}) - SELL signal")
                sell_score += 2

        # 2. MACD Analysis
        if all(
                col in daily_data.columns
                for col in ["MACD", "MACD_signal", "MACD_histogram"]
        ):
            macd_hist = latest["MACD_histogram"]
            if not pd.isna(macd_hist):
                # Look for crossover in recent data
                if len(daily_data) > 5:
                    recent_hist = daily_data["MACD_histogram"].tail(5)
                    if recent_hist.iloc[-1] > 0 and recent_hist.iloc[-2] <= 0:
                        signals.append("MACD bullish crossover - BUY signal")
                        buy_score += 2
                    elif recent_hist.iloc[-1] < 0 and recent_hist.iloc[-2] >= 0:
                        signals.append("MACD bearish crossover - SELL signal")
                        sell_score += 2

        # 3. Moving Average Analysis
        if all(col in daily_data.columns for col in ["SMA_20", "SMA_50", "SMA_200"]):
            price = latest["Close"]
            sma20 = latest["SMA_20"]
            sma50 = latest["SMA_50"]
            sma200 = latest["SMA_200"]

            if not any(pd.isna([price, sma20, sma50, sma200])):
                if price > sma20 > sma50 > sma200:
                    signals.append("Strong uptrend - All MAs aligned - BUY")
                    buy_score += 2
                elif price < sma20 < sma50 < sma200:
                    signals.append("Strong downtrend - All MAs aligned - SELL")
                    sell_score += 2
                elif price > sma20 and sma20 > sma50:
                    signals.append("Short-term uptrend - BUY signal")
                    buy_score += 1
                elif price < sma20 and sma20 < sma50:
                    signals.append("Short-term downtrend - SELL signal")
                    sell_score += 1

        # 4. Bollinger Bands Analysis
        if all(
                col in daily_data.columns for col in ["BB_upper", "BB_lower", "BB_middle"]
        ):
            price = latest["Close"]
            bb_upper = latest["BB_upper"]
            bb_lower = latest["BB_lower"]
            bb_middle = latest["BB_middle"]

            if not any(pd.isna([price, bb_upper, bb_lower, bb_middle])):
                bb_position = (price - bb_lower) / (bb_upper - bb_lower)

                if bb_position <= 0.05:  # Near lower band
                    signals.append("Price near lower Bollinger Band - BUY signal")
                    buy_score += 1
                elif bb_position >= 0.95:  # Near upper band
                    signals.append("Price near upper Bollinger Band - SELL signal")
                    sell_score += 1

        # 5. Volume Analysis
        if "Volume_SMA" in daily_data.columns and not pd.isna(latest["Volume_SMA"]):
            if latest["Volume"] > latest["Volume_SMA"] * 1.5:
                signals.append("High volume confirms trend strength")
                # Add to existing trend
                if buy_score > sell_score:
                    buy_score += 1
                elif sell_score > buy_score:
                    sell_score += 1

        # 6. ADX Trend Strength
        if "ADX" in daily_data.columns and not pd.isna(latest["ADX"]):
            adx = latest["ADX"]
            if adx > 25:
                signals.append(f"Strong trend confirmed (ADX: {adx:.1f})")
            elif adx < 20:
                signals.append(f"Weak trend - Consolidation (ADX: {adx:.1f})")

        # 7. Portfolio-specific analysis
        if holding_info:
            pnl_percent = holding_info.get("pnl_percent", 0)

            # Stop-loss logic
            if pnl_percent < -20:
                signals.append(f"Major loss {pnl_percent:.1f}% - Consider stop-loss")
                sell_score += 2
            elif pnl_percent < -10:
                signals.append(f"Loss {pnl_percent:.1f}% - Monitor closely")
                sell_score += 1

            # Profit booking logic
            if pnl_percent > 30:
                signals.append(
                    f"Strong profit {pnl_percent:.1f}% - Consider partial booking"
                )
                sell_score += 1
            elif pnl_percent > 50:
                signals.append(f"Exceptional profit {pnl_percent:.1f}% - Book profits")
                sell_score += 2

        # 8. Market condition influence
        if self.market_condition == "BEARISH":
            sell_score += 1
            signals.append("Overall market bearish - Caution advised")
        elif self.market_condition == "BULLISH":
            buy_score += 1
            signals.append("Overall market bullish - Favorable conditions")

        # 9. Add multitimeframe confirmation
        if timeframe_scores["buy"] > timeframe_scores["sell"]:
            buy_score += 1
            signals.append("Multi-timeframe analysis supports BUY")
        elif timeframe_scores["sell"] > timeframe_scores["buy"]:
            sell_score += 1
            signals.append("Multi-timeframe analysis supports SELL")

        # Final signal determination
        total_score = buy_score + sell_score
        if total_score == 0:
            final_signal = "HOLD"
            confidence = 0
        else:
            signal_strength = abs(buy_score - sell_score)
            base_confidence = min(90, (signal_strength / max(total_score, 1)) * 100)

            if buy_score > sell_score:
                final_signal = "BUY"
                confidence = base_confidence + min(10, signal_strength * 5)
            elif sell_score > buy_score:
                final_signal = "SELL"
                confidence = base_confidence + min(10, signal_strength * 5)
            else:
                final_signal = "HOLD"
                confidence = 30

        # Add risk metrics
        risk_metrics = {}
        if "ATR" in daily_data.columns and not pd.isna(latest["ATR"]):
            risk_metrics["volatility"] = (
                "High" if latest["ATR"] > daily_data["ATR"].mean() * 1.5 else "Normal"
            )

        if "info" in stock_data and stock_data["info"]:
            risk_metrics["beta"] = stock_data["info"].get("beta", 1.0)

        return {
            "signal": final_signal,
            "confidence": min(95, max(0, round(confidence, 1))),
            "reasons": signals,
            "buy_score": buy_score,
            "sell_score": sell_score,
            "risk_metrics": risk_metrics,
            "rsi": latest.get("RSI", "N/A"),
            "macd_histogram": latest.get("MACD_histogram", "N/A"),
            "price_vs_sma20": (
                "Above"
                if latest.get("SMA_20", 0) and latest["Close"] > latest["SMA_20"]
                else "Below"
            ),
            "adx": latest.get("ADX", "N/A"),
            "volume_ratio": (
                latest["Volume"] / latest.get("Volume_SMA", 1)
                if not pd.isna(latest.get("Volume_SMA", np.nan))
                else "N/A"
            ),
            "patterns": (
                pattern_analysis
                if pattern_analysis
                else {"patterns_detected": 0, "top_3_patterns": []}
            ),
        }

    def analyze_portfolio_composition(self):
        """Analyze portfolio composition and diversification."""
        if not self.portfolio_data or not self.portfolio_data["holdings"]:
            return {}

        holdings = self.portfolio_data["holdings"]

        # Sector analysis
        sector_allocation = {}
        total_value = sum(
            h.get("last_price", h.get("current_price", 0)) * h.get("quantity", 0) for h in holdings
        )

        for holding in holdings:
            symbol = holding.get("tradingsymbol", "")
            sector = self.sector_mapping.get(symbol, "Other")
            current_price = holding.get("last_price", holding.get("current_price", 0))
            value = current_price * holding.get("quantity", 0)

            if sector not in sector_allocation:
                sector_allocation[sector] = {"value": 0, "percentage": 0, "stocks": []}

            sector_allocation[sector]["value"] += value
            sector_allocation[sector]["stocks"].append(symbol)

        # Calculate percentages
        for sector in sector_allocation:
            sector_allocation[sector]["percentage"] = (
                sector_allocation[sector]["value"] / total_value * 100
                if total_value > 0
                else 0
            )

        # Risk assessment
        risk_assessment = {
            "concentration_risk": (
                "High"
                if any(s["percentage"] > 40 for s in sector_allocation.values())
                else "Low"
            ),
            "diversification_score": len(sector_allocation),
            "largest_sector": (
                max(sector_allocation.items(), key=lambda x: x[1]["percentage"])
                if sector_allocation
                else None
            ),
        }

        return {
            "sector_allocation": sector_allocation,
            "risk_assessment": risk_assessment,
            "total_value": total_value,
            "stock_count": len(holdings),
        }

    def run_complete_analysis(self):
        """Run complete portfolio analysis with all features."""
        print("🚀 Starting Smart Portfolio Analysis...")
        print("=" * 60)

        # Step 1: Fetch real portfolio data
        portfolio_data = self.fetch_real_portfolio_data()
        if not portfolio_data:
            print("❌ Failed to fetch portfolio data.")
            return None

        # Step 2: Assess market condition
        self.assess_market_condition()

        # Step 3: Analyze portfolio composition
        composition_analysis = self.analyze_portfolio_composition()

        # Step 4: Analyze each holding
        analysis_results = []

        print(f"\n🔍 Analyzing {len(portfolio_data['holdings'])} holdings...")

        for holding in portfolio_data["holdings"]:
            symbol = holding["tradingsymbol"]
            exchange = holding.get("exchange", "NSE")
            print(f"\n📊 Analyzing {symbol}...")

            # Download enhanced data
            stock_data = self.download_enhanced_stock_data(symbol, period="1y", exchange=exchange)

            if stock_data and "daily" in stock_data and not stock_data["daily"].empty:
                # Calculate indicators
                stock_data["daily"] = self.calculate_advanced_indicators(
                    stock_data["daily"]
                )

                # Generate enhanced signals
                signals = self.generate_enhanced_signals(stock_data, holding)

                # Prepare comprehensive result
                result = {
                    "symbol": symbol,
                    "sector": self.sector_mapping.get(symbol, "Other"),
                    "quantity": holding["quantity"],
                    "avg_price": holding["average_price"],
                    "current_price": holding["last_price"],
                    "investment": holding["quantity"] * holding["average_price"],
                    "current_value": holding["quantity"] * holding["last_price"],
                    "pnl": holding["pnl"],
                    "pnl_percent": holding["pnl_percent"],
                    "signal": signals["signal"],
                    "confidence": signals["confidence"],
                    "reasons": signals["reasons"][:5],  # Top 5 reasons
                    "risk_metrics": signals["risk_metrics"],
                    "technical_data": {
                        "rsi": signals["rsi"],
                        "macd_histogram": signals["macd_histogram"],
                        "price_vs_sma20": signals["price_vs_sma20"],
                        "adx": signals["adx"],
                        "volume_ratio": signals["volume_ratio"],
                    },
                    "stock_info": stock_data.get("info", {}),
                    "patterns": signals.get(
                        "patterns", {"patterns_detected": 0, "top_3_patterns": []}
                    ),
                }

                analysis_results.append(result)

            else:
                # Fallback for data unavailable
                result = {
                    "symbol": symbol,
                    "sector": self.sector_mapping.get(symbol, "Other"),
                    "quantity": holding["quantity"],
                    "avg_price": holding["average_price"],
                    "current_price": holding["last_price"],
                    "investment": holding["quantity"] * holding["average_price"],
                    "current_value": holding["quantity"] * holding["last_price"],
                    "pnl": holding["pnl"],
                    "pnl_percent": holding["pnl_percent"],
                    "signal": "HOLD",
                    "confidence": 0,
                    "reasons": ["Technical data unavailable"],
                    "risk_metrics": {},
                    "technical_data": {},
                    "stock_info": {},
                    "patterns": {"patterns_detected": 0, "top_3_patterns": []},
                }
                analysis_results.append(result)

        self.analysis_results = analysis_results

        # Step 5: Generate comprehensive report
        self.generate_comprehensive_report(analysis_results, composition_analysis)

        return analysis_results

    def generate_comprehensive_report(self, analysis_results, composition_analysis):
        """Generate a comprehensive analysis report with actionable insights."""
        print("\n" + "=" * 80)
        print("📈 SMART PORTFOLIO ANALYSIS REPORT")
        print("=" * 80)

        # Portfolio overview
        df = pd.DataFrame(analysis_results)

        total_investment = df["investment"].sum()
        total_current_value = df["current_value"].sum()
        total_pnl = df["pnl"].sum()
        total_pnl_percent = (
            (total_pnl / total_investment) * 100 if total_investment > 0 else 0
        )

        print(f"\n💰 PORTFOLIO OVERVIEW:")
        print(f"   📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   🌡️  Market Condition: {self.market_condition}")
        print(f"   💵 Total Investment: ₹{total_investment:,.2f}")
        print(f"   💎 Current Value: ₹{total_current_value:,.2f}")
        print(f"   📊 Total P&L: ₹{total_pnl:,.2f} ({total_pnl_percent:+.2f}%)")
        print(f"   🎯 Portfolio Size: {len(analysis_results)} stocks")

        # Signal distribution
        signal_counts = df["signal"].value_counts()
        print(f"\n🎯 SIGNAL DISTRIBUTION:")
        for signal, count in signal_counts.items():
            emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
            print(f"   {emoji} {signal}: {count} stocks")

        # High-confidence recommendations
        high_conf_buy = df[(df["signal"] == "BUY") & (df["confidence"] > 70)]
        high_conf_sell = df[(df["signal"] == "SELL") & (df["confidence"] > 70)]

        print(f"\n🚀 HIGH-CONFIDENCE RECOMMENDATIONS:")

        if not high_conf_buy.empty:
            print("   📈 STRONG BUY SIGNALS:")
            for _, row in high_conf_buy.iterrows():
                print(f"      🟢 {row['symbol']}: {row['confidence']:.1f}% confidence")
                print(
                    f"         💰 Investment: ₹{row['investment']:,.0f} | P&L: {row['pnl_percent']:+.1f}%"
                )
                print(
                    f"         📊 Top reason: {row['reasons'][0] if row['reasons'] else 'N/A'}"
                )

        if not high_conf_sell.empty:
            print("   📉 STRONG SELL SIGNALS:")
            for _, row in high_conf_sell.iterrows():
                print(f"      🔴 {row['symbol']}: {row['confidence']:.1f}% confidence")
                print(
                    f"         💰 Investment: ₹{row['investment']:,.0f} | P&L: {row['pnl_percent']:+.1f}%"
                )
                print(
                    f"         📊 Top reason: {row['reasons'][0] if row['reasons'] else 'N/A'}"
                )

        # Risk analysis
        print(f"\n⚠️  RISK ANALYSIS:")

        high_loss_positions = df[df["pnl_percent"] < -15]
        if not high_loss_positions.empty:
            print("   🚨 HIGH-LOSS POSITIONS (>15% loss):")
            for _, row in high_loss_positions.iterrows():
                print(
                    f"      ❌ {row['symbol']}: {row['pnl_percent']:+.1f}% (₹{row['pnl']:,.0f})"
                )

        high_gain_positions = df[df["pnl_percent"] > 25]
        if not high_gain_positions.empty:
            print("   💎 HIGH-GAIN POSITIONS (>25% profit):")
            for _, row in high_gain_positions.iterrows():
                print(
                    f"      ✅ {row['symbol']}: {row['pnl_percent']:+.1f}% (₹{row['pnl']:,.0f})"
                )

        # Sector analysis
        if composition_analysis:
            print(f"\n🏭 SECTOR ALLOCATION:")
            sector_data = composition_analysis.get("sector_allocation", {})
            for sector, data in sorted(
                    sector_data.items(), key=lambda x: x[1]["percentage"], reverse=True
            ):
                print(
                    f"   📊 {sector}: {data['percentage']:.1f}% (₹{data['value']:,.0f})"
                )
                print(f"      Stocks: {', '.join(data['stocks'])}")

            risk_data = composition_analysis.get("risk_assessment", {})
            print(
                f"   ⚖️  Concentration Risk: {risk_data.get('concentration_risk', 'Unknown')}"
            )
            print(
                f"   🎯 Diversification Score: {risk_data.get('diversification_score', 0)} sectors"
            )

        # Detailed stock analysis
        print(f"\n📋 DETAILED STOCK ANALYSIS:")
        print("-" * 80)

        for _, row in df.iterrows():
            symbol = row["symbol"]
            signal = row["signal"]
            confidence = row["confidence"]

            # Signal emoji and color
            if signal == "BUY":
                signal_emoji = "🟢"
            elif signal == "SELL":
                signal_emoji = "🔴"
            else:
                signal_emoji = "🟡"

            print(f"\n{signal_emoji} {symbol} ({row['sector']}):")
            print(
                f"   💼 Holdings: {row['quantity']:,} shares @ ₹{row['avg_price']:.2f}"
            )
            print(
                f"   💰 Current: ₹{row['current_price']:.2f} | P&L: {row['pnl_percent']:+.2f}%"
            )
            print(f"   🎯 Signal: {signal} (Confidence: {confidence:.1f}%)")

            # Technical indicators
            tech_data = row.get("technical_data", {})
            if tech_data.get("rsi") and tech_data.get("rsi") != "N/A":
                print(f"   📊 RSI: {tech_data['rsi']:.1f}")
            if tech_data.get("price_vs_sma20") and tech_data.get("price_vs_sma20") != "N/A":
                print(f"   📈 vs SMA20: {tech_data['price_vs_sma20']}")
            if tech_data.get("adx") and tech_data.get("adx") != "N/A":
                print(f"   🎯 ADX: {tech_data['adx']:.1f}")

            # Pattern Analysis (NEW)
            patterns = row.get("patterns", {})
            if patterns and patterns.get("patterns_detected", 0) > 0:
                print(f"   🎨 Patterns: {patterns['patterns_detected']} detected")
                if patterns.get("top_3_patterns"):
                    for i, pattern in enumerate(
                            patterns["top_3_patterns"][:2], 1
                    ):  # Show top 2
                        pattern_emoji = (
                            "📈"
                            if pattern.get("signal") == "BUY"
                            else "📉" if pattern.get("signal") == "SELL" else "⚖️"
                        )
                        print(
                            f"      {pattern_emoji} {pattern.get('pattern', 'Unknown')}: {pattern.get('confidence', 0):.0f}% confidence"
                        )

                if patterns.get("pattern_summary"):
                    print(f"   📝 Pattern Summary: {patterns['pattern_summary']}")
            else:
                print(f"   🎨 Patterns: No significant patterns detected")

            # Top reasons
            print(f"   📝 Key Reasons:")
            for i, reason in enumerate(row["reasons"][:3], 1):
                print(f"      {i}. {reason}")

        # Action items
        print(f"\n🎬 IMMEDIATE ACTION ITEMS:")
        print("-" * 50)

        action_items = []

        # Strong buy recommendations
        strong_buys = df[(df["signal"] == "BUY") & (df["confidence"] >= 80)]
        if not strong_buys.empty:
            action_items.append("📈 CONSIDER BUYING:")
            for _, row in strong_buys.iterrows():
                action_items.append(
                    f"   • {row['symbol']} (Confidence: {row['confidence']:.1f}%)"
                )

        # Strong sell recommendations
        strong_sells = df[(df["signal"] == "SELL") & (df["confidence"] >= 80)]
        if not strong_sells.empty:
            action_items.append("📉 CONSIDER SELLING:")
            for _, row in strong_sells.iterrows():
                action_items.append(
                    f"   • {row['symbol']} (Confidence: {row['confidence']:.1f}%)"
                )

        # Stop-loss alerts
        stop_loss_needed = df[df["pnl_percent"] < -20]
        if not stop_loss_needed.empty:
            action_items.append("🛑 URGENT - STOP-LOSS REVIEW:")
            for _, row in stop_loss_needed.iterrows():
                action_items.append(
                    f"   • {row['symbol']}: {row['pnl_percent']:+.1f}% loss"
                )

        if action_items:
            for item in action_items:
                print(item)
        else:
            print("   ✅ No immediate actions required. Continue monitoring.")

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"smart_portfolio_analysis_{timestamp}.csv"
        df.to_csv(filename, index=False)

        print(f"\n💾 REPORT SAVED:")
        print(f"   📄 CSV Report: {filename}")
        print(f"   🔄 Next Analysis: Recommended in 1-4 hours during market hours")

        print("\n" + "=" * 80)
        print("⚡ Powered by Smart Portfolio Analyzer")
        print("🔗 Zerodha MCP + Yahoo Finance + Advanced Technical Analysis")
        print("=" * 80)


def main():
    """Main function to run the smart portfolio analysis."""
    analyzer = SmartPortfolioAnalyzer()
    results = analyzer.run_complete_analysis()
    return results


if __name__ == "__main__":
    main()
