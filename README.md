<div align="center">

# 🕵️ Kod Dedektifi

**`Kişisel Otomasyon Merkezi · Python · Tkinter`**

<br>

[![Live Demo](https://img.shields.io/badge/🌐_Canlı_Demo-GitHub_Pages-1f6feb?style=for-the-badge)](https://eren-oztk.github.io/kod-dedektifi)
[![Language](https://img.shields.io/badge/Python-100%25-3776AB?style=for-the-badge&logo=python)](https://github.com/Eren-Oztk/kod-dedektifi)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge)](https://github.com/Eren-Oztk/kod-dedektifi)

</div>

---

**Versiyon:** v1.0.0

**TR:** Günlük kullanım için geliştirilmiş, tek ekrandan yönetilen kişisel Python araçları koleksiyonu.  
**EN:** A personal collection of Python utility tools managed from a single launcher interface.

---

## Ne Yapar?

Kod Dedektifi, sık kullanılan işlemleri tek bir arayüzden yönetmeni sağlayan bir **otomasyon merkezi**dir. `Launcher.py` çalıştırılınca Scripts klasöründeki tüm araçlar otomatik olarak kart şeklinde listelenir; üstlerine tıklayarak açabilirsin.

## Araçlar

| Araç | Açıklama |
|---|---|
| **Dosya Dedektifi** (`codeSearch.py`) | Klasörler içinde kod ve belge arama, içerik önizleme |
| **Hızlı Arama** (`hizli_arama.py`) | Dosya adına göre hızlı arama, tür filtresi |
| **ClipMaster** | Pano geçmişi yöneticisi, metin ve görsel arşivleme |
| **Sistem Gözü** | CPU/RAM/GPU/Disk/Net anlık izleme (şeffaf HUD) |
| **WiFi Şifreleri** | Kayıtlı ağların şifrelerini listeler |
| **Güvenlik Raporu** | Windows güvenlik loglarını analiz eder, Telegram'a gönderir |
| **Ekran Çekici** | Kısayol tuşuyla otomatik screenshot |
| **PDF Çakısı** | PDF birleştirme ve görsel dönüştürme |
| **Yedek Bulucu** | MD5 hash ile kopya dosya tespiti |
| **Dosya Düzenleyici** | Uzantıya göre otomatik dosya organizasyonu |

## Kurulum

```bash
git clone https://github.com/Eren-Oztk/kod-dedektifi.git
cd kod-dedektifi
pip install -r requirements.txt
```

### Güvenlik Raporu için (Opsiyonel)

`.env.example` dosyasını `.env` olarak kopyala ve token'ını doldur:

```bash
copy .env.example .env
# .env içine TELEGRAM_TOKEN ve CHAT_ID değerlerini yaz
```

> BotFather ile bot oluştur, Chat ID için @userinfobot'u kullan.

## Başlatma

```bash
# GUI ile başlat
pythonw Launcher.py

# Veya
Baslat.bat
```

## Gereksinimler

| Paket | Versiyon | Kullanım |
|---|---|---|
| PyPDF2 | ≥3.0.0 | PDF okuma |
| python-docx | ≥0.8.11 | Word belgesi |
| Pillow | ≥10.0.0 | Görsel işleme |
| psutil | ≥5.9.0 | Sistem izleme |
| GPUtil | ≥1.4.0 | GPU bilgisi |
| requests | ≥2.31.0 | Telegram API |
| pywin32 | ≥306 | Windows Event Log |
| pyautogui | ≥0.9.54 | Screenshot |
| keyboard | ≥0.13.5 | Kısayol tuşları |
| python-dotenv | ≥1.0.0 | Ortam değişkenleri |

## Bilinen Limitasyonlar

- Yalnızca Windows'ta çalışır (pywin32, winsound, netsh bağımlılıkları)
- Güvenlik Raporu aracı yönetici yetkisi gerektirir
- WiFi Şifreleri aracı yönetici yetkisi gerektirir

## Lisans

MIT
