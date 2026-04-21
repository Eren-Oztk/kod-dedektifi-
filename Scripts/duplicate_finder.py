import os
import hashlib
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


class KopyaDosyaAvcisi:
    def __init__(self, root):
        self.root = root
        self.root.title("Kopya Dosya Avcısı v1.0")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f5f5f5")

        # Veri Saklama
        self.kopya_gruplari = {}  # hash: [dosya_yollari]

        # --- ÜST PANEL ---
        frame_top = tk.Frame(root, bg="white", padx=10, pady=10, relief="raised")
        frame_top.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_top, text="Taranacak Klasör:", bg="white", font=("Arial", 10, "bold")).pack(side="left")
        self.entry_yol = tk.Entry(frame_top, width=50)
        self.entry_yol.pack(side="left", padx=10)

        tk.Button(frame_top, text="📁 Klasör Seç", command=self.klasor_sec, bg="#2196F3", fg="white").pack(side="left")
        self.btn_baslat = tk.Button(frame_top, text="🕵️ KOPYALARI BUL", command=self.taramayi_baslat, bg="#FF9800",
                                    fg="white", font=("Arial", 10, "bold"))
        self.btn_baslat.pack(side="left", padx=10)

        # --- ORTA PANEL (SPLIT VIEW) ---
        paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned_window.pack(fill="both", expand=True, padx=10)

        # SOL: Kopya Grupları Listesi
        frame_left = tk.Frame(paned_window)
        paned_window.add(frame_left, width=300)

        tk.Label(frame_left, text="Bulunan Kopya Grupları", font=("Arial", 10, "bold")).pack(anchor="w")
        self.list_gruplar = tk.Listbox(frame_left, font=("Arial", 10))
        self.list_gruplar.pack(fill="both", expand=True)
        self.list_gruplar.bind('<<ListboxSelect>>', self.grup_secildi)

        # SAĞ: Dosya Detayları ve Seçim
        frame_right = tk.Frame(paned_window, bg="white")
        paned_window.add(frame_right)

        tk.Label(frame_right, text="Gruptaki Dosyalar (Silinecekleri Seçin)", bg="white",
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=5)

        # Checkboxlı Liste (Treeview kullanarak simüle edeceğiz)
        self.tree = ttk.Treeview(frame_right, columns=("boyut", "yol"), show="headings", selectmode="extended")
        self.tree.heading("boyut", text="Boyut")
        self.tree.heading("yol", text="Dosya Yolu")
        self.tree.column("boyut", width=80)
        self.tree.column("yol", width=500)
        self.tree.pack(fill="both", expand=True, padx=5)

        # --- ALT PANEL (İŞLEMLER) ---
        frame_bottom = tk.Frame(root, bg="#f5f5f5", pady=10)
        frame_bottom.pack(fill="x", padx=10)

        self.lbl_durum = tk.Label(frame_bottom, text="Hazır", bg="#f5f5f5", fg="#555")
        self.lbl_durum.pack(side="left")

        # Akıllı Seçim Butonları
        tk.Button(frame_bottom, text="✅ Hepsini Seç (Biri Hariç)", command=self.birini_tut_digerlerini_sec).pack(
            side="right", padx=5)

        self.btn_temizle = tk.Button(frame_bottom, text="🗑️ SEÇİLENLERİ TAŞI (_COP_KUTUSU_)",
                                     command=self.secilenleri_tasi, bg="#F44336", fg="white",
                                     font=("Arial", 10, "bold"), state="disabled")
        self.btn_temizle.pack(side="right", padx=20)

    def klasor_sec(self):
        klasor = filedialog.askdirectory()
        if klasor:
            self.entry_yol.delete(0, tk.END)
            self.entry_yol.insert(0, klasor)

    def dosya_hash_hesapla(self, dosya_yolu, chunk_size=65536):
        """Dosyanın MD5 parmak izini çıkarır."""
        md5 = hashlib.md5()
        try:
            with open(dosya_yolu, 'rb') as f:
                while chunk := f.read(chunk_size):
                    md5.update(chunk)
            return md5.hexdigest()
        except:
            return None

    def taramayi_baslat(self):
        klasor = self.entry_yol.get()
        if not os.path.exists(klasor):
            messagebox.showwarning("Hata", "Geçerli bir klasör seçin.")
            return

        self.btn_baslat.config(state="disabled")
        self.lbl_durum.config(text="Taranıyor... (Bu işlem dosya boyutuna göre sürebilir)")
        self.root.update()

        # İşlemi thread içinde yap (Arayüz donmasın)
        threading.Thread(target=self.arka_plan_tarama, args=(klasor,)).start()

    def arka_plan_tarama(self, klasor):
        # 1. Aşama: Boyutlarına Göre Grupla (Hızlandırma için)
        boyut_gruplari = {}
        for root, dirs, files in os.walk(klasor):
            if "_COP_KUTUSU_" in root: continue  # Çöp kutusunu tarama

            for f in files:
                path = os.path.join(root, f)
                try:
                    size = os.path.getsize(path)
                    if size not in boyut_gruplari:
                        boyut_gruplari[size] = []
                    boyut_gruplari[size].append(path)
                except:
                    pass

        # 2. Aşama: Sadece aynı boyuttaki dosyaların içeriğine bak (Hash)
        self.kopya_gruplari = {}
        toplam_dosya = sum(len(files) for files in boyut_gruplari.values() if len(files) > 1)
        islenen = 0

        for size, files in boyut_gruplari.items():
            if len(files) < 2: continue  # Tek olanları atla

            for path in files:
                file_hash = self.dosya_hash_hesapla(path)
                if file_hash:
                    if file_hash not in self.kopya_gruplari:
                        self.kopya_gruplari[file_hash] = []
                    self.kopya_gruplari[file_hash].append(path)

                islenen += 1
                if islenen % 10 == 0:  # Arayüzü güncelle
                    self.lbl_durum.config(text=f"Analiz ediliyor: {islenen}/{toplam_dosya}")

        # Sadece 1'den fazla kopyası olanları filtrele
        self.kopya_gruplari = {k: v for k, v in self.kopya_gruplari.items() if len(v) > 1}

        # Listeyi GUI'de göster
        self.root.after(0, self.sonuclari_goster)

    def sonuclari_goster(self):
        self.list_gruplar.delete(0, tk.END)
        kopya_sayisi = 0
        kazanc = 0

        for h, yollar in self.kopya_gruplari.items():
            dosya_adi = os.path.basename(yollar[0])
            adet = len(yollar)
            boyut = os.path.getsize(yollar[0])
            kazanc += boyut * (adet - 1)

            self.list_gruplar.insert(tk.END, f"{dosya_adi} --- ({adet} Kopya)")
            kopya_sayisi += 1

        mb_kazanc = round(kazanc / (1024 * 1024), 2)
        self.lbl_durum.config(text=f"Tarama Bitti! {kopya_sayisi} grup bulundu. Potansiyel kazanç: {mb_kazanc} MB")
        self.btn_baslat.config(state="normal")
        self.btn_temizle.config(state="normal")

    def grup_secildi(self, event):
        selection = self.list_gruplar.curselection()
        if not selection: return

        index = selection[0]
        # Hash'i bulmak biraz dolaylı olacak (Dictionary sırasına güveniyoruz - Python 3.7+ için ok)
        secilen_hash = list(self.kopya_gruplari.keys())[index]
        dosyalar = self.kopya_gruplari[secilen_hash]

        # Sağ paneli temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        for yol in dosyalar:
            boyut = f"{round(os.path.getsize(yol) / 1024, 1)} KB"
            self.tree.insert("", tk.END, values=(boyut, yol))

    def birini_tut_digerlerini_sec(self):
        # Treeview'daki her şeyi seçer ama İLKİNİ seçmez (Onu orijinal kabul eder)
        items = self.tree.get_children()
        if len(items) > 0:
            # Seçimi temizle
            self.tree.selection_remove(self.tree.selection())
            # İlk dosya hariç diğerlerini seç
            to_select = items[1:]
            self.tree.selection_set(to_select)
            messagebox.showinfo("Seçildi", "İlk dosya hariç diğerleri işaretlendi.")

    def secilenleri_tasi(self):
        secili_items = self.tree.selection()
        if not secili_items:
            messagebox.showwarning("Uyarı", "Hiçbir dosya seçmediniz!")
            return

        hedef_klasor = self.entry_yol.get()
        cop_klasoru = os.path.join(hedef_klasor, "_COP_KUTUSU_")
        if not os.path.exists(cop_klasoru):
            os.makedirs(cop_klasoru)

        tasinan = 0
        for item in secili_items:
            path = self.tree.item(item)['values'][1]  # Dosya yolu
            try:
                dosya_adi = os.path.basename(path)
                yeni_yol = os.path.join(cop_klasoru, dosya_adi)

                # İsim çakışması varsa
                if os.path.exists(yeni_yol):
                    isim, uzanti = os.path.splitext(dosya_adi)
                    yeni_yol = os.path.join(cop_klasoru, f"{isim}_kopya{uzanti}")

                shutil.move(path, yeni_yol)
                self.tree.delete(item)  # Listeden kaldır
                tasinan += 1
            except Exception as e:
                print(f"Hata: {e}")

        messagebox.showinfo("Başarılı",
                            f"{tasinan} adet dosya '_COP_KUTUSU_' klasörüne taşındı.\n\nEğer bir sorun yoksa o klasörü silebilirsiniz.")


if __name__ == "__main__":
    root = tk.Tk()
    app = KopyaDosyaAvcisi(root)
    root.mainloop()