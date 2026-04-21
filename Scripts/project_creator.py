import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- PROJE ŞABLONLARI ---
SABLONLAR = {
    "🌐 Web Projesi (HTML/CSS/JS)": {
        "extension": ".html",
        "default_name": "index",
        "folders": ["css", "js", "assets/img"],
        "files": {
            "TARGET": """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yeni Proje</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <h1>Proje Başlatıldı!</h1>
    <script src="js/script.js"></script>
</body>
</html>""",
            "css/style.css": "body { margin: 0; padding: 0; font-family: sans-serif; background: #f4f4f4; }",
            "js/script.js": "console.log('Merhaba Dünya');"
        }
    },

    "🐍 Python Projesi": {
        "extension": ".py",
        "default_name": "main",
        "folders": ["src", "data"],
        "files": {
            "TARGET": """def main():
    print("Python Projesi Çalışıyor...")

if __name__ == "__main__":
    main()""",
            "requirements.txt": "requests\npandas",
            "README.md": "# Proje Dokümantasyonu"
        }
    },

    "⚡ Arduino / ESP32 Projesi": {
        "extension": ".ino",
        "default_name": "main",
        "folders": [],
        "files": {
            "TARGET": """void setup() {
  Serial.begin(115200);
}

void loop() {
  // Ana döngü
}"""
        }
    },

    "🎲 3D / Blender Projesi": {
        "extension": ".txt",
        "default_name": "Proje_Notlari",
        "folders": ["Models", "Textures", "Renders", "References"],
        "files": {
            "TARGET": "Model detayları ve referans linkleri buraya..."
        }
    }
}


class ProjeOlusturucu:
    def __init__(self, root):
        self.root = root
        self.root.title("Proje Oluşturucu v2.1")
        self.root.geometry("550x450")
        self.root.configure(bg="#2c3e50")

        # --- ENTER TUŞU İÇİN DİNLEYİCİ ---
        # Pencerenin neresinde olursan ol Enter'a basınca 'projeyi_olustur' çalışır.
        self.root.bind('<Return>', lambda event: self.projeyi_olustur())

        # Başlık
        tk.Label(root, text="🚀 YENİ PROJE SİHİRBAZI", bg="#2c3e50", fg="white", font=("Segoe UI", 16, "bold")).pack(
            pady=20)

        # Form Alanı
        frame = tk.Frame(root, bg="#34495e", padx=20, pady=20)
        frame.pack(padx=20, fill="both")

        # 1. Proje Türü
        tk.Label(frame, text="Proje Türü:", bg="#34495e", fg="white").grid(row=0, column=0, sticky="w", pady=10)
        self.combo_tip = ttk.Combobox(frame, values=list(SABLONLAR.keys()), state="readonly", width=35)
        self.combo_tip.current(0)
        self.combo_tip.grid(row=0, column=1, pady=10)
        self.combo_tip.bind("<<ComboboxSelected>>", self.tur_degisti)

        # 2. Proje (Klasör) Adı
        tk.Label(frame, text="Proje (Klasör) Adı:", bg="#34495e", fg="white").grid(row=1, column=0, sticky="w", pady=10)
        self.entry_ad = tk.Entry(frame, width=37)
        self.entry_ad.grid(row=1, column=1, pady=10)
        # Açılışta imleç direkt buraya odaklansın (Hemen yazmaya başla diye)
        self.entry_ad.focus_set()

        # 3. Ana Dosya İsmi
        self.lbl_dosya = tk.Label(frame, text="Ana Dosya Adı:", bg="#34495e", fg="#bdc3c7")
        self.lbl_dosya.grid(row=2, column=0, sticky="w", pady=10)

        self.entry_dosya = tk.Entry(frame, width=37, fg="grey")
        self.entry_dosya.grid(row=2, column=1, pady=10)
        self.placeholder_text = "Varsayılan: index.html"
        self.entry_dosya.insert(0, self.placeholder_text)
        self.entry_dosya.bind("<FocusIn>", self.clear_placeholder)
        self.entry_dosya.bind("<FocusOut>", self.add_placeholder)

        # 4. Kayıt Yeri
        tk.Label(frame, text="Kayıt Yeri:", bg="#34495e", fg="white").grid(row=3, column=0, sticky="w", pady=10)
        self.entry_yol = tk.Entry(frame, width=37)
        masaustu = os.path.join(os.path.expanduser("~"), "Desktop")
        self.entry_yol.insert(0, masaustu)
        self.entry_yol.grid(row=3, column=1, pady=10)

        tk.Button(frame, text="...", command=self.konum_sec, width=3).grid(row=3, column=2, padx=5)

        # Oluştur Butonu
        tk.Button(root, text="✨ OLUŞTUR (Enter)", command=self.projeyi_olustur,
                  bg="#27ae60", fg="white", font=("Arial", 12, "bold"), height=2, width=20).pack(pady=20)

        # İlk açılışta placeholder'ı güncelle
        self.tur_degisti(None)

    def clear_placeholder(self, event):
        if self.entry_dosya.get() == self.placeholder_text:
            self.entry_dosya.delete(0, tk.END)
            self.entry_dosya.config(fg='black')

    def add_placeholder(self, event):
        if not self.entry_dosya.get():
            self.entry_dosya.insert(0, self.placeholder_text)
            self.entry_dosya.config(fg='grey')

    def tur_degisti(self, event):
        secilen_tur = self.combo_tip.get()
        sablon = SABLONLAR[secilen_tur]
        varsayilan = f"{sablon['default_name']}{sablon['extension']}"
        self.placeholder_text = f"Varsayılan: {varsayilan} (Boş bırakırsan bu olur)"

        if self.entry_dosya.get().startswith("Varsayılan:") or not self.entry_dosya.get():
            self.entry_dosya.delete(0, tk.END)
            self.entry_dosya.insert(0, self.placeholder_text)
            self.entry_dosya.config(fg='grey')

    def konum_sec(self):
        yol = filedialog.askdirectory()
        if yol:
            self.entry_yol.delete(0, tk.END)
            self.entry_yol.insert(0, yol)

    def projeyi_olustur(self):
        proje_tipi = self.combo_tip.get()
        proje_adi = self.entry_ad.get().strip()
        ana_konum = self.entry_yol.get()

        girilen_dosya_adi = self.entry_dosya.get().strip()
        if girilen_dosya_adi == self.placeholder_text:
            girilen_dosya_adi = ""

        if not proje_adi:
            messagebox.showwarning("Hata", "Lütfen bir Proje Adı girin!")
            return

        hedef_klasor = os.path.join(ana_konum, proje_adi)

        if os.path.exists(hedef_klasor):
            messagebox.showerror("Hata", "Bu isimde bir klasör zaten var!")
            return

        try:
            sablon = SABLONLAR[proje_tipi]

            if girilen_dosya_adi:
                final_dosya_adi = girilen_dosya_adi
                if not final_dosya_adi.endswith(sablon["extension"]):
                    final_dosya_adi += sablon["extension"]
            else:
                final_dosya_adi = f"{sablon['default_name']}{sablon['extension']}"

            os.makedirs(hedef_klasor)
            for klasor in sablon["folders"]:
                os.makedirs(os.path.join(hedef_klasor, klasor), exist_ok=True)

            for dosya_key, icerik in sablon["files"].items():
                if dosya_key == "TARGET":
                    dosya_yolu = os.path.join(hedef_klasor, final_dosya_adi)
                else:
                    dosya_yolu = os.path.join(hedef_klasor, dosya_key)

                with open(dosya_yolu, "w", encoding="utf-8") as f:
                    f.write(icerik)

            # Başarılı olunca klasörü aç ve pencereyi kapat
            os.startfile(hedef_klasor)
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProjeOlusturucu(root)
    root.mainloop()