import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def connect():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE')
        )
        print("Connection to MySQL successful!")

    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")

    return conn

def get_symbols():
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM symbols WHERE symbol IN (SELECT DISTINCT symbol FROM orders o JOIN positions p ON o.id = p.order_id WHERE p.status = 1);")
        symbols = cursor.fetchall()
        print(symbols)
    finally:
        if cursor in locals() and cursor is not None:
            cursor.close()
        if conn in locals() and conn is not None:
            conn.close()

    return [symbol[1] for symbol in symbols]

def update_or_create_symbol(symbol: str, bid: float, ask: float):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM symbols WHERE symbol = %s;", (symbol,))
        count = cursor.fetchone()[0]

        if count == 0:
            now = datetime.now()
            cursor.execute("INSERT INTO symbols (symbol, bid, ask, created_at, updated_at) VALUES (%s, %s, %s, %s, %s);", (symbol, bid, ask, now, now))
        else:
            cursor.execute("UPDATE symbols SET bid = %s, ask = %s, updated_at = %s WHERE symbol = %s;", (bid, ask, datetime.now(), symbol))

        conn.commit()
    finally:
        if cursor in locals() and cursor is not None:
            cursor.close()
        if conn in locals() and conn is not None:
            conn.close()