import matplotlib.pyplot as plt
import io
import base64
from ..models import StockData
from .backtester import backtest_strategy
from ml_predictor.models import train_and_predict

def generate_report(symbol, initial_investment, buy_ma, sell_ma):
    # Ensure correct types
    symbol = str(symbol)
    initial_investment = float(initial_investment)
    buy_ma = int(buy_ma)
    sell_ma = int(sell_ma)

    # Fetch data
    data = StockData.objects.filter(symbol=symbol).order_by('date')
    
    # Perform backtesting
    backtest_result = backtest_strategy(symbol, initial_investment, buy_ma, sell_ma)
    
    # Get predictions
    predictions = train_and_predict(symbol)
    
    # Convert QuerySet to list for easier handling
    dates = list(data.values_list('date', flat=True))
    prices = list(data.values_list('close_price', flat=True))
    
    # Generate plot
    plt.figure(figsize=(12, 6))
    plt.plot(dates, prices, label='Actual')
    plt.plot(dates[-30:], predictions, label='Predicted')
    plt.title(f'{symbol} Stock Price - Actual vs Predicted')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    
    # Save plot to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    
    # Prepare report data
    report_data = {
        'symbol': symbol,
        'backtest_result': backtest_result,
        'predictions': predictions,
        'plot': graphic
    }
    
    return report_data
# def generate_report(symbol, initial_investment, buy_ma, sell_ma):
#     # Fetch data
#     data = StockData.objects.filter(symbol=symbol).order_by('date')
#     symbol = str(symbol)
#     initial_investment = float(initial_investment)
#     buy_ma = int(buy_ma)
#     sell_ma = int(sell_ma)

#     backtest_result = backtest_strategy(symbol, initial_investment, buy_ma, sell_ma)
#     # Perform backtesting
#     backtest_result = backtest_strategy(symbol, initial_investment, buy_ma, sell_ma)
    
#     # Get predictions
#     predictions = train_and_predict(symbol)
    
#     # Generate plot
#     plt.figure(figsize=(12, 6))
#     plt.plot(data.values_list('date', flat=True), data.values_list('close_price', flat=True), label='Actual')
#     plt.plot(data.values_list('date', flat=True)[-30:], predictions, label='Predicted')
#     plt.title(f'{symbol} Stock Price - Actual vs Predicted')
#     plt.xlabel('Date')
#     plt.ylabel('Price')
#     plt.legend()
    
#     # Save plot to buffer
#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')
#     buffer.seek(0)
#     image_png = buffer.getvalue()
#     buffer.close()
#     graphic = base64.b64encode(image_png)
#     graphic = graphic.decode('utf-8')
    
#     # Prepare report data
#     report_data = {
#         'symbol': symbol,
#         'backtest_result': backtest_result,
#         'predictions': predictions,
#         'plot': graphic
#     }
    
#     return report_data