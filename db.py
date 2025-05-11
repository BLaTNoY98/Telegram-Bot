import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'bot.db'

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    create_tables()

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
        CREATE TABLE IF NOT EXISTS targetologs (
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
            video_url TEXT,
            price_operator INTEGER,
            price_targetolog INTEGER,
            is_enabled INTEGER DEFAULT 1
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
            FOREIGN KEY (targetolog_id) REFERENCES targetologs (id),
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
            FOREIGN KEY (targetolog_id) REFERENCES targetologs (id)
        )
    ''')

    conn.commit()
    conn.close()

def generate_lead_uid(lead_id):
    return f"L{str(lead_id).zfill(5)}"

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

def update_targetolog_balance(targetolog_id, hold_delta=0, main_delta=0):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE targetologs
        SET hold_balance = hold_balance + ?, main_balance = main_balance + ?
        WHERE id = ?
    """, (hold_delta, main_delta, targetolog_id))
    conn.commit()
    conn.close()

def update_lead_status(lead_uid, status):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE leads SET status = ? WHERE lead_uid = ?
    """, (status, lead_uid))
    conn.commit()
    conn.close()

def get_product(product_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def get_operator_by_tg_id(tg_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operators WHERE tg_id = ?", (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_operator_by_id(id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operators WHERE id = ?", (id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_targetolog_by_id(id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targetologs WHERE id = ?", (id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_targetolog_by_tg_id(tg_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM targetologs WHERE tg_id = ?", (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_operators():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, tg_id, blocked FROM operators")
    result = cursor.fetchall()
    conn.close()
    return result

def get_all_targetologs():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, tg_id, blocked FROM targetologs")
    result = cursor.fetchall()
    conn.close()
    return result

def is_admin(tg_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE tg_id = ?", (tg_id,))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None

def block_operator(operator_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE operators SET blocked = 1 WHERE id = ?", (operator_id,))
    conn.commit()
    conn.close()

def unblock_operator(operator_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE operators SET blocked = 0 WHERE id = ?", (operator_id,))
    conn.commit()
    conn.close()

def block_targetolog(targetolog_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE targetologs SET blocked = 1 WHERE id = ?", (targetolog_id,))
    conn.commit()
    conn.close()

def unblock_targetolog(targetolog_id: int):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE targetologs SET blocked = 0 WHERE id = ?", (targetolog_id,))
    conn.commit()
    conn.close()

def get_all_products():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, video_url, price_targetolog, price_operator, is_enabled FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_statistics():
    conn = connect()
    cursor = conn.cursor()

    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
    month_start = today.replace(day=1).strftime('%Y-%m-%d')

    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_at) = ?", (today_str,))
    today_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_at) >= ?", (week_start,))
    weekly_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE DATE(created_at) >= ?", (month_start,))
    monthly_leads = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total_leads,
        "today": today_leads,
        "week": weekly_leads,
        "month": monthly_leads
    }
def is_registered(tg_id):
    conn = connect()
    cursor = conn.cursor()

    # Check in operators
    cursor.execute("SELECT 1 FROM operators WHERE tg_id = ?", (tg_id,))
    if cursor.fetchone():
        conn.close()
        return True

    # Check in targetologs
    cursor.execute("SELECT 1 FROM targetologs WHERE tg_id = ?", (tg_id,))
    if cursor.fetchone():
        conn.close()
        return True

    conn.close()
    return False

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

def add_admin(tg_id, full_name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO admins (tg_id, full_name) VALUES (?, ?)", (tg_id, full_name))
    conn.commit()
    conn.close()

def add_operator(tg_id, full_name, phone_number):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO operators (tg_id, full_name, phone_number)
        VALUES (?, ?, ?)
    """, (tg_id, full_name, phone_number))
    conn.commit()
    conn.close()

def add_targetolog(tg_id, full_name, phone_number, unique_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO targetologs (tg_id, full_name, phone_number, unique_id)
        VALUES (?, ?, ?, ?)
    """, (tg_id, full_name, phone_number, unique_id))
    conn.commit()
    conn.close()

def get_lead_by_uid(lead_uid):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE lead_uid = ?", (lead_uid,))
    lead = cursor.fetchone()
    conn.close()
    return lead

def insert_product(title, description, video_url, price_operator, price_targetolog):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (title, description, video_url, price_operator, price_targetolog)
        VALUES (?, ?, ?, ?, ?)
    """, (title, description, video_url, price_operator, price_targetolog))
    conn.commit()
    conn.close()

def update_product(product_id, title, description, video_url, price_operator, price_targetolog):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products SET title = ?, description = ?, video_url = ?, price_operator = ?, price_targetolog = ?
        WHERE id = ?
    """, (title, description, video_url, price_operator, price_targetolog, product_id))
    conn.commit()
    conn.close()

def set_product_enabled(product_id, enabled: bool):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET is_enabled = ? WHERE id = ?", (int(enabled), product_id))
    conn.commit()
    conn.close()
