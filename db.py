# db.py
import sqlite3

# ==== DB ulanish ====
def connect():
    return sqlite3.connect("data.db")


# ==== Dastlabki jadval yaratish ====
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
            telegram_id INTEGER UNIQUE,
            name TEXT,
            hold_balance REAL DEFAULT 0,
            main_balance REAL DEFAULT 0,
            is_blocked INTEGER DEFAULT 0
        );
    """)

    # Foydalanuvchilar jadvali (faqat telefon uchun)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            phone_number TEXT
        );
    """)

    # Mahsulotlar (offers)
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

    # Leadlar
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

    # Savdolar
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

    # Pul yechish so‘rovlari
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

# ==== Ruxsat tekshiruvlari ====
def is_operator(telegram_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM operators WHERE telegram_id = ? AND is_blocked = 0", (telegram_id,))
    return cursor.fetchone() is not None

def is_targetolog(telegram_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM targetologlar WHERE telegram_id = ? AND is_blocked = 0", (telegram_id,))
    return cursor.fetchone() is not None

def is_registered(telegram_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
    return cursor.fetchone() is not None

def register_user(telegram_id: int, phone_number: str):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (telegram_id, phone_number) VALUES (?, ?)", (telegram_id, phone_number))
    conn.commit()
    conn.close()

# ==== Lead ID generator ====
def generate_lead_uid(lead_id: int) -> str:
    return f"L{str(lead_id).zfill(5)}"

# ==== Admin panel funksiyalari ====
def add_operator(name, telegram_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO operators (name, telegram_id) VALUES (?, ?)", (name, telegram_id))
    conn.commit()
    conn.close()

def get_all_operators():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, telegram_id, is_blocked FROM operators")
    return cursor.fetchall()

def add_targetolog(name, telegram_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO targetologlar (name, telegram_id) VALUES (?, ?)", (name, telegram_id))
    conn.commit()
    conn.close()

def get_all_targetologs():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, telegram_id, is_blocked FROM targetologlar")
    return cursor.fetchall()

def count_operators():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM operators")
    return cursor.fetchone()[0]

def count_targetologs():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM targetologlar")
    return cursor.fetchone()[0]

def count_leads():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    return cursor.fetchone()[0]

# ==== Mahsulot funksiyalari ====
def add_product(title, description, video, price_operator, price_targetolog):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (title, description, video, price_operator, price_targetolog)
        VALUES (?, ?, ?, ?, ?)
    """, (title, description, video, price_operator, price_targetolog))
    conn.commit()
    conn.close()

def get_all_products():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, video, price_operator, price_targetolog, is_active FROM products")
    return cursor.fetchall()

def get_product_by_id(product_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    return cursor.fetchone()

def toggle_product_status(product_id, is_active):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET is_active = ? WHERE id = ?", (is_active, product_id))
    conn.commit()
    conn.close()

def get_active_products():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE is_active = 1")
    return cursor.fetchall()

# ==== Lead status yangilash ====
def update_lead_status_and_address(lead_uid, status, address=None):
    conn = connect()
    cursor = conn.cursor()
    if address:
        cursor.execute("UPDATE leads SET status = ?, address = ? WHERE lead_uid = ?", (status, address, lead_uid))
    else:
        cursor.execute("UPDATE leads SET status = ? WHERE lead_uid = ?", (status, lead_uid))
    conn.commit()
    conn.close()

# ==== Pul yechish holatini yangilash ====
def update_withdrawal_status(withdrawal_id, new_status):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE withdrawals SET status = ? WHERE id = ?", (new_status, withdrawal_id))
    conn.commit()
    conn.close()

# ==== Admin tekshiruvi ====
def is_admin(telegram_id: int) -> bool:
    return telegram_id in [1471552584]  # Adminlar ro'yxati shu yerda
