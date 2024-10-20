import requests
from datetime import datetime, timedelta

def fetch_stock_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=full'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if 'Time Series (Daily)' not in data:
        raise ValueError(f"Unable to fetch data for symbol {symbol}")

    time_series = data['Time Series (Daily)']
    two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    filtered_data = {date: values for date, values in time_series.items() if date >= two_years_ago}
    return filtered_data