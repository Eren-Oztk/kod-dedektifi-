import tkinter as tk
from tkinter import ttk
import subprocess
import os
import sys

# --- AYARLAR ---
# Buraya scriptlerinin tam isimlerini yaz (Aynı klasörde olsunlar)
SCRIPTS = {
    "🧹 Dijital Temizlikçi": "duzenleyici_gui.py",
    "🔍 Hızlı Dosya Bul": "hizli_arama.py",
    "🕵️ Kopya Dosya Avcısı": "duplicate_finder.py",
    "✨ Proje Oluşturucu": "project_creator.py",
    "🎮 Sistem Gözü": "sistem_gozu.py"# <-- YENİ EKLENEN SATIR
}

class AnaMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Apollo Dijital Asistan v1.0")
        self.root.geometry("400x500")
        self.root.configure(bg="#263238")

        # Başlık
        tk.Label(root, text="🛠️ KONTROL PANELİ", bg="#263238", fg="white",
                 font=("Segoe UI", 18, "bold")).pack(pady=30)

        # Butonlar
        for isim, dosya in SCRIPTS.items():
            btn = tk.Button(root, text=isim,
                            command=lambda d=dosya: self.uygulamayi_ac(d),
                            bg="#37474f", fg="white", font=("Arial", 12),
                            activebackground="#546e7a", activeforeground="white",
                            relief="flat", height=2, width=30)
            btn.pack(pady=10)

        # Alt Bilgi
        tk.Label(root, text="Sistem Hazır", bg="#263238", fg="#b0bec5").pack(side="bottom", pady=10)

    def uygulamayi_ac(self, dosya_adi):
        # Dosyanın tam yolunu bul
        klasor = os.path.dirname(os.path.abspath(__file__))
        dosya_yolu = os.path.join(klasor, dosya_adi)

        if os.path.exists(dosya_yolu):
            # Python ile başlat (subprocess kullanarak ana menüyü dondurmadan açar)
            # pythonw kullanıyoruz ki siyah ekran çıkmasın
            subprocess.Popen(["pythonw", dosya_yolu], shell=True)
        else:
            print(f"Hata: {dosya_adi} bulunamadı!")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnaMenu(root)
    root.mainloop()