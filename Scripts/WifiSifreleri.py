import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext


# Bu scripti tek başına çalıştırırsan da çalışır,
# Launcher üzerinden çalıştırırsan da çalışır.

def sifreleri_getir():
    try:
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="ignore").split(
            '\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]

        sonuc_metni = ""

        for i in profiles:
            try:
                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8',
                                                                                                               errors="ignore").split(
                    '\n')
                results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                try:
                    sonuc_metni += "{:<30} |  {}\n".format(i, results[0])
                except IndexError:
                    sonuc_metni += "{:<30} |  {:<}\n".format(i, "")
            except subprocess.CalledProcessError:
                sonuc_metni += "{:<30} |  HATA\n".format(i)

        return sonuc_metni

    except Exception as e:
        return f"Hata oluştu: {e}"


def arayuz_goster():
    window = tk.Tk()
    window.title("Wi-Fi Şifreleri")
    window.geometry("500x400")
    window.configure(bg="#1e1e1e")

    lbl = tk.Label(window, text="KAYITLI WI-FI ŞİFRELERİ", font=("Segoe UI", 12, "bold"), bg="#1e1e1e", fg="#007acc")
    lbl.pack(pady=10)

    text_area = scrolledtext.ScrolledText(window, width=55, height=20, font=("Consolas", 10), bg="#252526",
                                          fg="#cccccc", borderwidth=0)
    text_area.pack(padx=10, pady=5)

    sifreler = sifreleri_getir()
    text_area.insert(tk.END, "WIFI ADI (SSID)                |  ŞİFRE\n")
    text_area.insert(tk.END, "-" * 50 + "\n")
    text_area.insert(tk.END, sifreler)
    text_area.config(state="disabled")  # Sadece okunabilir yap

    window.mainloop()


if __name__ == "__main__":
    arayuz_goster()