from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from backtester.models import StockData

def train_and_predict(symbol):
    data = StockData.objects.filter(symbol=symbol).order_by('date')
    df = pd.DataFrame(list(data.values()))
    
    df['target'] = df['close_price'].shift(-1)
    df = df.dropna()
    
    X = df[['open_price', 'high_price', 'low_price', 'close_price', 'volume']]
    y = df['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Predict the next 30 days
    last_30_days = X.tail(30)
    predictions = model.predict(last_30_days)
    
    return predictions.tolist()