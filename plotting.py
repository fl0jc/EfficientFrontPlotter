#plotting.py
# This file contains the functions to plot the efficient frontier and the optimal portfolio

import matplotlib.pyplot as plt
import numpy as np

def plot_efficient_frontier(efficient_results, mean_returns, cov_matrix, rf, w_opt, portfolio_label="Optimal Portfolio"):
    """
    Plot the efficient frontier, the individual assets, and the chosen optimal portfolio.
    """
    vols = [res[0] for res in efficient_results]
    rets = [res[1] for res in efficient_results]

    plt.figure(figsize=(10,6))
    plt.plot(vols, rets, 'b-', label='Efficient Frontier')

    annualized_std_dev = np.sqrt(np.diag(cov_matrix))
    plt.scatter(annualized_std_dev, mean_returns, c='red', marker='o', label='Individual Assets')
    for i, ticker in enumerate(mean_returns.index):
        plt.annotate(ticker, (annualized_std_dev[i], mean_returns[i]))

    from portfolio_optimization import portfolio_performance
    r_opt, vol_opt = portfolio_performance(w_opt, mean_returns, cov_matrix)
    plt.scatter(vol_opt, r_opt, c='green', marker='X', s=200, label=portfolio_label)

    plt.xlabel('Volatility (Std. Dev.)')
    plt.ylabel('Expected Return (Annualized)')
    plt.title('Mean-Variance Optimization\nEfficient Frontier and Selected Portfolio')
    plt.grid(True)
    plt.legend()
    plt.show()
