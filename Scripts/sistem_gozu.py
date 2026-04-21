import tkinter as tk
import psutil
import time
import threading

try:
    import GPUtil
except ImportError:
    GPUtil = None


class SistemGozuPro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistem Gözü Pro")

        # --- PENCERE AYARLARI ---
        self.root.overrideredirect(True)  # Çerçevesiz
        self.root.attributes("-topmost", True)  # Hep üstte
        self.root.attributes("-alpha", 0.85)  # Şeffaflık
        self.root.configure(bg='#121212')  # Koyu tema (Spotify/Discord siyahı)

        # Boyut ve Konum (Sağ üst köşe)
        w, h = 220, 150
        x_pos = self.root.winfo_screenwidth() - w - 20
        y_pos = 20
        self.root.geometry(f"{w}x{h}+{x_pos}+{y_pos}")

        # --- ÜST BAR (BAŞLIK ve KAPATMA) ---
        # Sürüklemek için bir tutma alanı
        title_bar = tk.Frame(self.root, bg="#1e1e1e", height=25)
        title_bar.pack(fill="x", side="top")

        # Başlık
        lbl_title = tk.Label(title_bar, text="SYSTEM HUD", fg="#bbbbbb", bg="#1e1e1e", font=("Impact", 10))
        lbl_title.pack(side="left", padx=5)

        # Kapatma Butonu (X)
        self.btn_close = tk.Label(title_bar, text="✕", fg="white", bg="#1e1e1e", font=("Arial", 10, "bold"), width=4,
                                  cursor="hand2")
        self.btn_close.pack(side="right")
        # Hover Efekti
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.config(bg="#d32f2f"))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.config(bg="#1e1e1e"))
        self.btn_close.bind("<Button-1>", lambda e: self.root.destroy())

        # Sürükleme Özelliği (Üst bardan tutup çek)
        title_bar.bind("<Button-1>", self.baslat_tasima)
        title_bar.bind("<B1-Motion>", self.tasi)

        # --- GÖVDE (VERİLER) ---
        self.frame_data = tk.Frame(self.root, bg="#121212", padx=10, pady=5)
        self.frame_data.pack(fill="both", expand=True)

        # Etiketler (Label)
        self.lbl_cpu = self.etiket_olustur("CPU: %0")
        self.lbl_ram = self.etiket_olustur("RAM: %0")
        self.lbl_gpu = self.etiket_olustur("GPU: --")
        self.lbl_disk = self.etiket_olustur("DSK: 0 MB/s")
        self.lbl_net = self.etiket_olustur("NET: 0 KB/s")

        # Değişkenler (Hız hesabı için)
        self.last_net = psutil.net_io_counters()
        self.last_disk = psutil.disk_io_counters()
        self.last_time = time.time()

        # Güncelleme
        self.bilgileri_guncelle()
        self.root.mainloop()

    def etiket_olustur(self, metin):
        lbl = tk.Label(self.frame_data, text=metin, font=("Consolas", 10, "bold"),
                       fg="#00ff00", bg="#121212", anchor="w")
        lbl.pack(fill="x", pady=1)
        return lbl

    def baslat_tasima(self, event):
        self.x = event.x
        self.y = event.y

    def tasi(self, event):
        x = self.root.winfo_pointerx() - self.x
        y = self.root.winfo_pointery() - self.y
        self.root.geometry(f"+{x}+{y}")

    def renk_belirle(self, yuzde, limit=80):
        if yuzde < 50: return "#00ff00"  # Yeşil
        if yuzde < limit: return "#ffeb3b"  # Sarı
        return "#ff1744"  # Kırmızı

    def bilgileri_guncelle(self):
        try:
            # 1. CPU & RAM
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent

            self.lbl_cpu.config(text=f"CPU: %{cpu:<3}", fg=self.renk_belirle(cpu))
            self.lbl_ram.config(text=f"RAM: %{ram:<3}", fg=self.renk_belirle(ram, 85))

            # 2. GPU (NVIDIA RTX 4070)
            if GPUtil:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # İlk ekran kartı
                    load = gpu.load * 100
                    temp = gpu.temperature
                    # GPU verisi: %Yük | Sıcaklık
                    self.lbl_gpu.config(text=f"GPU: %{int(load):<2} | {temp}°C", fg=self.renk_belirle(temp, 75))
                else:
                    self.lbl_gpu.config(text="GPU: Yok/AMD", fg="#757575")

            # 3. Disk & Net Hızı Hesabı
            current_time = time.time()
            dt = current_time - self.last_time

            if dt > 0.5:  # Çok hızlı yenileme yapma
                net = psutil.net_io_counters()
                disk = psutil.disk_io_counters()

                # Net
                d_speed = (net.bytes_recv - self.last_net.bytes_recv) / 1024 / dt
                u_speed = (net.bytes_sent - self.last_net.bytes_sent) / 1024 / dt

                # Disk
                read_speed = (disk.read_bytes - self.last_disk.read_bytes) / 1024 / 1024 / dt  # MB
                write_speed = (disk.write_bytes - self.last_disk.write_bytes) / 1024 / 1024 / dt  # MB

                # Formatla
                net_str = f"⬇{int(d_speed)} ⬆{int(u_speed)} KB"
                if d_speed > 1024: net_str = f"⬇{d_speed / 1024:.1f} ⬆{u_speed / 1024:.1f} MB"

                disk_str = f"R:{read_speed:.1f} W:{write_speed:.1f} MB/s"

                self.lbl_net.config(text=net_str, fg="#03a9f4")  # Mavi
                self.lbl_disk.config(text=disk_str, fg="#e040fb")  # Mor

                # Değerleri güncelle
                self.last_net = net
                self.last_disk = disk
                self.last_time = current_time

        except Exception as e:
            print(f"Hata: {e}")

        # 1000ms (1 saniye) sonra tekrar çalış
        self.root.after(1000, self.bilgileri_guncelle)


if __name__ == "__main__":
    SistemGozuPro()