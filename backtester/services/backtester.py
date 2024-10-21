import pandas as pd
from ..models import StockData

def calculate_moving_average(data, window):
    return data['close_price'].astype(float).rolling(window=window).mean()
    #return data['close_price'].rolling(window=window).mean()

#developed backtesting strategy by using exisitng data objects
def backtest_strategy(symbol, initial_investment, buy_ma, sell_ma):
    data = StockData.objects.filter(symbol=symbol).order_by('date')
    df = pd.DataFrame(list(data.values()))
    for field in ['open_price', 'high_price', 'low_price', 'close_price']:
        df[field] = df[field].astype(float)
    df['buy_ma'] = calculate_moving_average(df, buy_ma)
    df['sell_ma'] = calculate_moving_average(df, sell_ma)

    initial_investment = float(initial_investment)
    cash=initial_investment
    shares = 0
    trades = 0
    
    for i in range(len(df)):
        if cash > 0 and df['close_price'][i] < df['buy_ma'][i]:
            shares_to_buy = cash // df['close_price'][i]
            shares += shares_to_buy
            cash -= shares_to_buy * df['close_price'][i]
            trades += 1
        elif shares > 0 and df['close_price'][i] > df['sell_ma'][i]:
            cash += shares * df['close_price'][i]
            shares = 0
            trades += 1
    
    final_value = cash + shares * df['close_price'].iloc[-1]
    total_return = (final_value - initial_investment) / initial_investment * 100
    
    return {
        'total_return': round(total_return, 2),
        'final_value': round(final_value, 2),
        'trades': trades
    }