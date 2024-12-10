#database.py
# This file contains the functions to create the database and tables, and to manage the connection pool

import psycopg2
from psycopg2 import pool
import logging
from config import DB_PARAMS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

connection_pool = None

def create_database_and_tables(db_params=DB_PARAMS):
    """
    Create the database (if it does not exist) and the necessary tables.
    """
    try:
        with psycopg2.connect(
            dbname='postgres',
            user=db_params['user'],
            password=db_params['password'],
            host=db_params['host'],
            port=db_params['port']
        ) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_params['dbname'],))
                exists = cur.fetchone()
                if not exists:
                    cur.execute(f"CREATE DATABASE {db_params['dbname']}")
                    logger.info(f"Database '{db_params['dbname']}' created.")
                else:
                    logger.info(f"Database '{db_params['dbname']}' already exists.")
    except psycopg2.Error as e:
        logger.error(f"Error creating the database: {e}")
        
    global connection_pool
    try:
        connection_pool = pool.SimpleConnectionPool(1, 20, **db_params)
        logger.info("Connection pool created.")
    except psycopg2.Error as e:
        logger.error(f"Error creating connection pool: {e}")

    try:
        conn = connection_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS financial_data (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    date DATE NOT NULL,
                    open DECIMAL(15,4),
                    high DECIMAL(15,4),
                    low DECIMAL(15,4),
                    close DECIMAL(15,4),
                    adj_close DECIMAL(15,4),
                    volume BIGINT,
                    UNIQUE(symbol, date)
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_financial_data_symbol_date
                ON financial_data (symbol, date);
            """)
            conn.commit()
            logger.info("Table created successfully.")
    except psycopg2.Error as e:
        logger.error(f"Error creating the table: {e}")
    finally:
        connection_pool.putconn(conn)

def get_connection():
    return connection_pool.getconn()

def return_connection(conn):
    connection_pool.putconn(conn)

def close_connection_pool():
    connection_pool.closeall()
    logger.info("Connection pool closed.")
