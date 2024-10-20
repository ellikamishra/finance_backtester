from django.urls import path
from .views import FetchStockDataView
from ml_predictor.views import predict_stock_prices
urlpatterns = [
    path('fetch-stock-data/', FetchStockDataView.as_view(), name='fetch_stock_data'),
    path('backtest/', FetchStockDataView.backtest, name='backtest'),
    path('predict/', predict_stock_prices, name='predict'),
    path('report/', FetchStockDataView.generate_report_view, name='report'),
]