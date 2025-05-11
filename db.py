import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            phone_number TEXT,
            role TEXT,
            unique_code TEXT,
            is_blocked INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            address TEXT,
            status TEXT,
            operator_id INTEGER,
            targetolog_id INTEGER,
            product_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balances (
            user_id INTEGER PRIMARY KEY,
            hold_balance REAL DEFAULT 0,
            main_balance REAL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            status TEXT DEFAULT 'pending',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            video TEXT,
            price_operator REAL,
            price_targetolog REAL,
            is_active INTEGER DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY
        )
    """)

    conn.commit()

def add_user(user_id, full_name, phone, role, unique_code):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, full_name, phone_number, role, unique_code) VALUES (?, ?, ?, ?, ?)",
                   (user_id, full_name, phone, role, unique_code))
    cursor.execute("INSERT OR IGNORE INTO balances (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def is_registered(user_id):
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def block_user(user_id):
    cursor.execute("UPDATE users SET is_blocked = 1 WHERE user_id = ?", (user_id,))
    conn.commit()

def unblock_user(user_id):
    cursor.execute("UPDATE users SET is_blocked = 0 WHERE user_id = ?", (user_id,))
    conn.commit()

def add_admin(user_id):
    cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_admins():
    cursor.execute("SELECT user_id FROM admins")
    return [row[0] for row in cursor.fetchall()]

def get_all_operators():
    cursor.execute("SELECT * FROM users WHERE role = 'operator'")
    return cursor.fetchall()

def get_all_targetologs():
    cursor.execute("SELECT * FROM users WHERE role = 'targetolog'")
    return cursor.fetchall()

def create_lead(lead_id, name, phone, address, targetolog_id, product_id):
    cursor.execute("""
        INSERT INTO leads (lead_id, name, phone, address, status, targetolog_id, product_id)
        VALUES (?, ?, ?, ?, 'new', ?, ?)
    """, (lead_id, name, phone, address, targetolog_id, product_id))
    conn.commit()

def get_leads_by_status(user_id, role, status):
    if role == 'operator':
        cursor.execute("SELECT * FROM leads WHERE operator_id = ? AND status = ?", (user_id, status))
    elif role == 'targetolog':
        cursor.execute("SELECT * FROM leads WHERE targetolog_id = ? AND status = ?", (user_id, status))
    return cursor.fetchall()

def update_lead_status(lead_id, status, operator_id=None):
    if operator_id:
        cursor.execute("UPDATE leads SET status = ?, operator_id = ? WHERE lead_id = ?", (status, operator_id, lead_id))
    else:
        cursor.execute("UPDATE leads SET status = ? WHERE lead_id = ?", (status, lead_id))
    conn.commit()

def update_lead_address(lead_id, address):
    cursor.execute("UPDATE leads SET address = ? WHERE lead_id = ?", (address, lead_id))
    conn.commit()

def get_next_lead_id():
    cursor.execute("SELECT COUNT(*) FROM leads")
    count = cursor.fetchone()[0] + 1
    return f"L{count:05d}"

def get_balance(user_id):
    cursor.execute("SELECT hold_balance, main_balance FROM balances WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def update_hold_balance(user_id, amount):
    cursor.execute("UPDATE balances SET hold_balance = hold_balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

def move_hold_to_main(user_id, amount):
    cursor.execute("""
        UPDATE balances
        SET hold_balance = hold_balance - ?, main_balance = main_balance + ?
        WHERE user_id = ?
    """, (amount, amount, user_id))
    conn.commit()

def add_withdraw_request(user_id, amount):
    cursor.execute("INSERT INTO withdrawals (user_id, amount) VALUES (?, ?)", (user_id, amount))
    conn.commit()

def get_withdrawals(user_id=None):
    if user_id:
        cursor.execute("SELECT * FROM withdrawals WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT * FROM withdrawals")
    return cursor.fetchall()
def block_operator(user_id):
    cursor.execute("UPDATE users SET is_blocked = 1 WHERE user_id = ? AND role = 'operator'", (user_id,))
    conn.commit()

def unblock_operator(user_id):
    cursor.execute("UPDATE users SET is_blocked = 0 WHERE user_id = ? AND role = 'operator'", (user_id,))
    conn.commit()

def unblock_targetolog(user_id):
    cursor.execute("UPDATE users SET is_blocked = 0 WHERE user_id = ? AND role = 'targetolog'", (user_id,))
    conn.commit()

def block_targetolog(user_id):
    cursor.execute("UPDATE users SET is_blocked = 1 WHERE user_id = ? AND role = 'targetolog'", (user_id,))
    conn.commit()

def update_withdraw_status(withdraw_id, status):
    cursor.execute("UPDATE withdrawals SET status = ? WHERE id = ?", (status, withdraw_id))
    conn.commit()
    
    def update_withdraw_status(withdraw_id, status):
    cursor.execute("UPDATE withdrawals SET status = ? WHERE id = ?", (status, withdraw_id))
    conn.commit()

def get_statistics():
    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'operator'")
    total_operators = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'targetolog'")
    total_targetologs = cursor.fetchone()[0]

    return {
        "total_leads": total_leads,
        "total_operators": total_operators,
        "total_targetologs": total_targetologs
    }
    

def add_product(title, description, video, price_operator, price_targetolog):
    cursor.execute("""
        INSERT INTO products (title, description, video, price_operator, price_targetolog)
        VALUES (?, ?, ?, ?, ?)
    """, (title, description, video, price_operator, price_targetolog))
    conn.commit()

def get_all_products(active_only=True):
    if active_only:
        cursor.execute("SELECT * FROM products WHERE is_active = 1")
    else:
        cursor.execute("SELECT * FROM products")
    return cursor.fetchall()

def get_product(product_id):
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    return cursor.fetchone()

def update_product(product_id, title, description, video, price_operator, price_targetolog, is_active):
    cursor.execute("""
        UPDATE products
        SET title = ?, description = ?, video = ?, price_operator = ?, price_targetolog = ?, is_active = ?
        WHERE id = ?
    """, (title, description, video, price_operator, price_targetolog, is_active, product_id))
    conn.commit()
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            name TEXT,
            phone TEXT,
            role TEXT,
            is_blocked INTEGER DEFAULT 0
        )
        """)
        conn.commit()
        init_db()
