#portfolio_optimization.py
# This file contains the functions to perform portfolio optimization and risk analysis

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from database import get_connection, return_connection
from config import RISK_FREE_RATE

def fetch_prices_from_db(tickers, start_date, end_date):
    """
    Fetch adjusted closing prices for given tickers and date range from the database.
    """
    conn = get_connection()
    try:
        query = """
        SELECT date, symbol, adj_close
        FROM financial_data
        WHERE symbol = ANY(%s) AND date >= %s AND date <= %s
        ORDER BY date;
        """
        df = pd.read_sql(query, conn, params=(tickers, start_date, end_date))
        prices = df.pivot(index='date', columns='symbol', values='adj_close').dropna()
        return prices
    finally:
        return_connection(conn)

def portfolio_performance(weights, mean_returns, cov_matrix):
    """
    Calculate portfolio performance: expected return and volatility.
    """
    ret = np.dot(weights, mean_returns)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return ret, vol

def max_utility(mean_returns, cov_matrix, risk_aversion):
    """
    Solve the mean-variance utility maximization problem.
    Utility = E[R] - (a/2)*Var(R)
    subject to sum(weights)=1 and weights>=0.
    """
    num_assets = len(mean_returns)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    x0 = np.ones(num_assets) / num_assets

    def utility_obj(w):
        mu_p, vol_p = portfolio_performance(w, mean_returns, cov_matrix)
        return -(mu_p - risk_aversion * 0.5 * (vol_p ** 2))

    result = minimize(utility_obj, x0, method='SLSQP', bounds=bounds, constraints=constraints)
    return result.x

def efficient_frontier(mean_returns, cov_matrix, num_points=200):
    """
    Compute points on the efficient frontier by minimizing volatility for
    various target returns.
    Using a higher number of points to increase the 'smoothness' and reduce
    numerical artifacts at the tangency points.
    """
    max_ret = mean_returns.max()
    min_ret = mean_returns.min()
    target_returns = np.linspace(min_ret, max_ret, num_points)
    ef = []
    num_assets = len(mean_returns)

    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints_base = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})

    for target_return in target_returns:
        constraints = (
            constraints_base,
            {'type': 'eq', 'fun': lambda x: np.dot(x, mean_returns) - target_return}
        )
        x0 = np.ones(num_assets)/num_assets

        def vol_obj(w):
            return portfolio_performance(w, mean_returns, cov_matrix)[1]

        result = minimize(vol_obj, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        if result.success:
            w = result.x
            _, vol = portfolio_performance(w, mean_returns, cov_matrix)
            ef.append((vol, target_return, w))
    return ef

def sortino_ratio(returns, rf=RISK_FREE_RATE):
    """
    Compute the Sortino ratio:
    Sortino = (mean(returns - rf)) / downside_deviation
    Downside deviation is std dev of returns that are below rf.
    """
    excess = returns - rf/52.0
    negative_excess = excess[excess < 0]
    if len(negative_excess) == 0:
        return np.inf
    downside_deviation = np.sqrt((negative_excess**2).mean())
    annualized_excess = (excess.mean() * 52)  
    annualized_downside_dev = downside_deviation * np.sqrt(52)
    return annualized_excess / annualized_downside_dev

def max_drawdown(returns):
    """
    Compute Maximum Drawdown of the return series.
    """
    cum_returns = (1 + returns).cumprod()
    peak = cum_returns.cummax()
    drawdown = (cum_returns - peak) / peak
    return drawdown.min()
