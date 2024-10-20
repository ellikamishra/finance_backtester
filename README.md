# Financial Backtester

This Django-based project fetches financial data from Alpha Vantage, stores it in a PostgreSQL database, and provides basic backtesting functionality.

## Setup

1. Clone the repository and navigate to the directory:

   ```
   git clone https://github.com/ellikamishra/financial-backtester.git
   cd financial-backtester
   ```

2. Create a `.env` file in the project root and add the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key_here
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_
   ```
3. Create a virtual environment using "python -m venv venv" and activate it using "source venv/bin/activate"

4. Install all dependencies using "pip install -r requirements.txt"

5. Setup the database using "docker-compose up -d db"

6. Run python migrations using python manage.py makemigrations, python manage.py migrate

7. Start django server using python manage.py runserver

8. Test the endpoints using curl, like "curl -X POST -H "Content-Type: application/json" -d '{"symbol":"AAPL"}' http://127.0.0.1:8000/api/fetch-stock-data/"
