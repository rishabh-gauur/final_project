import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'hospital.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Users table covers both admins and staff
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            mobile_number TEXT,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    # Allocations table maps staff to wards and beds
    conn.execute('''
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ward_number TEXT NOT NULL,
            bed_number TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Insert default admin if none exists
    admin = conn.execute("SELECT * FROM users WHERE role = 'admin'").fetchone()
    if not admin:
        conn.execute('''
            INSERT INTO users (name, username, email, password, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('System Admin', 'admin', 'admin@hospital.com', 'admin123', 'admin'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized at hospital.db")
