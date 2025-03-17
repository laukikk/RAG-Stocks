import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from dotenv import load_dotenv

def get_db_connection():
    """
    Establish a connection to the PostgreSQL database (Neon).
    The NEON_DATABASE_URL environment variable must contain the connection string.
    """
    # Load environment variables from .env file
    load_dotenv()

    NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")
    if not NEON_DATABASE_URL:
        raise HTTPException(status_code=500, detail="NEON_DATABASE_URL not found in environment variables")

    try:
        conn = psycopg2.connect(NEON_DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def get_user_portfolios(user_id: int):
    """
    Example function to retrieve all portfolios for a given user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM portfolios WHERE user_id = %s", (user_id,))
        portfolios = cursor.fetchall()
        return portfolios
    finally:
        cursor.close()
        conn.close()
        
def get_user_transactions(user_id: int):
    """
    Example function to retrieve all transactions for a given user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s", (user_id,))
        transactions = cursor.fetchall()
        return transactions
    finally:
        cursor.close()
        conn.close()
        
def get_user_holdings(user_id: int):
    """
    Example function to retrieve all holdings for a given user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM holdings WHERE user_id = %s", (user_id,))
        holdings = cursor.fetchall()
        return holdings
    finally:
        cursor.close()
        conn.close()