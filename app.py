"""
Streamlit Web Application for Stock Portfolio Optimization
Interactive dashboard to compare DP vs Greedy algorithms
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load environment variables from .env file
import os
from dotenv import load_dotenv
load_dotenv()

from data.fetch_stocks import get_real_portfolio
from algorithms import solve_knapsack_2d_with_details, solve_knapsack_1d_with_details, solve_knapsack_greedy_with_details
from analysis.performance import PerformanceBenchmark


def create_portfolio_comparison_chart(dp_result, greedy_result):
    """Create visualization comparing algorithm results"""
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("DP Algorithm Portfolio", "Greedy Algorithm Portfolio"),
        specs=[[{"type": "pie"}, {"type": "pie"}]]
    )
    
    # DP pie chart
    dp_stocks = dp_result['selected_tickers']
    dp_values = [s['expected_return'] for s in dp_result['portfolio_details']]
    
    fig.add_trace(
        go.Pie(labels=dp_stocks, values=dp_values, name="DP Stocks", hole=0.3),
        row=1, col=1
    )
    
    # Greedy pie chart
    greedy_stocks = greedy_result['selected_tickers']
    greedy_values = [s['expected_return'] for s in greedy_result['portfolio_details']]
    
    fig.add_trace(
        go.Pie(labels=greedy_stocks, values=greedy_values, name="Greedy Stocks", hole=0.3),
        row=1, col=2
    )
    
    fig.update_layout(height=500, title_text="Algorithm Comparison: Stock Selection")
    return fig


def create_performance_chart(dp_result, greedy_result):
    """Create metrics comparison bar chart"""
    
    metrics = {
        'Algorithm': ['DP Knapsack', 'Greedy'],
        'Total Return': [dp_result['max_return'], greedy_result['total_return']],
        'Stocks Selected': [dp_result['num_stocks'], greedy_result['num_stocks']],
        'Total Cost': [dp_result['total_cost'], greedy_result['total_cost']],
    }
    
    df = pd.DataFrame(metrics)
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Total Return", "Number of Stocks", "Total Cost ($)"),
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )
    
    fig.add_trace(
        go.Bar(x=df['Algorithm'], y=df['Total Return'], name='Return'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=df['Algorithm'], y=df['Stocks Selected'], name='Count'),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=df['Algorithm'], y=df['Total Cost'], name='Cost'),
        row=1, col=3
    )
    
    fig.update_layout(height=400, showlegend=False)
    return fig


def display_portfolio_details(result, title):
    """Display portfolio holdings as detailed table"""
    
    if not result['portfolio_details']:
        st.info(f"No stocks selected by {title}")
        return
    
    portfolio_df = pd.DataFrame(result['portfolio_details'])
    
    # Select relevant columns for display
    display_cols = ['ticker', 'current_price', 'expected_return', 'risk_score']
    display_cols = [col for col in display_cols if col in portfolio_df.columns]
    
    portfolio_df_display = portfolio_df[display_cols].copy()
    portfolio_df_display.columns = ['Ticker', 'Price', 'Expected Return', 'Risk Score']
    
    st.dataframe(portfolio_df_display, use_container_width=True)


def main():
    st.set_page_config(page_title="Portfolio Optimizer", layout="wide")
    
    st.title("📈 Stock Portfolio Optimization Tool")
    st.markdown("Compare **Dynamic Programming** vs **Greedy Algorithm** for optimal stock selection")
    
    # Create tabs
    tab1, tab2 = st.tabs(["🚀 Portfolio Optimization", "📊 Performance Benchmark"])
    
    with tab1:
        show_portfolio_optimization()
    
    with tab2:
        show_performance_benchmark()


def show_portfolio_optimization():
    """Main portfolio optimization interface"""
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        budget = st.slider("Budget ($)", min_value=1000, max_value=100000, value=10000, step=1000, key="opt_budget")
        
        risk_level = st.selectbox("Risk Level", ["low", "medium", "high"], key="opt_risk")
        
        num_stocks = st.slider("Number of Stocks to Consider", min_value=5, max_value=50, value=20, step=5, key="opt_stocks")
        
        run_analysis = st.button("🚀 Run Analysis", type="primary", key="run_opt")
    
    if run_analysis:
        with st.spinner("Fetching real stock data and running optimization..."):
            try:
                # Get real portfolio data
                portfolio_df = get_real_portfolio(risk_level, num_stocks)
                
                if portfolio_df is None or portfolio_df.empty:
                    st.error("❌ No portfolio data returned. Portfolio DataFrame is empty.")
                    st.info("Check the terminal for detailed error messages.")
                    return
                
                st.success(f"✅ Successfully fetched data for {len(portfolio_df)} stocks")
                
            except ValueError as e:
                st.error(f"❌ Failed to fetch stock data: {str(e)}")
                st.info("Please check:")
                st.info("1. Internet connection is working")
                st.info("2. MARKETSTACK_API_KEY environment variable is set")
                st.info("3. API rate limit not exceeded (check terminal)")
                return
            except Exception as e:
                st.error(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
                st.info("Check the terminal for detailed traceback.")
                import traceback
                st.code(traceback.format_exc())
                return
            
            stocks_list = portfolio_df.to_dict('records')
            
            # Solve with both algorithms
            dp_result = solve_knapsack_2d_with_details(stocks_list, budget)
            greedy_result = solve_knapsack_greedy_with_details(stocks_list, budget)
            
            # Display results
            st.header("📊 Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("DP Total Return", f"${dp_result['max_return']:.4f}", 
                         delta=f"{dp_result['num_stocks']} stocks")
            
            with col2:
                greedy_gap = ((dp_result['max_return'] - greedy_result['total_return']) / dp_result['max_return'] * 100) if dp_result['max_return'] > 0 else 0
                st.metric("Greedy Total Return", f"${greedy_result['total_return']:.4f}", 
                         delta=f"{greedy_gap:.2f}% gap vs DP")
            
            # Charts
            st.plotly_chart(create_portfolio_comparison_chart(dp_result, greedy_result), use_container_width=True)
            st.plotly_chart(create_performance_chart(dp_result, greedy_result), use_container_width=True)
            
            # Detailed tables
            st.header("📋 Portfolio Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("DP Knapsack (Optimal)")
                display_portfolio_details(dp_result, "DP")
                st.caption(f"Budget Used: ${dp_result['total_cost']} / ${budget}")
                st.caption(f"Remaining: ${dp_result['remaining_budget']}")
            
            with col2:
                st.subheader("Greedy Algorithm (Approximation)")
                display_portfolio_details(greedy_result, "Greedy")
                st.caption(f"Budget Used: ${greedy_result['total_cost']} / ${budget}")
                st.caption(f"Remaining: ${greedy_result['remaining_budget']}")
            
            # Summary
            st.header("📈 Summary")
            
            summary_data = {
                'Metric': [
                    'Algorithm',
                    'Total Return',
                    'Stocks Selected',
                    'Budget Used',
                    'Budget Remaining',
                    'Return per Dollar Spent'
                ],
                'DP Knapsack': [
                    'Dynamic Programming (Optimal)',
                    f"${dp_result['max_return']:.4f}",
                    dp_result['num_stocks'],
                    f"${dp_result['total_cost']}",
                    f"${dp_result['remaining_budget']}",
                    f"${dp_result['max_return'] / dp_result['total_cost']:.4f}" if dp_result['total_cost'] > 0 else "N/A"
                ],
                'Greedy': [
                    'Greedy Algorithm (Fast Approximation)',
                    f"${greedy_result['total_return']:.4f}",
                    greedy_result['num_stocks'],
                    f"${greedy_result['total_cost']}",
                    f"${greedy_result['remaining_budget']}",
                    f"${greedy_result['total_return'] / greedy_result['total_cost']:.4f}" if greedy_result['total_cost'] > 0 else "N/A"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            st.plotly_chart(create_portfolio_comparison_chart(dp_result, greedy_result), use_container_width=True)
            st.plotly_chart(create_performance_chart(dp_result, greedy_result), use_container_width=True)
            
            # Detailed tables
            st.header("📋 Portfolio Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("DP Knapsack (Optimal)")
                display_portfolio_details(dp_result, "DP")
                st.caption(f"Budget Used: ${dp_result['total_cost']} / ${budget}")
                st.caption(f"Remaining: ${dp_result['remaining_budget']}")
            
            with col2:
                st.subheader("Greedy Algorithm (Approximation)")
                display_portfolio_details(greedy_result, "Greedy")
                st.caption(f"Budget Used: ${greedy_result['total_cost']} / ${budget}")
                st.caption(f"Remaining: ${greedy_result['remaining_budget']}")
            
            # Summary
            st.header("📈 Summary")
            
            summary_data = {
                'Metric': [
                    'Algorithm',
                    'Total Return',
                    'Stocks Selected',
                    'Budget Used',
                    'Budget Remaining',
                    'Return per Dollar Spent'
                ],
                'DP Knapsack': [
                    'Dynamic Programming (Optimal)',
                    f"${dp_result['max_return']:.4f}",
                    dp_result['num_stocks'],
                    f"${dp_result['total_cost']}",
                    f"${dp_result['remaining_budget']}",
                    f"${dp_result['max_return'] / dp_result['total_cost']:.4f}" if dp_result['total_cost'] > 0 else "N/A"
                ],
                'Greedy': [
                    'Greedy Algorithm (Fast Approximation)',
                    f"${greedy_result['total_return']:.4f}",
                    greedy_result['num_stocks'],
                    f"${greedy_result['total_cost']}",
                    f"${greedy_result['remaining_budget']}",
                    f"${greedy_result['total_return'] / greedy_result['total_cost']:.4f}" if greedy_result['total_cost'] > 0 else "N/A"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    else:
        st.info("👈 Use the sidebar to configure parameters and run the optimization!")
        
        st.markdown("""
        ### 🎯 How It Works
        
        1. **Configure** your budget and risk preference in the sidebar
        2. **Select** the number of stocks to analyze
        3. **Run** the optimization to compare algorithms
        
        ### 🔍 Algorithm Comparison
        
        | Feature | DP Knapsack | Greedy |
        |---------|-------------|--------|
        | **Optimality** | Always optimal | Approximation |
        | **Speed** | O(n·W) | O(n·log n) |
        | **Memory** | O(n·W) | O(n) |
        | **Use Case** | Critical decisions | Quick estimates |
        
        ### 📚 Resources
        - [MarketStack API](https://marketstack.com)
        - [Streamlit Docs](https://docs.streamlit.io)
        """)


def show_performance_benchmark():
    """Performance benchmarking interface"""
    
    st.header("📊 Algorithm Performance Benchmark")
    st.markdown("Compare time, memory, and accuracy of different optimization algorithms")
    
    # Sidebar for benchmark configuration
    with st.sidebar:
        st.header("⚙️ Benchmark Settings")
        
        benchmark_budget = st.slider("Test Budget ($)", min_value=1000, max_value=50000, value=5000, step=1000, key="bench_budget")
        
        benchmark_stocks = st.slider("Number of Test Stocks", min_value=10, max_value=100, value=30, step=10, key="bench_stocks")
        
        benchmark_runs = st.slider("Benchmark Runs", min_value=1, max_value=10, value=3, step=1, key="bench_runs")
        
        run_benchmark = st.button("🚀 Run Benchmark", type="primary", key="run_bench")
    
    if run_benchmark:
        with st.spinner("Running performance benchmarks..."):
            try:
                # Create synthetic portfolio for benchmarking
                from data.fetch_stocks import create_synthetic_portfolio
                test_portfolio = create_synthetic_portfolio(benchmark_stocks, 'medium')
                stocks_list = test_portfolio.to_dict('records')
                
                # Initialize benchmark
                benchmark = PerformanceBenchmark()
                
                # Run accuracy comparison
                accuracy_results = benchmark.accuracy_comparison(stocks_list, benchmark_budget)
                
                # Run individual benchmarks
                dp2d_bench = benchmark.benchmark_algorithm('DP 2D', solve_knapsack_2d_with_details, stocks_list, benchmark_budget, benchmark_runs)
                dp1d_bench = benchmark.benchmark_algorithm('DP 1D', solve_knapsack_1d_with_details, stocks_list, benchmark_budget, benchmark_runs)
                greedy_bench = benchmark.benchmark_algorithm('Greedy', solve_knapsack_greedy_with_details, stocks_list, benchmark_budget, benchmark_runs)
                
                # Display results
                st.success("Benchmark completed successfully!")
                
                # Accuracy Comparison
                st.header("🎯 Accuracy Comparison")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("DP 2D (Optimal)", f"${accuracy_results['dp_2d_return']:.4f}", 
                             delta=f"{accuracy_results['dp_2d_stocks']} stocks")
                
                with col2:
                    st.metric("DP 1D (Optimal)", f"${accuracy_results['dp_1d_return']:.4f}", 
                             delta=f"{accuracy_results['dp1d_accuracy_percent']:.2f}% accuracy")
                
                with col3:
                    gap = accuracy_results['gap_greedy_vs_optimal_percent']
                    st.metric("Greedy (Approx)", f"${accuracy_results['greedy_return']:.4f}", 
                             delta=f"-{gap:.2f}% vs optimal")
                
                # Performance Metrics
                st.header("⚡ Performance Metrics")
                
                perf_data = {
                    'Algorithm': ['DP 2D', 'DP 1D', 'Greedy'],
                    'Avg Time (ms)': [
                        f"{dp2d_bench['avg_time_ms']:.2f}",
                        f"{dp1d_bench['avg_time_ms']:.2f}",
                        f"{greedy_bench['avg_time_ms']:.2f}"
                    ],
                    'Avg Memory (MB)': [
                        f"{dp2d_bench['avg_memory_mb']:.2f}",
                        f"{dp1d_bench['avg_memory_mb']:.2f}",
                        f"{greedy_bench['avg_memory_mb']:.2f}"
                    ],
                    'Stocks Selected': [
                        accuracy_results['dp_2d_stocks'],
                        accuracy_results['dp_1d_stocks'],
                        accuracy_results['greedy_stocks']
                    ]
                }
                
                perf_df = pd.DataFrame(perf_data)
                st.dataframe(perf_df, use_container_width=True, hide_index=True)
                
                # Performance Chart
                st.header("📈 Performance Visualization")
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Time (ms)',
                    x=perf_data['Algorithm'],
                    y=[float(x) for x in perf_data['Avg Time (ms)']],
                    marker_color='lightblue'
                ))
                
                fig.add_trace(go.Bar(
                    name='Memory (MB)',
                    x=perf_data['Algorithm'],
                    y=[float(x) for x in perf_data['Avg Memory (MB)']],
                    marker_color='lightgreen'
                ))
                
                fig.update_layout(
                    title="Algorithm Performance Comparison",
                    xaxis_title="Algorithm",
                    yaxis_title="Performance Metric",
                    barmode='group'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Key Insights
                st.header("🔍 Key Insights")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ✅ Strengths")
                    st.markdown("- **DP 2D**: Always optimal solution")
                    st.markdown("- **DP 1D**: Space-efficient optimal")
                    st.markdown("- **Greedy**: Fastest execution")
                
                with col2:
                    st.markdown("### ⚠️ Trade-offs")
                    st.markdown("- **DP 2D**: High memory usage")
                    st.markdown("- **DP 1D**: Best space efficiency")
                    st.markdown("- **Greedy**: May be suboptimal")
                
                st.markdown(f"""
                ### 📊 Summary
                - **Accuracy Gap**: Greedy is {accuracy_results['greedy_accuracy_percent']:.1f}% as accurate as optimal DP
                - **Speed Difference**: Greedy is ~{(dp2d_bench['avg_time_ms'] / greedy_bench['avg_time_ms']) if greedy_bench['avg_time_ms'] > 0 else 0:.0f}x faster than DP 2D
                - **Memory Efficiency**: DP 1D uses {(dp2d_bench['avg_memory_mb'] / dp1d_bench['avg_memory_mb']) if dp1d_bench['avg_memory_mb'] > 0 else 0:.1f}x less memory than DP 2D
                """)
                
            except Exception as e:
                st.error(f"Benchmark failed: {str(e)}")
                st.info("Try reducing the number of stocks or runs.")
    
    else:
        st.info("👈 Configure benchmark settings in the sidebar and run the analysis!")
        
        st.markdown("""
        ### 🎯 What This Benchmark Does
        
        - **Time Measurement**: How long each algorithm takes to solve
        - **Memory Usage**: RAM consumption during execution
        - **Accuracy Comparison**: How close Greedy gets to optimal DP solution
        
        ### 🔬 Test Scenarios
        
        | Scenario | Best Algorithm | Reason |
        |----------|----------------|--------|
        | **Small portfolios** (<50 stocks) | DP 2D | Simple, guaranteed optimal |
        | **Large portfolios** (50-500 stocks) | DP 1D | Memory-efficient optimal |
        | **Very large** (>500 stocks) | Greedy | Fast approximation |
        | **Real-time needs** | Greedy | Speed over accuracy |
        
        ### 📈 Why Benchmark?
        
        Understanding algorithm performance helps you choose the right tool for your use case:
        - **Investment decisions**: Use DP for accuracy
        - **Quick analysis**: Use Greedy for speed
        - **Large portfolios**: Balance time vs optimality
        """)


if __name__ == "__main__":
    main()
