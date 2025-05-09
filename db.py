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
            name TEXT,
            telegram_id INTEGER UNIQUE,
            is_blocked INTEGER DEFAULT 0
        );
    """)

    # Leadlar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            status TEXT DEFAULT 'new',
            operator_id INTEGER,
            targetolog_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(operator_id) REFERENCES operators(id),
            FOREIGN KEY(targetolog_id) REFERENCES targetologlar(id)
        );
    """)

    # Savdolar (balansdan pul olish yoki tushgan pul)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            targetolog_id INTEGER,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(targetolog_id) REFERENCES targetologlar(id)
        );
    """)

    # Ro‘yxatdan o‘tgan foydalanuvchilar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            phone_number TEXT
        );
    """)

    conn.commit()
    conn.close()

# --- RUXSAT FUNKSIYALARI ---

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

# --- ADMIN PANEL UCHUN FUNKSIYALAR ---

def add_operator(name: str, telegram_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO operators (name, telegram_id) VALUES (?, ?)", (name, telegram_id))
    conn.commit()
    conn.close()

def add_targetolog(name: str, telegram_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO targetologlar (name, telegram_id) VALUES (?, ?)", (name, telegram_id))
    conn.commit()
    conn.close()

def get_all_operators():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, telegram_id FROM operators")
    result = cursor.fetchall()
    conn.close()
    return result

def get_all_targetologs():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, telegram_id FROM targetologlar")
    result = cursor.fetchall()
    conn.close()
    return result

def count_operators():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM operators")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def count_targetologs():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM targetologlar")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def count_leads():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    result = cursor.fetchone()[0]
    conn.close()
    return result

# --- TARGETOLOG PANEL UCHUN FUNKSIYALAR ---

def get_targetolog_id(telegram_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM targetologlar WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_targetolog_leads_by_status(targetolog_id: int, status: str):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, phone, address, status, created_at 
        FROM leads 
        WHERE targetolog_id = ? AND status = ?
        ORDER BY created_at DESC
    """, (targetolog_id, status))
    leads = cursor.fetchall()
    conn.close()
    return leads

def get_targetolog_balance(telegram_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT hold_balance, main_balance FROM operators WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, 0)

def request_withdrawal(targetolog_id: int, amount: float):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sales (targetolog_id, amount) VALUES (?, ?)", (targetolog_id, -abs(amount)))
    conn.commit()
    conn.close()

def count_leads_by_period(targetolog_id: int, period: str):
    conn = connect()
    cursor = conn.cursor()

    if period == "daily":
        cursor.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE targetolog_id = ? AND date(created_at) = date('now')
        """, (targetolog_id,))
    elif period == "weekly":
        cursor.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE targetolog_id = ? AND created_at >= date('now', '-7 days')
        """, (targetolog_id,))
    elif period == "monthly":
        cursor.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE targetolog_id = ? AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        """, (targetolog_id,))

    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0
