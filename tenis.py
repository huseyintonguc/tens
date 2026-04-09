import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. KULLANICI BİLGİLERİ VE AYARLAR ---
def tr_upper(text):
    """İsimleri Türkçe kurallarına göre BÜYÜK HARFE çevirir."""
    return text.replace('i', 'İ').replace('ı', 'I').upper()

# 4 KİŞİNİN BİLGİLERİNİ BURAYA YAZIN
GRUP = [
    {"tc": "53272681026", "ad": tr_upper("HÜSEYİN TONGUÇ"), "tel": "5532285951"}, # 1. Rezervasyon Asıl
    {"tc": "48394037974", "ad": tr_upper("PINAR TONGUÇ"), "tel": "5461403467"}, # 1. Rezervasyon Partner
    {"tc": "33333333330", "ad": tr_upper("Ayşe Kaya"), "tel": "5XXXXXXXXX"},    # 2. Rezervasyon Asıl
    {"tc": "44444444440", "ad": tr_upper("Fatma Çelik"), "tel": "5XXXXXXXXX"}   # 2. Rezervasyon Partner
]

# Takip edilecek saatler (Test için 08:00'i ekleyebilirsiniz)
HEDEF_SAATLER = ["08:00"] 

# --- 2. TARAYICI AYARLARI ---
chrome_options = Options()
# reCAPTCHA'da sorun yaşıyorsanız aşağıdaki satırın başındaki '#' işaretini kaldırıp 
# kendi profil yolunuzu ekleyebilirsiniz.
# chrome_options.add_argument(f"user-data-dir=C:\\Users\\KULLANICI_ADINIZ\\AppData\\Local\\Google\\Chrome\\User Data")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
alinanlar = []

def pusu_modu():
    print(f"{'='*30}\nBOT BASLATILDI\nHEDEF: {HEDEF_SAATLER}\n{'='*30}")
    
    while len(alinanlar) < 2:
        try:
            driver.get("https://kultursanat.silivri.bel.tr/tenis-kortu")
            time.sleep(3) # Sayfanın yüklenmesini bekle

            # Hangi grubu kullanacağız? (İlk rezervasyon için 0-1, ikinci için 2-3)
            idx = 0 if len(alinanlar) == 0 else 2
            asıl = GRUP[idx]
            partner = GRUP[idx+1]

            # SAAT SEÇİMİ
            try:
                # Sayfadaki saat dropdown'ını bul
                select_element = driver.find_element(By.TAG_NAME, "select")
                saat_listesi = Select(select_element)
                
                hedef_bulundu = False
                for hedef in HEDEF_SAATLER:
                    if hedef in alinanlar: continue
                    
                    for option in saat_listesi.options:
                        # Saati ve DOLU olmadığını kontrol et
                        if hedef in option.text and "(DOLU)" not in option.text:
                            saat_listesi.select_by_visible_text(option.text)
                            print(f"Buldum! {option.text} seçiliyor...")
                            hedef_bulundu = True
                            secilen_saat = hedef
                            break
                    if hedef_bulundu: break
                
                if not hedef_bulundu:
                    print(f"Henüz boşluk yok... ({time.strftime('%H:%M:%S')})")
                    time.sleep(25) # 25 saniye bekle ve yenile
                    driver.refresh()
                    continue

                # FORM DOLDURMA (Görseldeki ID'lere göre)
                # 1. Kişi (Asıl)
                driver.find_element(By.ID, "tc1").clear()
                driver.find_element(By.ID, "tc1").send_keys(asıl["tc"])
                driver.find_element(By.ID, "name1").clear()
                driver.find_element(By.ID, "name1").send_keys(asıl["ad"])
                
                # Telefon (tel1 veya input type=tel üzerinden)
                try:
                    driver.find_element(By.ID, "tel1").send_keys(asıl["tel"])
                except:
                    driver.find_element(By.XPATH, "//input[@type='tel']").send_keys(asıl["tel"])

                # 2. Kişi (Partner)
                driver.find_element(By.ID, "tc2").send_keys(partner["tc"])
                driver.find_element(By.ID, "name2").send_keys(partner["ad"])

                print("Form dolduruldu. reCAPTCHA bekleniyor...")

                # reCAPTCHA TIKLAMA
                # reCAPTCHA genelde bir iframe içindedir
                time.sleep(1)
                frames = driver.find_elements(By.TAG_NAME, "iframe")
                driver.switch_to.frame(frames[0])
                driver.find_element(By.ID, "recaptcha-anchor").click()
                
                print("Lütfen reCAPTCHA'nın yeşil tik olmasını bekleyin (veya gerekirse manuel çözün)")
                time.sleep(4) # Yeşil tik için bekleme süresi
                
                driver.switch_to.default_content()

                # ONAY BUTONU (Metin üzerinden bulma)
                onay_butonu = driver.find_element(By.XPATH, "//*[contains(text(), 'Randevunuzu Onaylayın')]")
                onay_butonu.click()
                
                print(f"BAŞARILI! {secilen_saat} için rezervasyon yapıldı.")
                alinanlar.append(secilen_saat)
                
                if len(alinanlar) < 2:
                    print("İkinci saat için 10 saniye sonra tekrar başlanıyor...")
                    time.sleep(10)
                
            except Exception as sub_e:
                print(f"İşlem sırasında hata: {sub_e}")
                time.sleep(5)

        except Exception as e:
            print(f"Ana döngüde bir hata oluştu: {e}")
            time.sleep(5)

if __name__ == "__main__":
    pusu_modu()
