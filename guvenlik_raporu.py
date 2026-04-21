import win32evtlog
import win32evtlogutil
import win32con
import win32security
import datetime
import requests
import socket
import os
import re
from dotenv import load_dotenv

load_dotenv()

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

# --- RAPORLANACAK OLAYLAR ---
OLAY_TIPLERI = {
    4624: {"mesaj": "Giriş Başarılı", "ikon": "🟢", "risk": 1},
    4625: {"mesaj": "HATALI ŞİFRE DENEMESİ", "ikon": "🔴", "risk": 3},
    4688: {"mesaj": "Yeni İşlem/Program Başlatıldı", "ikon": "⚙️", "risk": 0},  # Filtreleyeceğiz
    4720: {"mesaj": "YENİ KULLANICI OLUŞTURULDU", "ikon": "👤", "risk": 3},
    4726: {"mesaj": "Kullanıcı Silindi", "ikon": "🗑️", "risk": 2},
    1102: {"mesaj": "GÜVENLİK LOGLARI TEMİZLENDİ!", "ikon": "🔥", "risk": 5},  # Çok kritik
}


def html_sablonu_olustur(pc_adi, tarih, istatistikler, olaylar_html):
    renk = "#2ecc71"  # Yeşil (Güvenli)
    durum_mesaji = "Sistem Stabil"

    if istatistikler['yuksek_risk'] > 0:
        renk = "#e74c3c"  # Kırmızı
        durum_mesaji = "⚠️ GÜVENLİK İHLALİ OLABİLİR"
    elif istatistikler['orta_risk'] > 0:
        renk = "#f1c40f"  # Sarı
        durum_mesaji = "Dikkat Edilmeli"

    html = f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Güvenlik Raporu</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; }}
        .container {{ max_width: 600px; margin: 0 auto; background-color: #1e1e1e; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
        .header {{ background-color: {renk}; color: #121212; padding: 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 5px 0 0; font-weight: bold; opacity: 0.8; }}
        .stats {{ display: flex; justify-content: space-around; padding: 15px; border-bottom: 1px solid #333; }}
        .stat-box {{ text-align: center; }}
        .stat-val {{ font-size: 20px; font-weight: bold; display: block; }}
        .stat-label {{ font-size: 12px; color: #aaa; }}
        .timeline {{ padding: 0; list-style: none; margin: 0; }}
        .event {{ padding: 15px; border-bottom: 1px solid #333; display: flex; align-items: start; }}
        .event:last-child {{ border-bottom: none; }}
        .event-icon {{ font-size: 24px; margin-right: 15px; min-width: 30px; }}
        .event-content {{ flex-grow: 1; }}
        .time {{ font-size: 12px; color: #777; }}
        .title {{ font-weight: bold; font-size: 14px; margin-bottom: 2px; display: block; }}
        .detail {{ font-size: 12px; color: #bbb; display: block; word-break: break-all; }}
        .tag {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-left: 5px; }}
        .tag-danger {{ background: #c0392b; color: white; }}
        .tag-warn {{ background: #d35400; color: white; }}
    </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ {pc_adi}</h1>
                <p>{durum_mesaji}</p>
                <small>{tarih}</small>
            </div>
            <div class="stats">
                <div class="stat-box"><span class="stat-val">{istatistikler['toplam']}</span><span class="stat-label">Olay</span></div>
                <div class="stat-box"><span class="stat-val" style="color:#e74c3c">{istatistikler['yuksek_risk']}</span><span class="stat-label">Tehdit</span></div>
                <div class="stat-box"><span class="stat-val">{istatistikler['powershell']}</span><span class="stat-label">PowerShell</span></div>
            </div>
            <ul class="timeline">
                {olaylar_html}
            </ul>
        </div>
    </body>
    </html>
    """
    return html


def telegram_dosya_gonder(dosya_yolu, caption):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        with open(dosya_yolu, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}
            requests.post(url, files=files, data=data)
        print("✅ HTML Rapor gönderildi.")
    except Exception as e:
        print(f"❌ Gönderim hatası: {e}")


def loglari_analiz_et():
    server = 'localhost'
    log_type = 'Security'
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

    try:
        hand = win32evtlog.OpenEventLog(server, log_type)
    except:
        return None

    # Sadece bugünün raporu (Saat 00:00'dan itibaren)
    bugun_baslangic = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    olaylar_listesi = []
    stats = {'toplam': 0, 'yuksek_risk': 0, 'orta_risk': 0, 'powershell': 0}

    print("🔍 Güvenlik logları taranıyor...")

    while True:
        events = win32evtlog.ReadEventLog(hand, flags, 0)
        if not events: break

        for event in events:
            # Zaman kontrolü
            olay_zamani = event.TimeGenerated.replace(tzinfo=None)  # Timezone sorununu çöz
            if olay_zamani < bugun_baslangic:
                continue

            eid = event.EventID

            # Sadece ilgilendiğimiz olaylar
            if eid in OLAY_TIPLERI:
                data = OLAY_TIPLERI[eid]
                detay = ""

                # --- DETAYLI ANALİZ ---

                # 1. PowerShell ve CMD Kontrolü (Olay ID 4688)
                if eid == 4688:
                    # Log içeriğini metne çevirip içinde arama yapalım
                    # (StringInserts listesi karmaşıktır, bazen process path 5. bazen 18. indexte olur)
                    if event.StringInserts:
                        full_str = " ".join([str(s) for s in event.StringInserts]).lower()

                        if "powershell" in full_str:
                            detay = "⚠️ PowerShell çalıştırıldı!"
                            stats['powershell'] += 1
                            stats['orta_risk'] += 1
                            data['mesaj'] = "PowerShell Aktivitesi"
                            data['risk'] = 2
                        elif "cmd.exe" in full_str:
                            detay = "Komut İstemi (CMD) açıldı."
                        else:
                            # Diğer exe'leri rapora ekleyip şişirmeyelim
                            continue

                            # 2. Giriş/Çıkışlar
                elif eid == 4624:
                    # Sadece insan girişlerini al (Type 2 ve 7)
                    if event.StringInserts and event.StringInserts[8] not in ['2', '7']:
                        continue
                    detay = "Kullanıcı oturum açtı."

                # 3. Hatalı Şifre
                elif eid == 4625:
                    stats['yuksek_risk'] += 1
                    detay = "Yanlış şifre girildi! Yetkisiz deneme."

                # 4. Log Silme (Çok Tehlikeli)
                elif eid == 1102:
                    stats['yuksek_risk'] += 1
                    detay = "Biri izlerini kaybetmek için logları sildi!"

                # Listeye Ekle
                stats['toplam'] += 1
                saat = olay_zamani.strftime('%H:%M:%S')

                tag_html = ""
                if data['risk'] >= 3:
                    tag_html = '<span class="tag tag-danger">KRİTİK</span>'
                elif data['risk'] == 2:
                    tag_html = '<span class="tag tag-warn">UYARI</span>'

                html_item = f"""
                <li class="event">
                    <div class="event-icon">{data['ikon']}</div>
                    <div class="event-content">
                        <span class="title">{data['mesaj']} {tag_html}</span>
                        <span class="time">{saat}</span>
                        <span class="detail">{detay}</span>
                    </div>
                </li>
                """
                olaylar_listesi.append(html_item)

    win32evtlog.CloseEventLog(hand)

    # HTML Oluştur
    pc_adi = socket.gethostname()
    tarih_str = datetime.datetime.now().strftime("%d.%m.%Y")

    # Olay yoksa
    if not olaylar_listesi:
        olaylar_listesi.append(
            '<li class="event"><div class="event-content">Bugün kayda değer bir olay yaşanmadı.</div></li>')

    # HTML'i birleştir
    full_html = html_sablonu_olustur(pc_adi, tarih_str, stats, "".join(olaylar_listesi))

    return full_html, stats


if __name__ == "__main__":
    html_icerik, istatistik = loglari_analiz_et()

    if html_icerik:
        # Dosyayı kaydet
        dosya_adi = f"Guvenlik_Raporu_{datetime.date.today()}.html"
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(html_icerik)

        # Caption (Mesajın altındaki yazı)
        durum = "✅ Sistem Temiz"
        if istatistik['yuksek_risk'] > 0:
            durum = "🚨 DİKKAT: TEHDİT ALGILANDI!"
        elif istatistik['powershell'] > 0:
            durum = "⚠️ PowerShell Kullanımı Tespit Edildi"

        ozet_mesaj = f"🛡️ *GÜNLÜK RAPOR HAZIR*\n\n{durum}\n📊 Toplam Olay: {istatistik['toplam']}\n🔴 Hatalı Giriş: {istatistik['yuksek_risk']}\n⚙️ PowerShell: {istatistik['powershell']}\n\n_Detaylı rapor ektedir._"

        # Gönder
        telegram_dosya_gonder(dosya_adi, ozet_mesaj)

        # Temizlik (Gönderdikten sonra dosyayı silebilirsin istersen)
        # os.remove(dosya_adi)