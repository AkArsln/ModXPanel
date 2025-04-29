import sqlite3
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS salary_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    baslangic TEXT NOT NULL,
    bitis TEXT NOT NULL,
    toplam_mesaj INTEGER NOT NULL,
    kazanc REAL NOT NULL,
    kapatma_tarihi TEXT NOT NULL
)
''')

conn.commit()
conn.close()
