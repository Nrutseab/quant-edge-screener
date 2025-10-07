import yaml
import logging
import pandas as pd
from datetime import datetime
import backtrader as bt
import yfinance as yf  # Lazy import for main
from src.data import get_universe
from src.factors import compute_factors
from src.strategy import FactorStrategy

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path: str = 'config.yaml') -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_backtest(config: dict):
    # Fetch data
    prices, fundamentals = get_universe(
        config['data']['start_date'],
        config['data']['end_date'],
        config['data']['universe_size']
    )
    
    # Compute factors
    factors = compute_factors(prices, fundamentals, config)
    logger.info(f"Factors computed. Top score: {factors['score'].max():.2f}")
    
    # Backtest
    cerebro = bt.Cerebro()
    data_names = prices.columns.tolist()
    for name in data_names:
        cerebro.adddata(bt.feeds.PandasData(dataname=prices[name], name=name))
    
    # Benchmark (with fallback)
    benchmark_ticker = config['data']['benchmark']
    spy_data = None
    try:
        spy_data = yf.download(benchmark_ticker, start=config['data']['start_date'], end=config['data']['end_date'])['Adj Close']
        if spy_data.empty:
            raise ValueError("SPY data empty")
        logger.info("Live SPY benchmark fetched")
    except Exception as e:
        logger.warning(f"SPY fetch failed: {e}. Using portfolio average as benchmark.")
        spy_data = prices.mean(axis=1)
    spy_data.name = benchmark_ticker
    cerebro.adddata(bt.feeds.PandasData(dataname=spy_data, name=benchmark_ticker))
    
    # Strategy
    cerebro.addstrategy(FactorStrategy, factors=factors, data_names=data_names)
    
    # Broker settings (realism)
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=config['strategy']['transaction_cost'])
    cerebro.broker.set_slippage_perc(config['strategy']['slippage'])
    
    # Analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    
    logger.info(f"Starting backtest: {config['data']['start_date']} to {config['data']['end_date']}")
    results = cerebro.run()
    strat = results[0]
    
    # Metrics
    final_value = cerebro.broker.getvalue()
    total_return = (final_value / 100000 - 1) * 100
    sharpe = strat.analyzers.sharpe.get_analysis().get('sharperatio', 0)
    max_dd = strat.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0)
    
    # Alpha
    benchmark_return = (spy_data.iloc[-1] / spy_data.iloc[0] - 1)
    strategy_return = (final_value / 100000 - 1)
    alpha = strategy_return - benchmark_return
    
    logger.info(f"Final Value: ${final_value:,.2f}")
    logger.info(f"Total Return: {total_return:.2f}%")
    logger.info(f"Sharpe Ratio: {sharpe:.2f}")
    logger.info(f"Max Drawdown: {max_dd:.2f}%")
    logger.info(f"Alpha vs. {benchmark_ticker}: {alpha:.2%}")
    
    # Plot (optional; comment out for CI)
    # cerebro.plot(style='candlestick')
    
    return results

if __name__ == "__main__":
    config = load_config()
    run_backtest(config)
