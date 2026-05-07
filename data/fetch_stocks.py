"""
Stock data fetching module using MarketStack API
Retrieves real stock data and calculates return & risk metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import time
import requests
from typing import Optional, List

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


def fetch_stock_data(tickers: List[str], period: str = "1y") -> Optional[pd.DataFrame]:
    """
    Fetch historical stock data from MarketStack API using bulk requests
    
    Args:
        tickers (list): List of stock symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])
        period (str): Data period ('1y', '6mo', '3mo', '1mo')
    
    Returns:
        pd.DataFrame: Historical stock data (Close prices)
    """
    # Get API key from environment variable
    api_key = os.getenv('MARKETSTACK_API_KEY')
    if not api_key:
        raise ValueError("MARKETSTACK_API_KEY environment variable not set. Please set your MarketStack API key.")

    # Map period to date range
    end_date = datetime.now()
    if period == "1y":
        start_date = end_date - timedelta(days=365)
    elif period == "6mo":
        start_date = end_date - timedelta(days=180)
    elif period == "3mo":
        start_date = end_date - timedelta(days=90)
    elif period == "1mo":
        start_date = end_date - timedelta(days=30)
    else:
        start_date = end_date - timedelta(days=365)

    # MarketStack allows up to 5 symbols per request on free tier
    BATCH_SIZE = 5
    ticker_batches = [tickers[i:i + BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    
    all_data = {}
    
    print(f"Fetching data for {len(tickers)} stocks in {len(ticker_batches)} API calls...")
    
    for i, batch in enumerate(ticker_batches):
        try:
            print(f"API call {i+1}/{len(ticker_batches)}: {batch}")
            
            # MarketStack API endpoint
            url = "http://api.marketstack.com/v1/eod"
            symbols_param = ','.join(batch)
            
            params = {
                'access_key': api_key,
                'symbols': symbols_param,
                'date_from': start_date.strftime('%Y-%m-%d'),
                'date_to': end_date.strftime('%Y-%m-%d'),
                'limit': 1000  # Maximum allowed per request
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if 'data' in data and data['data']:
                # Group data by symbol
                symbol_data = {}
                for item in data['data']:
                    symbol = item['symbol']
                    if symbol not in symbol_data:
                        symbol_data[symbol] = []
                    symbol_data[symbol].append(item)

                # Process each symbol in the batch
                for symbol in batch:
                    if symbol in symbol_data:
                        symbol_items = symbol_data[symbol]
                        
                        # Sort by date (oldest first)
                        symbol_items.sort(key=lambda x: x['date'])
                        
                        # Extract close prices
                        prices = []
                        dates = []
                        for item in symbol_items:
                            if 'close' in item and item['close'] is not None:
                                prices.append(item['close'])
                                dates.append(item['date'])

                        if prices:
                            all_data[symbol] = pd.Series(prices, index=pd.to_datetime(dates))
                            print(f"  ✓ {symbol}: {len(prices)} data points")
                        else:
                            print(f"  ⚠ {symbol}: No valid price data")
                    else:
                        print(f"  ✗ {symbol}: No data in API response")
            else:
                print(f"  ✗ Batch {batch}: No data returned from API")

            # Respect rate limit (30 requests per minute = ~2 seconds between requests)
            if i < len(ticker_batches) - 1:  # Don't sleep after last request
                time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP error for batch {batch}: {e}")
            continue
        except Exception as e:
            print(f"❌ Unexpected error for batch {batch}: {e}")
            continue

    if not all_data:
        return None

    # Create DataFrame from collected data
    df = pd.DataFrame(all_data)
    print(f"✅ Successfully fetched data for {len(all_data)}/{len(tickers)} stocks")
    return df

def calculate_metrics(stock_prices):
    """
    Calculate expected return and risk (volatility) for each stock
    
    Args:
        stock_prices (pd.DataFrame): DataFrame with stock prices
    
    Returns:
        pd.DataFrame: DataFrame with columns [ticker, current_price, expected_return, risk_score]
    """
    metrics = []
    
    print(f"DEBUG: calculate_metrics received data shape: {stock_prices.shape}")
    print(f"DEBUG: Columns: {stock_prices.columns.tolist()}")
    
    for ticker in stock_prices.columns:
        try:
            prices = stock_prices[ticker].dropna()
            
            if len(prices) < 2:
                print(f"  ⚠ {ticker}: Insufficient data points ({len(prices)})")
                continue
            
            # Calculate daily returns
            daily_returns = prices.pct_change().dropna()
            
            if len(daily_returns) == 0:
                print(f"  ⚠ {ticker}: No valid returns calculated")
                continue
            
            # Expected return (annualized)
            expected_return = daily_returns.mean() * 252  # 252 trading days per year
            
            # Risk score (annualized volatility / standard deviation)
            risk_score = daily_returns.std() * np.sqrt(252)
            
            # Current price
            current_price = prices.iloc[-1]
            
            if current_price <= 0:
                print(f"  ⚠ {ticker}: Invalid current price ({current_price})")
                continue
            
            metrics.append({
                'ticker': ticker,
                'current_price': round(current_price, 2),
                'expected_return': round(expected_return, 4),
                'risk_score': round(risk_score, 4),
                'return_per_dollar': round(expected_return / current_price, 6) if current_price > 0 else 0
            })
            print(f"  ✓ {ticker}: return={expected_return:.4f}, risk={risk_score:.4f}")
        except Exception as e:
            print(f"  ❌ {ticker}: Error - {str(e)}")
            continue
    
    return pd.DataFrame(metrics)


def filter_by_risk_level(metrics_df, risk_level='medium'):
    """
    Filter stocks based on risk preference
    
    Args:
        metrics_df (pd.DataFrame): Stock metrics
        risk_level (str): 'low', 'medium', or 'high'
    
    Returns:
        pd.DataFrame: Filtered stock metrics
    """
    if risk_level == 'low':
        return metrics_df[metrics_df['risk_score'] < metrics_df['risk_score'].quantile(0.33)]
    elif risk_level == 'high':
        return metrics_df[metrics_df['risk_score'] > metrics_df['risk_score'].quantile(0.67)]
    else:  # medium
        return metrics_df


def get_real_portfolio(risk_level='medium', num_stocks=20):
    """
    Get a real portfolio with specified risk level using actual stock data from MarketStack
    
    Args:
        risk_level (str): 'low', 'medium', or 'high'
        num_stocks (int): Number of stocks to include
    
    Returns:
        pd.DataFrame: Real portfolio metrics
    """
    # Popular tech and market stocks (removed SQ as it's delisted)
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'TSLA', 'NVDA', 'JPM', 'BAC', 'WFC',
        'XOM', 'CVX', 'JNJ', 'PG', 'KO',
        'PEP', 'MCD', 'DIS', 'NKE', 'ADBE',
        'CSCO', 'IBM', 'INTC', 'AMD', 'PYPL',
        'SHOP', 'UBER', 'LYFT', 'COIN'
    ]
    
    # Fetch data using MarketStack
    stock_data = fetch_stock_data(tickers[:num_stocks], period='1y')
    
    if stock_data is None or stock_data.empty:
        raise ValueError("Failed to fetch real stock data from MarketStack. No data received.")
    
    # Calculate metrics
    try:
        metrics = calculate_metrics(stock_data)
    except Exception as e:
        raise ValueError(f"Error calculating metrics: {str(e)}")
    
    if metrics.empty:
        raise ValueError("No valid stock metrics could be calculated from the data.")
    
    # Filter by risk level
    try:
        filtered = filter_by_risk_level(metrics, risk_level)
    except Exception as e:
        raise ValueError(f"Error filtering by risk level: {str(e)}")
    
    if filtered.empty:
        # If filtering results in no stocks, return unfiltered but warn
        print(f"Warning: No stocks matched the {risk_level} risk criteria. Returning all available stocks.")
        return metrics.reset_index(drop=True)
    
    return filtered.reset_index(drop=True)


def create_synthetic_portfolio(num_stocks=20, risk_level='medium'):
    """
    Create synthetic stock data for performance testing and benchmarking only.
    NOT used in the main application - real data only.

    Args:
        num_stocks (int): Number of synthetic stocks
        risk_level (str): 'low', 'medium', or 'high'

    Returns:
        pd.DataFrame: Synthetic portfolio metrics
    """
    np.random.seed(42)

    if risk_level == 'low':
        prices = np.random.uniform(50, 150, num_stocks)
        returns = np.random.uniform(0.05, 0.15, num_stocks)
        risks = np.random.uniform(0.1, 0.2, num_stocks)
    elif risk_level == 'high':
        prices = np.random.uniform(10, 300, num_stocks)
        returns = np.random.uniform(0.1, 0.5, num_stocks)
        risks = np.random.uniform(0.3, 0.6, num_stocks)
    else:  # medium
        prices = np.random.uniform(30, 200, num_stocks)
        returns = np.random.uniform(0.08, 0.25, num_stocks)
        risks = np.random.uniform(0.15, 0.35, num_stocks)

    data = {
        'ticker': [f'STOCK{i}' for i in range(1, num_stocks + 1)],
        'current_price': prices,
        'expected_return': returns,
        'risk_score': risks,
        'return_per_dollar': returns / prices
    }

    return pd.DataFrame(data)





if __name__ == "__main__":
    # Example usage
    print("Fetching real portfolio (medium risk, 15 stocks)...")
    portfolio = get_real_portfolio('medium', 15)
    print(portfolio)
    print(f"\nTotal stocks: {len(portfolio)}")
