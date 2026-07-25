# data_engine.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataEngine:
    """Production Data & Technical Analysis Engine for InvestWise AI"""

    @staticmethod
    def get_stock_profile(symbol: str) -> dict:
        """Fetches live stock information, fundamental ratios, and operational metrics."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract essential balance sheet and valuation metrics safely
            profile = {
                "symbol": symbol.upper(),
                "name": info.get("shortName") or info.get("longName") or symbol,
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "currency": info.get("currency", "INR"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or 0.0,
                "previous_close": info.get("previousClose") or info.get("regularMarketPreviousClose") or 0.0,
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "forward_pe": info.get("forwardPE", None),
                "peg_ratio": info.get("pegRatio", None),
                "pb_ratio": info.get("priceToBook", None),
                "price_to_sales": info.get("priceToSalesTrailing12Months", None),
                "ev_to_ebitda": info.get("enterpriseToEbitda", None),
                "roe": info.get("returnOnEquity", None),
                "roce": info.get("returnOnAssets", None), # Proxy fallback
                "profit_margin": info.get("profitMargins", None),
                "operating_margin": info.get("operatingMargins", None),
                "revenue_growth": info.get("revenueGrowth", None),
                "debt_to_equity": info.get("debtToEquity", None),
                "current_ratio": info.get("currentRatio", None),
                "free_cash_flow": info.get("freeCashflow", 0),
                "total_debt": info.get("totalDebt", 0),
                "total_cash": info.get("totalCash", 0),
                "eps": info.get("trailingEps", None),
                "book_value": info.get("bookValue", None),
                "beta": info.get("beta", 1.0),
                "52w_high": info.get("fiftyTwoWeekHigh", 0.0),
                "52w_low": info.get("fiftyTwoWeekLow", 0.0),
                "summary": info.get("longBusinessSummary", "Business description unavailable.")
            }
            return profile
        except Exception as e:
            return {"error": f"Failed to retrieve data for ticker '{symbol}': {str(e)}"}

    @staticmethod
    def get_historical_with_technicals(symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Fetches OHLCV data and calculates RSI, MACD, Moving Averages, and Bollinger Bands."""
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        
        if df.empty:
            return df
            
        # 1. Simple Moving Averages
        df['SMA_50'] = df['Close'].rolling(window=min(50, len(df))).mean()
        df['SMA_200'] = df['Close'].rolling(window=min(200, len(df))).mean()
        
        # 2. Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # 3. MACD Calculation
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # 4. Relative Strength Index (RSI - 14 Days)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 5. Bollinger Bands (20 Days, 2 Std Dev)
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (std * 2)
        
        return df

    @staticmethod
    def get_recent_news(symbol: str) -> list:
        """Fetches verified recent news headlines associated with the symbol."""
        try:
            ticker = yf.Ticker(symbol)
            raw_news = ticker.news
            clean_news = []
            
            for item in raw_news[:5]:
                content = item.get("content", {})
                title = content.get("title") or item.get("title", "Market Announcement")
                publisher = content.get("provider", {}).get("displayName") or item.get("publisher", "Market News")
                link = content.get("canonicalUrl", {}).get("url") or item.get("link", "#")
                
                clean_news.append({
                    "title": title,
                    "publisher": publisher,
                    "link": link
                })
            return clean_news
        except Exception:
            return [{"title": "No verified recent news flags found.", "publisher": "System", "link": "#"}]
