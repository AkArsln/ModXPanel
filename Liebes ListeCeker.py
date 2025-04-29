from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


def giris_yap():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.get("https://liebesfun.de/A_center/ad.php")

    # Doğru XPath'lerle giriş bilgilerini doldur
    driver.find_element(By.XPATH, '//*[@id="f1"]/form/table/tbody/tr[1]/td[2]/input').send_keys("AkA-Kaan")
    driver.find_element(By.XPATH, '//*[@id="f1"]/form/table/tbody/tr[2]/td[2]/input').send_keys("dsvcds#xw2")
    driver.find_element(By.XPATH, '//*[@id="f1"]/form/table/tbody/tr[3]/td/input').click()

    print("✅ Giriş başarılı:", driver.current_url)
    return driver


def kickit_liste_cek(driver):
    driver.get("https://liebesfun.de/A_center/kickit_v3.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

    top_listesi = {"evvelsi_gun": [], "dun": [], "bugun": []}

    # Tabloların XPath'leri
    xpath_evvelsi = "/html/body/center/div[4]/center/table[1]/tbody/tr/td[1]/div/table"
    xpath_dun = "/html/body/center/div[4]/center/table[1]/tbody/tr/td[2]/div/table"
    xpath_bugun = "/html/body/center/div[4]/center/table[1]/tbody/tr/td[3]/div/table"

    def tabloyu_ayikla(xpath):
        tablo = driver.find_element(By.XPATH, xpath)
        satirlar = tablo.find_elements(By.XPATH, ".//tr")[1:]  # başlığı atla
        liste = []
        for satir in satirlar:
            kolonlar = satir.find_elements(By.TAG_NAME, "td")
            if len(kolonlar) >= 2:
                # Kullanıcı adı ve coin sayısı ikinci kolonda
                try:
                    isim = kolonlar[1].find_element(By.XPATH, ".//span[1]").text.strip()
                    coins = kolonlar[1].find_elements(By.XPATH, ".//span")[-1].text.strip()
                    liste.append({"isim": isim, "coins": coins})
                except:
                    continue
        return liste

    top_listesi["evvelsi_gun"] = tabloyu_ayikla(xpath_evvelsi)
    top_listesi["dun"] = tabloyu_ayikla(xpath_dun)
    top_listesi["bugun"] = tabloyu_ayikla(xpath_bugun)

    print("✅ Global Top 10 listesi çekildi.")
    print(json.dumps(top_listesi, indent=2, ensure_ascii=False))
    return top_listesi

def ajans_calisanlari_cek(driver):
    url = "https://liebesfun.de/A_center/agenturumsatz_v3.php"
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/center/div[4]/center/table")))

    tablo = driver.find_element(By.XPATH, "/html/body/center/div[4]/center/table")
    satirlar = tablo.find_elements(By.XPATH, ".//tr")

    calisanlar = []

    for i, satir in enumerate(satirlar[1:], start=2):  # başlık satırını atla
        hucreler = satir.find_elements(By.TAG_NAME, "td")

        # Toplam satırları ("gesamt") atla ve eksik verileri atla
        if len(hucreler) < 8:
            continue

        nick = hucreler[0].text.strip()
        coins_ges = hucreler[7].text.strip()

        # Coins değeri sayıya çevrilebilir mi kontrol et
        try:
            coins_ges = int(coins_ges.replace(".", "").replace(",", "").replace(" ", "").strip())
        except ValueError:
            coins_ges = 0

        calisanlar.append({
            "nick": nick,
            "coins_ges": coins_ges
        })

    # Coins'e göre azalan sırala
    calisanlar_sirali = sorted(calisanlar, key=lambda x: x["coins_ges"], reverse=True)

    print("✅ Çalışanlar başarıyla çekildi ve sıralandı.")
    return calisanlar_sirali



def verileri_kaydet(top10, ajanslar):
    veri = {
        "top10": top10,
        "ajanslar": ajanslar,
        "tarih": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("veri_gunluk.json", "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)
    print("✅ Veriler JSON olarak kaydedildi.")


def mesaj_olanlari_cek(driver):
    driver.get("https://liebesfun.de/A_center/agentenmanagment.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/center/div[4]/center/table[2]")))

    tablo = driver.find_element(By.XPATH, "/html/body/center/div[4]/center/table[2]")
    satirlar = tablo.find_elements(By.TAG_NAME, "tr")[1:]

    mesaj_olanlar = []

    for satir in satirlar:
        hucreler = satir.find_elements(By.TAG_NAME, "td")
        if len(hucreler) >= 22:
            nick = hucreler[0].text.strip()
            open_mesaj = hucreler[21].text.strip()
            try:
                open_mesaj_sayi = int(open_mesaj)
            except ValueError:
                continue
            if open_mesaj_sayi > 0:
                mesaj_olanlar.append({"nick": nick, "mesaj": open_mesaj_sayi})

    print("✅ Açık mesajı olanlar çekildi:")
    print(json.dumps(mesaj_olanlar, indent=2, ensure_ascii=False))
    return mesaj_olanlar

def verileri_kaydet(top10, ajanslar, mesaj_olanlar):
    veri = {
        "top10": top10,
        "ajanslar": ajanslar,
        "mesaj_olanlar": mesaj_olanlar,
        "tarih": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("veri_gunluk.json", "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)
    print("✅ Liebesfun verileri JSON olarak kaydedildi.")


if __name__ == "__main__":
    driver = giris_yap()

    try:
        while True:
            print("🔄 Veri çekiliyor...")

            top10 = kickit_liste_cek(driver)
            ajanslar = ajans_calisanlari_cek(driver)
            mesaj_olanlar = mesaj_olanlari_cek(driver)

            verileri_kaydet(top10, ajanslar, mesaj_olanlar)

            print("⏱ 100 saniye sonra tekrar denenecek...\n")
            time.sleep(100)  # Bekle

            try:
                driver.title  # Bu satır tarayıcının hala açık olup olmadığını anlamamıza yarıyor.
            except:
                print("🛠 Tarayıcı kapandı, yeniden başlatılıyor...")
                driver = giris_yap()

    except KeyboardInterrupt:
        print("⛔ Bot manuel olarak durduruldu.")

    finally:
        driver.quit()
