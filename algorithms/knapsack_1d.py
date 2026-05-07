
import numpy as np
from typing import List, Tuple, Dict


def solve_knapsack_1d(stocks: List[Dict], budget: int) -> Tuple[float, List[str]]:
    """
    Solve stock portfolio optimization using space-optimized 1D DP knapsack
    
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
    
    # Create 1D DP array
    # dp[w] = maximum return with budget w
    dp = [0.0 for _ in range(budget + 1)]
    
    # Track which item was used (for backtracking)
    # used[w][i] = True if stock i was used at capacity w
    used = [[False] * n for _ in range(budget + 1)]
    
    # Fill the DP array
    for i in range(n):
        # Traverse from right to left to avoid using same item twice
        for w in range(budget, weights[i] - 1, -1):
            if dp[w - weights[i]] + values[i] > dp[w]:
                dp[w] = dp[w - weights[i]] + values[i]
                # Mark that we used stock i
                used[w] = used[w - weights[i]].copy()
                used[w][i] = True
    
    # Backtrack to find selected stocks
    selected = []
    for i in range(n):
        if used[budget][i]:
            selected.append(stocks[i]['ticker'])
    
    max_return = dp[budget]
    
    return max_return, selected


def solve_knapsack_1d_with_details(stocks: List[Dict], budget: int) -> Dict:
    """
    Solve knapsack and return detailed results using 1D DP
    
    Returns:
        dict: Contains max_return, selected_tickers, total_cost, portfolio_details
    """
    n = len(stocks)
    weights = [int(stock['current_price']) for stock in stocks]
    values = [stock['expected_return'] for stock in stocks]
    
    # Create 1D DP array
    dp = [0.0 for _ in range(budget + 1)]
    used = [[False] * n for _ in range(budget + 1)]
    
    for i in range(n):
        for w in range(budget, weights[i] - 1, -1):
            if dp[w - weights[i]] + values[i] > dp[w]:
                dp[w] = dp[w - weights[i]] + values[i]
                used[w] = used[w - weights[i]].copy()
                used[w][i] = True
    
    # Find selected stocks
    selected_indices = [i for i in range(n) if used[budget][i]]
    
    # Calculate details
    total_cost = sum(weights[i] for i in selected_indices)
    max_return = dp[budget]
    portfolio_details = [stocks[i] for i in selected_indices]
    
    return {
        'max_return': max_return,
        'selected_tickers': [s['ticker'] for s in portfolio_details],
        'total_cost': total_cost,
        'remaining_budget': budget - total_cost,
        'num_stocks': len(selected_indices),
        'portfolio_details': portfolio_details,
        'dp_space_complexity': budget + 1,
        'algorithm': '1D DP Knapsack (Space-Optimized)'
    }


def get_dp_value(stocks: List[Dict], budget: int) -> float:
    """Quick getter for DP table value"""
    max_return, _ = solve_knapsack_1d(stocks, budget)
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
    result = solve_knapsack_1d_with_details(test_stocks, budget)
    
    print(f"Algorithm: {result['algorithm']}")
    print(f"Max Return: {result['max_return']:.4f}")
    print(f"Selected Stocks: {result['selected_tickers']}")
    print(f"Total Cost: ${result['total_cost']}")
    print(f"Remaining Budget: ${result['remaining_budget']}")
    print(f"Space Complexity: O({result['dp_space_complexity']})")
