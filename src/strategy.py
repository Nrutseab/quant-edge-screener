import backtrader as bt
import pandas as pd  # Added for DataFrame type hint
from typing import List  # Added for List type hint
import logging

logger = logging.getLogger(__name__)

class FactorStrategy(bt.Strategy):
    """
    Backtrader strategy: Rebalance to top-ranked holdings quarterly.
    """
    params = (
        ('hold_period', 63),
        ('top_holdings', 10),
        ('allocation_per_holding', 0.1),
    )

    def __init__(self, factors: pd.DataFrame, data_names: List[str]):
        self.factors = factors
        self.data_names = data_names
        self.bar_executed = len(self)
        self.rebalance_date = len(self) + self.params.hold_period

    def next(self):
        if len(self) >= self.rebalance_date:
            # Sell all
            for data in self.datas:
                if self.getposition(data).size > 0:
                    self.close(data=data)
            
            # Buy top picks (simulate fresh factors; in live, refetch)
            top_picks = self.factors.nlargest(self.params.top_holdings, 'score').index.tolist()
            for pick in top_picks:
                if pick in self.data_names:
                    data = self.getdatabyname(pick)
                    size = int((self.broker.getcash() * self.params.allocation_per_holding) / data.close[0])
                    self.buy(data=data, size=size)
                    logger.info(f"Bought {size} shares of {pick}")
            
            self.bar_executed = len(self)
            self.rebalance_date += self.params.hold_period
            logger.info(f"Rebalanced at bar {len(self)}")

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        logger.info(f"Trade Closed: {trade.getdataname()} | PNL: {trade.pnl:.2f} ({trade.pnl/trade.value:.2%})")
