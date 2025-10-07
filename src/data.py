import yfinance as yf
import pandas as pd
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)

# Static S&P 500 tickers (subset of ~50 for speed; update as needed)
SP500_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ASML', 'WMT',
    'JPM', 'V', 'PG', 'UNH', 'HD', 'MA', 'JNJ', 'COST', 'ABBV', 'NFLX',
    'CRM', 'AMD', 'ADBE', 'LIN', 'TMO', 'ACN', 'DHR', 'MCD', 'NKE', 'QCOM',
    'ABT', 'TXN', 'WFC', 'CVX', 'XOM', 'MRK', 'PM', 'ORCL', 'KO', 'LOW',
    'DIS', 'BAC', 'NEE', 'CSCO', 'AMGN', 'BMY', 'HON', 'RTX', 'SPGI', 'GILD'
]

def get_universe(start_date: str, end_date: str, universe_size: int = 50) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch price data and fundamentals for S&P 500 subset using static tickers.
    """
    try:
        tickers = SP500_TICKERS[:universe_size]  # Use static list
        logger.info(f"Using static {len(tickers)} tickers from {start_date} to {end_date}")
        
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
                logger.warning(f"Failed to fetch fundamentals for {ticker}: {e}")
                fundamentals[ticker] = {'trailingPE': float('nan'), 'marketCap': float('nan')}
        
        return prices, pd.DataFrame(fundamentals).T
    except Exception as e:
        logger.error(f"Data fetch failed: {e}")
        raise
