"""
Greedy Algorithm for Stock Portfolio Optimization
Selects stocks based on best return-to-price ratio until budget runs out
"""

from typing import List, Tuple, Dict


def solve_knapsack_greedy(stocks: List[Dict], budget: int) -> Tuple[float, List[str]]:
    """
    Solve stock portfolio optimization using greedy algorithm
    Selects stocks with highest return-per-dollar ratio first
    
    Args:
        stocks (list): List of stock dicts with keys:
                      {'ticker', 'current_price', 'expected_return', 'return_per_dollar', ...}
        budget (int): Total budget available (in dollars)
    
    Returns:
        tuple: (total_return, selected_tickers)
    """
    # Create a copy and sort by return-per-dollar ratio (descending)
    sorted_stocks = sorted(stocks, key=lambda x: x.get('return_per_dollar', x['expected_return'] / x['current_price']), reverse=True)
    
    selected = []
    total_return = 0.0
    remaining_budget = budget
    
    # Greedily select stocks
    for stock in sorted_stocks:
        price = int(stock['current_price'])
        if price <= remaining_budget:
            selected.append(stock['ticker'])
            total_return += stock['expected_return']
            remaining_budget -= price
    
    return total_return, selected


def solve_knapsack_greedy_with_details(stocks: List[Dict], budget: int) -> Dict:
    """
    Solve knapsack greedily and return detailed results
    
    Returns:
        dict: Contains total_return, selected_tickers, total_cost, portfolio_details
    """
    # Create a copy and calculate return-per-dollar if not present
    enriched_stocks = []
    for stock in stocks:
        stock_copy = stock.copy()
        if 'return_per_dollar' not in stock_copy:
            stock_copy['return_per_dollar'] = stock_copy['expected_return'] / stock_copy['current_price']
        enriched_stocks.append(stock_copy)
    
    # Sort by return-per-dollar ratio (descending)
    sorted_stocks = sorted(enriched_stocks, key=lambda x: x['return_per_dollar'], reverse=True)
    
    selected_indices = []
    total_return = 0.0
    total_cost = 0
    remaining_budget = budget
    
    # Greedily select stocks
    for stock in sorted_stocks:
        price = int(stock['current_price'])
        if price <= remaining_budget:
            selected_indices.append(stock['ticker'])
            total_return += stock['expected_return']
            total_cost += price
            remaining_budget -= price
    
    # Get portfolio details
    portfolio_details = [s for s in sorted_stocks if s['ticker'] in selected_indices]
    
    return {
        'total_return': total_return,
        'selected_tickers': selected_indices,
        'total_cost': total_cost,
        'remaining_budget': remaining_budget,
        'num_stocks': len(selected_indices),
        'portfolio_details': portfolio_details,
        'sorting_metric': 'return-per-dollar',
        'algorithm': 'Greedy Algorithm'
    }


def get_greedy_value(stocks: List[Dict], budget: int) -> float:
    """Quick getter for greedy solution value"""
    total_return, _ = solve_knapsack_greedy(stocks, budget)
    return total_return


def compare_ratio_types(stocks: List[Dict], budget: int) -> Dict[str, Tuple[float, List[str]]]:
    """
    Compare different greedy sorting metrics
    
    Returns:
        dict: Results for each metric (return-per-dollar, total-return, risk-adjusted)
    """
    results = {}
    
    # Strategy 1: Return per dollar
    stocks_by_ratio = sorted(stocks, key=lambda x: x['expected_return'] / x['current_price'], reverse=True)
    result1 = greedy_select(stocks_by_ratio, budget)
    results['return-per-dollar'] = result1
    
    # Strategy 2: Pure return (ignoring cost)
    stocks_by_return = sorted(stocks, key=lambda x: x['expected_return'], reverse=True)
    result2 = greedy_select(stocks_by_return, budget)
    results['total-return'] = result2
    
    # Strategy 3: Risk-adjusted (return / risk_score)
    stocks_by_risk_adj = sorted(stocks, 
                                key=lambda x: x['expected_return'] / max(x['risk_score'], 0.01), 
                                reverse=True)
    result3 = greedy_select(stocks_by_risk_adj, budget)
    results['risk-adjusted'] = result3
    
    return results


def greedy_select(sorted_stocks: List[Dict], budget: int) -> Tuple[float, List[str]]:
    """Helper to select greedily from pre-sorted stocks"""
    selected = []
    total_return = 0.0
    remaining_budget = budget
    
    for stock in sorted_stocks:
        price = int(stock['current_price'])
        if price <= remaining_budget:
            selected.append(stock['ticker'])
            total_return += stock['expected_return']
            remaining_budget -= price
    
    return total_return, selected


if __name__ == "__main__":
    # Test example
    test_stocks = [
        {'ticker': 'AAPL', 'current_price': 150, 'expected_return': 0.20, 'risk_score': 0.25},
        {'ticker': 'GOOGL', 'current_price': 140, 'expected_return': 0.18, 'risk_score': 0.22},
        {'ticker': 'MSFT', 'current_price': 380, 'expected_return': 0.22, 'risk_score': 0.20},
        {'ticker': 'TSLA', 'current_price': 250, 'expected_return': 0.35, 'risk_score': 0.45},
        {'ticker': 'META', 'current_price': 480, 'expected_return': 0.25, 'risk_score': 0.35},
    ]
    
    # Compute return-per-dollar
    for stock in test_stocks:
        stock['return_per_dollar'] = stock['expected_return'] / stock['current_price']
    
    budget = 1000
    result = solve_knapsack_greedy_with_details(test_stocks, budget)
    
    print(f"Algorithm: {result['algorithm']}")
    print(f"Total Return: {result['total_return']:.4f}")
    print(f"Selected Stocks: {result['selected_tickers']}")
    print(f"Total Cost: ${result['total_cost']}")
    print(f"Remaining Budget: ${result['remaining_budget']}")
