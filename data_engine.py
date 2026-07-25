# data_engine.py
import yfinance as yf
import pandas as pd
import feedparser
import urllib.parse

class IndianMarketEngine:
    """Production Engine strictly tuned for the NSE/BSE Indian Market."""

    @staticmethod
    def format_inr(value):
        """Converts raw numbers into Indian Crores and Lakhs."""
        if value is None or value == 0:
            return "N/A"
        
        abs_value = abs(value)
        if abs_value >= 1_000_000_000_000:  # Trillion -> Lakh Crore
            formatted = f"₹{value / 1_000_000_000_000:.2f} Lakh Cr"
        elif abs_value >= 10_000_000:       # 10 Million -> Crore
            formatted = f"₹{value / 10_000_000:.2f} Cr"
        elif abs_value >= 100_000:          # 100k -> Lakh
            formatted = f"₹{value / 100_000:.2f} Lakh"
        else:
            formatted = f"₹{value:,.2f}"
        return formatted

    @staticmethod
    def clean_ticker(symbol: str) -> str:
        """Automatically appends .NS (National Stock Exchange) if missing."""
        symbol = symbol.upper().strip()
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol += ".NS"
        return symbol

    @staticmethod
    def get_stock_profile(symbol: str) -> dict:
        nse_symbol = IndianMarketEngine.clean_ticker(symbol)
        
        try:
            ticker = yf.Ticker(nse_symbol)
            info = ticker.info
            
            # If the dict is empty, the ticker is invalid
            if not info or 'shortName' not in info:
                return {"error": f"Could not find Indian stock: {nse_symbol}. Check spelling."}
            
            return {
                "symbol": nse_symbol,
                "name": info.get("shortName") or info.get("longName"),
                "sector": info.get("sector", "N/A"),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice", 0.0),
                "market_cap_fmt": IndianMarketEngine.format_inr(info.get("marketCap")),
                "pe_ratio": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A",
                "roe": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else "N/A",
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "summary": info.get("longBusinessSummary", "Business description unavailable.")
            }
        except Exception as e:
            return {"error": f"API Error for {nse_symbol}: {str(e)}"}

    @staticmethod
    def get_chart_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Bulletproof chart fetcher that handles NSE market holidays/empty data."""
        nse_symbol = IndianMarketEngine.clean_ticker(symbol)
        df = yf.Ticker(nse_symbol).history(period=period)
        
        if df.empty:
            return df
            
        # Clean Indian market NaNs and flatten index for Plotly
        df = df.dropna()
        df.reset_index(inplace=True)
        # Ensure the date column is clean
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        return df

    @staticmethod
    def get_live_indian_news(symbol: str) -> list:
        """Fetches breaking news strictly from the last 24h using Google News India RSS."""
        base_name = symbol.replace(".NS", "").replace(".BO", "")
        # Query specifically for Indian news (gl=IN) in the last 1 day (when:1d)
        query = urllib.parse.quote(f"{base_name} share news when:1d")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        
        try:
            feed = feedparser.parse(url)
            clean_news = []
            for entry in feed.entries[:5]:
                clean_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published
                })
            
            if not clean_news:
                return [{"title": f"No major breaking news for {base_name} in the last 24 hours.", "link": "#"}]
            return clean_news
        except Exception:
            return [{"title": "Failed to fetch live Indian news feed.", "link": "#"}]
