from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from datetime import date
import json

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'
DB_PATH = 'data.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('dashboard'))
        flash('Kullanıcı adı veya şifre yanlış.')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))

    username = session['username']
    selected_date = request.form.get('tarih') if request.method == 'POST' else date.today().isoformat()

    conn = get_db_connection()

    # Günlük ve toplam mesaj
    mesajlar = conn.execute('''
        SELECT * FROM messages
        WHERE username = ? AND tarih = ?
        ORDER BY project ASC
    ''', (username, selected_date)).fetchall()

    gunluk_toplam = conn.execute('''
        SELECT SUM(mesaj_sayisi) FROM messages
        WHERE username = ? AND tarih = ?
    ''', (username, selected_date)).fetchone()[0] or 0

    gunluk_kazanc = gunluk_toplam * 0.15

    tum_toplam = conn.execute('''
        SELECT SUM(mesaj_sayisi) FROM messages
        WHERE username = ?
    ''', (username,)).fetchone()[0] or 0

    # Grafik verileri (Momaily & Liebesfun)
    momaily_data = conn.execute('''
        SELECT tarih, SUM(mesaj_sayisi) as toplam FROM messages
        WHERE username = ? AND project = 'Momaily'
        GROUP BY tarih ORDER BY tarih ASC
    ''', (username,)).fetchall()

    liebes_data = conn.execute('''
        SELECT tarih, SUM(mesaj_sayisi) as toplam FROM messages
        WHERE username = ? AND project = 'Liebesfun'
        GROUP BY tarih ORDER BY tarih ASC
    ''', (username,)).fetchall()

    # Bugün herkesin toplam mesajı
    bugun = date.today().isoformat()
    toplu_mesajlar = conn.execute('''
        SELECT username, SUM(mesaj_sayisi) AS toplam
        FROM messages
        WHERE tarih = ?
        GROUP BY username
        ORDER BY toplam DESC
    ''', (bugun,)).fetchall()



    # Momaily mesajlı kullanıcılar
    try:
        with open("momaily_veri_gunluk.json", "r", encoding="utf-8") as f:
            momaily_json = json.load(f)
            momaily_mesaj_olanlar = momaily_json.get("mesaj_olanlar", [])
    except:
        momaily_mesaj_olanlar = []

    # Liebes mesajlı kullanıcılar
    try:
        with open("veri_gunluk.json", "r", encoding="utf-8") as f:
            liebes_json = json.load(f)
            liebes_mesaj_olanlar = liebes_json.get("mesaj_olanlar", [])
    except:
        liebes_mesaj_olanlar = []

    conn.close()

    return render_template('dashboard.html',
                           username=username,
                           mesajlar=mesajlar,
                           gunluk_toplam=gunluk_toplam,
                           tum_toplam=tum_toplam,
                           gunluk_kazanc=gunluk_kazanc,
                           selected_date=selected_date,
                           momaily_data=momaily_data,
                           liebes_data=liebes_data,
                           toplu_mesajlar=toplu_mesajlar,
                           momaily_mesaj_olanlar=momaily_mesaj_olanlar,
                           liebes_mesaj_olanlar=liebes_mesaj_olanlar)


@app.route('/admin/maaslar')
def admin_maaslar():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    maaslar = conn.execute('''
        SELECT * FROM salary_periods
        ORDER BY kapatma_tarihi DESC
    ''').fetchall()
    conn.close()

    return render_template('admin_maaslar.html', maaslar=maaslar)

import json

@app.route('/momaily/liste')
def momaily_liste():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        with open("momaily_veri_gunluk.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            global_liste = data["top10"]["bugun"]
            ajans_liste = data["ajanslar"]
    except Exception as e:
        print(f"Hata: {e}")
        global_liste = []
        ajans_liste = []

    return render_template("proje_liste.html",
                           proje="Momaily",
                           global_liste=global_liste,
                           ajans_liste=ajans_liste)




@app.route('/liebes/liste')
def liebes_liste():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        with open("veri_gunluk.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            global_liste = data["top10"]["bugun"]
            ajans_liste = data["ajanslar"]
    except Exception as e:
        print(f"Hata: {e}")
        global_liste = []
        ajans_liste = []

    return render_template("proje_liste.html",
                           proje="Liebesfun",
                           global_liste=global_liste,
                           ajans_liste=ajans_liste)




@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Toplam kullanıcı
    toplam_kullanici = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]

    # Toplam mesaj
    toplam_mesaj = conn.execute('SELECT SUM(mesaj_sayisi) FROM messages').fetchone()[0] or 0

    # Toplam kazanç
    toplam_kazanc = toplam_mesaj * 0.15

    # En çok mesaj atan kullanıcı
    top_user = conn.execute('''
        SELECT username, SUM(mesaj_sayisi) as toplam FROM messages
        GROUP BY username ORDER BY toplam DESC LIMIT 1
    ''').fetchone()

    # Günlük mesaj grafiği
    gunluk_veriler = conn.execute('''
        SELECT tarih, SUM(mesaj_sayisi) as toplam FROM messages
        GROUP BY tarih ORDER BY tarih ASC
    ''').fetchall()

    conn.close()

    return render_template('admin_dashboard.html',
                           toplam_kullanici=toplam_kullanici,
                           toplam_mesaj=toplam_mesaj,
                           toplam_kazanc=toplam_kazanc,
                           top_user=top_user,
                           gunluk_veriler=gunluk_veriler)


@app.route('/admin/kullanicilar', methods=['GET', 'POST'])
def admin_kullanicilar():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'ekle':
            username = request.form['username']
            password = request.form['password']
            is_admin = 1 if request.form.get('is_admin') == 'on' else 0
            conn.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                         (username, password, is_admin))
            conn.commit()

        elif action == 'sil':
            user_id = request.form['user_id']
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()

        elif action == 'sifre_degistir':
            user_id = request.form['user_id']
            yeni_sifre = request.form['yeni_sifre']
            conn.execute('UPDATE users SET password = ? WHERE id = ?', (yeni_sifre, user_id))
            conn.commit()

    kullanicilar = conn.execute('SELECT * FROM users ORDER BY id ASC').fetchall()
    conn.close()
    return render_template('admin_kullanicilar.html', kullanicilar=kullanicilar)



@app.route('/announcements', methods=['GET', 'POST'])
def announcements():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # En son duyuruyu al
    announcement = conn.execute('SELECT * FROM announcements ORDER BY created_at DESC LIMIT 1').fetchone()

    # Kullanıcı bu duyuruyu daha önce okudu mu?
    already_read = False
    if announcement:
        read_check = conn.execute('SELECT * FROM announcement_reads WHERE username = ? AND announcement_id = ?',
                                  (session['username'], announcement['id'])).fetchone()
        if read_check:
            already_read = True

    # Duyuru okundu butonuna basıldıysa:
    if request.method == 'POST' and announcement and not already_read:
        conn.execute('INSERT INTO announcement_reads (username, announcement_id) VALUES (?, ?)',
                     (session['username'], announcement['id']))
        conn.commit()
        already_read = True

    conn.close()
    return render_template('announcements.html', announcement=announcement, already_read=already_read)



@app.route('/admin/duyurular', methods=['GET', 'POST'])
def admin_duyurular():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute('INSERT INTO announcements (title, content, created_at) VALUES (?, ?, ?)',
                     (title, content, now))
        conn.commit()

    if request.args.get('sil'):
        duyuru_id = request.args.get('sil')
        conn.execute('DELETE FROM announcements WHERE id = ?', (duyuru_id,))
        conn.execute('DELETE FROM announcement_reads WHERE announcement_id = ?', (duyuru_id,))
        conn.commit()

    duyurular = conn.execute('SELECT * FROM announcements ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_duyurular.html', duyurular=duyurular)

@app.route('/mesaj-girisi', methods=['GET', 'POST'])
def mesaj_girisi():
    if 'username' not in session:
        return redirect(url_for('login'))

    today = date.today().isoformat()
    message = ""

    if request.method == 'POST':
        tarih = request.form.get('tarih') or today
        proje = request.form['proje']
        sayi = int(request.form['mesaj_sayisi'])

        conn = get_db_connection()
        conn.execute('INSERT INTO messages (username, project, tarih, mesaj_sayisi) VALUES (?, ?, ?, ?)',
                     (session['username'], proje, tarih, sayi))
        conn.commit()
        conn.close()
        message = "✅ Mesaj başarıyla eklendi!"

    return render_template('mesaj_girisi.html', today=today, message=message)

@app.route('/maas-kapatma', methods=['GET', 'POST'])
def maas_kapatma():
    if 'username' not in session:
        return redirect(url_for('login'))

    result = None
    if request.method == 'POST':
        baslangic = request.form['baslangic']
        bitis = request.form['bitis']
        username = session['username']

        conn = get_db_connection()
        toplam_mesaj = conn.execute('''
            SELECT SUM(mesaj_sayisi) FROM messages
            WHERE username = ? AND tarih BETWEEN ? AND ?
        ''', (username, baslangic, bitis)).fetchone()[0]

        toplam_mesaj = toplam_mesaj or 0
        kazanc = toplam_mesaj * 0.15
        kapatma_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn.execute('''
            INSERT INTO salary_periods (username, baslangic, bitis, toplam_mesaj, kazanc, kapatma_tarihi)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, baslangic, bitis, toplam_mesaj, kazanc, kapatma_tarihi))
        conn.commit()
        conn.close()

        result = {"mesaj": toplam_mesaj, "kazanc": kazanc}

    return render_template('maas_kapatma.html', result=result)

@app.route('/maas-gecmisi')
def maas_gecmisi():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    maaslar = conn.execute('''
        SELECT * FROM salary_periods
        WHERE username = ?
        ORDER BY kapatma_tarihi DESC
    ''', (session['username'],)).fetchall()
    conn.close()

    return render_template('maas_gecmisi.html', maaslar=maaslar)

@app.route('/chat', methods=['GET', 'POST'])
def kullanici_chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    username = session['username']

    if request.method == 'POST':
        mesaj = request.form['mesaj']
        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute('INSERT INTO admin_messages (gonderen, alici, mesaj, zaman) VALUES (?, ?, ?, ?)',
                     (username, 'admin', mesaj, zaman))
        conn.commit()

    sohbet = conn.execute('''
        SELECT * FROM admin_messages
        WHERE gonderen = ? OR (alici = ? AND gonderen = 'admin')
        ORDER BY zaman ASC
    ''', (username, username)).fetchall()

    conn.close()
    return render_template('chat.html', sohbet=sohbet)

@app.route('/admin/chat')
def admin_chat():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    sohbetler = conn.execute('''
        SELECT * FROM admin_messages ORDER BY zaman DESC
    ''').fetchall()
    conn.close()

    return render_template('admin_chat.html', sohbetler=sohbetler)




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
