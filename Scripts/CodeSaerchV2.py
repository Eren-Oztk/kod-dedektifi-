import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import datetime
from collections import Counter

# --- Kütüphane Kontrolü ---
try:
    from PyPDF2 import PdfReader
    from docx import Document

    KUTUPHANELER_TAMAM = True
except ImportError:
    KUTUPHANELER_TAMAM = False


class KodDedektifiUltimateUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kod Dedektifi v11.0 - Pro Studio")
        self.root.geometry("1450x900")

        # --- RENK PALETİ (Modern Dark Theme) ---
        self.colors = {
            "bg_main": "#121212",  # En arka plan (Simsiyah değil, çok koyu gri)
            "bg_card": "#1e1e1e",  # Panel/Kutu arka planı
            "bg_input": "#2d2d2d",  # Yazı kutuları
            "text_main": "#e0e0e0",  # Ana metin
            "text_dim": "#a0a0a0",  # Açıklama metinleri
            "accent": "#3a86ff",  # Mavi Vurgu (Arama)
            "success": "#00b894",  # Yeşil Vurgu (Arşiv)
            "warning": "#fdcb6e",  # Sarı Vurgu (Vurgulama)
            "border": "#333333"  # Kenarlıklar
        }
        self.root.configure(bg=self.colors["bg_main"])

        # --- STİL AYARLARI ---
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Stil özelleştirmeye en uygun tema

        # Genel Çerçeve ve Etiketler
        self.style.configure("Card.TFrame", background=self.colors["bg_card"], relief="flat")
        self.style.configure("Main.TFrame", background=self.colors["bg_main"])

        self.style.configure("TLabel", background=self.colors["bg_card"], foreground=self.colors["text_main"],
                             font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background=self.colors["bg_card"], foreground=self.colors["accent"],
                             font=("Segoe UI", 16, "bold"))
        self.style.configure("Subtitle.TLabel", background=self.colors["bg_card"], foreground=self.colors["text_dim"],
                             font=("Segoe UI", 9))
        self.style.configure("Status.TLabel", background=self.colors["accent"], foreground="white",
                             font=("Segoe UI", 9, "bold"))

        # Butonlar (Modern, Düz)
        # Mavi Buton
        self.style.configure("Accent.TButton", background=self.colors["accent"], foreground="white", borderwidth=0,
                             font=("Segoe UI", 11, "bold"))
        self.style.map("Accent.TButton", background=[('active', "#2667cc")])  # Tıklanınca koyulaşsın

        # Yeşil Buton
        self.style.configure("Success.TButton", background=self.colors["success"], foreground="white", borderwidth=0,
                             font=("Segoe UI", 11, "bold"))
        self.style.map("Success.TButton", background=[('active', "#008f72")])

        # Gri Buton
        self.style.configure("Normal.TButton", background="#3e3e42", foreground="white", borderwidth=0,
                             font=("Segoe UI", 9))
        self.style.map("Normal.TButton", background=[('active', "#505055")])

        # Değişkenler
        self.aranacak_klasor = tk.StringVar()
        self.arama_kelimesi = tk.StringVar()
        self.ana_mod = tk.StringVar(value="Kodlar")
        self.alt_filtre = tk.StringVar(value="Tümü")
        self.sistem_dosyalari_engelle = tk.BooleanVar(value=True)
        self.secili_dosya_yolu = None
        self.bulunan_tum_dosyalar = {}

        self.arayuz_tasarla()

    def arayuz_tasarla(self):
        # Ana Bölücü (Splitter)
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors["bg_main"], sashwidth=6,
                                    sashrelief=tk.FLAT)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ================= SOL PANEL (KONTROL MERKEZİ) =================
        sol_panel = ttk.Frame(main_paned, style="Main.TFrame")
        main_paned.add(sol_panel, width=480)

        # --- BAŞLIK KARTI ---
        header_card = ttk.Frame(sol_panel, style="Card.TFrame", padding=20)
        header_card.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_card, text="⚡ KOD DEDEKTİFİ PRO", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header_card, text="Dosyalarını Bul, Analiz Et ve Düzenle", style="Subtitle.TLabel").pack(anchor="w")

        # --- ARAMA KARTI ---
        search_card = ttk.LabelFrame(sol_panel, text=" 🔍 ARAMA AYARLARI ", style="Card.TFrame", padding=15)
        search_card.pack(fill=tk.X, pady=(0, 10))

        # Klasör Seçimi
        ttk.Label(search_card, text="Hedef Klasör:").pack(anchor="w", pady=(0, 5))
        f_box = ttk.Frame(search_card, style="Card.TFrame")
        f_box.pack(fill=tk.X)

        self.entry_style_config(tk.Entry(f_box, textvariable=self.aranacak_klasor)).pack(side=tk.LEFT, fill=tk.X,
                                                                                         expand=True, ipady=5)
        ttk.Button(f_box, text="📂 Seç", style="Normal.TButton", width=6, command=self.klasor_sec).pack(side=tk.RIGHT,
                                                                                                       padx=(5, 0))

        # Kelime Arama
        ttk.Label(search_card, text="Kelime Ara (Opsiyonel):").pack(anchor="w", pady=(10, 5))
        self.entry_style_config(tk.Entry(search_card, textvariable=self.arama_kelimesi)).pack(fill=tk.X, ipady=5)

        # Filtreler (Grid Layout)
        filter_grid = ttk.Frame(search_card, style="Card.TFrame")
        filter_grid.pack(fill=tk.X, pady=15)

        ttk.Label(filter_grid, text="Kategori:").grid(row=0, column=0, sticky="w")
        ttk.Label(filter_grid, text="Uzantı:").grid(row=0, column=1, sticky="w", padx=10)

        self.combo_mod = ttk.Combobox(filter_grid, textvariable=self.ana_mod, values=["Kodlar", "Belgeler"],
                                      state="readonly", width=15)
        self.combo_mod.grid(row=1, column=0, sticky="w")
        self.combo_mod.bind("<<ComboboxSelected>>", self.filtreleri_guncelle)

        self.combo_alt = ttk.Combobox(filter_grid, textvariable=self.alt_filtre, state="readonly", width=20)
        self.combo_alt.grid(row=1, column=1, sticky="w", padx=10)
        self.filtreleri_guncelle(None)

        # Temizlik Checkbox (Modern Switch Hissi)
        chk = tk.Checkbutton(search_card, text="🛡️ Sistem Dosyalarını Gizle (site-packages, node_modules)",
                             variable=self.sistem_dosyalari_engelle,
                             bg=self.colors["bg_card"], fg=self.colors["text_dim"],
                             selectcolor=self.colors["bg_input"], activebackground=self.colors["bg_card"],
                             activeforeground="white")
        chk.pack(fill=tk.X, pady=10)

        # Başlat Butonu
        ttk.Button(search_card, text="🚀 TARAMAYI BAŞLAT", style="Accent.TButton", command=self.aramayi_baslat).pack(
            fill=tk.X, ipady=5)

        # --- ARŞİV KARTI ---
        arsiv_card = ttk.LabelFrame(sol_panel, text=" 📦 PROJE PAKETLEYİCİ ", style="Card.TFrame", padding=15)
        arsiv_card.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(arsiv_card, text="Dağınık projeleri, klasör yapılarını bozmadan\ntek bir arşiv klasörüne toplar.",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        self.btn_arsivle = ttk.Button(arsiv_card, text="💾 SONUÇLARI PAKETLE VE KAYDET", style="Success.TButton",
                                      command=self.arsivlemeyi_baslat, state="disabled")
        self.btn_arsivle.pack(fill=tk.X, ipady=5)

        # --- SONUÇ LİSTESİ ---
        list_card = ttk.Frame(sol_panel, style="Card.TFrame", padding=2)  # İnce çerçeve efekti
        list_card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(list_card, text="BULUNAN DOSYALAR:", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=5, pady=5)

        self.liste_sonuc = tk.Listbox(list_card, bg=self.colors["bg_input"], fg=self.colors["text_main"],
                                      selectbackground=self.colors["accent"], selectforeground="white",
                                      relief=tk.FLAT, font=("Consolas", 10), borderwidth=0, highlightthickness=0)
        self.liste_sonuc.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.liste_sonuc.bind('<<ListboxSelect>>', self.dosya_secildi)

        # ================= SAĞ PANEL (ÖNİZLEME) =================
        sag_panel = ttk.Frame(main_paned, style="Card.TFrame", padding=0)
        main_paned.add(sag_panel)

        # Toolbar
        toolbar = ttk.Frame(sag_panel, style="Card.TFrame", padding=10)
        toolbar.pack(fill=tk.X)

        ttk.Label(toolbar, text="👁️ KOD ÖNİZLEME", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        btn_box = ttk.Frame(toolbar, style="Card.TFrame")
        btn_box.pack(side=tk.RIGHT)
        ttk.Button(btn_box, text="📂 Klasör", style="Normal.TButton", command=self.klasoru_ac).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_box, text="📝 Düzenle", style="Normal.TButton", command=lambda: self.dosyayi_ac(None)).pack(
            side=tk.LEFT, padx=2)

        # Editör Alanı
        self.text_onizleme = scrolledtext.ScrolledText(sag_panel, wrap=tk.NONE, font=("Consolas", 11),
                                                       bg=self.colors["bg_main"], fg=self.colors["text_main"],
                                                       insertbackground="white", relief=tk.FLAT, borderwidth=0)
        self.text_onizleme.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        self.text_onizleme.tag_config('vurgu', background=self.colors["warning"], foreground="black")

        # Durum Çubuğu
        self.durum_cubugu = ttk.Label(self.root, text=" Hazır", style="Status.TLabel", padding=8)
        self.durum_cubugu.pack(side=tk.BOTTOM, fill=tk.X)

    # --- STİL YARDIMCISI ---
    def entry_style_config(self, entry_widget):
        """Entry widget'larını modernleştirmek için yardımcı fonksiyon"""
        entry_widget.config(bg=self.colors["bg_input"], fg="white", insertbackground="white", relief=tk.FLAT)
        return entry_widget

    # --- MANTIK FONKSİYONLARI (v10 ile aynı) ---
    def filtreleri_guncelle(self, event):
        secilen_mod = self.ana_mod.get()
        if secilen_mod == "Kodlar":
            degerler = ["Tümü", ".py", ".ino", ".html", ".css", ".js", ".cpp", ".txt", ".sql"]
        else:
            degerler = ["Tümü", ".pdf", ".docx", ".txt", ".md"]
        self.combo_alt['values'] = degerler
        self.combo_alt.current(0)

    def klasor_sec(self):
        klasor = filedialog.askdirectory()
        if klasor: self.aranacak_klasor.set(klasor)

    def icerik_al(self, yol):
        ext = os.path.splitext(yol)[1].lower()
        if ext == ".pdf" and KUTUPHANELER_TAMAM:
            try:
                return "\n".join([page.extract_text() for page in PdfReader(yol).pages])
            except:
                return ""
        if ext == ".docx" and KUTUPHANELER_TAMAM:
            try:
                return "\n".join([p.text for p in Document(yol).paragraphs])
            except:
                return ""
        try:
            with open(yol, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return ""

    def aramayi_baslat(self):
        self.btn_arsivle.config(state="disabled")
        threading.Thread(target=self.arama_islemi, daemon=True).start()

    def arama_islemi(self):
        klasor = self.aranacak_klasor.get()
        kelime = self.arama_kelimesi.get()
        mod = self.ana_mod.get()
        alt_filtre = self.alt_filtre.get().split(" ")[0]
        filtre_aktif = self.sistem_dosyalari_engelle.get()

        if not klasor: return

        self.liste_sonuc.delete(0, tk.END)
        self.text_onizleme.delete("1.0", tk.END)
        self.durum_cubugu.config(text=" ⏳ Taranıyor... Kahveni yudumla.")

        if mod == "Kodlar":
            izinli = ['.py', '.html', '.css', '.js', '.ino', '.txt', '.cpp', '.c', '.json', '.php', '.sql']
        else:
            izinli = ['.pdf', '.docx', '.txt', '.md', '.rtf']

        YASAKLI_KELIMELER = ['node_modules', '.git', 'venv', '.venv', 'env', '__pycache__', 'site-packages',
                             'dist-packages', 'Lib', 'lib', 'Scripts', 'Include', 'Program Files',
                             'Program Files (x86)', 'Windows', 'AppData', 'build', 'dist', 'bin', 'obj', 'debug',
                             'release', '$RECYCLE.BIN', 'System Volume Information', 'Microsoft', 'Android']

        self.bulunan_tum_dosyalar = {}

        for kok, klasorler, dosyalar in os.walk(klasor):
            if filtre_aktif:
                for i in range(len(klasorler) - 1, -1, -1):
                    if any(y in klasorler[i] for y in YASAKLI_KELIMELER) or any(
                            y in os.path.join(kok, klasorler[i]) for y in YASAKLI_KELIMELER):
                        del klasorler[i]

            for dosya in dosyalar:
                ext = os.path.splitext(dosya)[1].lower()
                if ext not in izinli: continue
                if alt_filtre != "Tümü" and ext != alt_filtre: continue

                tam_yol = os.path.join(kok, dosya)
                if filtre_aktif and ("site-packages" in tam_yol or "Lib\\" in tam_yol): continue

                eslesme = False
                if not kelime:
                    eslesme = True
                else:
                    icerik = self.icerik_al(tam_yol)
                    if kelime.lower() in icerik.lower() or kelime.lower() in dosya.lower(): eslesme = True

                if eslesme:
                    kisa_yol = tam_yol.replace(klasor, "")
                    gorunen = f"...{kisa_yol}"
                    self.root.after(0, self.listeye_ekle, gorunen, tam_yol)

        self.root.after(0, self.arama_bitti)

    def listeye_ekle(self, gorunen, yol):
        # Dosya türüne göre emoji ekle
        ikon = "📄"
        ext = os.path.splitext(yol)[1].lower()
        if ext == ".py":
            ikon = "🐍"
        elif ext == ".html":
            ikon = "🌐"
        elif ext == ".ino":
            ikon = "🤖"
        elif ext == ".css":
            ikon = "🎨"
        elif ext in [".pdf", ".docx"]:
            ikon = "📑"

        self.liste_sonuc.insert(tk.END, f"{ikon} {gorunen}")
        self.bulunan_tum_dosyalar[f"{ikon} {gorunen}"] = yol

    def arama_bitti(self):
        sayi = len(self.bulunan_tum_dosyalar)
        self.durum_cubugu.config(text=f" ✅ İşlem Tamamlandı. {sayi} dosya bulundu.")
        if sayi > 0: self.btn_arsivle.config(state="normal")

    def arsivlemeyi_baslat(self):
        hedef_klasor = filedialog.askdirectory(title="Arşivin Oluşturulacağı Klasörü Seç")
        if not hedef_klasor: return
        threading.Thread(target=self.arsiv_islemi, args=(hedef_klasor,), daemon=True).start()

    def arsiv_islemi(self, hedef_kok):
        self.durum_cubugu.config(text=" 📦 Projeler analiz ediliyor ve paketleniyor...")

        klasor_gruplari = {}
        for gorunen, tam_yol in self.bulunan_tum_dosyalar.items():
            ana_klasor = os.path.dirname(tam_yol)
            if ana_klasor not in klasor_gruplari: klasor_gruplari[ana_klasor] = []
            klasor_gruplari[ana_klasor].append(tam_yol)

        arsiv_ana = os.path.join(hedef_kok, "PROJE_ARSIVIM_" + datetime.datetime.now().strftime("%Y%m%d"))
        if not os.path.exists(arsiv_ana): os.makedirs(arsiv_ana)

        kopyalanan_dosya = 0

        for kaynak_klasor, dosyalar in klasor_gruplari.items():
            try:
                uzantilar = [os.path.splitext(f)[1].lower() for f in dosyalar]
                counts = Counter(uzantilar)

                kategori = "Karisik_Projeler"
                if ".ino" in counts:
                    kategori = "Arduino_Projeleri"
                elif ".py" in counts:
                    kategori = "Python_Projeleri"
                elif ".html" in counts or ".css" in counts or ".php" in counts:
                    kategori = "Web_Projeleri"
                elif ".pdf" in counts or ".docx" in counts:
                    kategori = "Belgeler"

                proje_adi = os.path.basename(kaynak_klasor)
                hedef_klasor_yolu = os.path.join(arsiv_ana, kategori, proje_adi)
                if not os.path.exists(hedef_klasor_yolu): os.makedirs(hedef_klasor_yolu)

                for kaynak_dosya in dosyalar:
                    dosya_adi = os.path.basename(kaynak_dosya)
                    hedef_dosya = os.path.join(hedef_klasor_yolu, dosya_adi)
                    cnt = 1
                    while os.path.exists(hedef_dosya):
                        ad, u = os.path.splitext(dosya_adi)
                        hedef_dosya = os.path.join(hedef_klasor_yolu, f"{ad}_{cnt}{u}")
                        cnt += 1
                    shutil.copy2(kaynak_dosya, hedef_dosya)
                    kopyalanan_dosya += 1

            except Exception as e:
                print(f"Hata: {e}")

        self.root.after(0, lambda: messagebox.showinfo("Harika!",
                                                       f"{kopyalanan_dosya} dosya arşivlendi!\nKonum: {arsiv_ana}"))
        self.root.after(0, lambda: self.durum_cubugu.config(text=" ✅ Arşivleme Tamamlandı."))

    def dosya_secildi(self, event):
        secim = self.liste_sonuc.curselection()
        if not secim: return
        yol = self.bulunan_tum_dosyalar.get(self.liste_sonuc.get(secim))
        self.secili_dosya_yolu = yol
        if yol:
            icerik = self.icerik_al(yol)
            limit = 20000
            goster = icerik[:limit] + ("\n..." if len(icerik) > limit else "")
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
    app = KodDedektifiUltimateUI(root)
    root.mainloop()