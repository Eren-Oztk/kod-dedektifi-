import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from PIL import ImageGrab, Image, ImageTk
import threading
import time
import os
import datetime


class ClipMasterV2:
    def __init__(self, root):
        self.root = root
        self.root.title("ClipMaster v2.0 - Görsel Önizleme & Akıllı Arşiv")
        self.root.geometry("800x600")  # Resim önizleme için biraz genişlettim

        # --- Modern Tema ---
        self.colors = {
            "bg": "#1e1e1e", "card": "#252526", "text": "#ffffff",
            "accent": "#ff9f43", "list_bg": "#2d2d2d", "list_fg": "#cccccc",
            "btn_save": "#00b894", "btn_del": "#ff4757"
        }
        self.root.configure(bg=self.colors["bg"])

        # Arşiv Klasörü (Sadece manuel kayıtta kullanılacak)
        self.arsiv_yolu = os.path.join(os.path.expanduser("~"), "Desktop", "PANO_ARSIVI")
        if not os.path.exists(self.arsiv_yolu):
            os.makedirs(self.arsiv_yolu)

        # Hafıza (Verileri burada tutacağız, dosyada değil)
        self.son_metin = ""
        self.son_resim_zamani = 0
        self.pano_gecmisi = []  # [{type: 'text/image', data: ..., time: '...'}, ...]

        self.arayuz_olustur()

        # Dinleyiciyi Başlat
        self.running = True
        self.thread = threading.Thread(target=self.panoyu_dinle, daemon=True)
        self.thread.start()

    def arayuz_olustur(self):
        # Ana Panel (Split)
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors["bg"], sashwidth=5)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- SOL PANEL (LİSTE) ---
        sol_frame = tk.Frame(main_paned, bg=self.colors["bg"])
        main_paned.add(sol_frame, width=300)

        tk.Label(sol_frame, text="📋 PANO GEÇMİŞİ (RAM)", font=("Segoe UI", 12, "bold"), bg=self.colors["bg"],
                 fg=self.colors["accent"]).pack(anchor="w", pady=(0, 5))

        self.liste = tk.Listbox(sol_frame, bg=self.colors["list_bg"], fg=self.colors["list_fg"],
                                font=("Segoe UI", 10), borderwidth=0, highlightthickness=0,
                                selectbackground=self.colors["accent"])
        self.liste.pack(fill=tk.BOTH, expand=True)
        self.liste.bind('<<ListboxSelect>>', self.secileni_goster)

        # Temizle Butonu
        tk.Button(sol_frame, text="🗑️ Geçmişi Temizle", bg=self.colors["btn_del"], fg="white", relief="flat",
                  command=self.temizle).pack(fill=tk.X, pady=(10, 0))

        # --- SAĞ PANEL (ÖNİZLEME) ---
        sag_frame = tk.Frame(main_paned, bg=self.colors["card"], padx=15, pady=15)
        main_paned.add(sag_frame)

        tk.Label(sag_frame, text="👁️ İÇERİK ÖNİZLEME", font=("Segoe UI", 12, "bold"), bg=self.colors["card"],
                 fg="white").pack(anchor="w")

        # 1. Metin Alanı (Başlangıçta görünür)
        self.text_area = scrolledtext.ScrolledText(sag_frame, bg=self.colors["bg"], fg="white", font=("Consolas", 11),
                                                   borderwidth=0, height=15)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=10)

        # 2. Resim Alanı (Başlangıçta gizli)
        self.img_label = tk.Label(sag_frame, bg=self.colors["bg"], text="Resim Önizleme Yok")
        # pack() yapmıyoruz, gerektiğinde göstereceğiz

        # Kaydet Butonu
        self.btn_kaydet = tk.Button(sag_frame, text="💾 SEÇİLENİ DOSYA OLARAK ARŞİVLE", bg=self.colors["btn_save"],
                                    fg="white",
                                    font=("Segoe UI", 10, "bold"), relief="flat", command=self.secileni_arsivle)
        self.btn_kaydet.pack(fill=tk.X, pady=5)

        # Bilgi Etiketi
        self.lbl_bilgi = tk.Label(sag_frame, text="Listeden bir öğe seçin...", bg=self.colors["card"], fg="#888888")
        self.lbl_bilgi.pack(pady=5)

    def panoyu_dinle(self):
        while self.running:
            try:
                # 1. Metin Kontrolü
                try:
                    text = self.root.clipboard_get()
                    if text != self.son_metin and text.strip() != "":
                        self.son_metin = text
                        self.ekle_metin(text)
                except:
                    pass

                # 2. Resim Kontrolü
                try:
                    img = ImageGrab.grabclipboard()
                    if isinstance(img, Image.Image):
                        # Aynı resmi sürekli kaydetmemek için zaman kontrolü
                        if time.time() - self.son_resim_zamani > 2:
                            self.son_resim_zamani = time.time()
                            # Panodan gelen resmi RAM'de sakla
                            self.ekle_resim(img)
                except:
                    pass

                time.sleep(1)
            except Exception as e:
                print(e)
                time.sleep(1)

    def ekle_metin(self, text):
        tarih = datetime.datetime.now().strftime("%H:%M:%S")
        # Veriyi hafızaya at (Dosyaya değil!)
        item = {"type": "text", "data": text, "time": tarih}
        self.pano_gecmisi.insert(0, item)

        kisa = (text[:40] + '..') if len(text) > 40 else text
        kisa = kisa.replace("\n", " ")
        self.root.after(0, lambda: self.liste.insert(0, f"📝 [{tarih}] {kisa}"))

    def ekle_resim(self, img):
        tarih = datetime.datetime.now().strftime("%H:%M:%S")
        # Resmi hafızada tutuyoruz (Dosyaya yazmıyoruz)
        item = {"type": "image", "data": img, "time": tarih}
        self.pano_gecmisi.insert(0, item)

        # Resim boyutunu al
        w, h = img.size
        self.root.after(0, lambda: self.liste.insert(0, f"🖼️ [{tarih}] GÖRSEL ({w}x{h})"))

    def secileni_goster(self, event):
        secim = self.liste.curselection()
        if not secim: return

        index = secim[0]
        item = self.pano_gecmisi[index]

        # Panoya tekrar kopyala (Otomatik)
        self.root.clipboard_clear()

        if item["type"] == "text":
            # Görüntüleme: Metin kutusunu aç, resmi gizle
            self.img_label.pack_forget()
            self.text_area.pack(fill=tk.BOTH, expand=True, pady=10)

            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, item["data"])
            self.root.clipboard_append(item["data"])
            self.lbl_bilgi.config(text="✅ Metin kopyalandı. Düzenleyip kaydedebilirsiniz.")

        elif item["type"] == "image":
            # Görüntüleme: Metni gizle, resmi aç
            self.text_area.pack_forget()
            self.img_label.pack(fill=tk.BOTH, expand=True, pady=10)

            # Resmi yeniden boyutlandır (Önizleme kutusuna sığsın diye)
            orj_img = item["data"]

            # Oran koruyarak küçültme (Thumbnail)
            base_width = 400
            w_percent = (base_width / float(orj_img.size[0]))
            h_size = int((float(orj_img.size[1]) * float(w_percent)))

            # Eğer resim zaten küçükse büyütme
            if orj_img.size[0] > base_width:
                img_resized = orj_img.resize((base_width, h_size), Image.Resampling.LANCZOS)
            else:
                img_resized = orj_img

            tk_img = ImageTk.PhotoImage(img_resized)

            self.img_label.config(image=tk_img)
            self.img_label.image = tk_img  # Referansı tutmazsak silinir!

            # Panoya kopyalama (Windows'ta biraz karışıktır, şimdilik atlıyoruz veya özel kütüphane gerekir)
            # Not: Python ile panoya resim geri yüklemek zordur, o yüzden kullanıcıya bilgi veriyoruz.
            self.lbl_bilgi.config(text="🖼️ Resim seçili. Arşivlemek için butona basın.")

    def secileni_arsivle(self):
        secim = self.liste.curselection()
        if not secim: return

        index = secim[0]
        item = self.pano_gecmisi[index]
        tarih_ad = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        if item["type"] == "text":
            # Metni Kaydet
            dosya_adi = f"Not_{tarih_ad}.txt"
            yol = os.path.join(self.arsiv_yolu, dosya_adi)
            # Metin kutusundaki son hali al (Belki kullanıcı düzenlemiştir)
            guncel_metin = self.text_area.get("1.0", tk.END)
            with open(yol, "w", encoding="utf-8") as f:
                f.write(guncel_metin)
            messagebox.showinfo("Başarılı", f"Metin kaydedildi:\n{yol}")

        elif item["type"] == "image":
            # Resmi Kaydet
            dosya_adi = f"SS_{tarih_ad}.png"
            yol = os.path.join(self.arsiv_yolu, dosya_adi)
            item["data"].save(yol, "PNG")
            messagebox.showinfo("Başarılı", f"Görsel kaydedildi:\n{yol}")

    def temizle(self):
        self.liste.delete(0, tk.END)
        self.pano_gecmisi = []
        self.text_area.delete("1.0", tk.END)
        self.img_label.config(image="")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClipMasterV2(root)
    root.mainloop()