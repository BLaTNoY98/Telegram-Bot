import sqlite3

def connect():
    return sqlite3.connect("data.db")

def init_db():
    conn = connect()
    cursor = conn.cursor()

    # Operatorlar jadvali
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

    # Targetologlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS targetologlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            telegram_id INTEGER UNIQUE,
            is_blocked INTEGER DEFAULT 0
        );
    """)

    # Mahsulotlar (Offerlar) jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            video TEXT,
            description TEXT,
            operator_price REAL,
            targetolog_price REAL,
            is_active INTEGER DEFAULT 1
        );
    """)

    # Leadlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_code TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            address TEXT,
            status TEXT DEFAULT 'new',
            product_id INTEGER,
            operator_id INTEGER,
            targetolog_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(operator_id) REFERENCES operators(id),
            FOREIGN KEY(targetolog_id) REFERENCES targetologlar(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
    """)

    # Sotuvlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_code TEXT,
            targetolog_id INTEGER,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(targetolog_id) REFERENCES targetologlar(id)
        );
    """)

    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            phone_number TEXT
        );
    """)

    conn.commit()
    conn.close()


# ------------------ Tekshiruv funksiyalar ------------------

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


# ------------------ Lead qo‘shish funksiyasi ------------------

def generate_lead_code():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    count = cursor.fetchone()[0]
    conn.close()
    return f"L{count + 1:05d}"

def add_lead(name, phone, address, targetolog_id, product_id):
    lead_code = generate_lead_code()
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (lead_code, name, phone, address, targetolog_id, product_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (lead_code, name, phone, address, targetolog_id, product_id))
    conn.commit()
    conn.close()
    return lead_code
