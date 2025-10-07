# Quant Edge Screener: Multi-Factor Momentum Tool

A Python-based tool for detecting trading edges via market inefficiencies, inspired by PyQuant Newsletter's "What is a trading edge (and how to find it)". 

This screener combines:
- **Technical Factor**: 12-month momentum.
- **Fundamental Factor**: Earnings yield (1/PE).
- **Statistical Factor**: Inverse volatility.

It ranks stocks (e.g., S&P 500 subset), simulates a long-only portfolio (top 10% holdings, quarterly rebalance), and measures alpha vs. SPY benchmark.

## Features
- Backtesting with Backtrader (incl. costs, slippage).
- Modular: Easy to add factors (e.g., ML-based).
- Configurable via YAML.
- Jupyter examples for visualization.

## Quick Start
1. Clone: `git clone https://github.com/yourusername/quant-edge-screener.git`
2. Install deps: `pip install -r requirements.txt`
3. Run: `python main.py` (outputs alpha, Sharpe, etc.)
4. Explore: Open `examples/backtest_notebook.ipynb` in Jupyter.

### Example Output
