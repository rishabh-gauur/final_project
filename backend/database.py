import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'nurses.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS nurses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            user_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            mobile_number TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()
