import sqlite3

def connect():
    return sqlite3.connect("data.db")

def init_db():
    conn = connect()
    cursor = conn.cursor()

    # operators jadvalini yaratish
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            name TEXT
        );
    """)

    # targetologlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS targetologlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            telegram_id INTEGER UNIQUE
        );
    """)

    # sales jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            targetolog_id INTEGER,
            amount REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # leads jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            status TEXT DEFAULT 'new',
            operator_id INTEGER,
            FOREIGN KEY(operator_id) REFERENCES operators(id)
        );
    """)

    # Balans ustunlarini qo‘shishga urinish
    try:
        cursor.execute("ALTER TABLE operators ADD COLUMN hold_balance REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE operators ADD COLUMN main_balance REAL DEFAULT 0")
    except:
        pass

    conn.commit()
    conn.close()

def is_operator(telegram_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM operators WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
