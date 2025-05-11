import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'bot.db'

def connect():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            full_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            full_name TEXT,
            phone_number TEXT,
            hold_balance INTEGER DEFAULT 0,
            main_balance INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targetologlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            full_name TEXT,
            phone_number TEXT,
            unique_id TEXT UNIQUE,
            hold_balance INTEGER DEFAULT 0,
            main_balance INTEGER DEFAULT 0,
            blocked INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            video TEXT,
            price_for_operator INTEGER,
            price_for_targetolog INTEGER,
            is_active INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_uid TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            address TEXT,
            operator_id INTEGER,
            targetolog_id INTEGER,
            product_id INTEGER,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (operator_id) REFERENCES operators (id),
            FOREIGN KEY (targetolog_id) REFERENCES targetologlar (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            targetolog_id INTEGER,
            amount INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (targetolog_id) REFERENCES targetologlar (id)
        )
    ''')

    conn.commit()
    conn.close()

# Lead UID Generator
def generate_lead_uid(lead_id):
    return f"L{str(lead_id).zfill(5)}"

# Lead Insert with UID
def insert_lead(name, phone, address, operator_id, targetolog_id, product_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads (name, phone, address, operator_id, targetolog_id, product_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, address, operator_id, targetolog_id, product_id))

    lead_id = cursor.lastrowid
    lead_uid = generate_lead_uid(lead_id)

    cursor.execute("UPDATE leads SET lead_uid = ? WHERE id = ?", (lead_uid, lead_id))

    conn.commit()
    conn.close()
    return lead_uid

# Operator Balance Update
def update_operator_balance(operator_id, hold_delta=0, main_delta=0):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE operators
        SET hold_balance = hold_balance + ?, main_balance = main_balance + ?
        WHERE id = ?
    """, (hold_delta, main_delta, operator_id))
    conn.commit()
    conn.close()

# Targetolog Balance Update
def update_targetolog_balance(targetolog_id, hold_delta=0, main_delta=0):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE targetologlar
        SET hold_balance = hold_balance + ?, main_balance = main_balance + ?
        WHERE id = ?
    """, (hold_delta, main_delta, targetolog_id))
    conn.commit()
    conn.close()

# Lead Count By Period
def count_leads_by_targetolog(targetolog_id, period='day'):
    conn = connect()
    cursor = conn.cursor()

    now = datetime.now()
    if period == 'day':
        since = now - timedelta(days=1)
    elif period == 'week':
        since = now - timedelta(weeks=1)
    elif period == 'month':
        since = now - timedelta(days=30)
    else:
        since = datetime.min

    cursor.execute("""
        SELECT COUNT(*) FROM leads
        WHERE targetolog_id = ? AND created_at >= ?
    """, (targetolog_id, since))

    result = cursor.fetchone()[0]
    conn.close()
    return result

# Lead Status Update
def update_lead_status(lead_uid, status):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE leads SET status = ? WHERE lead_uid = ?
    """, (status, lead_uid))
    conn.commit()
    conn.close()

# Get Product Info
def get_product(product_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

# Get Operator by tg_id
def get_operator_by_tg_id(tg_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operators WHERE tg_id = ?", (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Get Targetolog by tg_id
def get_targetolog_by_tg_id(tg_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targetologlar WHERE tg_id = ?", (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Check Admin
def is_admin(tg_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE tg_id = ?", (tg_id,))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None
