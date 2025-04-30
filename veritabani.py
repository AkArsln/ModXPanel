import sqlite3

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

def tablo_olustur():
    conn = get_db_connection()
    c = conn.cursor()

    # users tablosu
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
    ''')

    # messages tablosu
    c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        project TEXT,
        tarih TEXT,
        mesaj_sayisi INTEGER
    )
    ''')

    # salary_periods tablosu
    c.execute('''
    CREATE TABLE IF NOT EXISTS salary_periods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        baslangic TEXT,
        bitis TEXT,
        toplam_mesaj INTEGER,
        kazanc REAL,
        kapatma_tarihi TEXT
    )
    ''')

    # admin_messages tablosu
    c.execute('''
    CREATE TABLE IF NOT EXISTS admin_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gonderen TEXT,
        alici TEXT,
        mesaj TEXT,
        zaman TEXT
    )
    ''')

    # announcements tablosu
    c.execute('''
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        created_at TEXT
    )
    ''')

    # announcement_reads tablosu
    c.execute('''
    CREATE TABLE IF NOT EXISTS announcement_reads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        announcement_id INTEGER
    )
    ''')

    # Test admin eklemesi (sadece bir kere çalışır çünkü UNIQUE username)
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, is_admin)
    VALUES (?, ?, ?)
    ''', ("admin", "admin123", 1))

    conn.commit()
    conn.close()
