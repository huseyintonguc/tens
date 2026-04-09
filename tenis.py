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
ASIL_KISI = {"tc": "53272681026", "ad": tr_upper("HÜSEYİN TONGUÇ"), "tel": "5532285951"}
PARTNER_KISI = {"tc": "48394037974", "ad": tr_upper("PINAR TONGUÇ"), "tel": "5461403467"}

# Takip edilecek saatler (Test için 08:00'i ekleyebilirsiniz)
HEDEF_SAATLER = ["08:00"]

# --- 2. TARAYICI AYARLARI ---
chrome_options = Options()
# reCAPTCHA'da sorun yaşıyorsanız aşağıdaki satırın başındaki '#' işaretini kaldırıp
# kendi profil yolunuzu ekleyebilirsiniz.
# chrome_options.add_argument(f"user-data-dir=C:\\Users\\KULLANICI_ADINIZ\\AppData\\Local\\Google\\Chrome\\User Data")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def pusu_modu():
    print(f"{'='*30}\nBOT BASLATILDI\nHEDEF: {HEDEF_SAATLER}\n{'='*30}")

    while True:
        try:
            driver.get("https://kultursanat.silivri.bel.tr/tenis-kortu")
            time.sleep(3) # Sayfanın yüklenmesini bekle

            # Varsa SweetAlert (Swal) popup'larını kapat (Örn: "Seans bulunamadı")
            try:
                driver.execute_script("if(typeof Swal !== 'undefined') { Swal.close(); }")
            except:
                pass

            asıl = ASIL_KISI
            partner = PARTNER_KISI

            # SAAT SEÇİMİ
            try:
                # Yeni div tabanlı dropdown'ı aç
                time_input = driver.find_element(By.ID, "timeInput")
                driver.execute_script("arguments[0].click();", time_input)
                time.sleep(1) # Seçeneklerin açılması için kısa bekleme

                hedef_bulundu = False
                time_options = driver.find_element(By.ID, "timeOptions")
                options = time_options.find_elements(By.TAG_NAME, "div")

                for hedef in HEDEF_SAATLER:
                    for option in options:
                        # Div'in class attribute'unda 'disabled' olup olmadığına bakıyoruz
                        # Ayrıca text'in içinde hedef saat geçmeli
                        class_attr = option.get_attribute("class") or ""
                        if hedef in option.text and "disabled" not in class_attr:
                            driver.execute_script("arguments[0].click();", option)
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

                # 1. Kişi Telefon
                driver.find_element(By.ID, "phone1").clear()
                driver.find_element(By.ID, "phone1").send_keys(asıl["tel"])

                # 2. Kişi (Partner)
                driver.find_element(By.ID, "tc2").clear()
                driver.find_element(By.ID, "tc2").send_keys(partner["tc"])
                driver.find_element(By.ID, "name2").clear()
                driver.find_element(By.ID, "name2").send_keys(partner["ad"])
                driver.find_element(By.ID, "phone2").clear()
                driver.find_element(By.ID, "phone2").send_keys(partner["tel"])

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
                print("İşlem tamamlandı, bot durduruluyor...")
                break

            except Exception as sub_e:
                print(f"İşlem sırasında hata: {sub_e}")
                time.sleep(5)

        except Exception as e:
            print(f"Ana döngüde bir hata oluştu: {e}")
            time.sleep(5)

if __name__ == "__main__":
    pusu_modu()
