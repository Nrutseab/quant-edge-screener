import pandas as pd
import numpy as np
from typing import Dict

def compute_factors(prices: pd.DataFrame, fundamentals: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    Compute and rank factors for edge detection.
    """
    factors = pd.DataFrame(index=prices.columns)
    lookback_mom = config['factors']['momentum_lookback']
    lookback_vol = config['factors']['vol_lookback']
    weights = config['factors']['weights']
    
    # Technical: Momentum
    mom_returns = prices.pct_change(lookback_mom).iloc[-1]
    factors['momentum'] = mom_returns
    
    # Fundamental: Earnings Yield
    ey = 1 / fundamentals['trailingPE'].replace(0, np.nan)
    factors['earnings_yield'] = ey
    
    # Statistical: Inverse Volatility
    daily_returns = prices.pct_change(21)  # ~1 month
    vols = daily_returns.rolling(lookback_vol).std().iloc[-1] * np.sqrt(252)
    factors['inv_vol'] = 1 / vols.replace(0, np.nan)
    
    # Z-score normalize & weight
    for col in ['momentum', 'earnings_yield', 'inv_vol']:
        factors[f'z_{col}'] = (factors[col] - factors[col].mean()) / factors[col].std()
    
    factors['score'] = (
        weights['momentum'] * factors['z_momentum'] +
        weights['earnings_yield'] * factors['z_earnings_yield'] +
        weights['inv_vol'] * factors['z_inv_vol']
    ).rank(pct=True)  # Percentile rank for selection
    
    return factors.dropna()
