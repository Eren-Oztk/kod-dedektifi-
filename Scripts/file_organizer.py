import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path

# --- GELİŞMİŞ AYRIŞTIRMA HARİTASI ---
UZANTI_HARITASI = {
    "Kod_Python": [".py", ".ipynb", ".pyw", ".requirements"],
    "Kod_Web": [".html", ".css", ".js", ".php", ".asp"],
    "Kod_Arduino_Gomulu": [".ino", ".hex", ".bin", ".c", ".cpp"],
    "Kod_Java": [".java", ".jar", ".class"],
    "Kod_Veri": [".json", ".xml", ".sql", ".db", ".csv"],

    "3D_Blender": [".blend", ".blend1"],
    "3D_Genel_Model": [".obj", ".fbx", ".stl", ".3ds", ".dae", ".gltf", ".glb"],
    "3D_Textures": [".mat", ".tex", ".tga", ".dds", ".exr", ".hdr"],
    "Tasarim_Photoshop": [".psd", ".psb"],
    "Tasarim_Vector": [".ai", ".eps", ".svg", ".cdr"],

    "Belge_PDF": [".pdf"],
    "Belge_Word": [".doc", ".docx"],
    "Belge_Excel": [".xls", ".xlsx", ".csv"],
    "Belge_Sunum": [".ppt", ".pptx"],
    "Belge_Notlar": [".txt", ".md", ".log"],

    "Medya_Resimler": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"],
    "Medya_Videolar": [".mp4", ".mov", ".avi", ".mkv", ".flv"],
    "Medya_Ses": [".mp3", ".wav", ".ogg", ".flac"],

    "Sistem_Kurulum": [".exe", ".msi", ".iso"],
    "Sistem_Arsiv": [".zip", ".rar", ".7z", ".tar", ".gz"]
}


class TemizlikUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Dijital Temizlikçi v3.0")
        self.root.geometry("800x600")
        self.root.configure(bg="#eceff1")

        # Hareket Geçmişi (Geri Alma İçin)
        self.gecmis_hareketler = []

        # --- BAŞLIK ---
        tk.Label(root, text="🛡️ GÜVENLİ DOSYA ORGANİZATÖRÜ", bg="#eceff1", font=("Segoe UI", 16, "bold"),
                 fg="#37474f").pack(pady=10)

        # --- SEÇİM ALANI ---
        frame_ust = tk.Frame(root, bg="white", padx=10, pady=10, relief="groove", bd=1)
        frame_ust.pack(pady=5, padx=20, fill="x")

        tk.Label(frame_ust, text="Düzenlenecek Klasör:", bg="white", font=("Arial", 10)).pack(anchor="w")

        frame_input = tk.Frame(frame_ust, bg="white")
        frame_input.pack(fill="x", pady=5)

        self.entry_yol = tk.Entry(frame_input, font=("Consolas", 10), bd=2, relief="sunken")
        self.entry_yol.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_sec = tk.Button(frame_input, text="📁 Gözat", command=self.klasor_sec, bg="#2196F3", fg="white",
                                 font=("Arial", 9, "bold"))
        self.btn_sec.pack(side="right")

        # --- İLERLEME ÇUBUĞU ---
        self.progress = ttk.Progressbar(root, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(pady=10, padx=20, fill="x")

        # --- LOG EKRANI ---
        tk.Label(root, text="İşlem Kayıtları:", bg="#eceff1", font=("Arial", 9)).pack(anchor="w", padx=20)
        self.log_alani = scrolledtext.ScrolledText(root, width=80, height=15, font=("Consolas", 9))
        self.log_alani.pack(padx=20, pady=(0, 10), fill="both", expand=True)

        self.log_alani.tag_config("basari", foreground="green")
        self.log_alani.tag_config("hata", foreground="red")
        self.log_alani.tag_config("bilgi", foreground="blue")
        self.log_alani.tag_config("uyari", foreground="#FF8F00")  # Turuncu

        # --- BUTONLAR ---
        frame_btn = tk.Frame(root, bg="#eceff1")
        frame_btn.pack(pady=10, fill="x", padx=20)

        self.btn_baslat = tk.Button(frame_btn, text="🚀 BAŞLAT", command=self.temizlige_basla,
                                    bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), width=20, height=2)
        self.btn_baslat.pack(side="left", padx=(0, 10))

        self.btn_geri_al = tk.Button(frame_btn, text="↩️ GERİ AL (UNDO)", command=self.geri_al,
                                     bg="#F44336", fg="white", font=("Arial", 11, "bold"), width=20, height=2,
                                     state="disabled")
        self.btn_geri_al.pack(side="right")

    def log_yaz(self, mesaj, tur="normal"):
        self.log_alani.insert(tk.END, mesaj + "\n", tur)
        self.log_alani.see(tk.END)
        self.root.update()

    def klasor_sec(self):
        klasor_yolu = filedialog.askdirectory()
        if klasor_yolu:
            self.entry_yol.delete(0, tk.END)
            self.entry_yol.insert(0, klasor_yolu)
            self.log_yaz(f"Hedef: {klasor_yolu}", "bilgi")

    def dosya_adi_cakismasini_coz(self, hedef_yol):
        if not os.path.exists(hedef_yol): return hedef_yol
        dosya_adi, uzantisi = os.path.splitext(hedef_yol)
        sayac = 1
        while True:
            yeni_yol = f"{dosya_adi}_{sayac}{uzantisi}"
            if not os.path.exists(yeni_yol): return yeni_yol
            sayac += 1

    def temizlige_basla(self):
        hedef_klasor = self.entry_yol.get()
        if not hedef_klasor or not os.path.exists(hedef_klasor):
            messagebox.showerror("Hata", "Lütfen geçerli bir klasör seçin!")
            return

        path = Path(hedef_klasor)
        self.gecmis_hareketler = []  # Geçmişi sıfırla
        self.btn_geri_al.config(state="disabled")  # İşlem sırasında butonu kapat

        self.log_alani.delete(1.0, tk.END)
        self.log_yaz(f"=== {hedef_klasor} TARANIYOR ===", "bilgi")

        dosyalar = [f for f in path.iterdir() if f.is_file() and "duzenleyici" not in f.name]
        toplam_dosya = len(dosyalar)

        if toplam_dosya == 0:
            self.log_yaz("Düzenlenecek dosya bulunamadı.", "uyari")
            return

        self.progress["maximum"] = toplam_dosya
        self.progress["value"] = 0

        tasinan = 0

        for dosya in dosyalar:
            try:
                uzanti = dosya.suffix.lower()
                if not uzanti: continue

                hedef_kategori = None
                for kategori, uzantilar in UZANTI_HARITASI.items():
                    if uzanti in uzantilar:
                        hedef_kategori = kategori
                        break

                if hedef_kategori:
                    hedef_klasor_yolu = path / hedef_kategori
                    hedef_klasor_yolu.mkdir(exist_ok=True)

                    yeni_dosya_yolu = hedef_klasor_yolu / dosya.name
                    final_yol = self.dosya_adi_cakismasini_coz(str(yeni_dosya_yolu))

                    # DOSYAYI TAŞI
                    shutil.move(str(dosya), final_yol)

                    # GEÇMİŞE KAYDET (Kaynak, Hedef)
                    self.gecmis_hareketler.append((final_yol, str(dosya)))

                    self.log_yaz(f"✅ {dosya.name} -> {hedef_kategori}", "basari")
                    tasinan += 1

            except Exception as e:
                self.log_yaz(f"❌ HATA: {dosya.name} ({e})", "hata")

            self.progress["value"] += 1
            self.root.update()  # Arayüzü güncelle

        self.log_yaz(f"\n🎉 İşlem Bitti! {tasinan} dosya taşındı.", "bilgi")

        if tasinan > 0:
            self.btn_geri_al.config(state="normal")  # Geri al butonunu aç

            # Boş klasör temizliği sorusu
            cevap = messagebox.askyesno("Temizlik", "İşlem tamamlandı. Boş kalan klasörler silinsin mi?")
            if cevap:
                self.bos_klasorleri_sil(path)

    def bos_klasorleri_sil(self, path):
        silinen = 0
        for klasor in path.iterdir():
            if klasor.is_dir():
                try:
                    # Klasör boş mu diye bak (içinde dosya yoksa)
                    if not any(klasor.iterdir()):
                        klasor.rmdir()
                        self.log_yaz(f"🗑️ Boş klasör silindi: {klasor.name}", "uyari")
                        silinen += 1
                except:
                    pass
        if silinen > 0:
            messagebox.showinfo("Bilgi", f"{silinen} adet boş klasör temizlendi.")

    def geri_al(self):
        if not self.gecmis_hareketler:
            messagebox.showinfo("Bilgi", "Geri alınacak işlem yok.")
            return

        cevap = messagebox.askyesno("Dikkat", "Son yapılan işlemleri geri almak üzeresiniz. Emin misiniz?")
        if not cevap: return

        self.log_yaz("\n↩️ GERİ ALMA İŞLEMİ BAŞLATILIYOR...", "uyari")
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.gecmis_hareketler)

        hata_sayisi = 0

        # Listeyi tersten oku (En son taşınanı en başa al)
        for suanki_konum, eski_konum in reversed(self.gecmis_hareketler):
            try:
                if os.path.exists(suanki_konum):
                    shutil.move(suanki_konum, eski_konum)
                    self.log_yaz(f"🔙 Geri Taşındı: {os.path.basename(eski_konum)}", "bilgi")
                else:
                    self.log_yaz(f"⚠️ Dosya bulunamadı: {suanki_konum}", "hata")
                    hata_sayisi += 1
            except Exception as e:
                self.log_yaz(f"❌ Hata: {e}", "hata")
                hata_sayisi += 1

            self.progress["value"] += 1
            self.root.update()

        self.gecmis_hareketler = []  # Geçmişi temizle
        self.btn_geri_al.config(state="disabled")
        messagebox.showinfo("Tamamlandı", "Geri alma işlemi tamamlandı.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TemizlikUygulamasi(root)
    root.mainloop()