from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch
from datetime import timedelta
import pandas as pd

from models import StockData
from .services.data_fetcher import fetch_stock_data
from .services.backtester import backtest_strategy, calculate_moving_average

class FinancialBacktesterTestCase(TestCase):
    def setUp(self):
        # Create sample stock data for testing
        start_date = timezone.now().date() - timedelta(days=365)
        for i in range(365):
            date = start_date + timedelta(days=i)
            StockData.objects.create(
                symbol='AAPL',
                date=date,
                open_price=100 + i * 0.1,
                close_price=101 + i * 0.1,
                high_price=102 + i * 0.1,
                low_price=99 + i * 0.1,
                volume=1000000 + i * 1000
            )

    # Data Fetching Tests
    @patch('financial_backtester.tasks.requests.get')
    def test_fetch_stock_data(self, mock_get):
        # Mock the API response
        mock_response = {
            "Time Series (Daily)": {
                "2023-06-01": {
                    "1. open": "100.0",
                    "2. high": "105.0",
                    "3. low": "99.0",
                    "4. close": "102.0",
                    "5. volume": "1000000"
                },
                "2023-05-31": {
                    "1. open": "98.0",
                    "2. high": "103.0",
                    "3. low": "97.0",
                    "4. close": "100.0",
                    "5. volume": "950000"
                }
            }
        }
        mock_get.return_value.json.return_value = mock_response

        # Call the function
        fetch_stock_data('AAPL')

        # Check if data was saved correctly
        self.assertEqual(StockData.objects.count(), 367)  # 365 from setUp + 2 new
        latest_data = StockData.objects.latest('date')
        self.assertEqual(latest_data.symbol, 'AAPL')
        self.assertEqual(latest_data.open_price, 100.0)
        self.assertEqual(latest_data.close_price, 102.0)
        self.assertEqual(latest_data.high_price, 105.0)
        self.assertEqual(latest_data.low_price, 99.0)
        self.assertEqual(latest_data.volume, 1000000)

    @patch('financial_backtester.tasks.requests.get')
    def test_fetch_stock_data_error_handling(self, mock_get):
        # Simulate a network error
        mock_get.side_effect = Exception("Network error")

        with self.assertRaises(Exception):
            fetch_stock_data('AAPL')

        # Check that no new data was saved
        self.assertEqual(StockData.objects.count(), 365)  # Only the ones from setUp

    def test_stock_data_model(self):
        # Test the StockData model
        stock_data = StockData.objects.create(
            symbol='GOOGL',
            date=timezone.now().date(),
            open_price=2500.0,
            close_price=2550.0,
            high_price=2600.0,
            low_price=2480.0,
            volume=1500000
        )
        self.assertEqual(str(stock_data), f'GOOGL - {timezone.now().date()}')

    # Backtesting Tests
    def test_perform_backtest(self):
        params = {
            'symbol': 'AAPL',
            'initial_investment': 10000,
            'buy_ma': 50,
            'sell_ma': 200
        }
        result = backtest_strategy(params)

        # Check if the result contains the expected keys
        self.assertIn('total_return', result)
        self.assertIn('max_drawdown', result)
        self.assertIn('num_trades', result)

        # Check if the values are of the correct type
        self.assertIsInstance(result['total_return'], float)
        self.assertIsInstance(result['max_drawdown'], float)
        self.assertIsInstance(result['num_trades'], int)

        # Check if the values are within reasonable ranges
        self.assertGreater(result['total_return'], -100)  # Return should be greater than -100%
        self.assertLess(result['max_drawdown'], 100)  # Max drawdown should be less than 100%
        self.assertGreaterEqual(result['num_trades'], 0)  # Number of trades should be non-negative

    def test_perform_backtest_no_data(self):
        # Delete all stock data
        StockData.objects.all().delete()

        params = {
            'symbol': 'AAPL',
            'initial_investment': 10000,
            'buy_ma': 50,
            'sell_ma': 200
        }
        
        with self.assertRaises(ValueError):
            backtest_strategy(params)

    def test_perform_backtest_invalid_params(self):
        params = {
            'symbol': 'AAPL',
            'initial_investment': -1000,  # Invalid negative investment
            'buy_ma': 50,
            'sell_ma': 200
        }
        
        with self.assertRaises(ValueError):
            backtest_strategy(params)

    def test_moving_average_calculation(self):
        df = pd.DataFrame(list(StockData.objects.all().values()))
        ma_50 = calculate_moving_average(df, 50)
        ma_200 = calculate_moving_average(df, 200)

        # Check if moving averages are calculated correctly
        self.assertEqual(len(ma_50), len(df) - 49)
        self.assertEqual(len(ma_200), len(df) - 199)
        self.assertTrue(all(ma_50.notna()))
        self.assertTrue(all(ma_200.notna()))

    def test_backtest_different_market_conditions(self):
        # Test bullish market
        StockData.objects.all().delete()
        start_date = timezone.now().date() - timedelta(days=365)
        for i in range(365):
            date = start_date + timedelta(days=i)
            StockData.objects.create(
                symbol='AAPL',
                date=date,
                open_price=100 + i * 0.5,
                close_price=101 + i * 0.5,
                high_price=102 + i * 0.5,
                low_price=99 + i * 0.5,
                volume=1000000 + i * 1000
            )
        
        params = {
            'symbol': 'AAPL',
            'initial_investment': 10000,
            'buy_ma': 50,
            'sell_ma': 200
        }
        result_bullish = backtest_strategy(params)
        
        # Test bearish market
        StockData.objects.all().delete()
        for i in range(365):
            date = start_date + timedelta(days=i)
            StockData.objects.create(
                symbol='AAPL',
                date=date,
                open_price=200 - i * 0.5,
                close_price=201 - i * 0.5,
                high_price=202 - i * 0.5,
                low_price=199 - i * 0.5,
                volume=1000000 + i * 1000
            )
        
        result_bearish = backtest_strategy(params)
        
        # Check if the strategy performs differently in different market conditions
        self.assertNotEqual(result_bullish['total_return'], result_bearish['total_return'])