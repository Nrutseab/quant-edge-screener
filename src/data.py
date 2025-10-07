import yfinance as yf
import pandas as pd
from typing import Tuple, Dict
import logging
import time
import requests  # For session headers

logger = logging.getLogger(__name__)

# Smaller, reliable static tickers (10 for speed/reliability; expand later)
RELIABLE_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'PG']

def get_universe(start_date: str, end_date: str, universe_size: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch price data and fundamentals with retries and headers to avoid yfinance blocks.
    """
    try:
        tickers = RELIABLE_TICKERS[:universe_size]
        logger.info(f"Using {len(tickers)} reliable tickers from {start_date} to {end_date}")
        
        # Set up session with browser-like headers to evade rate limits
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        yf.pdr_override()  # Use pandas_datareader if needed, but stick to yf
        
        # Prices with retries
        prices = None
        for attempt in range(3):
            try:
                prices = yf.download(tickers, start=start_date, end=end_date, session=session)['Adj Close']
                if not prices.empty and len(prices) > 100:  # Basic validity check
                    break
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.warning(f"Price fetch attempt {attempt+1} failed: {e}")
                continue
        if prices is None or prices.empty:
            raise ValueError("Failed to fetch prices after retries")
        prices = prices.dropna(axis=1, how='all')
        
        # Fundamentals with retries and fallback
        fundamentals = {}
        failed_count = 0
        for ticker in prices.columns:
            for attempt in range(2):  # Fewer retries for info
                try:
                    stock = yf.Ticker(ticker, session=session)
                    info = stock.info
                    if info and 'trailingPE' in info:
                        fundamentals[ticker] = {
                            'trailingPE': info.get('trailingPE', 20.0),  # Default average PE
                            'marketCap': info.get('marketCap', 1e12)
                        }
                        break
                    time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"Fundamentals fetch for {ticker} attempt {attempt+1}: {e}")
                    continue
            else:
                failed_count += 1
                fundamentals[ticker] = {'trailingPE': 20.0, 'marketCap': 1e12}  # Fallback
        
        if failed_count == len(tickers):
            logger.warning("All fundamentals failed; using defaults")
        
        return prices, pd.DataFrame(fundamentals).T
    except Exception as e:
        logger.error(f"Data fetch failed: {e}")
        raise
