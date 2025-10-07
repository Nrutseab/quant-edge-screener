import pytest
import pandas as pd
import numpy as np
from src.factors import compute_factors

def test_compute_factors():
    # Mock data
    prices = pd.DataFrame(np.random.rand(300, 3), columns=['AAPL', 'GOOG', 'MSFT'])
    fundamentals = pd.DataFrame({'trailingPE': [20, 25, 15]}, index=['AAPL', 'GOOG', 'MSFT'])
    config = {'factors': {'weights': {'momentum':1, 'earnings_yield':1, 'inv_vol':1}}}
    
    factors = compute_factors(prices, fundamentals, config)
    assert 'score' in factors.columns
    assert not factors['score'].isna().all()
    assert 0 <= factors['score'].min() <= 1 <= factors['score'].max()
