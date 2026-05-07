"""
Performance analysis module
Benchmarks time, memory, and accuracy of different algorithms
"""

import time
import tracemalloc
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

from algorithms.knapsack_2d import solve_knapsack_2d_with_details as dp_2d_solve
from algorithms.knapsack_1d import solve_knapsack_1d_with_details as dp_1d_solve
from algorithms.greedy import solve_knapsack_greedy_with_details as greedy_solve
from data.fetch_stocks import create_synthetic_portfolio


class PerformanceBenchmark:
    """Benchmarking class for portfolio optimization algorithms"""
    
    def __init__(self):
        self.results = []
    
    def benchmark_algorithm(self, algorithm_name: str, algo_func, stocks: List[Dict], budget: int, runs=1) -> Dict:
        """
        Benchmark a single algorithm
        
        Args:
            algorithm_name (str): Name of algorithm
            algo_func: Function to benchmark
            stocks (list): Stock data
            budget (int): Budget constraint
            runs (int): Number of runs to average
        
        Returns:
            dict: Benchmark results
        """
        times = []
        memory_usage = []
        
        for _ in range(runs):
            tracemalloc.start()
            start_time = time.time()
            
            result = algo_func(stocks, budget)
            
            elapsed = time.time() - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            times.append(elapsed)
            memory_usage.append(peak / 1024 / 1024)  # Convert to MB
        
        avg_time = np.mean(times)
        avg_memory = np.mean(memory_usage)
        
        return {
            'algorithm': algorithm_name,
            'avg_time_ms': avg_time * 1000,
            'avg_memory_mb': avg_memory,
            'min_time_ms': min(times) * 1000,
            'max_time_ms': max(times) * 1000,
            'result': result
        }
    
    def run_scalability_test(self, budget=5000, max_stocks=500, step=50) -> pd.DataFrame:
        """
        Test algorithm performance as number of stocks increases
        
        Args:
            budget (int): Fixed budget
            max_stocks (int): Maximum number of stocks to test
            step (int): Increment step for stock count
        
        Returns:
            pd.DataFrame: Performance metrics for each stock count
        """
        results = []
        
        stock_counts = list(range(50, max_stocks + 1, step))
        
        for num_stocks in stock_counts:
            print(f"Testing with {num_stocks} stocks...")
            
            # Create synthetic portfolio
            stocks = create_synthetic_portfolio(num_stocks, risk_level='medium')
            portfolio_list = stocks.to_dict('records')
            
            # Benchmark each algorithm
            dp2d_bench = self.benchmark_algorithm('DP 2D', dp_2d_solve, portfolio_list, budget)
            dp1d_bench = self.benchmark_algorithm('DP 1D', dp_1d_solve, portfolio_list, budget)
            greedy_bench = self.benchmark_algorithm('Greedy', greedy_solve, portfolio_list, budget)
            
            results.append({
                'num_stocks': num_stocks,
                'dp_2d_time_ms': dp2d_bench['avg_time_ms'],
                'dp_2d_memory_mb': dp2d_bench['avg_memory_mb'],
                'dp_1d_time_ms': dp1d_bench['avg_time_ms'],
                'dp_1d_memory_mb': dp1d_bench['avg_memory_mb'],
                'greedy_time_ms': greedy_bench['avg_time_ms'],
                'greedy_memory_mb': greedy_bench['avg_memory_mb'],
            })
        
        return pd.DataFrame(results)
    
    def accuracy_comparison(self, stocks: List[Dict], budget: int) -> Dict:
        """
        Compare solution quality between algorithms
        DP should give optimal, Greedy may be suboptimal
        
        Returns:
            dict: Accuracy metrics and comparison
        """
        # Get solutions
        dp2d_result = dp_2d_solve(stocks, budget)
        dp1d_result = dp_1d_solve(stocks, budget)
        greedy_result = greedy_solve(stocks, budget)
        
        dp_optimal = dp2d_result['max_return']
        
        # Calculate accuracy (as % of optimal)
        greedy_accuracy = (greedy_result['total_return'] / dp_optimal * 100) if dp_optimal > 0 else 0
        dp1d_accuracy = (dp1d_result['max_return'] / dp_optimal * 100) if dp_optimal > 0 else 100
        
        return {
            'dp_2d_return': dp_optimal,
            'dp_1d_return': dp1d_result['max_return'],
            'greedy_return': greedy_result['total_return'],
            'dp1d_accuracy_percent': dp1d_accuracy,
            'greedy_accuracy_percent': greedy_accuracy,
            'gap_greedy_vs_optimal_percent': 100 - greedy_accuracy,
            'dp_2d_stocks': len(dp2d_result['selected_tickers']),
            'dp_1d_stocks': len(dp1d_result['selected_tickers']),
            'greedy_stocks': len(greedy_result['selected_tickers']),
        }
    
    def generate_report(self, scalability_df: pd.DataFrame) -> str:
        """
        Generate a text report of performance analysis
        
        Args:
            scalability_df (pd.DataFrame): Results from scalability test
        
        Returns:
            str: Formatted report
        """
        report = """
╔═══════════════════════════════════════════════════════════════════════════╗
║           PORTFOLIO OPTIMIZATION ALGORITHM PERFORMANCE REPORT             ║
╚═══════════════════════════════════════════════════════════════════════════╝

SCALABILITY ANALYSIS:
"""
        report += scalability_df.to_string()
        
        report += f"""

KEY FINDINGS:
- DP 2D Complexity: O(n*W) where n=stocks, W=budget
- DP 1D Complexity: O(n*W) time, O(W) space
- Greedy Complexity: O(n*log(n)) for sorting
- Greedy is fastest but may be suboptimal
- DP 1D has best space efficiency
- Both DP approaches give same optimal solution

RECOMMENDATIONS:
1. For portfolios <100 stocks: Use DP 2D (simple, clear)
2. For portfolios 100-500 stocks: Use DP 1D (space-efficient)
3. For portfolios >500 stocks: Consider Greedy for speed
4. Always validate Greedy solution vs DP optimal
"""
        return report


def quick_benchmark(stocks: List[Dict], budget: int):
    """Quick benchmark function for testing"""
    benchmark = PerformanceBenchmark()
    
    print("Running quick benchmark...")
    print("=" * 60)
    
    # Single run benchmark
    dp2d = benchmark.benchmark_algorithm('DP 2D', dp_2d_solve, stocks, budget)
    print(f"\n2D DP: {dp2d['avg_time_ms']:.4f} ms, {dp2d['avg_memory_mb']:.4f} MB")
    print(f"  Result: {dp2d['result']['max_return']:.4f}, {dp2d['result']['num_stocks']} stocks")
    
    dp1d = benchmark.benchmark_algorithm('DP 1D', dp_1d_solve, stocks, budget)
    print(f"\n1D DP: {dp1d['avg_time_ms']:.4f} ms, {dp1d['avg_memory_mb']:.4f} MB")
    print(f"  Result: {dp1d['result']['max_return']:.4f}, {dp1d['result']['num_stocks']} stocks")
    
    greedy = benchmark.benchmark_algorithm('Greedy', greedy_solve, stocks, budget)
    print(f"\nGreedy: {greedy['avg_time_ms']:.4f} ms, {greedy['avg_memory_mb']:.4f} MB")
    print(f"  Result: {greedy['result']['total_return']:.4f}, {greedy['result']['num_stocks']} stocks")
    
    # Accuracy
    print("\n" + "=" * 60)
    accuracy = benchmark.accuracy_comparison(stocks, budget)
    print(f"\nACCURACY COMPARISON:")
    print(f"DP 2D (optimal):     {accuracy['dp_2d_return']:.4f}")
    print(f"DP 1D (optimal):     {accuracy['dp_1d_return']:.4f} ({accuracy['dp1d_accuracy_percent']:.2f}%)")
    print(f"Greedy (approx):     {accuracy['greedy_return']:.4f} ({accuracy['greedy_accuracy_percent']:.2f}%)")
    print(f"Gap (Greedy vs DP):  {accuracy['gap_greedy_vs_optimal_percent']:.2f}%")


if __name__ == "__main__":
    # Test with synthetic data
    print("Creating test portfolio...")
    test_portfolio = create_synthetic_portfolio(30, 'medium')
    stocks_list = test_portfolio.to_dict('records')
    
    quick_benchmark(stocks_list, budget=5000)
