import yfinance as yf
import pandas as pd
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)

def get_universe(start_date: str, end_date: str, universe_size: int = 50) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch price data and fundamentals for S&P 500 subset.
    """
    try:
        sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500 = pd.read_html(sp500_url)[0]
        tickers = sp500['Symbol'].tolist()[:universe_size]
        logger.info(f"Fetching data for {len(tickers)} tickers from {start_date} to {end_date}")
        
        # Prices
        prices = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        prices = prices.dropna(axis=1, how='all')  # Clean NaNs
        
        # Fundamentals (basic; expand with API keys for prod)
        fundamentals = {}
        for ticker in prices.columns:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                fundamentals[ticker] = {
                    'trailingPE': info.get('trailingPE', float('nan')),
                    'marketCap': info.get('marketCap', float('nan'))
                }
            except Exception as e:
                logger.warning(f"Failed to fetch {ticker}: {e}")
                fundamentals[ticker] = {'trailingPE': float('nan'), 'marketCap': float('nan')}
        
        return prices, pd.DataFrame(fundamentals).T
    except Exception as e:
        logger.error(f"Data fetch failed: {e}")
        raise
