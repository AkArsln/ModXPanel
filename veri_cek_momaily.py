from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
#options.add_argument('--headless')  # GÖRÜNÜR YAP
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=options)
driver.get("https://momaily.de/AxAdmin/ad.php")

# Giriş yap
driver.find_element(By.NAME, "benutzer").send_keys("AkA-Kaan")
driver.find_element(By.NAME, "passwort").send_keys("df3f#f3a")
driver.find_element(By.NAME, "submit").click()
time.sleep(2)

print("✅ Giriş yapıldı, global liste sayfasına gidiliyor...")

# Global Liste
driver.get("https://momaily.de/AxAdmin/kickit_v3.php")
time.sleep(2)
soup = BeautifulSoup(driver.page_source, "html.parser")

table = soup.find("table")
if not table:
    print("❌ Tablo bulunamadı!")
else:
    print("✅ Tablo bulundu.")
    rows = table.find_all("tr")[1:]
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 3:
            print(f"Kullanıcı: {cells[1].text.strip()} | Mesaj: {cells[2].text.strip()}")

input("🛑 Kapatmak için Enter'a bas...")
driver.quit()
