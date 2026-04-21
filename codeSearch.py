import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading

# --- Kütüphane Kontrolü ---
try:
    from PyPDF2 import PdfReader
    from docx import Document

    KUTUPHANELER_TAMAM = True
except ImportError:
    KUTUPHANELER_TAMAM = False


class DosyaDedektifiV7:
    def __init__(self, root):
        self.root = root
        self.root.title("Dosya Dedektifi v7.0 - Dinamik Filtre")
        self.root.geometry("1350x850")

        # --- Modern Renkler ---
        self.colors = {
            "bg_dark": "#1e1e1e", "bg_panel": "#252526", "fg_text": "#cccccc",
            "fg_heading": "#ffffff", "accent": "#007acc", "accent_hover": "#0062a3",
            "list_select": "#37373d", "highlight": "#dcdcaa", "highlight_text": "#000000"
        }
        self.root.configure(bg=self.colors["bg_dark"])

        # --- Stil ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Panel.TFrame", background=self.colors["bg_panel"])
        self.style.configure("Main.TFrame", background=self.colors["bg_dark"])
        self.style.configure("TLabel", background=self.colors["bg_panel"], foreground=self.colors["fg_text"],
                             font=("Segoe UI", 10))
        self.style.configure("Heading.TLabel", background=self.colors["bg_panel"], foreground=self.colors["fg_heading"],
                             font=("Segoe UI", 11, "bold"))
        self.style.configure("Status.TLabel", background=self.colors["accent"], foreground="white",
                             font=("Segoe UI", 9))
        self.style.configure("Accent.TButton", background=self.colors["accent"], foreground="white", borderwidth=0,
                             font=("Segoe UI", 10, "bold"), padding=10)
        self.style.map("Accent.TButton", background=[('active', self.colors["accent_hover"])])
        self.style.configure("Normal.TButton", background="#3e3e42", foreground="white", borderwidth=0, padding=6)
        self.style.map("Normal.TButton", background=[('active', "#505055")])

        # Değişkenler
        self.aranacak_klasor = tk.StringVar()
        self.arama_kelimesi = tk.StringVar()
        self.ana_mod = tk.StringVar(value="Kodlar")
        self.alt_filtre = tk.StringVar(value="Tümü")  # .py, .pdf vb.
        self.secili_dosya_yolu = None
        self.dosya_cache = {}

        if not KUTUPHANELER_TAMAM:
            messagebox.showwarning("Uyarı", "PDF/Word kütüphaneleri eksik. Sadece kod araması çalışır.")

        self.arayuz_olustur()

    def arayuz_olustur(self):
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors["bg_dark"], sashwidth=4,
                                    sashrelief=tk.FLAT)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # --- SOL PANEL (AYARLAR) ---
        sol_frame = ttk.Frame(main_paned, style="Panel.TFrame", padding=15)
        main_paned.add(sol_frame, width=420)

        ttk.Label(sol_frame, text="DOSYA DEDEKTİFİ", font=("Segoe UI", 16, "bold"),
                  foreground=self.colors["accent"]).pack(anchor="w", pady=(0, 20))

        # 1. Klasör
        search_box = ttk.Frame(sol_frame, style="Panel.TFrame")
        search_box.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(search_box, text="KLASÖR SEÇ:", style="Heading.TLabel").pack(anchor="w")

        k_box = ttk.Frame(search_box, style="Panel.TFrame")
        k_box.pack(fill=tk.X, pady=5)
        entry_klasor = tk.Entry(k_box, textvariable=self.aranacak_klasor, bg="#3c3c3c", fg="white",
                                insertbackground="white", relief=tk.FLAT, font=("Segoe UI", 10))
        entry_klasor.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 5))
        ttk.Button(k_box, text="...", width=3, style="Normal.TButton", command=self.klasor_sec).pack(side=tk.RIGHT)

        # 2. Kelime
        ttk.Label(search_box, text="ARANACAK KELİME:", style="Heading.TLabel").pack(anchor="w", pady=(10, 0))
        entry_kelime = tk.Entry(search_box, textvariable=self.arama_kelimesi, bg="#3c3c3c", fg="white",
                                insertbackground="white", relief=tk.FLAT, font=("Segoe UI", 11))
        entry_kelime.pack(fill=tk.X, pady=5, ipady=5)
        entry_kelime.bind('<Return>', lambda e: self.aramayi_baslat())

        # 3. KATEGORİ VE DETAYLI FİLTRE (YAN YANA)
        filter_frame = ttk.Frame(search_box, style="Panel.TFrame")
        filter_frame.pack(fill=tk.X, pady=10)

        # Sol taraf: Ana Mod (Kod mu Belge mi?)
        f1 = ttk.Frame(filter_frame, style="Panel.TFrame")
        f1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Label(f1, text="Kategori:", font=("Segoe UI", 9)).pack(anchor="w")
        self.combo_mod = ttk.Combobox(f1, textvariable=self.ana_mod, values=["Kodlar", "Belgeler"], state="readonly")
        self.combo_mod.pack(fill=tk.X)
        self.combo_mod.bind("<<ComboboxSelected>>", self.filtreleri_guncelle)

        # Sağ taraf: Detaylı Uzantı (.py mi .ino mu?)
        f2 = ttk.Frame(filter_frame, style="Panel.TFrame")
        f2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        ttk.Label(f2, text="Uzantı Filtresi:", font=("Segoe UI", 9)).pack(anchor="w")
        self.combo_alt = ttk.Combobox(f2, textvariable=self.alt_filtre, state="readonly")
        self.combo_alt.pack(fill=tk.X)

        # Başlangıç filtrelerini yükle
        self.filtreleri_guncelle(None)

        # 4. Başlat Butonu
        ttk.Button(search_box, text="🔍 TARAMAYI BAŞLAT", style="Accent.TButton", command=self.aramayi_baslat).pack(
            fill=tk.X, pady=15)

        # Sonuçlar
        ttk.Label(sol_frame, text="🎯 SONUÇLAR", style="Heading.TLabel").pack(anchor="w")
        self.liste_sonuc = tk.Listbox(sol_frame, bg=self.colors["bg_dark"], fg=self.colors["fg_text"],
                                      selectbackground=self.colors["list_select"], selectforeground="white",
                                      relief=tk.FLAT, font=("Segoe UI", 10), highlightthickness=0)
        self.liste_sonuc.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        self.liste_sonuc.bind('<<ListboxSelect>>', self.dosya_secildi)
        self.liste_sonuc.bind('<Double-Button-1>', self.dosyayi_ac)

        # --- SAĞ PANEL ---
        sag_frame = ttk.Frame(main_paned, style="Main.TFrame")
        main_paned.add(sag_frame)

        toolbar = ttk.Frame(sag_frame, style="Main.TFrame", padding=10)
        toolbar.pack(fill=tk.X)
        ttk.Label(toolbar, text="İÇERİK ÖNİZLEME", font=("Segoe UI", 12, "bold"),
                  background=self.colors["bg_dark"]).pack(side=tk.LEFT)

        btn_box = ttk.Frame(toolbar, style="Main.TFrame")
        btn_box.pack(side=tk.RIGHT)
        ttk.Button(btn_box, text="📂 Klasörü Aç", style="Normal.TButton", command=self.klasoru_ac).pack(side=tk.LEFT,
                                                                                                       padx=2)
        ttk.Button(btn_box, text="📝 Aç", style="Accent.TButton", command=lambda: self.dosyayi_ac(None)).pack(
            side=tk.LEFT, padx=2)

        self.text_onizleme = scrolledtext.ScrolledText(sag_frame, wrap=tk.NONE, font=("Consolas", 11),
                                                       bg="#1e1e1e", fg="#d4d4d4", insertbackground="white",
                                                       relief=tk.FLAT, borderwidth=0)
        self.text_onizleme.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.text_onizleme.tag_config('vurgu', background=self.colors["highlight"],
                                      foreground=self.colors["highlight_text"])

        self.durum_cubugu = ttk.Label(self.root, text=" Hazır", style="Status.TLabel", padding=5)
        self.durum_cubugu.pack(side=tk.BOTTOM, fill=tk.X)

    # --- YENİ: DİNAMİK FİLTRE MANTIĞI ---
    def filtreleri_guncelle(self, event):
        """Kategori değişince (Kod/Belge) yandaki uzantı listesini değiştirir."""
        secilen_mod = self.ana_mod.get()

        if secilen_mod == "Kodlar":
            degerler = ["Tümü", ".py (Python)", ".ino (Arduino)", ".html (Web)", ".css", ".js", ".cpp", ".txt", ".sql"]
        else:  # Belgeler
            degerler = ["Tümü", ".pdf (PDF)", ".docx (Word)", ".txt (Metin)", ".md", ".rtf"]

        self.combo_alt['values'] = degerler
        self.combo_alt.current(0)  # İlk seçeneği (Tümü) seç

    def klasor_sec(self):
        klasor = filedialog.askdirectory()
        if klasor: self.aranacak_klasor.set(klasor)

    # --- OKUMA FONKSİYONLARI ---
    def pdf_oku(self, yol):
        try:
            reader = PdfReader(yol)
            return "\n".join([page.extract_text() for page in reader.pages])
        except:
            return ""

    def docx_oku(self, yol):
        try:
            doc = Document(yol)
            return "\n".join([p.text for p in doc.paragraphs])
        except:
            return ""

    def icerik_al(self, yol):
        ext = os.path.splitext(yol)[1].lower()
        if ext == ".pdf" and KUTUPHANELER_TAMAM: return self.pdf_oku(yol)
        if ext == ".docx" and KUTUPHANELER_TAMAM: return self.docx_oku(yol)
        try:
            with open(yol, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return ""

    def aramayi_baslat(self):
        threading.Thread(target=self.arama_islemi, daemon=True).start()

    def arama_islemi(self):
        klasor = self.aranacak_klasor.get()
        kelime = self.arama_kelimesi.get()
        mod = self.ana_mod.get()
        alt_filtre = self.alt_filtre.get().split(" ")[0]  # ".py" kısmını alır

        if not klasor: return

        self.liste_sonuc.delete(0, tk.END)
        self.text_onizleme.delete("1.0", tk.END)
        self.durum_cubugu.config(text=" Taranıyor...")

        # 1. Hangi uzantılar geçerli?
        if mod == "Kodlar":
            izinli_uzantilar = ['.py', '.html', '.css', '.js', '.ino', '.txt', '.cpp', '.c', '.json', '.php', '.sql']
        else:
            izinli_uzantilar = ['.pdf', '.docx', '.txt', '.md', '.rtf']

        YASAKLI = {'node_modules', '.git', 'venv', '__pycache__', 'build', 'dist', 'bin', 'obj', '$RECYCLE.BIN'}
        bulunanlar = 0
        self.dosya_cache = {}

        for kok, klasorler, dosyalar in os.walk(klasor):
            klasorler[:] = [d for d in klasorler if d not in YASAKLI]

            for dosya in dosyalar:
                ext = os.path.splitext(dosya)[1].lower()

                # A. Kategori Kontrolü
                if ext not in izinli_uzantilar: continue

                # B. Alt Filtre Kontrolü (Örn: Sadece .ino seçildiyse)
                if alt_filtre != "Tümü" and ext != alt_filtre: continue

                tam_yol = os.path.join(kok, dosya)
                icerik = self.icerik_al(tam_yol)

                if kelime.lower() in icerik.lower() or kelime.lower() in dosya.lower():
                    gorunen = f"{os.path.basename(kok)} / {dosya}"
                    self.root.after(0, self.listeye_ekle, gorunen, tam_yol)
                    bulunanlar += 1

        self.root.after(0, lambda: self.durum_cubugu.config(text=f" İşlem Tamamlandı. {bulunanlar} dosya bulundu."))

    def listeye_ekle(self, gorunen, yol):
        self.liste_sonuc.insert(tk.END, gorunen)
        self.dosya_cache[gorunen] = yol

    def dosya_secildi(self, event):
        secim = self.liste_sonuc.curselection()
        if not secim: return
        yol = self.dosya_cache.get(self.liste_sonuc.get(secim))
        self.secili_dosya_yolu = yol

        if yol:
            icerik = self.icerik_al(yol)
            limit = 20000
            goster = icerik[:limit] + ("\n... [Devamı Kesildi]" if len(icerik) > limit else "")

            self.text_onizleme.delete("1.0", tk.END)
            self.text_onizleme.insert(tk.END, goster)
            self.vurgula(self.arama_kelimesi.get())

    def vurgula(self, kelime):
        if not kelime: return
        start = '1.0'
        while True:
            pos = self.text_onizleme.search(kelime, start, stopindex=tk.END, nocase=1)
            if not pos: break
            end = f"{pos}+{len(kelime)}c"
            self.text_onizleme.tag_add('vurgu', pos, end)
            start = end

    def dosyayi_ac(self, event):
        if self.secili_dosya_yolu:
            try:
                os.startfile(self.secili_dosya_yolu)
            except:
                subprocess.call(['open', self.secili_dosya_yolu])

    def klasoru_ac(self):
        if self.secili_dosya_yolu: os.startfile(os.path.dirname(self.secili_dosya_yolu))


if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = DosyaDedektifiV7(root)
    root.mainloop()