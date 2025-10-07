import yfinance as yf
import pandas as pd
from typing import Tuple, Dict
import logging
import time
import os
import numpy as np

logger = logging.getLogger(__name__)

# Reliable tickers
RELIABLE_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'PG']

def get_universe(start_date: str, end_date: str, universe_size: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch price data and fundamentals; fallback to full inline mock if API or CSV fails.
    """
    try:
        tickers = RELIABLE_TICKERS[:universe_size]
        logger.info(f"Attempting fetch for {len(tickers)} tickers from {start_date} to {end_date}")
        
        # Prices with retries
        prices = None
        for attempt in range(3):
            try:
                prices = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
                if not prices.empty and len(prices) > 100:
                    logger.info("Live prices fetched successfully")
                    break
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Price fetch attempt {attempt+1} failed: {e}")
                continue
        
        # Fallback to mock if failed
        if prices is None or prices.empty:
            logger.info("Falling back to mock data for backtest")
            mock_path = os.path.join(os.path.dirname(__file__), '../data/mock_prices.csv')
            if os.path.exists(mock_path):
                prices = pd.read_csv(mock_path, index_col=0, parse_dates=True)
                if len(prices) < 252:  # Insufficient? Regenerate inline
                    logger.info("CSV too short; using inline mock")
                    prices = None
            
            if prices is None or len(prices) < 252:
                # Full inline reproducible mock (business days 2020-2025, ~0.05% daily drift for growth)
                dates = pd.date_range(start='2020-01-01', end='2025-10-01', freq='B')
                np.random.seed(42)
                mock_data = pd.DataFrame(
                    index=dates,
                    data={
                        t: 100.0 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, len(dates)))) 
                        for t in tickers
                    }
                )
                prices = mock_data
                logger.info("Generated full inline mock data (~1260 rows)")
        
        prices = prices.dropna(axis=1, how='all')
        if prices.empty or len(prices) < 252:
            raise ValueError(f"Mock prices insufficient: {len(prices)} rows")
        
        # Fundamentals: Static realistic defaults
        pe_values = [25, 30, 22, 35, 40, 28, 50, 12, 20, 18]  # Varied for factor diversity
        fundamentals = {}
        for i, ticker in enumerate(prices.columns):
            fundamentals[ticker] = {
                'trailingPE': pe_values[i % len(pe_values)],
                'marketCap': 1e12 + i * 1e11
            }
        logger.info("Fundamentals loaded (defaults for simulation)")
        
        return prices, pd.DataFrame(fundamentals).T
    except Exception as e:
        logger.error(f"Data fetch/mock failed: {e}")
        raise
