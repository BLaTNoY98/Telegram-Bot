import sqlite3

def connect():
    return sqlite3.connect("data.db")

def init_db(# leads jadvali
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

    # operatorlarga balans maydonlarini qo‘shamiz (agar hali yo‘q bo‘lsa)
    cursor.execute("ALTER TABLE operators ADD COLUMN hold_balance REAL DEFAULT 0")  # bu xatolik bermasligi uchun try/except bilan yozamiz quyida
    cursor.execute("ALTER TABLE operators ADD COLUMN main_balance REAL DEFAULT 0")):
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
def is_operator(telegram_id: int) -> bool:
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM operators WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
    conn.commit()
    conn.close()
