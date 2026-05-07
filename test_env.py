#!/usr/bin/env python
"""Test if .env file is loaded and portfolio fetch works"""

from data.fetch_stocks import get_real_portfolio

try:
    print("Fetching portfolio data...")
    portfolio = get_real_portfolio('medium', 5)
    print(f"✅ SUCCESS: Portfolio shape {portfolio.shape}")
    print(f"✅ Columns: {portfolio.columns.tolist()}")
    print(f"✅ First stock: {portfolio.iloc[0]['ticker']}")
    print("\nPortfolio preview:")
    print(portfolio.head())
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
