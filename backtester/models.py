from django.db import models

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('symbol', 'date')
        indexes = [
            models.Index(fields=['symbol', 'date']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.date}"

class BacktestResult(models.Model):
    symbol = models.CharField(max_length=10)
    start_date = models.DateField()
    end_date = models.DateField()
    initial_investment = models.DecimalField(max_digits=10, decimal_places=2)
    final_value = models.DecimalField(max_digits=10, decimal_places=2)
    total_return = models.DecimalField(max_digits=10, decimal_places=2)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=2)
    num_trades = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Backtest for {self.symbol} from {self.start_date} to {self.end_date}"