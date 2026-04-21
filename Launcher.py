import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess


class OtomasyonMerkeziFinal:
    def __init__(self, root):
        self.root = root
        self.root.title("Asistan v5.0 - GridFlow")
        self.root.geometry("950x700")

        # --- Modern Renkler ---
        self.colors = {
            "bg": "#121212",
            "card_bg": "#1e1e1e",
            "card_border": "#333333",
            "text": "#ffffff",
            "accent": "#007acc",
            "hover": "#2a2a2a"
        }
        self.root.configure(bg=self.colors["bg"])

        self.butonlar = []  # Buton referanslarını tutacağız

        # --- BAŞLIK ---
        header = tk.Frame(self.root, bg=self.colors["bg"], pady=20)
        header.pack(fill=tk.X)
        tk.Label(header, text="KONTROL MERKEZİ", font=("Segoe UI", 24, "bold"), bg=self.colors["bg"], fg="white").pack()
        tk.Label(header, text="Araçların her boyutta tam ortalanır", font=("Segoe UI", 10), bg=self.colors["bg"],
                 fg="#888888").pack()

        # --- SCROLL ALANI ---
        self.canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)

        # Butonların duracağı iç çerçeve
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors["bg"])

        # Canvas'a pencere ekle (anchor='nw' yani Sol Üst köşe referanslı)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Scroll Ayarları
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Eventler
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self.on_resize)  # Pencere boyutu değişince tetikle

        self.scriptleri_yukle()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def ikon_belirle(self, dosya_adi):
        ad = dosya_adi.lower()
        if "wifi" in ad: return "📶"
        if "sifre" in ad or "pass" in ad: return "🔑"
        if "snap" in ad or "foto" in ad or "ss" in ad: return "📸"
        if "clip" in ad or "pano" in ad: return "📋"
        if "kod" in ad or "dedektif" in ad or "search" in ad: return "🕵️‍♂️"
        if "borsa" in ad or "coin" in ad: return "📈"
        if "pdf" in ad: return "📑"
        if "renk" in ad or "color" in ad: return "🎨"
        if "indir" in ad or "download" in ad or "temiz" in ad: return "🧹"
        if "bot" in ad or "oto" in ad: return "🤖"
        if "dosya" in ad or "file" in ad or "duzen" in ad: return "🗂️"
        return "⚡"

    def scriptleri_yukle(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        scripts_folder = os.path.join(base_path, "Scripts")

        if not os.path.exists(scripts_folder):
            os.makedirs(scripts_folder)
            return

        dosyalar = [f for f in os.listdir(scripts_folder) if f.endswith(".py")]

        # Butonları oluştur (Henüz yerleştirme/grid yapmıyoruz)
        for dosya in dosyalar:
            script_yolu = os.path.join(scripts_folder, dosya)
            ad_ham = os.path.splitext(dosya)[0]
            ad_guzel = ad_ham.replace("_", " ").title()
            if len(ad_guzel) > 20: ad_guzel = ad_guzel[:17] + "..."
            ikon = self.ikon_belirle(ad_ham)

            # Kart Görünümlü Frame
            container = tk.Frame(self.scrollable_frame, bg=self.colors["card_border"], padx=1, pady=1)

            btn = tk.Button(container,
                            text=f"{ikon}\n\n{ad_guzel}",
                            font=("Segoe UI", 11, "bold"),
                            bg=self.colors["card_bg"],
                            fg="white",
                            activebackground=self.colors["hover"],
                            activeforeground="white",
                            relief="flat",
                            width=22, height=8,  # Boyutlar
                            cursor="hand2",
                            command=lambda p=script_yolu: self.scripti_calistir(p))
            btn.pack()
            self.butonlar.append(container)

    def on_resize(self, event):
        """Pencere her değiştiğinde matematiği yeniden kur"""
        canvas_width = event.width

        # AYARLAR
        ITEM_WIDTH = 200  # Buton çerçevesi + iç boşluk tahmini (Piksel)
        GAP = 20  # Butonlar arası boşluk

        # 1. Yan yana kaç tane sığar?
        columns = max(1, canvas_width // (ITEM_WIDTH + GAP))

        # 2. Bu kolonlar toplam ne kadar yer kaplar?
        total_grid_width = (columns * ITEM_WIDTH) + ((columns - 1) * GAP)

        # 3. Kalan boşluğu bul ve ikiye böl (SOL MARJ)
        left_margin = max(0, (canvas_width - total_grid_width) // 2)

        # 4. Pencereyi (Scrollable Frame) sol marja taşı
        self.canvas.coords(self.canvas_window, left_margin, 0)

        # 5. Butonları Izgaraya Diz
        for index, container in enumerate(self.butonlar):
            row = index // columns
            col = index % columns
            container.grid(row=row, column=col, padx=GAP // 2, pady=GAP // 2)

    def scripti_calistir(self, yol):
        try:
            subprocess.Popen(["python", yol], shell=True)
        except Exception as e:
            messagebox.showerror("Hata", f"Script başlatılamadı:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = OtomasyonMerkeziFinal(root)
    root.mainloop()