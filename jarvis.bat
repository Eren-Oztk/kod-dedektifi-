@echo off
:: Önce programın olduğu klasöre git (Çok önemli, yoksa scriptleri bulamaz)
cd /d "D:\PycharmProjects\pythonProject\Kod Dedektifi"

:: Arayüzü başlat (Siyah ekran çıkmasın diye pythonw kullanıyoruz)
start pythonw Launcher.py

:: Bu siyah pencereyi kapat
exit