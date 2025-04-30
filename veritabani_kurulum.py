import sqlite3

conn = sqlite3.connect("data.db")
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        project TEXT NOT NULL,
        tarih TEXT NOT NULL,
        mesaj_sayisi INTEGER NOT NULL
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS salary_periods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        baslangic TEXT,
        bitis TEXT,
        toplam_mesaj INTEGER,
        kazanc REAL,
        kapatma_tarihi TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        created_at TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS announcement_reads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        announcement_id INTEGER
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS admin_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gonderen TEXT,
        alici TEXT,
        mesaj TEXT,
        zaman TEXT
    )
''')

# Varsayılan admin kullanıcı (username: admin / password: admin)
c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ("admin", "admin", 1))

conn.commit()
conn.close()
