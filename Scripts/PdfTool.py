import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PyPDF2 import PdfMerger
from PIL import Image


class PdfIsvicreCakisi:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF İsviçre Çakısı - Merge & Convert")
        self.root.geometry("600x500")

        # --- Modern Tema ---
        self.colors = {
            "bg": "#1e1e1e", "card": "#252526", "text": "#ffffff",
            "accent": "#ff4757",  # Kırmızımsı (PDF rengi)
            "btn": "#2f3542", "success": "#2ed573"
        }
        self.root.configure(bg=self.colors["bg"])

        # Stil Ayarları
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"])
        self.style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.colors["btn"], foreground="white", padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", self.colors["accent"])])

        # Başlık
        tk.Label(self.root, text="📑 PDF ARAÇLARI", font=("Segoe UI", 16, "bold"), bg=self.colors["bg"],
                 fg=self.colors["accent"]).pack(pady=10)

        # Sekme Yapısı
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Sekme 1: PDF Birleştir
        self.tab_merge = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_merge, text="  PDF Birleştir  ")
        self.setup_merge_tab()

        # Sekme 2: Resim -> PDF
        self.tab_img = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_img, text="  Resimden PDF'e  ")
        self.setup_img_tab()

    def setup_merge_tab(self):
        # Liste
        frame_list = tk.Frame(self.tab_merge, bg=self.colors["bg"])
        frame_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.list_merge = tk.Listbox(frame_list, bg=self.colors["card"], fg="white",
                                     selectbackground=self.colors["accent"], borderwidth=0)
        self.list_merge.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame_list, command=self.list_merge.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_merge.config(yscrollcommand=scrollbar.set)

        # Butonlar
        frame_btn = tk.Frame(self.tab_merge, bg=self.colors["bg"])
        frame_btn.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(frame_btn, text="➕ Dosya Ekle", bg=self.colors["btn"], fg="white", relief="flat",
                  command=lambda: self.dosya_ekle("pdf")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="➖ Çıkar", bg=self.colors["btn"], fg="white", relief="flat",
                  command=lambda: self.dosya_cikar(self.list_merge)).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="⬆ Yukarı", bg=self.colors["btn"], fg="white", relief="flat",
                  command=lambda: self.yukari_tasi(self.list_merge)).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="⬇ Aşağı", bg=self.colors["btn"], fg="white", relief="flat",
                  command=lambda: self.asagi_tasi(self.list_merge)).pack(side=tk.LEFT, padx=2)

        tk.Button(frame_btn, text="🚀 BİRLEŞTİR VE KAYDET", bg=self.colors["success"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", command=self.pdf_birlestir).pack(side=tk.RIGHT)

    def setup_img_tab(self):
        # Liste
        frame_list = tk.Frame(self.tab_img, bg=self.colors["bg"])
        frame_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.list_img = tk.Listbox(frame_list, bg=self.colors["card"], fg="white",
                                   selectbackground=self.colors["accent"], borderwidth=0)
        self.list_img.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame_list, command=self.list_img.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.list_img.config(yscrollcommand=scrollbar.set)

        # Butonlar
        frame_btn = tk.Frame(self.tab_img, bg=self.colors["bg"])
        frame_btn.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(frame_btn, text="➕ Resim Ekle", bg=self.colors["btn"], fg="white", relief="flat",
                  command=lambda: self.dosya_ekle("img")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="➖ Çıkar", bg=self.colors["btn"], fg="white", relief="flat",
                  command=lambda: self.dosya_cikar(self.list_img)).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="⬆ Yukarı", bg=self.colors["btn"], fg="white", relief="flat",
                  command=lambda: self.yukari_tasi(self.list_img)).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_btn, text="⬇ Aşağı", bg=self.colors["btn"], fg="white", relief="flat",
                  command=lambda: self.asagi_tasi(self.list_img)).pack(side=tk.LEFT, padx=2)

        tk.Button(frame_btn, text="📸 PDF'E DÖNÜŞTÜR", bg=self.colors["success"], fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", command=self.resim_pdf_yap).pack(side=tk.RIGHT)

    # --- Ortak Fonksiyonlar ---
    def dosya_ekle(self, tur):
        if tur == "pdf":
            files = filedialog.askopenfilenames(filetypes=[("PDF Dosyaları", "*.pdf")])
            target_list = self.list_merge
        else:
            files = filedialog.askopenfilenames(filetypes=[("Resim Dosyaları", "*.jpg;*.jpeg;*.png;*.bmp")])
            target_list = self.list_img

        for f in files:
            target_list.insert(tk.END, f)

    def dosya_cikar(self, liste_widget):
        sel = liste_widget.curselection()
        for index in sel[::-1]:
            liste_widget.delete(index)

    def yukari_tasi(self, liste_widget):
        for i in liste_widget.curselection():
            if i == 0: continue
            text = liste_widget.get(i)
            liste_widget.delete(i)
            liste_widget.insert(i - 1, text)
            liste_widget.selection_set(i - 1)

    def asagi_tasi(self, liste_widget):
        for i in liste_widget.curselection():
            if i == liste_widget.size() - 1: continue
            text = liste_widget.get(i)
            liste_widget.delete(i)
            liste_widget.insert(i + 1, text)
            liste_widget.selection_set(i + 1)

    # --- İşlem Fonksiyonları ---
    def pdf_birlestir(self):
        files = self.list_merge.get(0, tk.END)
        if not files: return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not save_path: return

        try:
            merger = PdfMerger()
            for pdf in files:
                merger.append(pdf)
            merger.write(save_path)
            merger.close()
            messagebox.showinfo("Başarılı", f"PDF'ler birleştirildi!\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir sorun oluştu:\n{e}")

    def resim_pdf_yap(self):
        files = self.list_img.get(0, tk.END)
        if not files: return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not save_path: return

        try:
            image_list = []
            first_image = None

            for f in files:
                img = Image.open(f)
                img = img.convert('RGB')  # PDF için RGB şart
                if first_image is None:
                    first_image = img
                else:
                    image_list.append(img)

            if first_image:
                first_image.save(save_path, save_all=True, append_images=image_list)
                messagebox.showinfo("Başarılı", f"Resimler PDF yapıldı!\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Bir sorun oluştu:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PdfIsvicreCakisi(root)
    root.mainloop()