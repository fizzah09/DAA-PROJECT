
import numpy as np
from typing import List, Tuple, Dict


def solve_knapsack_2d(stocks: List[Dict], budget: int) -> Tuple[float, List[str]]:
    """
    Solve stock portfolio optimization using standard 2D DP knapsack
    
    Args:
        stocks (list): List of stock dicts with keys:
                      {'ticker', 'current_price', 'expected_return', 'risk_score', ...}
        budget (int): Total budget available (in dollars)
    
    Returns:
        tuple: (max_return, selected_tickers)
    """
    n = len(stocks)
    
    # Prepare weights (prices) and values (returns)
    weights = [int(stock['current_price']) for stock in stocks]
    values = [stock['expected_return'] for stock in stocks]
    
    # Create DP table
    # dp[i][w] = maximum return using first i stocks with budget w
    dp = [[0.0 for _ in range(budget + 1)] for _ in range(n + 1)]
    
    # Fill the DP table
    for i in range(1, n + 1):
        for w in range(budget + 1):
            # Don't include stock i-1
            dp[i][w] = dp[i-1][w]
            
            # Include stock i-1 if it fits
            if weights[i-1] <= w:
                include_value = dp[i-1][w - weights[i-1]] + values[i-1]
                dp[i][w] = max(dp[i][w], include_value)
    
    # Backtrack to find which stocks were selected
    selected = []
    w = budget
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(stocks[i-1]['ticker'])
            w -= weights[i-1]
    
    max_return = dp[n][budget]
    
    return max_return, selected[::-1]


def solve_knapsack_2d_with_details(stocks: List[Dict], budget: int) -> Dict:
    """
    Solve knapsack and return detailed results
    
    Returns:
        dict: Contains max_return, selected_tickers, total_cost, portfolio_details
    """
    n = len(stocks)
    weights = [int(stock['current_price']) for stock in stocks]
    values = [stock['expected_return'] for stock in stocks]
    
    # Create DP table
    dp = [[0.0 for _ in range(budget + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(budget + 1):
            dp[i][w] = dp[i-1][w]
            if weights[i-1] <= w:
                include_value = dp[i-1][w - weights[i-1]] + values[i-1]
                dp[i][w] = max(dp[i][w], include_value)
    
    # Backtrack
    selected_indices = []
    w = budget
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_indices.append(i-1)
            w -= weights[i-1]
    
    selected_indices = selected_indices[::-1]
    
    # Calculate details
    total_cost = sum(weights[i] for i in selected_indices)
    max_return = dp[n][budget]
    portfolio_details = [stocks[i] for i in selected_indices]
    
    return {
        'max_return': max_return,
        'selected_tickers': [s['ticker'] for s in portfolio_details],
        'total_cost': total_cost,
        'remaining_budget': budget - total_cost,
        'num_stocks': len(selected_indices),
        'portfolio_details': portfolio_details,
        'dp_table_size': (n+1, budget+1),
        'algorithm': '2D DP Knapsack'
    }


def get_dp_value(stocks: List[Dict], budget: int) -> float:
    """Quick getter for DP table value"""
    max_return, _ = solve_knapsack_2d(stocks, budget)
    return max_return


if __name__ == "__main__":
    # Test example
    test_stocks = [
        {'ticker': 'AAPL', 'current_price': 150, 'expected_return': 0.20},
        {'ticker': 'GOOGL', 'current_price': 140, 'expected_return': 0.18},
        {'ticker': 'MSFT', 'current_price': 380, 'expected_return': 0.22},
        {'ticker': 'TSLA', 'current_price': 250, 'expected_return': 0.35},
        {'ticker': 'META', 'current_price': 480, 'expected_return': 0.25},
    ]
    
    budget = 1000
    result = solve_knapsack_2d_with_details(test_stocks, budget)
    
    print(f"Algorithm: {result['algorithm']}")
    print(f"Max Return: {result['max_return']:.4f}")
    print(f"Selected Stocks: {result['selected_tickers']}")
    print(f"Total Cost: ${result['total_cost']}")
    print(f"Remaining Budget: ${result['remaining_budget']}")
