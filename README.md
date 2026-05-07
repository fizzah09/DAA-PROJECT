# Stock Portfolio Optimization Project

A comprehensive tool for optimizing stock portfolio selection using Dynamic Programming (0/1 Knapsack) vs Greedy Algorithm, with performance analysis and interactive visualization.

---

## Project Overview

This project implements and compares two algorithms for selecting the best stocks within a budget constraint:

- **Dynamic Programming (DP)** — Guarantees optimal solution
- **Greedy Algorithm** — Fast approximation algorithm

### Key Features

- Real stock data via Yahoo Finance
- Multiple algorithm implementations (2D DP, 1D DP Space-Optimized, Greedy)
- Performance benchmarking (time, memory, accuracy)
- Interactive Streamlit dashboard
- Scalability testing
- Detailed analysis and visualization

---

## Project Structure

```
portfolio-optimizer/
│
├── data/
│   └── fetch_stocks.py          # Stock data fetching & metrics calculation
│
├── algorithms/
│   ├── __init__.py              # Package exports
│   ├── knapsack_2d.py           # Standard 2D DP implementation
│   ├── knapsack_1d.py           # Space-optimized 1D DP
│   └── greedy.py                # Greedy algorithm
│
├── analysis/
│   └── performance.py           # Benchmarking & performance analysis
│
├── app.py                       # Streamlit web application
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Setup and Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/portfolio-optimizer.git
cd portfolio-optimizer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies:

```
numpy>=1.20.0
pandas>=1.2.0
matplotlib>=3.3.0
seaborn>=0.11.0
requests>=2.25.0
streamlit>=1.0.0
plotly>=5.0.0
yfinance>=0.2.0
```

### 3. Verify Installation

```bash
python -c "import streamlit; print('streamlit OK')"
python -c "import yfinance; print('yfinance OK')"
```

---

## Quick Start

### Run the Interactive Dashboard

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Run Performance Benchmark

```bash
python -m analysis.performance
```

### Use Algorithms Directly

```python
from data.fetch_stocks import get_real_portfolio
from algorithms import solve_knapsack_2d_with_details, solve_knapsack_greedy_with_details

portfolio = get_real_portfolio(risk_level='medium', num_stocks=20)
stocks = portfolio.to_dict('records')

dp_result = solve_knapsack_2d_with_details(stocks, budget=5000)
print(f"DP Result: {dp_result['max_return']:.4f}")

greedy_result = solve_knapsack_greedy_with_details(stocks, budget=5000)
print(f"Greedy Result: {greedy_result['total_return']:.4f}")
```

---

## Algorithm Comparison

### Dynamic Programming — 2D Standard

- **Time Complexity**: O(n x W)
- **Space Complexity**: O(n x W)
- **Optimality**: Guaranteed optimal solution
- **Use Case**: When correctness is critical

```python
dp[i][w] = max(
    dp[i-1][w],
    dp[i-1][w-price] + return
)
```

### Dynamic Programming — 1D Space Optimized

- **Time Complexity**: O(n x W)
- **Space Complexity**: O(W)
- **Optimality**: Guaranteed optimal solution
- **Use Case**: Large portfolios with memory constraints

```python
for i in range(n):
    for w in range(budget, price-1, -1):
        dp[w] = max(dp[w], dp[w-price] + return)
```

### Greedy Algorithm

- **Time Complexity**: O(n log n)
- **Space Complexity**: O(n)
- **Optimality**: Approximation, not always optimal
- **Use Case**: Quick estimates, large portfolios

```python
sort_by(stocks, key = return / price)
# Greedily select until budget exhausted
```

---

## Performance Analysis

| Metric | DP 2D | DP 1D | Greedy |
|--------|-------|-------|--------|
| Time (50 stocks) | ~5ms | ~4ms | less than 1ms |
| Memory (50 stocks) | ~2MB | ~0.5MB | less than 0.1MB |
| Time (500 stocks) | ~500ms | ~450ms | less than 10ms |
| Accuracy | 100% | 100% | 85–95% |

---

## Using the Streamlit App

1. Set your budget in the sidebar
2. Choose a risk level: low, medium, or high
3. Select the number of stocks
4. Click **Run Analysis**
5. View side-by-side algorithm results and charts

---

## Key Concepts

### The Knapsack Problem Mapping

| Knapsack | Portfolio |
|----------|-----------|
| Items | Stocks |
| Weight | Stock price |
| Value | Expected return |
| Capacity | Investor budget |

### Metrics Used

- **Expected Return** — Annualized average of daily returns
- **Risk Score** — Annualized volatility (standard deviation)
- **Return-per-Dollar** — Expected return divided by price (greedy sort key)

---

## Deployment

### Streamlit Community Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set main file to `app.py`
4. Share the live link

---

## Troubleshooting

**ModuleNotFoundError: yfinance**
```bash
pip install yfinance
```

**ModuleNotFoundError: streamlit**
```bash
pip install streamlit
```

**Stock data not loading**
Check your internet connection. The app fetches live data from Yahoo Finance.

**Streamlit app won't start**
```bash
streamlit cache clear
streamlit run app.py
```

---

## Resources

| Resource | Link |
|----------|------|
| yfinance Docs | https://pypi.org/project/yfinance |
| Streamlit Docs | https://docs.streamlit.io |
| 0/1 Knapsack Problem | https://www.geeksforgeeks.org/0-1-knapsack-problem |
| Dynamic Programming (Video) | https://www.youtube.com/watch?v=oPt_QkBAduA |

---

## Team

| Role | Responsibility |
|------|----------------|
| Backend Developer | Data fetching, algorithm implementation |
| Analytics Developer | Performance benchmarking, graphs |
| Frontend Developer | Streamlit UI, interactive dashboard |

---

## Future Enhancements

- Add transaction costs
- Multi-period portfolio optimization
- Risk-adjusted metrics (Sharpe ratio)
- Backtesting module
- Export portfolio to PDF report
- Machine learning return predictions

---

This project is educational material for algorithm comparison and analysis.
```
#
