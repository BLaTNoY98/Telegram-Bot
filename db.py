import sqlite3

def connect():
    return sqlite3.connect("data.db")

def init_db():
    conn = connect()
    cursor = conn.cursor()

    # Operators
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            hold_balance REAL DEFAULT 0,
            main_balance REAL DEFAULT 0,
            is_blocked INTEGER DEFAULT 0
        );
    """)

    # Targetologlar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS targetologlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT,
            hold_balance REAL DEFAULT 0,
            main_balance REAL DEFAULT 0,
            is_blocked INTEGER DEFAULT 0
        );
    """)

    # Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            phone_number TEXT
        );
    """)

    # Products (Offers)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            video TEXT,
            price_targetolog REAL,
            price_operator REAL,
            is_active INTEGER DEFAULT 1
        );
    """)

    # Leads
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_uid TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            address TEXT,
            status TEXT DEFAULT 'new',
            operator_id INTEGER,
            targetolog_id INTEGER,
            product_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(operator_id) REFERENCES operators(id),
            FOREIGN KEY(targetolog_id) REFERENCES targetologlar(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
    """)

    # Sales (for targetolog statistics)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            targetolog_id INTEGER,
            lead_id INTEGER,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(targetolog_id) REFERENCES targetologlar(id),
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        );
    """)

    # Withdrawal Requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            targetolog_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'pending',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

# === Basic Role Checks ===

def is_operator(telegram_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM operators WHERE telegram_id = ? AND is_blocked = 0", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def is_targetolog(telegram_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM targetologlar WHERE telegram_id = ? AND is_blocked = 0", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def is_registered(telegram_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def register_user(telegram_id: int, phone_number: str):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (telegram_id, phone_number) VALUES (?, ?)", (telegram_id, phone_number))
    conn.commit()
    conn.close()

# === Lead Unique ID Generator ===

def generate_lead_uid(lead_id: int) -> str:
    return f"L{str(lead_id).zfill(5)}"
