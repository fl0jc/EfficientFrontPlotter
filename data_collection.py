#data_collection.py
# This file contains the functions to download and store financial data

import logging
from datetime import datetime, timedelta
import yfinance as yf
from psycopg2.extras import execute_values
from database import get_connection, return_connection
from config import TICKERS
import pandas as pd

logger = logging.getLogger(__name__)

end_date = datetime.today()
start_date = end_date - timedelta(days=20*365)

def download_financial_data(ticker):
    df = yf.download(ticker, start=start_date, end=end_date)
    if df.empty:
        logger.warning(f"No data found for {ticker}")
        return pd.DataFrame()
    df.reset_index(inplace=True)
    df['Ticker'] = ticker
    return df

def clean_data(df):
    df = df[['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    df.columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    df.dropna(inplace=True)
    df['date'] = pd.to_datetime(df['date']).dt.date
    for col in ['open', 'high', 'low', 'close', 'adj_close']:
        df = df[df[col] >= 0]
    df = df[df['volume'] >= 0]
    return df

def insert_data_to_db(records):
    if not records:
        return
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
            INSERT INTO financial_data (symbol, date, open, high, low, close, adj_close, volume)
            VALUES %s
            ON CONFLICT (symbol, date) DO UPDATE SET
            open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low,
            close=EXCLUDED.close, adj_close=EXCLUDED.adj_close, volume=EXCLUDED.volume;
            """
            execute_values(cur, query, [(
                r['symbol'], r['date'], r['open'], r['high'], r['low'],
                r['close'], r['adj_close'], r['volume']
            ) for r in records])
            conn.commit()
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
    finally:
        return_connection(conn)

def fetch_and_store_financial_data(tickers):
    for ticker in tickers:
        logger.info(f"Downloading data for {ticker}...")
        df = download_financial_data(ticker)
        if df.empty:
            continue
        df = clean_data(df)
        if df.empty:
            continue
        records = df.to_dict('records')
        insert_data_to_db(records)
