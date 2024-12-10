#config.py
# This file contains the configuration parameters for the project 

from dotenv import load_dotenv
import os

load_dotenv()


DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'trading_bot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432)
}

TICKERS = [
    "EWL", "IEF", "SPY", "AAPL", "MSFT", "AMZN", "GOOGL", "BRK-B","JNJ", "JPM", "V", "PG", "UNH", "MA", "INTC", "HD", "VZ", "DIS", 'NVDA','TSLA','AMD', "NVS", "UBS", "ROG","CFR","ADEN"]

RISK_FREE_RATE = 0.015
