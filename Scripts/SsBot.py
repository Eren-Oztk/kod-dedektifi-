import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyautogui
import keyboard
import threading
import winsound  # SS alınca bip sesi çıkarması için
import time


class SnapShooter:
    def __init__(self, root):
        self.root = root
        self.root.title("Hızlı Çekim v1.0 - Screenshot Tool")
        self.root.geometry("600x450")
        self.is_running = False

        # --- Modern Tema Renkleri ---
        self.colors = {
            "bg": "#1e1e1e",
            "card": "#252526",
            "text": "#ffffff",
            "accent": "#e056fd",  # Neon Mor (Farklı olsun)
            "success": "#00b894",
            "input": "#2d2d2d"
        }
        self.root.configure(bg=self.colors["bg"])

        # Stil Ayarları
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"],
                             font=("Segoe UI", 10))
        self.style.configure("Card.TFrame", background=self.colors["card"], relief="flat")

        # Buton Stilleri
        self.style.configure("Accent.TButton", background=self.colors["accent"], foreground="white", borderwidth=0,
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[('active', "#be2edd")])
        self.style.configure("Stop.TButton", background="#ff4757", foreground="white", borderwidth=0,
                             font=("Segoe UI", 10, "bold"))
        self.style.map("Stop.TButton", background=[('active', "#ff6b81")])
        self.style.configure("Normal.TButton", background="#3e3e42", foreground="white", borderwidth=0)
        self.style.map("Normal.TButton", background=[('active', "#505055")])

        # Değişkenler
        self.kayit_yeri = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop", "EkranGoruntuleri"))
        self.dosya_oneki = tk.StringVar(value="ss")
        self.tetik_tusu = tk.StringVar(value="f9")

        self.arayuz_olustur()

    def arayuz_olustur(self):
        # Başlık
        header = tk.Frame(self.root, bg=self.colors["bg"], pady=15)
        header.pack(fill=tk.X)
        tk.Label(header, text="📸 SNAP SHOOTER", font=("Segoe UI", 18, "bold"), bg=self.colors["bg"],
                 fg=self.colors["accent"]).pack()
        tk.Label(header, text="Tek tuşla seri ekran görüntüsü yakala", font=("Segoe UI", 9), bg=self.colors["bg"],
                 fg="#888888").pack()

        # Ayarlar Kartı
        card = ttk.Frame(self.root, style="Card.TFrame", padding=20)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 1. Kayıt Yeri
        ttk.Label(card, text="Kayıt Klasörü:", background=self.colors["card"]).pack(anchor="w")
        f_box = ttk.Frame(card, style="Card.TFrame")
        f_box.pack(fill=tk.X, pady=(5, 15))

        self.entry_style(tk.Entry(f_box, textvariable=self.kayit_yeri)).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                             ipady=5)
        ttk.Button(f_box, text="📂 Seç", style="Normal.TButton", width=5, command=self.klasor_sec).pack(side=tk.RIGHT,
                                                                                                       padx=(5, 0))

        # 2. Tuş ve İsim (Yan Yana)
        grid_frame = ttk.Frame(card, style="Card.TFrame")
        grid_frame.pack(fill=tk.X, pady=(0, 20))

        # Sol: Tuş
        f1 = ttk.Frame(grid_frame, style="Card.TFrame")
        f1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(f1, text="Tetikleyici Tuş (Örn: f9, p, print screen):", background=self.colors["card"]).pack(
            anchor="w", pady=(0, 5))
        self.entry_style(tk.Entry(f1, textvariable=self.tetik_tusu)).pack(fill=tk.X, ipady=5)

        # Sağ: Önek
        f2 = ttk.Frame(grid_frame, style="Card.TFrame")
        f2.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(f2, text="Dosya Ön Eki (Örn: slide, ss):", background=self.colors["card"]).pack(anchor="w",
                                                                                                  pady=(0, 5))
        self.entry_style(tk.Entry(f2, textvariable=self.dosya_oneki)).pack(fill=tk.X, ipady=5)

        # Başlat / Durdur Butonları
        self.btn_baslat = ttk.Button(card, text="▶ DİNLEMEYİ BAŞLAT", style="Accent.TButton", command=self.baslat)
        self.btn_baslat.pack(fill=tk.X, ipady=8)

        self.btn_durdur = ttk.Button(card, text="⏹ DURDUR", style="Stop.TButton", command=self.durdur)
        # Başlangıçta gizli olsun veya disabled olsun, pack etmiyoruz şimdilik

        # Durum Logu
        self.lbl_durum = tk.Label(self.root, text="Hazır. Başlatmak için butona basın.", bg=self.colors["bg"],
                                  fg="#888888", font=("Consolas", 10))
        self.lbl_durum.pack(side=tk.BOTTOM, pady=15)

    def entry_style(self, widget):
        widget.config(bg=self.colors["input"], fg="white", insertbackground="white", relief=tk.FLAT)
        return widget

    def klasor_sec(self):
        d = filedialog.askdirectory()
        if d: self.kayit_yeri.set(d)

    def baslat(self):
        klasor = self.kayit_yeri.get()
        tus = self.tetik_tusu.get()

        if not os.path.exists(klasor):
            try:
                os.makedirs(klasor)
            except:
                messagebox.showerror("Hata", "Klasör oluşturulamadı!")
                return

        try:
            # Tuşu test et (Geçerli bir tuş mu?)
            keyboard.parse_hotkey(tus)
        except:
            messagebox.showerror("Hata", "Geçersiz tuş adı! (f9, a, enter gibi şeyler yazın)")
            return

        self.is_running = True

        # Arayüzü güncelle
        self.btn_baslat.pack_forget()
        self.btn_durdur.pack(fill=tk.X, ipady=8)
        self.lbl_durum.config(text=f"🔴 DİNLENİYOR... '{tus}' tuşuna basarak çek.", fg=self.colors["accent"])

        # Keyboard hook başlat
        keyboard.add_hotkey(tus, self.ekran_goruntusu_al)

    def durdur(self):
        self.is_running = False
        keyboard.unhook_all()

        self.btn_durdur.pack_forget()
        self.btn_baslat.pack(fill=tk.X, ipady=8)
        self.lbl_durum.config(text="Durduruldu.", fg="#888888")

    def ekran_goruntusu_al(self):
        if not self.is_running: return

        try:
            klasor = self.kayit_yeri.get()
            onek = self.dosya_oneki.get()

            # Akıllı İsimlendirme: ss_1 var mı? ss_2 yap.
            counter = 1
            while True:
                dosya_adi = f"{onek}_{counter}.png"
                tam_yol = os.path.join(klasor, dosya_adi)
                if not os.path.exists(tam_yol):
                    break
                counter += 1

            # Çekim Yap
            screenshot = pyautogui.screenshot()
            screenshot.save(tam_yol)

            # Sesli Bildirim (Bip)
            winsound.Beep(1000, 100)  # 1000Hz, 100ms

            # Arayüzü güncelle (Thread güvenli olması için after kullanıyoruz)
            self.root.after(0,
                            lambda: self.lbl_durum.config(text=f"✅ Kaydedildi: {dosya_adi}", fg=self.colors["success"]))

        except Exception as e:
            self.root.after(0, lambda: self.lbl_durum.config(text=f"Hata: {e}", fg="red"))

    def on_closing(self):
        keyboard.unhook_all()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SnapShooter(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()