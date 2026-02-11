import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def connect():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_DATABASE'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

    return conn

def get_symbols():
    try:
        conn = connect()
        cursor = conn.cursor()
        # cursor.execute("SELECT * FROM symbols WHERE symbol IN (SELECT DISTINCT symbol FROM orders o JOIN positions p ON o.id = p.order_id WHERE p.status = 1);")
        cursor.execute("SELECT * FROM symbols;")
        symbols = cursor.fetchall()
    except psycopg2.Error as error:
        print("Error fetching symbols:", error)
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
    except psycopg2.Error as error:
        print("Error updating or creating symbol:", error)
    finally:
        if cursor in locals() and cursor is not None:
            cursor.close()
        if conn in locals() and conn is not None:
            conn.close()