#main.py
# This file contains the main script to run the project

import logging
import pandas as pd
from datetime import datetime
from database import create_database_and_tables, close_connection_pool
from data_collection import fetch_and_store_financial_data
from portfolio_optimization import (fetch_prices_from_db, portfolio_performance,
                                    max_utility, efficient_frontier, sortino_ratio, max_drawdown)
from plotting import plot_efficient_frontier
from config import TICKERS, RISK_FREE_RATE

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    create_database_and_tables()

    logging.info("Downloading and storing financial data...")
    fetch_and_store_financial_data(TICKERS)
    logging.info("Data successfully collected.")

    START_DATE = '2012-12-31'
    END_DATE = '2024-06-30'
    prices = fetch_prices_from_db(TICKERS, START_DATE, END_DATE)
    prices.index = pd.to_datetime(prices.index)

    weekly_prices = prices.resample('W').last().dropna()
    weekly_returns = weekly_prices.pct_change().dropna()

    mean_returns = weekly_returns.mean() * 52
    cov_matrix = weekly_returns.cov() * 52

    logging.info("Annualized expected returns of individual assets:")
    logging.info(mean_returns)
    logging.info(f"Risk-free rate used: {RISK_FREE_RATE:.4f}")

    risk_aversion = float(input("Enter your risk aversion coefficient (e.g. 5): "))

    w_opt = max_utility(mean_returns, cov_matrix, risk_aversion)
    r_opt, vol_opt = portfolio_performance(w_opt, mean_returns, cov_matrix)
    sharpe_opt = (r_opt - RISK_FREE_RATE) / vol_opt

    logging.info(f"Expected return: {r_opt:.4f}")
    logging.info(f"Volatility: {vol_opt:.4f}")
    logging.info(f"Sharpe Ratio: {sharpe_opt:.4f}")
    
    portfolio_weekly_returns = (weekly_returns * w_opt).sum(axis=1)
    sortino = sortino_ratio(portfolio_weekly_returns, rf=RISK_FREE_RATE)
    mdd = max_drawdown(portfolio_weekly_returns)

    logging.info(f"Sortino Ratio: {sortino:.4f}")
    logging.info(f"Maximum Drawdown: {mdd:.2%}")

    ef_results = efficient_frontier(mean_returns, cov_matrix)

    df_opt = pd.DataFrame({
        'Ticker': mean_returns.index,
        'Weight (%)': w_opt * 100
    })
    df_opt = df_opt.sort_values(by='Weight (%)', ascending=False)
    df_opt['Weight (%)'] = df_opt['Weight (%)'].round(2)
    logging.info("\nOptimal Portfolio Weights:\n" + df_opt.to_string(index=False))
    
    plot_efficient_frontier(ef_results, mean_returns, cov_matrix, RISK_FREE_RATE, w_opt)

    close_connection_pool()
