import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading


class DosyaAramaMotoru:
    def __init__(self, root):
        self.root = root
        self.root.title("Hızlı Dosya Bulucu v1.0")
        self.root.geometry("900x600")

        # Stil Ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Segoe UI', 11, 'bold'))

        # --- ÜST PANEL (ARAMA) ---
        frame_top = tk.Frame(root, bg="#f0f0f0", pady=10, padx=10)
        frame_top.pack(fill="x")

        tk.Label(frame_top, text="Aranacak Klasör:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
        self.entry_klasor = tk.Entry(frame_top, width=50)
        self.entry_klasor.grid(row=0, column=1, padx=5)
        tk.Button(frame_top, text="📂 Seç", command=self.klasor_sec).grid(row=0, column=2, padx=5)

        tk.Label(frame_top, text="Aranacak Kelime:", bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=10)
        self.entry_arama = tk.Entry(frame_top, width=50, font=("Arial", 11))
        self.entry_arama.grid(row=1, column=1, padx=5)
        # Enter tuşuna basınca arama yapsın
        self.entry_arama.bind('<Return>', lambda event: self.aramayi_baslat())

        tk.Label(frame_top, text="Uzantı Filtresi (Opsiyonel):", bg="#f0f0f0").grid(row=2, column=0, sticky="w")
        self.combo_uzanti = ttk.Combobox(frame_top, values=["Tümü", ".blend", ".py", ".pdf", ".jpg", ".mp4", ".psd", ".ino", ".png", ".stl" ],
                                         width=10)
        self.combo_uzanti.current(0)
        self.combo_uzanti.grid(row=2, column=1, sticky="w", padx=5)

        self.btn_ara = tk.Button(frame_top, text="🔍 BUL", command=self.aramayi_baslat,
                                 bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_ara.grid(row=1, column=2, padx=5, rowspan=2)

        # --- ORTA PANEL (SONUÇ LİSTESİ) ---
        frame_mid = tk.Frame(root)
        frame_mid.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("dosya_adi", "uzanti", "yol", "boyut")
        self.tree = ttk.Treeview(frame_mid, columns=columns, show="headings")

        self.tree.heading("dosya_adi", text="Dosya Adı")
        self.tree.heading("uzanti", text="Tür")
        self.tree.heading("yol", text="Konum")
        self.tree.heading("boyut", text="Boyut (KB)")

        self.tree.column("dosya_adi", width=250)
        self.tree.column("uzanti", width=80)
        self.tree.column("yol", width=400)
        self.tree.column("boyut", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Çift tıklama olayı
        self.tree.bind("<Double-1>", self.dosyayi_ac)

        # --- ALT PANEL (BİLGİ) ---
        self.lbl_durum = tk.Label(root, text="Hazır", bd=1, relief="sunken", anchor="w")
        self.lbl_durum.pack(side="bottom", fill="x")

    def klasor_sec(self):
        klasor = filedialog.askdirectory()
        if klasor:
            self.entry_klasor.delete(0, tk.END)
            self.entry_klasor.insert(0, klasor)

    def aramayi_baslat(self):
        klasor = self.entry_klasor.get()
        kelime = self.entry_arama.get().lower()
        uzanti_filtre = self.combo_uzanti.get()

        if not klasor or not os.path.exists(klasor):
            messagebox.showwarning("Hata", "Lütfen geçerli bir klasör seçin.")
            return

        # Listeyi temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.lbl_durum.config(text="Aranıyor... Lütfen bekleyin.")

        # Arama işlemini ayrı bir thread'de yap (Arayüz donmasın diye)
        threading.Thread(target=self.arkaplan_arama, args=(klasor, kelime, uzanti_filtre)).start()

    def arkaplan_arama(self, klasor, kelime, uzanti_filtre):
        sonuc_sayisi = 0

        try:
            for kok_dizin, klasorler, dosyalar in os.walk(klasor):
                for dosya in dosyalar:
                    # Filtreleme Mantığı
                    if kelime in dosya.lower():
                        dosya_uzantisi = os.path.splitext(dosya)[1].lower()

                        # Uzantı filtresi seçiliyse kontrol et
                        if uzanti_filtre != "Tümü" and dosya_uzantisi != uzanti_filtre:
                            continue

                        tam_yol = os.path.join(kok_dizin, dosya)
                        boyut_kb = round(os.path.getsize(tam_yol) / 1024, 1)

                        # Listeye ekle (GUI güncellemesi ana thread'den yapılmalı ama Tkinter bunu tolere eder)
                        self.tree.insert("", tk.END, values=(dosya, dosya_uzantisi, tam_yol, f"{boyut_kb} KB"))
                        sonuc_sayisi += 1
        except Exception as e:
            print(f"Hata: {e}")

        self.lbl_durum.config(text=f"Arama Tamamlandı! {sonuc_sayisi} dosya bulundu.")

    def dosyayi_ac(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return

        item = self.tree.item(selected_item)
        dosya_yolu = item['values'][2]  # 3. sütun (Yol)

        try:
            os.startfile(dosya_yolu)  # Dosyayı varsayılan programla aç
            self.lbl_durum.config(text=f"Açıldı: {dosya_yolu}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya açılamadı:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DosyaAramaMotoru(root)
    root.mainloop()